"""Lookup user / premium / bot."""

from pyrogram import Client, filters
from pyrogram.types import LinkPreviewOptions, Message

from cekid import bot, store
from cekid.ask import ask
from cekid.keyboards import TXT_BOT, TXT_PREMIUM, TXT_USER, user_picker
from cekid.utils import user_card

PROMPT = (
    "🔎 Kirim <b>id</b>, <b>@username</b>, balas sebuah pesan, "
    "atau tekan tombol <b>🔍 Pilih User</b> di bawah."
)

async def send_card(message: Message, user) -> Message:
    text, photo = await user_card(bot, user)
    if photo:
        try:
            return await message.reply_photo(photo, caption=text)
        except Exception:
            pass
    return await message.reply(text, link_preview_options=LinkPreviewOptions(is_disabled=True))


async def ask_target(message: Message, prompt: str):
    """Minta target user (picker / balas pesan / id / @username). -> User | None."""
    from cekid.utils import resolve_user

    asked = await ask(
        bot,
        message.chat.id,
        prompt,
        filter=filters.text | filters.users_shared,
        reply_markup=user_picker(),
    )
    if asked is None:
        return None
    return await resolve_user(bot, asked)


@Client.on_message(filters.private & filters.text & filters.regex(f"^{TXT_USER}$"))
async def cek_user(_, message: Message):
    store.save_chat(message.chat)
    user = await ask_target(message, PROMPT)
    if user is None:
        return await message.reply("❌ User tidak ditemukan.", reply_markup=None)
    return await send_card(message, user)


@Client.on_message(filters.private & filters.text & filters.regex(f"^{TXT_PREMIUM}$"))
async def cek_premium(_, message: Message):
    store.save_chat(message.chat)
    user = await ask_target(message, "⭐️ Kirim target user untuk dicek status premium-nya.\n\n" + PROMPT)
    if user is None:
        return await message.reply("❌ User tidak ditemukan.")
    text, photo = await user_card(bot, user)
    badge = "⭐️ <b>Premium:</b> Yes" if user.is_premium else "⭐️ <b>Premium:</b> No"
    text = f"{badge}\n\n{text}"
    if photo:
        try:
            return await message.reply_photo(photo, caption=text)
        except Exception:
            pass
    return await message.reply(text, link_preview_options=LinkPreviewOptions(is_disabled=True))


@Client.on_message(filters.private & filters.text & filters.regex(f"^{TXT_BOT}$"))
async def cek_bot(_, message: Message):
    store.save_chat(message.chat)
    user = await ask_target(message, "🤖 Kirim bot (id / @username) untuk dicek.\n\n" + PROMPT)
    if user is None:
        return await message.reply("❌ Bot tidak ditemukan.")
    if not user.is_bot:
        return await message.reply(
            f"⚠️ <a href=\"tg://user?id={user.id}\">Akun ini</a> bukan bot."
        )
    return await send_card(message, user)


@Client.on_message(filters.command("cek"))
async def cek_cmd(_, message: Message):
    store.save_chat(message.chat)
    from cekid.utils import resolve_user

    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target = await bot.get_users(message.command[1])
        except Exception:
            target = None

    if target is None:
        target = await ask_target(message, PROMPT)
    if target is None:
        return await message.reply("❌ User tidak ditemukan.")
    return await send_card(message, target)
