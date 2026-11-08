"""Bankanın kart teslim servisi: tüm iş kuralları ve kapasite garantileri burada.

LLM'e güvenilmez: kimlik doğrulama, kapasite, ilçe kontrolü ve tek aktif randevu
kuralları bu katmanda (ve DB kısıtlarında) uygulanır.
"""
from __future__ import annotations

import json
import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path

SCHEMA = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")
TABLES = ["call_events", "notifications", "escalations", "waitlist_entries",
          "appointments", "calls", "delivery_slots", "customers"]

MAX_VERIFY_ATTEMPTS = 2
ESCALATION_REASONS = {"capacity_request", "address_change", "third_party",
                      "verification_failed", "customer_request", "other"}

DAYS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
MONTHS = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz",
          "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
ADDRESS_LABEL = {"home": "ev", "work": "iş yeri"}

CUSTOMERS = [
    ("Ayşe Kaya", "0532 000 00 01", "1988-03-14", "Kadıköy", "home"),
    ("Mehmet Demir", "0532 000 00 02", "1975-11-02", "Kadıköy", "work"),
    ("Zeynep Arslan", "0532 000 00 03", "1993-06-27", "Kadıköy", "home"),
    ("Can Yıldız", "0532 000 00 04", "1981-01-09", "Ataşehir", "home"),
    ("Elif Şahin", "0532 000 00 05", "1990-08-30", "Ataşehir", "work"),
    ("Burak Çelik", "0532 000 00 06", "1969-12-18", "Şişli", "home"),
    ("Selin Aydın", "0532 000 00 07", "1999-04-05", "Şişli", "home"),
    ("Ali Öztürk", "0532 000 00 08", "1984-07-21", "Beşiktaş", "work"),
]
# (ilçe, hafta günü 3=Perşembe 4=Cuma, başlangıç, bitiş, kapasite)
SLOTS = [
    ("Kadıköy", 3, "09:00", "13:00", 1),
    ("Kadıköy", 4, "14:00", "18:00", 1),
    ("Ataşehir", 3, "14:00", "18:00", 2),
    ("Şişli", 4, "09:00", "13:00", 2),
    ("Beşiktaş", 3, "09:00", "13:00", 1),
]


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def date_label(d: date) -> str:
    return f"{DAYS[d.weekday()]} {d.day} {MONTHS[d.month - 1]}"


def upcoming(today: date, weekday: int) -> date:
    return today + timedelta(days=(weekday - today.weekday()) % 7)


def parse_birth_date(value: str) -> str | None:
    """YYYY-MM-DD (tercih edilen) veya DD.MM.YYYY / DD/MM/YYYY kabul eder."""
    value = (value or "").strip()
    m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", value)
    if m:
        y, mo, d = m.groups()
    else:
        m = re.fullmatch(r"(\d{1,2})[./](\d{1,2})[./](\d{4})", value)
        if not m:
            return None
        d, mo, y = m.groups()
    try:
        return date(int(y), int(mo), int(d)).isoformat()
    except ValueError:
        return None


def mask_phone(phone: str) -> str:
    return phone[:4] + " *** ** " + phone[-2:]


class BankError(Exception):
    def __init__(self, code: str, status: int = 400, **extra):
        super().__init__(code)
        self.code, self.status, self.extra = code, status, extra

    def body(self) -> dict:
        return {"ok": False, "error": self.code, **self.extra}


