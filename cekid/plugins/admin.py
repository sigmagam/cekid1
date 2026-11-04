"""Admin commands: /broadcast to every user, /stats."""

import asyncio
import logging

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from cekid import bot, config, rich, store
from cekid.safety import safe

log = logging.getLogger("cekid.admin")

ADMIN = filters.user(config.ADMIN_IDS) if config.ADMIN_IDS else filters.user([])

@Client.on_message(filters.command("stats") & ADMIN)
@safe
async def stats(_, message: Message):
    total = store.count()
    rows = [("👥 Total users", str(total)), ("🗄 Database", config.DB_PATH)]
    return await rich.reply(
        bot, message,
        blocks=[rich.title("📊 Statistics"), rich.divider(),
                rich.table(rows, striped=True, compact=True)],
        fallback=(f"📊 <b>Statistics</b>\n\n👥 <b>Total users:</b> <code>{total}</code>\n"
                  f"🗄 <b>Database:</b> <code>{config.DB_PATH}</code>"),
    )

@Client.on_message(filters.command("broadcast") & ADMIN)
@safe
async def broadcast(_, message: Message):
    src = message.reply_to_message
    parts = (message.text or "").split(None, 1)

    if not src and len(parts) < 2:
        return await rich.reply(
            bot, message,
            blocks=[
                rich.heading("📣 Broadcast", 3),
                rich.para("Reply to a message, or send:"),
                rich.para([rich.code("/broadcast your message here")]),
            ],
            fallback=("📣 <b>Broadcast</b>\n\nReply to a message, or send:\n"
                      "<code>/broadcast your message here</code>"),
        )
    if src and (getattr(src, "empty", False) or getattr(src, "service", False)):
        return await rich.reply(bot, message, fallback="❌ That message is empty and cannot be sent.")

    users = store.user_ids()
    if not users:
        return await rich.reply(bot, message, fallback="No user has started the bot yet.")

    status = await rich.reply(
        bot, message,
        blocks=[rich.heading("📣 Broadcast", 3),
                rich.para(["Sending to ", rich.bold(str(len(users))), " users..."])],
        fallback=f"📣 Sending to <b>{len(users)}</b> users...",
    )
    ok = fail = 0
    for uid in users:
        try:
            if src:
                await src.copy(uid)
            else:
                await bot.send_message(uid, parts[1])
            ok += 1
        except FloodWait as err:
            await asyncio.sleep(err.value + 1)
            try:
                if src:
                    await src.copy(uid)
                else:
                    await bot.send_message(uid, parts[1])
                ok += 1
            except Exception:
                fail += 1
        except Exception as err:
            fail += 1
            log.debug("Broadcast to %s failed: %s", uid, err)
        await asyncio.sleep(0.05)

    return await rich.edit(
        bot, status,
        blocks=[rich.heading("✅ Broadcast finished", 3),
                rich.table([("Delivered", str(ok)), ("Failed", str(fail))],
                           striped=True, compact=True)],
        fallback=(f"✅ <b>Done</b>\n\nDelivered: <code>{ok}</code>\n"
                  f"Failed: <code>{fail}</code>"),
    )
