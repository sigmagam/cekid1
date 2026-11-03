"""Group / Channel / Forum (tombol request → hasil langsung) + daftar chat bot."""

from pyrogram import Client, filters
from pyrogram.types import LinkPreviewOptions, Message

from cekid import bot, store
from cekid.keyboards import TXT_MYCHANNEL, TXT_MYGROUP
from cekid.utils import chat_card, resolve_chat


@Client.on_message(filters.group | filters.channel, group=-1)
async def record(_, message: Message):
    """Catat setiap chat yang bot lihat -> dipakai tombol My Group / My Channel."""
    store.save_chat(message.chat)


@Client.on_message(filters.chat_shared)
async def on_chat_shared(_, message: Message):
    """Dari tombol 👥 Group / 📢 Channel / 💬 Forum."""
    store.save_chat(message.chat)
    shared = message.chat_shared
    if not shared or not shared.chat:
        return
    store.save_chat(shared.chat)
    return await message.reply(await chat_card(bot, shared.chat))


@Client.on_message(filters.command("id"))
async def chat_id(_, message: Message):
    store.save_chat(message.chat)
    if len(message.command) > 1:
        chat = await resolve_chat(bot, message.command[1])
        if chat is None:
            return await message.reply("❌ Chat tidak ditemukan.")
        store.save_chat(chat)
        return await message.reply(await chat_card(bot, chat))

    chat = message.chat
    lines = [f"🆔 <b>Chat ID:</b> <code>{chat.id}</code>",
             f"💬 <b>Type:</b> {chat.type}"]
    if message.reply_to_message and message.reply_to_message.from_user:
        lines.append(f"👤 <b>User ID:</b> <code>{message.reply_to_message.from_user.id}</code>")
    return await message.reply("\n".join(lines))


def _list_text(rows, title: str) -> str:
    if not rows:
        return (
            f"{title}\n\nBelum ada data. Tambahkan bot ke chat itu dulu, "
            "lalu kirim /id di sana supaya bot mengenalinya."
        )
    lines = [title, ""]
    for i, row in enumerate(rows, start=1):
        link = (
            f"https://t.me/{row['username']}"
            if row["username"]
            else f"https://t.me/c/{abs(row['chat_id'])}"
        )
        name = row["title"] or row["chat_id"]
        lines.append(f"{i}. <a href=\"{link}\">{name}</a> — <code>{row['chat_id']}</code>")
    return "\n".join(lines)


@Client.on_message(filters.private & filters.text & filters.regex(f"^{TXT_MYGROUP}$"))
async def my_groups(_, message: Message):
    rows = store.chats(["ChatType.GROUP", "ChatType.SUPERGROUP"])
    return await message.reply(
        _list_text(rows, "🗂 <b>My Group</b>"),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


@Client.on_message(filters.private & filters.text & filters.regex(f"^{TXT_MYCHANNEL}$"))
async def my_channels(_, message: Message):
    rows = store.chats(["ChatType.CHANNEL"])
    return await message.reply(
        _list_text(rows, "📚 <b>My Channel</b>"),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )
