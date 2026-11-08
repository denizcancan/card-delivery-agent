"""Prompt'lar PROMPTS.md içindeki ```prompt <ad> bloklarından okunur (tek kaynak)."""
import re
from string import Template

from ..bank.service import date_label
from ..config import ROOT, settings

PROMPTS_FILE = ROOT / "PROMPTS.md"
_BLOCK = re.compile(r"```prompt (\w+)\n(.*?)```", re.S)


def load_prompts() -> dict[str, Template]:
    text = PROMPTS_FILE.read_text(encoding="utf-8")
    blocks = {m.group(1): Template(m.group(2).strip()) for m in _BLOCK.finditer(text)}
    missing = {"system", "opening"} - blocks.keys()
    if missing:
        raise RuntimeError(f"PROMPTS.md içinde eksik prompt blokları: {missing}")
    return blocks


def today_label() -> str:
    return f"{date_label(settings.today)} {settings.today.year}"


def render(full_name: str) -> tuple[str, str]:
    p = load_prompts()
    values = {"full_name": full_name, "today_label": today_label()}
    return p["system"].safe_substitute(values), p["opening"].safe_substitute(values)
