"""Konfigurasi dari environment (.env)."""

import os

from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

DB_PATH = os.getenv("DB_PATH", "cekid.db")

if not (API_ID and API_HASH and BOT_TOKEN):
    raise SystemExit(
        "API_ID / API_HASH / BOT_TOKEN belum diisi. Copy .env.example ke .env dulu."
    )
