"""Configuration from the environment (.env)."""

import os

from dotenv import load_dotenv

load_dotenv()


def _ids(name: str, default: str) -> list[int]:
    raw = os.getenv(name, default)
    return [int(x) for x in raw.replace(" ", "").split(",") if x]


API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Admins: receive reports and the database backup.
ADMIN_IDS = _ids("ADMIN_IDS", os.getenv("ADMIN_ID", "728397761"))

# Wajib join sebelum bisa pakai bot (kosongkan untuk mematikan).
FSUB_REQUIRED = _ids("FSUB_REQUIRED", "-1002695864434")

# Link manual per chat id (dipakai kalau bot tidak bisa resolve id-nya).
FSUB_LINKS = os.getenv(
    "FSUB_LINKS",
    "-1002695864434=https://t.me/AllBotAccel,"
    "-1002642740878=https://t.me/AgentxRouter",
)

# Opsional: cuma ditampilkan tombolnya, tidak memblokir.
FSUB_OPTIONAL = _ids("FSUB_OPTIONAL", "-1002642740878")

DB_PATH = os.getenv("DB_PATH", "cekid.db")

# Rich messages: set 0 if rich rendering looks odd on your client.
RICH_MESSAGE = os.getenv("RICH_MESSAGE", "1").strip().lower() not in ("0", "false", "off", "no")

# Message effects (private chats). Set 0 to disable.
EFFECTS_ENABLED = os.getenv("EFFECTS", "1").strip().lower() not in ("0", "false", "off", "no")

if not (API_ID and API_HASH and BOT_TOKEN):
    raise SystemExit(
        "API_ID / API_HASH / BOT_TOKEN are missing. Copy .env.example to .env first."
    )
