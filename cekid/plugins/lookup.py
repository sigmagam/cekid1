"""Lookup user / premium / bot (tombol request → kartu rich langsung)."""

from pyrogram import Client, filters
from pyrogram.types import Message

from cekid import bot, rich, store
from cekid.keyboards import REQ_BOT, REQ_PREMIUM
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

    if shared.button_id == REQ_BOT and not user.is_bot:
        return await rich.reply(bot, message, fallback=f"⚠️ {full_name(user)} bukan bot.")
    if shared.button_id == REQ_PREMIUM:
        badge = "⭐️ <b>Premium:</b> Yes" if user.is_premium else "⭐️ <b>Premium:</b> No"
        return await reply_user_card(bot, message, user, badge=badge)
    return await reply_user_card(bot, message, user)


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
                rich.heading("🔎 Cara Pakai /cek", 3),
                rich.para("• <code>/cek 123456789</code>"),
                rich.para("• <code>/cek @username</code>"),
                rich.para("• balas pesan user lalu ketik <code>/cek</code>"),
                rich.para("• atau tekan tombol 👤 User / 🤖 Bot / ⭐️ Premium"),
            ],
            fallback=CEK_HELP,
        )
    return await reply_user_card(bot, message, target)
