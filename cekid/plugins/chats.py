"""Group / Channel / Forum / My Group / My Channel (tombol request)."""

from pyrogram import Client, filters
from pyrogram.types import Message

from cekid import bot, rich, store
from cekid.utils import reply_chat_card, resolve_chat


@Client.on_message(filters.chat_shared)
async def on_chat_shared(_, message: Message):
    """Dari tombol 👥 Group / 📢 Channel / 💬 Forum / 🗂 My Group / 📚 My Channel."""
    store.save_user(message.from_user)
    shared = message.chat_shared
    if not shared or not shared.chat:
        return
    return await reply_chat_card(bot, message, shared.chat)


@Client.on_message(filters.command("id"))
async def chat_id(_, message: Message):
    if len(message.command) > 1:
        chat = await resolve_chat(bot, message.command[1])
        if chat is None:
            return await rich.reply(bot, message, fallback="❌ Chat tidak ditemukan.")
        return await reply_chat_card(bot, message, chat)

    chat = message.chat
    rows = [("🆔 Chat ID", str(chat.id)), ("💬 Type", str(chat.type))]
    text = (
        f"🆔 <b>Chat ID:</b> <code>{chat.id}</code>\n"
        f"💬 <b>Type:</b> {chat.type}"
    )
    if message.reply_to_message and message.reply_to_message.from_user:
        uid = message.reply_to_message.from_user.id
        rows.append(("👤 User ID", str(uid)))
        text += f"\n👤 <b>User ID:</b> <code>{uid}</code>"
    return await rich.reply(
        bot, message,
        blocks=[rich.heading("🆔 Info Chat", 3), rich.table(rows, striped=True)],
        fallback=text,
    )
