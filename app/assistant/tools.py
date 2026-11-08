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
SLOT_ID = {"type": "object", "properties": {"slot_id": {"type": "integer"}}, "required": ["slot_id"]}


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def build_bank_server(session: "CallSession"):
    bank, call_id = session.bank, session.call_id

    async def run(name: str, args: dict, coro):
        result = await coro
        await session.on_tool(name, args, result)
        return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}

    async def invalid(name, args, error):
        async def _r():
            return {"ok": False, "error": error}
        return await run(name, args, _r())

    @tool("verify_identity",
          "Telefondaki kişinin kart sahibi olduğunu doğrular. Kart, teslimat ya da adres hakkında hiçbir "
          "şey konuşmadan önce çağrılmalı. Müşterinin söylediği doğum tarihini YYYY-MM-DD biçiminde gönder. "
          "Başarılıysa kayıtlı teslimat adresini döner.",
          {"type": "object",
           "properties": {"birth_date": {"type": "string", "description": "YYYY-MM-DD, örn. 1988-03-14"}},
           "required": ["birth_date"]})
    async def verify_identity(args):
        return await run("verify_identity", args, bank.verify(call_id, str(args.get("birth_date", ""))))

    @tool("confirm_address",
          "Müşteri, kendisine okunan kayıtlı adresin teslimat için doğru olduğunu onayladıysa çağır.",
          EMPTY)
    async def confirm_address(args):
        return await run("confirm_address", args, bank.confirm_address(call_id))

    @tool("set_delivery_address",
          "Kart kayıtlı adresten farklı bir adrese gidecekse çağır. Önce müşteriden açık adresi ve ilçeyi al, "
          "sonra kayıtlı adresinin de bu adresle değiştirilmesini isteyip istemediğini sor ve cevabı "
          "update_registered olarak gönder.",
          {"type": "object",
           "properties": {
               "address": {"type": "string", "description": "Mahalle, cadde/sokak, numara, daire ve ilçe"},
               "district": {"type": "string", "description": "İlçe adı, örn. Ataşehir"},
               "update_registered": {"type": "boolean",
                                     "description": "true: kayıtlı adres de güncellensin; false: yalnızca bu teslimat"},
               "address_type": {"type": "string", "enum": ["home", "work", "other"]}},
           "required": ["address", "district", "update_registered"]})
    async def set_delivery_address(args):
        return await run("set_delivery_address", args, bank.set_address(
            call_id, str(args.get("address", "")), str(args.get("district", "")),
            bool(args.get("update_registered")), args.get("address_type")))

    @tool("list_available_slots",
          "Teyit edilen teslimat adresinin ilçesindeki bu haftanın boş kurye zamanlarını döner. Yalnızca burada "
          "dönen zamanları teklif et. İlçe doluysa ya da kurye o ilçeye gitmiyorsa overflow alanı dolu gelir.",
          EMPTY)
    async def list_available_slots(args):
        return await run("list_available_slots", args, bank.slots(call_id))

    @tool("book_slot",
          "Seçilen zamanı rezerve eder. Yalnızca günü ve saati müşteriye tekrar edip açık onay aldıktan sonra "
          "çağır. Zaten randevu varsa bunun yerine reschedule_appointment kullan.",
          SLOT_ID)
    async def book_slot(args):
        slot_id = _int(args.get("slot_id"))
        if slot_id is None:
            return await invalid("book_slot", args, "invalid_slot_id")
        return await run("book_slot", args, bank.book(call_id, slot_id))

    @tool("reschedule_appointment",
          "Mevcut randevuyu başka bir boş zamana taşır. Müşteri yeni zamanı onayladıktan sonra çağır.",
          SLOT_ID)
    async def reschedule_appointment(args):
        slot_id = _int(args.get("slot_id"))
        if slot_id is None:
            return await invalid("reschedule_appointment", args, "invalid_slot_id")
        return await run("reschedule_appointment", args, bank.reschedule(call_id, slot_id))

    @tool("cancel_appointment",
          "Müşterinin bu görüşmede aldığı teslimat randevusunu iptal eder. Yalnızca müşteri iptali açıkça "
          "teyit ettikten sonra çağır.",
          EMPTY)
    async def cancel_appointment(args):
        return await run("cancel_appointment", args, bank.cancel(call_id))

    @tool("join_waitlist",
          "İlçede boş zaman yoksa müşteriyi bekleme listesine ekler. Yer açılırsa kabul ettiği zamanlardan "
          "birine otomatik atanır ve SMS gider; açılmazsa gelecek hafta önceliklidir. Kurye o ilçeye hiç "
          "gitmiyorsa boş listeyle çağır (yalnızca gelecek hafta önceliği).",
          {"type": "object",
           "properties": {"accepted_slot_ids": {
               "type": "array", "items": {"type": "integer"},
               "description": "Yer açılırsa müşterinin kabul edeceği zamanlar (overflow.district_slots içinden)"}},
           "required": ["accepted_slot_ids"]})
    async def join_waitlist(args):
        ids = [i for i in (_int(x) for x in args.get("accepted_slot_ids") or []) if i is not None]
        return await run("join_waitlist", args, bank.waitlist(call_id, ids))

    @tool("escalate",
          "Asistanın yetkisi dışındaki durumlar için operasyon ekibine talep açar: ek kapasite isteği, "
          "üçüncü kişiye teslim isteği, insanla görüşme isteği. Söz verme; 'talebinizi ilettim' de.",
          {"type": "object",
           "properties": {
               "reason": {"type": "string",
                          "enum": ["capacity_request", "third_party", "customer_request", "other"]},
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

    tools = [verify_identity, confirm_address, set_delivery_address, list_available_slots, book_slot,
             reschedule_appointment, cancel_appointment, join_waitlist, escalate, end_call]
    names = [f"mcp__{SERVER}__{t.name}" for t in tools]
    return create_sdk_mcp_server(SERVER, "1.0.0", tools), names
