"""Group / Channel / Forum / My Group / My Channel (request buttons)."""

from pyrogram import Client, filters
from pyrogram.types import Message

from cekid import bot, rich, store
from cekid.utils import reply_chat_card, resolve_chat
from cekid.safety import safe

@Client.on_message(filters.chat_shared)
@safe
async def on_chat_shared(_, message: Message):
    """From 👥 Group / 📢 Channel / 💬 Forum / 🗂 My Group / 📚 My Channel."""
    store.save_user(message.from_user)
    shared = message.chat_shared
    if not shared or not shared.chat:
        return await rich.reply(bot, message, fallback="❌ No chat was selected.")
    return await reply_chat_card(bot, message, shared.chat)

@Client.on_message(filters.command("id"))
@safe
async def chat_id(_, message: Message):
    if len(message.command) > 1:
        chat = await resolve_chat(bot, message.command[1])
        if chat is None:
            return await rich.reply(bot, message, fallback="❌ Chat not found.")
        return await reply_chat_card(bot, message, chat)

    chat = message.chat
    rows = [("🆔 Chat ID", rich.code(chat.id)), ("💬 Type", str(chat.type))]
    text = (f"🆔 <b>Chat ID:</b> <code>{chat.id}</code>\n"
            f"💬 <b>Type:</b> {chat.type}")
    if message.reply_to_message and message.reply_to_message.from_user:
        uid = message.reply_to_message.from_user.id
        rows.append(("👤 User ID", rich.code(uid)))
        text += f"\n👤 <b>User ID:</b> <code>{uid}</code>"
    return await rich.reply(
        bot, message,
        blocks=[rich.title("🆔 Chat Info"), rich.divider(),
                rich.table(rows, striped=True, compact=True)],
        fallback=text,
    )
