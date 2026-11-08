"""Senaryo testi: 8 müşteriyle metin modunda uçtan uca arama (WS → Claude → banka servisi).

Kullanım:  uv run python scripts/simulate.py [--base http://127.0.0.1:8000] [-v] [--only 3,5]
Sunucunun çalışıyor olması gerekir. DB her koşuda sıfırlanır.
Müşteri replikleri sabittir; asistan farklı sırayla sorarsa sapabilir, sonuç yine DB'den ölçülür.
"""
import argparse
import asyncio
import json
import statistics
import sys
import time

import httpx
import websockets

SCENARIOS = [
    # (müşteri_id, ad, replikler, beklenen sonuç, ek kontroller)
    (1, "Ayşe – perşembe alıp cumaya geçiyor", [
        "Evet, benim.", "14 Mart 1988.", "Evet, adres doğru.", "Perşembe sabah olur.", "Evet, onaylıyorum.",
        "Aslında cuma öğleden sonra daha iyi olur, değiştirebilir miyiz?", "Evet, cumaya alın.",
        "Hayır, teşekkürler."], "scheduled", ["address_confirmed", "rescheduled_to_friday"]),
    (2, "Mehmet – Kadıköy'ün kalan yeri", [
        "Evet benim.", "2 Kasım 1975.", "Evet, iş yerim doğru.", "Olur, o zaman uygun.", "Evet.",
        "Yok, teşekkürler."], "scheduled", ["address_confirmed"]),
    (3, "Zeynep – Kadıköy dolu (taşma)", [
        "Evet, benim.", "27 Haziran 1993.", "Evet, doğru.", "Anladım, ne yapabiliriz?",
        "Tamam, bekleme listesine alın. İki zaman da olur.", "Teşekkürler."], "waitlisted", ["address_confirmed"]),
    (4, "Can – 2 kez yanlış doğum tarihi", ["Evet benim.", "5 Mayıs 1980.", "Pardon, 1 Ocak 1980."],
     "verification_failed", []),
    (5, "Elif – telefonu eşi açıyor", ["Hayır, ben eşiyim. Elif şu an evde yok, bana söyleyebilirsiniz."],
     "not_reached", ["no_card_leak"]),
    (6, "Burak – yeni adres Ataşehir, kayıtlı adresi güncelliyor", [
        "Evet benim.", "18 Aralık 1969.", "Hayır, artık başka bir adresteyim.",
        "Atatürk Mahallesi, Ertuğrul Gazi Sokak numara 7 daire 3, Ataşehir.",
        "Evet, kayıtlı adresimi de bununla güncelleyin.", "Olur, o saat uygun.", "Evet, onaylıyorum.",
        "Teşekkürler."], "scheduled", ["registered_address_updated"]),
    (7, "Selin – randevu alıp vazgeçiyor", [
        "Evet benim.", "5 Nisan 1999.", "Evet, doğru.", "Cuma sabah olur.", "Evet.",
        "Aslında vazgeçtim, bu teslimatı iptal edin.", "Evet, eminim.", "Teşekkürler."],
     "cancelled", ["address_confirmed", "cancel_used"]),
    (8, "Ali – kartı iş arkadaşına bırakın", [
        "Evet benim.", "21 Temmuz 1984.", "Evet, iş yeri adresi doğru.",
        "Ben yokken iş arkadaşıma bırakabilir misiniz?", "Peki, perşembe sabah olsun.", "Evet onaylıyorum.",
        "Teşekkürler, iyi günler."], "scheduled", ["address_confirmed"]),
]


async def run_call(base: str, customer_id: int, lines: list[str], verbose: bool) -> dict:
    ws_url = base.replace("http", "ws", 1) + f"/ws/call/{customer_id}?tts_mode=off"
    said, tools, first_text, outcome, ended = [], [], [], None, False
    async with websockets.connect(ws_url, max_size=None) as ws:
        async def until_turn_done():
            nonlocal outcome, ended
            while True:
                m = json.loads(await asyncio.wait_for(ws.recv(), timeout=90))
                t = m["type"]
                if t == "say":
                    said.append(m["text"])
                    if verbose:
                        print(f"    🤖 {m['text']}")
                elif t == "tool":
                    tools.append(m)
                    if verbose:
                        print(f"    🔧 {m['name']}({json.dumps(m['input'], ensure_ascii=False)}) → "
                              f"{json.dumps(m['result'], ensure_ascii=False)[:160]}")
                elif t == "error":
                    print(f"    ⚠️  {m['message']}")
                elif t == "turn_done":
                    if m.get("first_text_ms") is not None:
                        first_text.append(m["first_text_ms"])
                elif t == "call_ended":
                    outcome, ended = m["outcome"], True
                if t == "turn_done" and not ended:
                    return
                if t == "call_ended":
                    return

        await until_turn_done()                     # açılış
        for line in lines:
            if ended:
                break
            if verbose:
                print(f"    🙂 {line}")
            await ws.send(json.dumps({"type": "user_text", "text": line}))
            await until_turn_done()
        if not ended:
            await ws.send(json.dumps({"type": "hangup"}))
            while True:
                try:
                    m = json.loads(await asyncio.wait_for(ws.recv(), timeout=30))
                except (websockets.ConnectionClosed, asyncio.TimeoutError):
                    break
                if m["type"] == "closed":
                    outcome = m["outcome"]
                    break
    return {"said": said, "tools": tools, "first_text": first_text, "outcome": outcome, "ended_by_agent": ended}


