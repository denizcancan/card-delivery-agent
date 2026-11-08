"""Uygulama: banka servisi (/bank), sesli arama WebSocket'i (/ws/call/{id}) ve arayüz (/).

Ses hattı:  Chrome Web Speech (STT) → WS metin → CallSession (Claude) → cümleler
            → ElevenLabs PCM akışı → WS binary [4 bayt tur no + PCM] → tarayıcıda çalınır.
"""
import asyncio
import contextlib
import struct
import time
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from .assistant.bank_client import BankClient
from .assistant.session import CallSession
from .assistant.tts import SAMPLE_RATE, ElevenLabsTTS, clean_for_speech
from .bank.api import create_bank_app
from .bank.service import Bank
from .config import ROOT, settings

bank = Bank(settings.db_path, settings.today)
bank.init()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(timeout=httpx.Timeout(30, connect=5))
    app.state.tts = ElevenLabsTTS(settings.eleven_key, settings.eleven_voice, settings.eleven_model,
                                  app.state.http)
    yield
    await app.state.http.aclose()


app = FastAPI(title="Freya Kart Teslim Asistanı", lifespan=lifespan)
app.mount("/bank", create_bank_app(bank))


@app.middleware("http")
async def no_cache_ui(request, call_next):
    """Arayüz dosyaları önbelleğe alınmasın: geliştirirken tarayıcı eski app.js'i çalıştırmasın."""
    response = await call_next(request)
    if not request.url.path.startswith(("/bank", "/api")):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/api/config")
async def config():
    return {"model": settings.llm_model, "tts_available": app.state.tts.enabled,
            "voice_id": settings.eleven_voice, "tts_model": settings.eleven_model,
            "sample_rate": SAMPLE_RATE}


@app.websocket("/ws/call/{customer_id}")
async def call_ws(ws: WebSocket, customer_id: int, tts_mode: str = "eleven"):
    await ws.accept()
    tts: ElevenLabsTTS = app.state.tts
    send_lock = asyncio.Lock()
    state = {"mode": tts_mode if tts.enabled or tts_mode != "eleven" else "browser", "cancel_upto": 0}
    tts_queue: asyncio.Queue = asyncio.Queue()
    tasks: set[asyncio.Task] = set()

    async def send(data):
        async with send_lock:
            if isinstance(data, bytes):
                await ws.send_bytes(data)
            else:
                await ws.send_json(data)

    async def emit(ev: dict):
        if ev["type"] == "say" and state["mode"] == "eleven":
            tts_queue.put_nowait((ev["turn"], ev["text"]))
        with contextlib.suppress(Exception):
            await send(ev)

    session = CallSession(customer_id, emit, BankClient(settings.bank_url, app.state.http))

    async def tts_worker():
        reported: set[int] = set()
        while True:
            turn, text = await tts_queue.get()
            if turn <= state["cancel_upto"] or state["mode"] != "eleven":
                continue
            carry = b""
            try:
                async for chunk in tts.stream(clean_for_speech(text)):
                    if turn <= state["cancel_upto"]:
                        break
                    data = carry + chunk
                    cut = len(data) - len(data) % 2      # int16 hizası
                    data, carry = data[:cut], data[cut:]
                    if not data:
                        continue
                    if turn not in reported:
                        reported.add(turn)
                        started = session.turn_started.get(turn, time.perf_counter())
                        await send({"type": "metric", "turn": turn,
                                    "first_audio_ms": int((time.perf_counter() - started) * 1000)})
                    await send(struct.pack("<I", turn) + data)
            except Exception as e:  # kredi bitti / ağ hatası → tarayıcı sesine düş
                state["mode"] = "browser"
                await send({"type": "tts_error", "message": str(e)[:200], "fallback": "browser"})
                await send({"type": "say_fallback", "turn": turn, "text": text})

    def spawn(coro):
        t = asyncio.create_task(coro)
        tasks.add(t)
        t.add_done_callback(tasks.discard)

    spawn(tts_worker())
    spawn(session.start())
    try:
        while True:
            msg = await ws.receive_json()
            kind = msg.get("type")
            if kind == "user_text":
                spawn(session.user_said(msg.get("text", "")))
            elif kind == "interrupt":          # söz kesme: bu turun kalan sesini at
                state["cancel_upto"] = session.turn
            elif kind == "tts_mode":
                state["mode"] = msg.get("mode", "off")
            elif kind == "hangup":
                break
    except WebSocketDisconnect:
        pass
    finally:
        for t in list(tasks):
            t.cancel()
        await session.close()
        with contextlib.suppress(Exception):
            await send({"type": "closed", "outcome": session.outcome})
            await ws.close()


app.mount("/", StaticFiles(directory=ROOT / "static", html=True), name="static")
