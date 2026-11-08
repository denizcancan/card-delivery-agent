"""Banka servisinin REST yüzü. Asistan bu uç noktaları tool'lar üzerinden çağırır.

Müşteri kimliği yalnızca POST /calls'ta verilir; sonraki tüm işlemler call_id üzerinden
yürür ve müşteri sunucuda çağrıya bağlıdır (LLM başka müşteri adına işlem yapamaz).
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .service import Bank, BankError


class StartCall(BaseModel):
    customer_id: int


class Verify(BaseModel):
    birth_date: str


class Book(BaseModel):
    slot_id: int


class DeliveryAddress(BaseModel):
    address: str
    district: str
    update_registered: bool = False
    address_type: str | None = None


class Waitlist(BaseModel):
    accepted_slot_ids: list[int] = Field(default_factory=list)


class Escalate(BaseModel):
    reason: str
    note: str | None = None


class EndCall(BaseModel):
    summary: str | None = None


class Event(BaseModel):
    kind: str
    payload: dict


def create_bank_app(bank: Bank) -> FastAPI:
    app = FastAPI(title="Freya Bank – Kart Teslim Servisi",
                  description="Müşteri, kurye slotu, randevu, bekleme listesi ve operasyon talepleri.")

    @app.exception_handler(BankError)
    async def _bank_error(_: Request, exc: BankError):
        return JSONResponse(exc.body(), status_code=exc.status)

    # Asistanın kullandığı uç noktalar (sync def → threadpool'da çalışır)
    @app.post("/calls")
    def start_call(body: StartCall):
        return bank.start_call(body.customer_id)

    @app.post("/calls/{call_id}/verify")
    def verify(call_id: str, body: Verify):
        return bank.verify_identity(call_id, body.birth_date)

    @app.post("/calls/{call_id}/address/confirm")
    def confirm_address(call_id: str):
        return bank.confirm_address(call_id)

    @app.post("/calls/{call_id}/address")
    def set_address(call_id: str, body: DeliveryAddress):
        return bank.set_delivery_address(call_id, body.address, body.district,
                                         body.update_registered, body.address_type)

    @app.get("/calls/{call_id}/slots")
    def slots(call_id: str):
        return bank.list_slots(call_id)

    @app.post("/calls/{call_id}/appointments")
    def book(call_id: str, body: Book):
        return bank.book_slot(call_id, body.slot_id)

    @app.post("/calls/{call_id}/appointment/reschedule")
    def reschedule(call_id: str, body: Book):
        return bank.reschedule(call_id, body.slot_id)

    @app.post("/calls/{call_id}/appointment/cancel")
    def cancel_for_call(call_id: str):
        return bank.cancel_for_call(call_id)

    @app.post("/calls/{call_id}/waitlist")
    def waitlist(call_id: str, body: Waitlist):
        return bank.join_waitlist(call_id, body.accepted_slot_ids)

    @app.post("/calls/{call_id}/escalations")
    def escalate(call_id: str, body: Escalate):
        return bank.escalate(call_id, body.reason, body.note)

    @app.post("/calls/{call_id}/end")
    def end(call_id: str, body: EndCall):
        return bank.end_call(call_id, body.summary)

    @app.post("/calls/{call_id}/events")
    def add_event(call_id: str, body: Event):
        return bank.add_event(call_id, body.kind, body.payload)

    @app.get("/calls/{call_id}/events")
    def events(call_id: str):
        return bank.events(call_id)

    # Operasyon / demo arayüzü
    @app.get("/board")
    def board():
        return bank.board()

    @app.post("/appointments/{appointment_id}/cancel")
    def cancel(appointment_id: int):
        return bank.cancel_appointment(appointment_id)

    @app.post("/admin/reset")
    def reset():
        bank.init(reset=True)
        return {"ok": True}

    return app
