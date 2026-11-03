"""Konfigurasi dari environment (.env)."""

import os

from dotenv import load_dotenv

load_dotenv()


def _ids(name: str, default: str) -> list[int]:
    raw = os.getenv(name, default)
    return [int(x) for x in raw.replace(" ", "").split(",") if x]


API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Admin: terima laporan & backup database.
ADMIN_IDS = _ids("ADMIN_IDS", os.getenv("ADMIN_ID", "728397761"))

DB_PATH = os.getenv("DB_PATH", "cekid.db")

# Rich message: set 0 kalau tampilan rich di Telegram kamu aneh.
RICH_MESSAGE = os.getenv("RICH_MESSAGE", "1").strip().lower() not in ("0", "false", "off", "no")

# Efek animasi pesan (private chat). Isi 0 untuk mematikan.
EFFECTS_ENABLED = os.getenv("EFFECTS", "1").strip().lower() not in ("0", "false", "off", "no")

if not (API_ID and API_HASH and BOT_TOKEN):
    raise SystemExit(
        "API_ID / API_HASH / BOT_TOKEN belum diisi. Copy .env.example ke .env dulu."
    )
