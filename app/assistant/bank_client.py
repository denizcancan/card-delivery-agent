"""Banka servisine HTTP istemcisi. Hata durumunda da gövdeyi döner (LLM hatayı görüp toparlasın)."""
import httpx


class BankClient:
    def __init__(self, base_url: str, http: httpx.AsyncClient):
        self.base = base_url.rstrip("/")
        self.http = http

    async def _req(self, method: str, path: str, json: dict | None = None) -> dict:
        try:
            r = await self.http.request(method, self.base + path, json=json, timeout=10)
        except httpx.HTTPError as e:
            return {"ok": False, "error": "bank_unreachable", "detail": str(e)}
        try:
            return r.json()
        except ValueError:
            return {"ok": False, "error": "bad_response", "status": r.status_code}

    async def start_call(self, customer_id: int):
        return await self._req("POST", "/calls", {"customer_id": customer_id})

    async def verify(self, call_id: str, birth_date: str):
        return await self._req("POST", f"/calls/{call_id}/verify", {"birth_date": birth_date})

    async def slots(self, call_id: str):
        return await self._req("GET", f"/calls/{call_id}/slots")

    async def book(self, call_id: str, slot_id: int):
        return await self._req("POST", f"/calls/{call_id}/appointments", {"slot_id": slot_id})

    async def waitlist(self, call_id: str, accepted_slot_ids: list[int]):
        return await self._req("POST", f"/calls/{call_id}/waitlist", {"accepted_slot_ids": accepted_slot_ids})

    async def escalate(self, call_id: str, reason: str, note: str | None):
        return await self._req("POST", f"/calls/{call_id}/escalations", {"reason": reason, "note": note})

    async def end_call(self, call_id: str, summary: str | None):
        return await self._req("POST", f"/calls/{call_id}/end", {"summary": summary})

    async def event(self, call_id: str, kind: str, payload: dict):
        return await self._req("POST", f"/calls/{call_id}/events", {"kind": kind, "payload": payload})
