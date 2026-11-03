"""/start — kartu user + keyboard menu utama."""

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, LinkPreviewOptions, Message

from cekid import bot, store
from cekid.keyboards import close_inline, main_menu
from cekid.utils import chat_card, user_card

HELP = (
    "🤖 <b>CekID Bot</b>\n\n"
    "Tekan tombol di keyboard — sekali tekan langsung buka dialog pilih:\n"
    "👤 <b>User</b> · ⭐️ <b>Premium</b> · 🤖 <b>Bot</b>\n"
    "💬 <b>Forum</b> · 👥 <b>Group</b> · 📢 <b>Channel</b>\n"
    "🗂 <b>My Group</b> · 📚 <b>My Channel</b> (chat yang bot sudah lihat)\n\n"
    "Perintah: /start · /id · /cek · /help"
)

async def send_user_card(message: Message, user, reply_markup=None) -> Message:
    text, photo = await user_card(bot, user)
    if photo:
        try:
            return await message.reply_photo(photo, caption=text, reply_markup=reply_markup)
        except Exception:
            pass
    return await message.reply(text, reply_markup=reply_markup, link_preview_options=LinkPreviewOptions(is_disabled=True))


@Client.on_message(filters.command("start") & filters.private)
async def start(_, message: Message):
    store.save_chat(message.chat)
    return await send_user_card(message, message.from_user, main_menu())


@Client.on_message(filters.command("help"))
async def help_cmd(_, message: Message):
    store.save_chat(message.chat)
    return await message.reply(HELP, reply_markup=close_inline())


@Client.on_callback_query(filters.regex("^close$"))
async def close(_, cq: CallbackQuery):
    try:
        return await cq.message.delete()
    except Exception:
        return await cq.answer("Tidak bisa ditutup.", show_alert=True)


@Client.on_message(filters.command("start") & ~filters.private)
async def start_chat(_, message: Message):
    store.save_chat(message.chat)
    return await message.reply(await chat_card(bot, message.chat))
