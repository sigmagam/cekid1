"""Group / Channel / Forum / My Group / My Channel (tombol request)."""

from pyrogram import Client, filters
from pyrogram.types import LinkPreviewOptions, Message

from cekid import bot, store
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
            return await message.reply("❌ Chat tidak ditemukan.")
        return await reply_chat_card(bot, message, chat)

    chat = message.chat
    lines = [f"🆔 <b>Chat ID:</b> <code>{chat.id}</code>",
             f"💬 <b>Type:</b> {chat.type}"]
    if message.reply_to_message and message.reply_to_message.from_user:
        lines.append(f"👤 <b>User ID:</b> <code>{message.reply_to_message.from_user.id}</code>")
    return await message.reply(
        "\n".join(lines), link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
