"""Group / Channel / Forum + daftar chat yang pernah dilihat bot."""

from pyrogram import Client, filters
from pyrogram.types import LinkPreviewOptions, Message

from cekid import bot, store
from cekid.ask import ask
from cekid.keyboards import (TXT_CHANNEL, TXT_FORUM, TXT_GROUP, TXT_MYCHANNEL,
                             TXT_MYGROUP, chat_picker)
from cekid.utils import chat_card, resolve_chat

PROMPT_CHAT = (
    "🔎 Kirim <b>id</b>, <b>@username</b>, balas sebuah pesan dari chat itu, "
    "atau tekan tombol pilih di bawah."
)


@Client.on_message(filters.group | filters.channel, group=-1)
async def record(_, message: Message):
    """Catat setiap chat yang bot lihat -> dipakai tombol My Group / My Channel."""
    store.save_chat(message.chat)


@Client.on_message(filters.command("id"))
async def chat_id(_, message: Message):
    store.save_chat(message.chat)
    chat = message.chat
    target = message.reply_to_message.from_user if message.reply_to_message else None
    lines = [f"🆔 <b>Chat ID:</b> <code>{chat.id}</code>",
             f"💬 <b>Type:</b> {chat.type}"]
    if target:
        lines.append(f"👤 <b>User ID:</b> <code>{target.id}</code>")
    return await message.reply("\n".join(lines))


async def _pick_and_show(message: Message, prompt: str, expect_forum: bool = False):
    asked = await ask(
        bot,
        message.chat.id,
        prompt,
        filter=filters.text | filters.chat_shared,
        reply_markup=chat_picker(),
    )
    if asked is None:
        return
    chat = await resolve_chat(bot, asked, expect_forum=expect_forum)
    if chat is None:
        return await message.reply("❌ Chat tidak ditemukan / bot belum mengenalnya.")
    store.save_chat(chat)
    return await message.reply(await chat_card(bot, chat))


@Client.on_message(filters.private & filters.text & filters.regex(f"^{TXT_GROUP}$"))
async def cek_group(_, message: Message):
    return await _pick_and_show(
        message, f"👥 Kirim target <b>group</b>.\n\n{PROMPT_CHAT}"
    )


@Client.on_message(filters.private & filters.text & filters.regex(f"^{TXT_CHANNEL}$"))
async def cek_channel(_, message: Message):
    return await _pick_and_show(
        message, f"📢 Kirim target <b>channel</b>.\n\n{PROMPT_CHAT}"
    )


@Client.on_message(filters.private & filters.text & filters.regex(f"^{TXT_FORUM}$"))
async def cek_forum(_, message: Message):
    return await _pick_and_show(
        message, f"💬 Kirim target <b>forum</b> (supergroup dengan topik).\n\n{PROMPT_CHAT}",
        expect_forum=True,
    )


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
    return await message.reply(_list_text(rows, "🗂 <b>My Group</b>"), link_preview_options=LinkPreviewOptions(is_disabled=True))


@Client.on_message(filters.private & filters.text & filters.regex(f"^{TXT_MYCHANNEL}$"))
async def my_channels(_, message: Message):
    rows = store.chats(["ChatType.CHANNEL"])
    return await message.reply(_list_text(rows, "📚 <b>My Channel</b>"), link_preview_options=LinkPreviewOptions(is_disabled=True))
