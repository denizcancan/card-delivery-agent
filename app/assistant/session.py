"""Tek bir müşteri araması: Claude Agent SDK oturumu (claude2 aboneliği) + banka tool'ları.

Metin akışı cümlelere bölünerek `say` olayları halinde yayılır; TTS katmanı bunları seslendirir.
"""
from __future__ import annotations

import asyncio
import re
import time
from typing import Awaitable, Callable

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, ResultMessage, StreamEvent

from ..config import settings
from .bank_client import BankClient
from .prompts import render
from .tools import build_bank_server

Emit = Callable[[dict], Awaitable[None]]
# Cümle sonu: noktalama + ardından boşluk (09.00 gibi yazımlar bölünmez)
SENTENCE_END = re.compile(r"[.!?…]+[\"')»]*(?=\s)")
# Seslendirme güvenlik ağı: modelin sızdırdığı iç düşünce / düzeltme / cinsiyetli hitap
_PARENS = re.compile(r"\([^)]*\)")
_HONORIFIC = re.compile(r",?\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+\s+(Hanım|Bey)\b")
_META = re.compile(r"\b(avoid|let me|restate|gender\w*|must|should|actually|i will|i'll|i need|note)\b"
                   r"|hitap kural", re.I)


def speakable(text: str) -> str:
    """Müşteriye okunmaması gereken parçaları ayıklar; tamamen meta ise boş döner."""
    text = _HONORIFIC.sub("", _PARENS.sub("", text)).strip(" :;-—")
    if not re.search(r"\w", text) or _META.search(text):
        return ""
    return re.sub(r"\s{2,}", " ", text)


def ms_since(t0: float) -> int:
    return int((time.perf_counter() - t0) * 1000)


class CallSession:
    def __init__(self, customer_id: int, emit: Emit, bank: BankClient, model: str | None = None):
        self.customer_id = customer_id
        self.emit = emit
        self.bank = bank
        self.model = model or settings.llm_model
        self.call_id: str | None = None
        self.customer: dict | None = None
        self.client: ClaudeSDKClient | None = None
        self.turn = 0
        self.turn_started: dict[int, float] = {}
        self.ended = False
        self.outcome: str | None = None
        self.ready = asyncio.Event()
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        try:
            res = await self.bank.start_call(self.customer_id)
            if not res.get("ok"):
                raise RuntimeError(f"Arama başlatılamadı: {res}")
            self.call_id, self.customer = res["call_id"], res["customer"]
            system_prompt, opening = render(self.customer["full_name"])
            server, tool_names = build_bank_server(self)
            options = ClaudeAgentOptions(
                model=self.model,
                system_prompt=system_prompt,
                tools=[],                       # Claude Code'un yerleşik tool'ları (Bash, Read...) kapalı
                mcp_servers={"bank": server},
                strict_mcp_config=True,         # kullanıcı ayarlarındaki MCP sunucuları yüklenmez
                allowed_tools=tool_names,
                setting_sources=[],             # CLAUDE.md / settings.json yüklenmez
                include_partial_messages=True,  # token akışı → cümle cümle TTS
                thinking={"type": "disabled"},  # sesli kanalda gecikme öncelikli
                max_turns=8,
                env={"CLAUDE_CONFIG_DIR": settings.claude_config_dir},
                cwd=str(settings.data_dir),
            )
            t0 = time.perf_counter()
            self.client = ClaudeSDKClient(options)
            await self.client.connect()
            await self.emit({"type": "call_started", "call_id": self.call_id, "customer": self.customer,
                             "model": self.model, "connect_ms": ms_since(t0)})
            self.ready.set()
            await self._log("system", {"model": self.model})
            await self._run_turn(opening)
        except Exception as e:  # UI'ya görünür hata
            await self.emit({"type": "error", "message": f"Başlatma hatası: {e}"})
            raise

    async def user_said(self, text: str) -> None:
        text = (text or "").strip()
        if not text:
            return
        await self.ready.wait()
        if self.ended:
            return
        await self._log("user", {"text": text})
        await self._run_turn(text)

    async def _run_turn(self, prompt: str) -> None:
        async with self._lock:
            if self.ended or not self.client:
                return
            self.turn += 1
            turn, t0 = self.turn, time.perf_counter()
            self.turn_started[turn] = t0
            await self.emit({"type": "turn_started", "turn": turn})
            buf, spoken, first_text = "", [], None

            async def flush(force: bool = False):
                nonlocal buf
                while buf:
                    m = SENTENCE_END.search(buf)
                    if m:
                        piece, buf = buf[:m.end()], buf[m.end():]
                    elif force:
                        piece, buf = buf, ""
                    else:
                        return
                    raw, piece = piece.strip(), speakable(piece)
                    if raw and raw != piece:
                        await self._log("system", {"filtered": raw, "kept": piece})
                    if piece and not self.ended:   # end_call sonrası metin müşteriye okunmaz
                        spoken.append(piece)
                        await self.emit({"type": "say", "turn": turn, "text": piece})

            try:
                await self.client.query(prompt)
                async for msg in self.client.receive_response():
                    if isinstance(msg, StreamEvent):
                        ev = msg.event
                        if ev.get("type") == "content_block_delta" and ev.get("delta", {}).get("type") == "text_delta":
                            if first_text is None:
                                first_text = ms_since(t0)
                            buf += ev["delta"]["text"]
                            await flush()
                        elif ev.get("type") == "content_block_stop":
                            await flush(force=True)
                    elif isinstance(msg, ResultMessage):
                        await flush(force=True)
                        if msg.is_error:
                            await self.emit({"type": "error", "message": f"LLM hatası: {msg.result or msg.subtype}"})
            except Exception as e:
                await self.emit({"type": "error", "message": f"Tur hatası: {e}"})
            if spoken:
                await self._log("assistant", {"text": " ".join(spoken), "turn": turn})
            await self.emit({"type": "turn_done", "turn": turn, "first_text_ms": first_text,
                             "total_ms": ms_since(t0)})
            if self.ended:
                await self.emit({"type": "call_ended", "turn": turn, "outcome": self.outcome})

    async def on_tool(self, name: str, args: dict, result: dict) -> None:
        await self.emit({"type": "tool", "turn": self.turn, "name": name, "input": args, "result": result})
        await self._log("tool", {"name": name, "input": args, "result": result})
        if name == "end_call" and result.get("ok"):
            self.ended, self.outcome = True, result.get("outcome")
        await self.emit({"type": "board_changed"})

    async def _log(self, kind: str, payload: dict) -> None:
        if self.call_id:
            await self.bank.event(self.call_id, kind, payload)

    async def close(self) -> None:
        if self.call_id and not self.ended:
            res = await self.bank.end_call(self.call_id, "Görüşme kullanıcı tarafından kapatıldı.")
            self.ended, self.outcome = True, res.get("outcome")
        if self.client:
            try:
                await self.client.disconnect()
            except Exception:
                pass
