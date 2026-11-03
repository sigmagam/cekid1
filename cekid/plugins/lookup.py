"""Lookup user / premium / bot (tombol request → kartu rich langsung)."""

from pyrogram import Client, filters
from pyrogram.types import Message

from cekid import bot, rich, store
from cekid.keyboards import REQ_BOT, REQ_PREMIUM, REQ_USER
from cekid.utils import full_name, reply_user_card

CEK_HELP = (
    "🔎 <b>Cara pakai /cek</b>\n\n"
    "• <code>/cek 123456789</code>\n"
    "• <code>/cek @username</code>\n"
    "• balas pesan user lalu ketik <code>/cek</code>\n"
    "• atau tekan tombol 👤 User / 🤖 Bot / ⭐️ Premium di menu."
)

@Client.on_message(filters.users_shared)
async def on_user_shared(_, message: Message):
    """Dari tombol 👤 User / ⭐️ Premium / 🤖 Bot."""
    store.save_user(message.from_user)
    shared = message.users_shared
    try:
        user = await bot.get_users(shared.users[0].id)
    except Exception:
        return await rich.reply(bot, message, fallback="❌ User tidak bisa dibaca.")

    # Tombol 👤 User = user biasa. Kalau client tetap kasih bot, jangan tampil kartu bot.
    if shared.button_id in (REQ_USER, REQ_PREMIUM) and user.is_bot:
        return await rich.reply(
            bot, message,
            blocks=[
                rich.heading("⚠️ Itu bot, bukan user", 3),
                rich.para(f"{full_name(user)} adalah bot. Pakai tombol 🤖 Bot."),
            ],
            fallback=f"⚠️ {full_name(user)} adalah bot. Pakai tombol 🤖 Bot.",
        )

    if shared.button_id == REQ_BOT and not user.is_bot:
        return await rich.reply(
            bot, message,
            blocks=[
                rich.heading("⚠️ Itu bukan bot", 3),
                rich.para(f"{full_name(user)} bukan bot. Pakai tombol 👤 User."),
            ],
            fallback=f"⚠️ {full_name(user)} bukan bot. Pakai tombol 👤 User.",
        )

    badge = None
    if shared.button_id == REQ_PREMIUM:
        badge = ("⭐️ <b>User premium</b>" if user.is_premium
                 else "⭐️ <b>Bukan user premium</b>")
    elif shared.button_id == REQ_BOT:
        badge = "🤖 <b>Bot</b>"
    return await reply_user_card(bot, message, user, badge=badge)

@Client.on_message(filters.command("cek"))
async def cek_cmd(_, message: Message):
    store.save_user(message.from_user)
    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target = await bot.get_users(message.command[1])
        except Exception:
            target = None

    if target is None:
        return await rich.reply(
            bot, message,
            blocks=[
                rich.title("🔎 Cara pakai /cek"),
                rich.divider(),
                rich.bullets([
                    "<code>/cek 123456789</code>",
                    "<code>/cek @username</code>",
                    "balas pesan user lalu ketik <code>/cek</code>",
                    "atau tekan tombol 👤 User / 🤖 Bot / ⭐️ Premium",
                ]),
            ],
            fallback=CEK_HELP,
        )
    return await reply_user_card(bot, message, target)
