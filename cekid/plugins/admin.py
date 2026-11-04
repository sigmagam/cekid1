"""Command admin: /broadcast ke semua user, /stats."""

import asyncio
import logging

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from cekid import bot, config, rich, store

log = logging.getLogger("cekid.admin")

ADMIN = filters.user(config.ADMIN_IDS) if config.ADMIN_IDS else filters.user([])


@Client.on_message(filters.command("stats") & ADMIN)
async def stats(_, message: Message):
    rows = [("👥 Total user", str(store.count())),
            ("🗄 Database", config.DB_PATH)]
    return await rich.reply(
        bot, message,
        blocks=[rich.heading("📊 Statistik", 3), rich.table(rows, striped=True)],
        fallback=(f"📊 <b>Statistik</b>\n\n👥 <b>Total user:</b> "
                  f"<code>{store.count()}</code>\n🗄 <b>Database:</b> "
                  f"<code>{config.DB_PATH}</code>"),
    )


@Client.on_message(filters.command("broadcast") & ADMIN)
async def broadcast(_, message: Message):
    src = message.reply_to_message
    parts = (message.text or "").split(None, 1)

    if not src and len(parts) < 2:
        return await rich.reply(
            bot, message,
            blocks=[
                rich.heading("📣 Broadcast", 3),
                rich.para("Balas sebuah pesan, atau tulis:"),
                rich.para([rich.code("/broadcast teks pesan")]),
            ],
            fallback=("📣 <b>Broadcast</b>\n\nBalas sebuah pesan, atau tulis:\n"
                      "<code>/broadcast teks pesan</code>"),
        )
    if src and (getattr(src, "empty", False) or getattr(src, "service", False)):
        return await rich.reply(bot, message, fallback="❌ Pesan itu kosong / tidak bisa dikirim.")

    users = store.user_ids()
    if not users:
        return await rich.reply(bot, message, fallback="Belum ada user yang /start.")

    status = await rich.reply(
        bot, message,
        blocks=[rich.heading("📣 Broadcast", 3),
                rich.para(["Mengirim ke ", rich.bold(str(len(users))),
                           " user..."])],
        fallback=f"📣 Mengirim ke <b>{len(users)}</b> user...",
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
            log.debug("Broadcast ke %s gagal: %s", uid, err)
        await asyncio.sleep(0.05)

    return await rich.edit(
        bot, status,
        blocks=[rich.heading("✅ Broadcast selesai", 3),
                rich.table([("Berhasil", str(ok)), ("Gagal", str(fail))],
                           striped=True)],
        fallback=(f"✅ <b>Selesai</b>\n\nBerhasil: <code>{ok}</code>\n"
                  f"Gagal: <code>{fail}</code>"),
    )
