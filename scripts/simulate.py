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
    # (müşteri_id, ad, replikler, beklenen sonuç, ek kontrol)
    (1, "Ayşe – mutlu yol", ["Evet, benim.", "14 Mart 1988.", "Perşembe sabah olur.", "Evet, onaylıyorum.",
                             "Hayır, teşekkürler."], "scheduled", None),
    (2, "Mehmet – Kadıköy'ün son yeri", ["Evet benim.", "2 Kasım 1975.", "Cuma öğleden sonra uygun.", "Evet.",
                                         "Yok, teşekkürler."], "scheduled", None),
    (3, "Zeynep – Kadıköy dolu (taşma)", ["Evet, benim.", "27 Haziran 1993.", "Anladım, ne yapabiliriz?",
                                          "Tamam, bekleme listesine alın. İki zaman da olur.", "Teşekkürler."],
     "waitlisted", None),
    (4, "Can – 2 kez yanlış doğum tarihi", ["Evet benim.", "5 Mayıs 1980.", "Pardon, 1 Ocak 1980."],
     "verification_failed", None),
    (5, "Elif – telefonu eşi açıyor", ["Hayır, ben eşiyim. Elif şu an evde yok, bana söyleyebilirsiniz."],
     "not_reached", "no_card_leak"),
    (6, "Burak – adres değişikliği", ["Evet benim.", "18 Aralık 1969.", "Kartı başka bir adrese gönderebilir misiniz?",
                                      "Tamam, o zaman mevcut adrese cuma sabah olsun.", "Evet, onaylıyorum.",
                                      "Teşekkürler."], "scheduled", "address_escalation"),
    (7, "Selin – komşuya bırakın", ["Evet benim.", "5 Nisan 1999.", "Ben yokken komşuma bırakabilir misiniz?",
                                    "Peki, cuma sabah olsun.", "Evet.", "Teşekkürler."], "scheduled", None),
    (8, "Ali – mutlu yol", ["Evet benim.", "21 Temmuz 1984.", "Perşembe sabah uygun.", "Evet onaylıyorum.",
                            "Teşekkürler, iyi günler."], "scheduled", None),
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


def extra_check(kind, res, board) -> str | None:
    if kind == "no_card_leak":
        leaked = [s for s in res["said"] if "kart" in s.lower()]
        return f"üçüncü kişiye kart bilgisi sızdı: {leaked}" if leaked else None
    if kind == "address_escalation":
        ok = any(t["name"] == "escalate" and t["input"].get("reason") == "address_change" for t in res["tools"])
        return None if ok else "address_change escalation açılmadı"
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
        for cid, name, lines, expected, check in SCENARIOS:
            if only and cid not in only:
                continue
            print(f"▶ {name}")
            t0 = time.perf_counter()
            res = await run_call(args.base, cid, lines, args.verbose)
            board = (await http.get("/bank/board")).json()
            problems = []
            if res["outcome"] != expected:
                problems.append(f"sonuç {res['outcome']} (beklenen {expected})")
            if check and (p := extra_check(check, res, board)):
                problems.append(p)
            # Akış kontrolü: doğrulandığı turda müşteriyi bekletmeden slotlara bakmalı
            verified_turns = {t["turn"] for t in res["tools"]
                              if t["name"] == "verify_identity" and t["result"].get("verified")}
            slot_turns = {t["turn"] for t in res["tools"] if t["name"] == "list_available_slots"}
            if verified_turns - slot_turns:
                problems.append("doğrulamadan sonra slotlara bakmadan durdu")
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