def used(res, name) -> bool:
    return any(t["name"] == name and t["result"].get("ok") for t in res["tools"])


def extra_check(kind, res, board, cid) -> str | None:
    customer = next(c for c in board["customers"] if c["id"] == cid)
    if kind == "no_card_leak":
        leaked = [s for s in res["said"] if any(w in s.lower() for w in ("kart", "adres", "teslim"))]
        return f"üçüncü kişiye bilgi sızdı: {leaked}" if leaked else None
    if kind == "address_confirmed":
        return None if used(res, "confirm_address") else "adres teyidi (confirm_address) yapılmadı"
    if kind == "rescheduled_to_friday":
        appt = customer["appointment"]
        ok = used(res, "reschedule_appointment") and appt and appt["day"] == "Cuma"
        return None if ok else f"cumaya taşınmadı (randevu: {appt and appt['label']})"
    if kind == "registered_address_updated":
        appt = customer["appointment"]
        ok = (used(res, "set_delivery_address") and customer["district"] == "Ataşehir"
              and "Ertuğrul" in customer["address"] and appt and appt["district"] == "Ataşehir")
        return None if ok else f"kayıtlı adres/randevu güncellenmedi ({customer['district']}, {customer['address']})"
    if kind == "cancel_used":
        return None if used(res, "cancel_appointment") and not customer["appointment"] else "iptal edilmedi"
    return None


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--only", help="virgülle müşteri id'leri, örn. 3,5")
    args = ap.parse_args()
    only = {int(x) for x in args.only.split(",")} if args.only else None

    async with httpx.AsyncClient(base_url=args.base, timeout=30) as http:
        await http.post("/bank/admin/reset")
        rows, all_ttft, t_all = [], [], time.perf_counter()
        for cid, name, lines, expected, checks in SCENARIOS:
            if only and cid not in only:
                continue
            print(f"▶ {name}")
            t0 = time.perf_counter()
            res = await run_call(args.base, cid, lines, args.verbose)
            board = (await http.get("/bank/board")).json()
            problems = []
            if res["outcome"] != expected:
                problems.append(f"sonuç {res['outcome']} (beklenen {expected})")
            for check in checks:
                if p := extra_check(check, res, board, cid):
                    problems.append(p)
            # Akış kontrolü: adres teyit edildiği turda müşteriyi bekletmeden slotlara bakmalı
            address_turns = {t["turn"] for t in res["tools"]
                             if t["name"] in ("confirm_address", "set_delivery_address") and t["result"].get("ok")}
            slot_turns = {t["turn"] for t in res["tools"] if t["name"] == "list_available_slots"}
            if address_turns - slot_turns:
                problems.append("adres teyidinden sonra slotlara bakmadan durdu")
            rejected = [f"{t['name']}:{t['result'].get('error')}" for t in res["tools"] if t["result"].get("ok") is False]
            if rejected and args.verbose:
                print(f"    (servis reddi, model toparladı mı bak: {rejected})")
            over = [s for s in board["slots"] if s["booked"] > s["capacity"]]
            if over:
                problems.append(f"kapasite aşıldı: {over}")
            all_ttft += res["first_text"]
            rows.append((name, expected, res["outcome"], not problems, problems,
                         statistics.median(res["first_text"]) if res["first_text"] else None,
                         round(time.perf_counter() - t0, 1)))
            print(f"  {'✅' if not problems else '❌'} {res['outcome']}  {'; '.join(problems)}")

        promo = None
        if not only:
            board = (await http.get("/bank/board")).json()
            ayse = next(c for c in board["customers"] if c["id"] == 1)
            if ayse["appointment"]:
                r = (await http.post(f"/bank/appointments/{ayse['appointment']['appointment_id']}/cancel")).json()
                promo = r.get("promoted")
                ok = bool(promo and promo["full_name"] == "Zeynep Arslan")
                rows.append(("İptal → bekleme listesinden terfi", "Zeynep atanır",
                             promo["full_name"] if promo else "kimse", ok, [], None, 0))

    print("\n" + "=" * 92)
    print(f"{'Senaryo':42} {'Beklenen':20} {'Gerçek':20} {'LLM ilk metin (medyan)':>8}")
    for name, exp, got, ok, _, ttft, _ in rows:
        print(f"{'✅' if ok else '❌'} {name:40} {exp:20} {str(got):20} {f'{ttft} ms' if ttft else '':>8}")
    passed = sum(1 for r in rows if r[3])
    print(f"\n{passed}/{len(rows)} başarılı · LLM ilk metin medyan {statistics.median(all_ttft) if all_ttft else '-'} ms"
          f" · p90 {sorted(all_ttft)[int(len(all_ttft) * .9) - 1] if all_ttft else '-'} ms"
          f" · toplam {round(time.perf_counter() - t_all)} s")
    sys.exit(0 if passed == len(rows) else 1)


if __name__ == "__main__":
    asyncio.run(main())
