"""Agent SDK tool'ları. Her arama için ayrı bir in-process MCP sunucusu kurulur;
call_id closure ile bağlanır, LLM'in müşteri seçme imkânı yoktur."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

from claude_agent_sdk import create_sdk_mcp_server, tool

if TYPE_CHECKING:
    from .session import CallSession

SERVER = "bank"
EMPTY = {"type": "object", "properties": {}}


def build_bank_server(session: "CallSession"):
    bank, call_id = session.bank, session.call_id

    async def run(name: str, args: dict, coro):
        result = await coro
        await session.on_tool(name, args, result)
        return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}

    @tool("verify_identity",
          "Telefondaki kişinin kart sahibi olduğunu doğrular. Kart, teslimat ya da slot hakkında hiçbir "
          "şey konuşmadan önce çağrılmalı. Müşterinin söylediği doğum tarihini YYYY-MM-DD biçiminde gönder.",
          {"type": "object",
           "properties": {"birth_date": {"type": "string", "description": "YYYY-MM-DD, örn. 1988-03-14"}},
           "required": ["birth_date"]})
    async def verify_identity(args):
        return await run("verify_identity", args, bank.verify(call_id, str(args.get("birth_date", ""))))

    @tool("list_available_slots",
          "Doğrulanmış müşterinin ilçesindeki bu haftanın boş kurye slotlarını döner. Yalnızca burada dönen "
          "slotları teklif et. İlçe doluysa slots boş gelir ve overflow alanında seçenekler bulunur.",
          EMPTY)
    async def list_available_slots(args):
        return await run("list_available_slots", args, bank.slots(call_id))

    @tool("book_slot",
          "Seçilen slotu rezerve eder. Yalnızca günü ve saati müşteriye tekrar edip açık onay aldıktan sonra çağır.",
          {"type": "object", "properties": {"slot_id": {"type": "integer"}}, "required": ["slot_id"]})
    async def book_slot(args):
        try:
            slot_id = int(args.get("slot_id"))
        except (TypeError, ValueError):
            return await run("book_slot", args, _const({"ok": False, "error": "invalid_slot_id"}))
        return await run("book_slot", args, bank.book(call_id, slot_id))

    @tool("join_waitlist",
          "İlçede boş slot yoksa müşteriyi bu haftanın bekleme listesine ekler. Yer açılırsa kabul ettiği "
          "slotlardan birine otomatik atanır ve SMS gider. Açılmazsa gelecek hafta önceliklidir.",
          {"type": "object",
           "properties": {"accepted_slot_ids": {
               "type": "array", "items": {"type": "integer"},
               "description": "Yer açılırsa müşterinin kabul edeceği slotlar (overflow.district_slots içinden)"}},
           "required": ["accepted_slot_ids"]})
    async def join_waitlist(args):
        ids = [int(i) for i in args.get("accepted_slot_ids") or [] if str(i).lstrip("-").isdigit()]
        return await run("join_waitlist", args, bank.waitlist(call_id, ids))

    @tool("escalate",
          "Asistanın yetkisi dışındaki durumlar için operasyon ekibine talep açar: ek kapasite isteği, adres "
          "değişikliği, üçüncü kişiye teslim isteği, insanla görüşme isteği. Söz verme; 'talebinizi ilettim' de.",
          {"type": "object",
           "properties": {
               "reason": {"type": "string", "enum": ["capacity_request", "address_change", "third_party",
                                                     "customer_request", "other"]},
               "note": {"type": "string", "description": "Kısa açıklama"}},
           "required": ["reason"]})
    async def escalate(args):
        return await run("escalate", args, bank.escalate(call_id, str(args.get("reason")), args.get("note")))

    @tool("end_call",
          "Görüşmeyi kapatır. Vedalaştıktan sonra en son çağır. Sonuç durumu sunucuda hesaplanır.",
          {"type": "object", "properties": {"summary": {"type": "string", "description": "Tek cümlelik özet"}},
           "required": ["summary"]})
    async def end_call(args):
        return await run("end_call", args, bank.end_call(call_id, args.get("summary")))

    tools = [verify_identity, list_available_slots, book_slot, join_waitlist, escalate, end_call]
    names = [f"mcp__{SERVER}__{t.name}" for t in tools]
    return create_sdk_mcp_server(SERVER, "1.0.0", tools), names


async def _const(value: dict) -> dict:
    return value
