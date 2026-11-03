"""CekID — bot cek ID user/chat Telegram (kurigram / pyrogram fork)."""

import asyncio
import logging

from pyrogram import Client
from pyrogram.types import BotCommand

from cekid import config
from cekid.store import Store

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

log = logging.getLogger("cekid")

store = Store(config.DB_PATH)

COMMANDS = [
    BotCommand("start", "Mulai / tampilkan info kamu"),
    BotCommand("cek", "Cek ID user (balas pesan / @username / id)"),
    BotCommand("id", "Lihat ID chat ini"),
    BotCommand("help", "Bantuan"),
]


class CekIdBot(Client):
    def __init__(self) -> None:
        super().__init__(
            name="cekid",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            plugins=dict(root="cekid/plugins"),
        )

    async def start(self) -> "CekIdBot":
        await super().start()
        await self.set_bot_commands(COMMANDS)
        me = await self.get_me()
        log.info("✅ Bot aktif sebagai @%s", me.username or me.id)
        return self

    async def stop(self, *args):
        await super().stop()
        log.info("Bot berhenti.")


bot = CekIdBot()
