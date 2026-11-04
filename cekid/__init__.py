"""CekID — Telegram user/chat ID lookup bot (kurigram / pyrogram fork)."""

import asyncio
import logging

from pyrogram import Client
from pyrogram.types import BotCommand

from cekid import config
from cekid.store import Store
from cekid.tasks import backup_loop

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

log = logging.getLogger("cekid")

store = Store(config.DB_PATH)

COMMANDS = [
    BotCommand("start", "Your own account info"),
    BotCommand("cek", "Look up a user (reply / @username / id)"),
    BotCommand("id", "Show the ID of this chat"),
    BotCommand("help", "Help"),
    BotCommand("broadcast", "Send to all users (admin)"),
    BotCommand("stats", "User count (admin)"),
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

    async def start(self, *args, **kwargs) -> "CekIdBot":
        await super().start(*args, **kwargs)
        await self.set_bot_commands(COMMANDS)
        # Backup database tiap 00:00 WIB.
        self._bg = [asyncio.create_task(backup_loop(self))]
        me = await self.get_me()
        log.info("Ready as @%s", me.username or me.id)
        return self

    async def stop(self, *args, **kwargs):
        for task in getattr(self, "_bg", []):
            task.cancel()
        await super().stop(*args, **kwargs)
        log.info("Bot stopped.")


bot = CekIdBot()
