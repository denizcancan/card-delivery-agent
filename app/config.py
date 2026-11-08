import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


class Settings:
    data_dir = ROOT / "data"
    db_path = Path(os.getenv("DB_PATH", str(ROOT / "data" / "bank.db")))
    # Asistan banka servisine HTTP ile gider; servis ayrı süreçte de çalışabilir.
    bank_url = os.getenv("BANK_URL", "http://127.0.0.1:8000/bank")

    llm_model = os.getenv("LLM_MODEL", "claude-haiku-5-5")
    claude_config_dir = os.path.expanduser(os.getenv("CLAUDE_CONFIG_DIR", "~/.claude-2"))

    eleven_key = os.getenv("ELEVENLABS_API_KEY", "")
    eleven_voice = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
    eleven_model = os.getenv("ELEVENLABS_MODEL", "eleven_flash_v2_5")

    today = date.fromisoformat(os.getenv("SCENARIO_TODAY", "2026-11-11"))


settings = Settings()