class Bank:
    def __init__(self, db_path: str | Path, today: date):
        self.db_path = Path(db_path)
        self.today = today

    # ---------- altyapı ----------
    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, isolation_level=None, timeout=10,
                               check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @contextmanager
    def _tx(self):
        """Yazma işlemleri: BEGIN IMMEDIATE ile tek yazar, hata olursa rollback."""
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            yield conn
            conn.execute("COMMIT")
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

    @contextmanager
    def _read(self):
        conn = self._connect()
        try:
            yield conn
        finally:
            conn.close()

    def init(self, reset: bool = False) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._read() as conn:
            conn.execute("PRAGMA journal_mode = WAL")
            if reset:
                conn.executescript("".join(f"DROP TABLE IF EXISTS {t};" for t in TABLES))
            conn.executescript(SCHEMA)
            if conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 0:
                conn.executemany(
                    "INSERT INTO customers(full_name, phone, birth_date, district, address_type)"
                    " VALUES (?,?,?,?,?)", CUSTOMERS)
                conn.executemany(
                    "INSERT INTO delivery_slots(district, slot_date, start_time, end_time, capacity)"
                    " VALUES (?,?,?,?,?)",
                    [(d, upcoming(self.today, wd).isoformat(), s, e, c) for d, wd, s, e, c in SLOTS])

    # ---------- yardımcılar ----------
    @staticmethod
    def _slot_view(r: sqlite3.Row) -> dict:
        d = date.fromisoformat(r["slot_date"])
        return {
            "slot_id": r["id"], "district": r["district"], "date": r["slot_date"],
            "day": DAYS[d.weekday()], "start": r["start_time"], "end": r["end_time"],
            "label": f"{date_label(d)}, {r['start_time']}-{r['end_time']}",
            "remaining": r["capacity"] - r["booked"], "capacity": r["capacity"],
        }

    @staticmethod
    def _customer_view(call: sqlite3.Row) -> dict:
        return {"first_name": call["full_name"].split()[0], "full_name": call["full_name"],
                "district": call["district"],
                "delivery_address": ADDRESS_LABEL[call["address_type"]]}

    @staticmethod
    def _call(conn, call_id: str, open_only: bool = True) -> sqlite3.Row:
        row = conn.execute(
            "SELECT c.*, u.full_name, u.birth_date, u.district, u.address_type"
            " FROM calls c JOIN customers u ON u.id = c.customer_id WHERE c.id = ?",
            (call_id,)).fetchone()
        if not row:
            raise BankError("call_not_found", 404)
        if open_only and row["ended_at"]:
            raise BankError("call_ended", 409)
        return row

    @staticmethod
    def _require_verified(call: sqlite3.Row) -> None:
        if not call["verified_at"]:
            raise BankError("not_verified", 403,
                            hint="Önce verify_identity ile kimlik doğrulanmalı.")

    def _district_slots(self, conn, district: str) -> list[dict]:
        rows = conn.execute(
            "SELECT * FROM delivery_slots WHERE district = ? ORDER BY slot_date, start_time",
            (district,)).fetchall()
        return [self._slot_view(r) for r in rows]

    def _active_appointment(self, conn, customer_id: int) -> dict | None:
        r = conn.execute(
            "SELECT a.id AS appointment_id, a.source, s.* FROM appointments a"
            " JOIN delivery_slots s ON s.id = a.slot_id"
            " WHERE a.customer_id = ? AND a.status = 'confirmed'", (customer_id,)).fetchone()
        if not r:
            return None
        return {"appointment_id": r["appointment_id"], "source": r["source"], **self._slot_view(r)}

    @staticmethod
    def _notify(conn, customer_id: int, body: str) -> None:
        conn.execute("INSERT INTO notifications(customer_id, body, created_at) VALUES (?,?,?)",
                     (customer_id, body, now()))

    # ---------- arama yaşam döngüsü ----------
    def start_call(self, customer_id: int) -> dict:
        with self._tx() as conn:
            cust = conn.execute("SELECT id, full_name FROM customers WHERE id = ?",
                                (customer_id,)).fetchone()
            if not cust:
                raise BankError("customer_not_found", 404)
            call_id = uuid.uuid4().hex[:12]
            conn.execute("INSERT INTO calls(id, customer_id, started_at) VALUES (?,?,?)",
                         (call_id, customer_id, now()))
        return {"ok": True, "call_id": call_id,
                "customer": {"id": cust["id"], "full_name": cust["full_name"]}}

    def verify_identity(self, call_id: str, birth_date: str) -> dict:
        parsed = parse_birth_date(birth_date)
        if not parsed:
            raise BankError("invalid_format", 422, hint="Doğum tarihini YYYY-MM-DD gönder.")
        with self._tx() as conn:
            call = self._call(conn, call_id)
            if call["verified_at"]:
                return {"ok": True, "verified": True, "customer": self._customer_view(call)}
            if call["verification_attempts"] >= MAX_VERIFY_ATTEMPTS:
                raise BankError("locked", 423, verified=False, locked=True)
            attempts = call["verification_attempts"] + 1
            if parsed == call["birth_date"]:
                conn.execute("UPDATE calls SET verification_attempts = ?, verified_at = ? WHERE id = ?",
                             (attempts, now(), call_id))
                return {"ok": True, "verified": True, "customer": self._customer_view(call)}
            conn.execute("UPDATE calls SET verification_attempts = ? WHERE id = ?",
                         (attempts, call_id))
            if attempts >= MAX_VERIFY_ATTEMPTS:
                conn.execute(
                    "INSERT INTO escalations(customer_id, call_id, reason, note, created_at)"
                    " VALUES (?,?,?,?,?)",
                    (call["customer_id"], call_id, "verification_failed",
                     f"{MAX_VERIFY_ATTEMPTS} hatalı doğum tarihi denemesi", now()))
                return {"ok": True, "verified": False, "locked": True}
            return {"ok": True, "verified": False, "attempts_left": MAX_VERIFY_ATTEMPTS - attempts}

    def list_slots(self, call_id: str) -> dict:
        with self._read() as conn:
            call = self._call(conn, call_id)
            self._require_verified(call)
            slots = self._district_slots(conn, call["district"])
            free = [s for s in slots if s["remaining"] > 0]
            res = {"ok": True, "district": call["district"], "slots": free,
                   "current_appointment": self._active_appointment(conn, call["customer_id"]),
                   "overflow": None}
            if not free:
                res["overflow"] = {
                    "reason": "district_full",
                    "options": ["waitlist", "next_week_priority", "capacity_request"],
                    "district_slots": slots,
                }
            return res

    def book_slot(self, call_id: str, slot_id: int) -> dict:
        with self._tx() as conn:
            call = self._call(conn, call_id)
            self._require_verified(call)
            cid = call["customer_id"]
            slot = conn.execute("SELECT * FROM delivery_slots WHERE id = ?", (slot_id,)).fetchone()
            if not slot:
                raise BankError("slot_not_found", 404)
            if slot["district"] != call["district"]:
                raise BankError("wrong_district", 409, district=call["district"])
            existing = self._active_appointment(conn, cid)
            if existing:
                raise BankError("already_booked", 409, appointment=existing)
            cur = conn.execute(
                "UPDATE delivery_slots SET booked = booked + 1 WHERE id = ? AND booked < capacity",
                (slot_id,))
            if cur.rowcount == 0:
                free = [s for s in self._district_slots(conn, call["district"]) if s["remaining"] > 0]
                raise BankError("slot_full", 409, available=free)
            aid = conn.execute(
                "INSERT INTO appointments(customer_id, slot_id, call_id, status, source, created_at)"
                " VALUES (?,?,?,'confirmed','call',?)", (cid, slot_id, call_id, now())).lastrowid
            conn.execute("UPDATE waitlist_entries SET status = 'cancelled'"
                         " WHERE customer_id = ? AND status = 'waiting'", (cid,))
            view = self._slot_view(conn.execute("SELECT * FROM delivery_slots WHERE id = ?",
                                                (slot_id,)).fetchone())
            self._notify(conn, cid,
                         f"Freya: Kartınız {view['label']} arasında {ADDRESS_LABEL[call['address_type']]}"
                         " adresinize teslim edilecek. Kart yalnızca size, kimliğiniz görülerek verilir.")
        return {"ok": True, "booked": True, "appointment_id": aid, "slot": view}

    def join_waitlist(self, call_id: str, accepted_slot_ids: list[int]) -> dict:
        with self._tx() as conn:
            call = self._call(conn, call_id)
            self._require_verified(call)
            cid = call["customer_id"]
            if self._active_appointment(conn, cid):
                raise BankError("already_booked", 409)
            slots = self._district_slots(conn, call["district"])
            free = [s for s in slots if s["remaining"] > 0]
            if free:
                raise BankError("slots_available", 409, available=free,
                                hint="Boş slot varken bekleme listesine alınmaz; slot teklif et.")
            ids = {s["slot_id"] for s in slots}
            accepted = [int(i) for i in accepted_slot_ids or []]
            if any(i not in ids for i in accepted):
                raise BankError("invalid_slot", 422, district_slots=slots)
            existing = conn.execute("SELECT id FROM waitlist_entries WHERE customer_id = ?"
                                    " AND status = 'waiting'", (cid,)).fetchone()
            if existing:
                wid = existing["id"]
                conn.execute("UPDATE waitlist_entries SET accepted_slot_ids = ? WHERE id = ?",
                             (json.dumps(accepted), wid))
            else:
                wid = conn.execute(
                    "INSERT INTO waitlist_entries(customer_id, call_id, accepted_slot_ids, status, created_at)"
                    " VALUES (?,?,?,'waiting',?)", (cid, call_id, json.dumps(accepted), now())).lastrowid
            position = conn.execute(
                "SELECT COUNT(*) FROM waitlist_entries w JOIN customers c ON c.id = w.customer_id"
                " WHERE c.district = ? AND w.status = 'waiting' AND w.id <= ?",
                (call["district"], wid)).fetchone()[0]
            self._notify(conn, cid,
                         f"Freya: Bu haftaki teslimat için bekleme listesindesiniz (sıra {position})."
                         " Yer açılırsa teslim zamanınızı SMS ile bildireceğiz; açılmazsa gelecek"
                         " hafta önceliklisiniz.")
        return {"ok": True, "waitlisted": True, "position": position, "next_week_priority": True}

    def escalate(self, call_id: str, reason: str, note: str | None = None) -> dict:
        if reason not in ESCALATION_REASONS:
            raise BankError("invalid_reason", 422, allowed=sorted(ESCALATION_REASONS))
        with self._tx() as conn:
            call = self._call(conn, call_id)
            tid = conn.execute(
                "INSERT INTO escalations(customer_id, call_id, reason, note, created_at)"
                " VALUES (?,?,?,?,?)", (call["customer_id"], call_id, reason, note, now())).lastrowid
        return {"ok": True, "ticket_id": tid, "message": "Talep operasyon ekibine iletildi."}

    def end_call(self, call_id: str, summary: str | None = None) -> dict:
        with self._tx() as conn:
            call = self._call(conn, call_id, open_only=False)
            if call["ended_at"]:
                return {"ok": True, "outcome": call["outcome"], "already_ended": True}
            outcome = self._outcome(conn, call)
            conn.execute("UPDATE calls SET ended_at = ?, outcome = ?, summary = ? WHERE id = ?",
                         (now(), outcome, summary, call_id))
        return {"ok": True, "outcome": outcome}

    def _outcome(self, conn, call: sqlite3.Row) -> str:
        cid = call["customer_id"]
        if conn.execute("SELECT 1 FROM appointments WHERE customer_id = ? AND status = 'confirmed'",
                        (cid,)).fetchone():
            return "scheduled"
        if conn.execute("SELECT 1 FROM waitlist_entries WHERE customer_id = ? AND status = 'waiting'",
                        (cid,)).fetchone():
            return "waitlisted"
        if not call["verified_at"] and call["verification_attempts"] >= MAX_VERIFY_ATTEMPTS:
            return "verification_failed"
        if conn.execute("SELECT 1 FROM escalations WHERE call_id = ?", (call["id"],)).fetchone():
            return "escalated"
        if not call["verified_at"]:
            return "not_reached"
        return "declined"

    # ---------- operasyon (UI) ----------
    def cancel_appointment(self, appointment_id: int) -> dict:
        """Teslimat iptali; boşalan yer bekleme listesindeki ilk uygun müşteriye otomatik atanır."""
        with self._tx() as conn:
            a = conn.execute("SELECT * FROM appointments WHERE id = ? AND status = 'confirmed'",
                             (appointment_id,)).fetchone()
            if not a:
                raise BankError("appointment_not_found", 404)
            conn.execute("UPDATE appointments SET status = 'cancelled', cancelled_at = ? WHERE id = ?",
                         (now(), appointment_id))
            conn.execute("UPDATE delivery_slots SET booked = booked - 1 WHERE id = ?", (a["slot_id"],))
            w = conn.execute(
                "SELECT w.* FROM waitlist_entries w, json_each(w.accepted_slot_ids) j"
                " WHERE w.status = 'waiting' AND j.value = ? ORDER BY w.created_at, w.id LIMIT 1",
                (a["slot_id"],)).fetchone()
            promoted = None
            if w:
                conn.execute("UPDATE delivery_slots SET booked = booked + 1"
                             " WHERE id = ? AND booked < capacity", (a["slot_id"],))
                conn.execute(
                    "INSERT INTO appointments(customer_id, slot_id, call_id, status, source, created_at)"
                    " VALUES (?,?,NULL,'confirmed','waitlist_promotion',?)",
                    (w["customer_id"], a["slot_id"], now()))
                conn.execute("UPDATE waitlist_entries SET status = 'promoted' WHERE id = ?", (w["id"],))
                slot = self._slot_view(conn.execute("SELECT * FROM delivery_slots WHERE id = ?",
                                                    (a["slot_id"],)).fetchone())
                self._notify(conn, w["customer_id"],
                             f"Freya: Kartınız için yer açıldı! Teslimat: {slot['label']}."
                             " Kimliğinizi hazır bulundurun. Uygun değilse bu mesajı yanıtlayın.")
                name = conn.execute("SELECT full_name FROM customers WHERE id = ?",
                                    (w["customer_id"],)).fetchone()[0]
                promoted = {"customer_id": w["customer_id"], "full_name": name, "slot": slot}
        return {"ok": True, "cancelled": appointment_id, "promoted": promoted}

    def add_event(self, call_id: str, kind: str, payload: dict) -> dict:
        with self._tx() as conn:
            conn.execute("INSERT INTO call_events(call_id, ts, kind, payload) VALUES (?,?,?,?)",
                         (call_id, now(), kind, json.dumps(payload, ensure_ascii=False)))
        return {"ok": True}

    def events(self, call_id: str) -> dict:
        with self._read() as conn:
            rows = conn.execute("SELECT ts, kind, payload FROM call_events WHERE call_id = ? ORDER BY id",
                                (call_id,)).fetchall()
        return {"ok": True, "events": [{"ts": r["ts"], "kind": r["kind"],
                                        **json.loads(r["payload"])} for r in rows]}

    def board(self) -> dict:
        with self._read() as conn:
            slot_rows = conn.execute("SELECT * FROM delivery_slots ORDER BY slot_date, start_time, district").fetchall()
            booked_by = {}
            for r in conn.execute("SELECT a.id, a.slot_id, a.source, c.full_name FROM appointments a"
                                  " JOIN customers c ON c.id = a.customer_id WHERE a.status = 'confirmed'"):
                booked_by.setdefault(r["slot_id"], []).append(r["full_name"])
            slots = [{**self._slot_view(r), "booked": r["booked"], "customers": booked_by.get(r["id"], [])}
                     for r in slot_rows]

            customers = []
            for c in conn.execute("SELECT * FROM customers ORDER BY id").fetchall():
                appt = self._active_appointment(conn, c["id"])
                wait = conn.execute("SELECT * FROM waitlist_entries WHERE customer_id = ? AND status = 'waiting'",
                                    (c["id"],)).fetchone()
                last = conn.execute("SELECT id, outcome, ended_at FROM calls WHERE customer_id = ?"
                                    " ORDER BY started_at DESC, rowid DESC LIMIT 1", (c["id"],)).fetchone()
                if appt:
                    status = "scheduled"
                elif wait:
                    status = "waitlisted"
                elif last and last["outcome"]:
                    status = last["outcome"]
                else:
                    status = "pending"
                customers.append({
                    "id": c["id"], "full_name": c["full_name"], "phone": mask_phone(c["phone"]),
                    "district": c["district"], "delivery_address": ADDRESS_LABEL[c["address_type"]],
                    "status": status, "appointment": appt, "last_call_id": last["id"] if last else None,
                })

            waitlist = [dict(r) | {"accepted_slot_ids": json.loads(r["accepted_slot_ids"])} for r in conn.execute(
                "SELECT w.id, w.customer_id, c.full_name, c.district, w.accepted_slot_ids, w.created_at"
                " FROM waitlist_entries w JOIN customers c ON c.id = w.customer_id"
                " WHERE w.status = 'waiting' ORDER BY w.created_at, w.id")]
            escalations = [dict(r) for r in conn.execute(
                "SELECT e.id, c.full_name, e.reason, e.note, e.status, e.created_at FROM escalations e"
                " JOIN customers c ON c.id = e.customer_id ORDER BY e.id DESC")]
            sms = [dict(r) for r in conn.execute(
                "SELECT n.id, c.full_name, n.body, n.created_at FROM notifications n"
                " JOIN customers c ON c.id = n.customer_id ORDER BY n.id DESC LIMIT 20")]
        return {"ok": True, "customers": customers, "slots": slots, "waitlist": waitlist,
                "escalations": escalations, "sms": sms,
                "totals": {"customers": len(customers), "capacity": sum(s["capacity"] for s in slots)}}
