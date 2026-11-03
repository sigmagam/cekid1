"""Lookup user / premium / bot (tombol request → hasil langsung)."""

from pyrogram import Client, filters
from pyrogram.types import LinkPreviewOptions, Message

from cekid import bot, store
from cekid.keyboards import REQ_BOT, REQ_PREMIUM
from cekid.utils import user_card


async def send_card(message: Message, user, badge: str | None = None) -> Message:
    text, photo = await user_card(bot, user)
    if badge:
        text = f"{badge}\n\n{text}"
    if photo:
        try:
            return await message.reply_photo(photo, caption=text)
        except Exception:
            pass
    return await message.reply(text, link_preview_options=LinkPreviewOptions(is_disabled=True))


@Client.on_message(filters.users_shared)
async def on_user_shared(_, message: Message):
    """Dari tombol 👤 User / ⭐️ Premium / 🤖 Bot."""
    store.save_chat(message.chat)
    shared = message.users_shared
    try:
        user = await bot.get_users(shared.users[0].id)
    except Exception:
        return await message.reply("❌ User tidak bisa dibaca.")

    if shared.button_id == REQ_BOT and not user.is_bot:
        return await message.reply(f"⚠️ {user.mention} bukan bot.")
    if shared.button_id == REQ_PREMIUM:
        badge = "⭐️ <b>Premium:</b> Yes" if user.is_premium else "⭐️ <b>Premium:</b> No"
        return await send_card(message, user, badge)
    return await send_card(message, user)


@Client.on_message(filters.command("cek"))
async def cek_cmd(_, message: Message):
    store.save_chat(message.chat)
    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target = await bot.get_users(message.command[1])
        except Exception:
            target = None

    if target is None:
        return await message.reply(
            "Pakai salah satu:\n"
            "• <code>/cek 123456789</code>\n"
            "• <code>/cek @username</code>\n"
            "• balas pesan user lalu ketik <code>/cek</code>\n"
            "• atau tekan tombol 👤 User / 🤖 Bot / ⭐️ Premium di menu."
        )
    return await send_card(message, target)
