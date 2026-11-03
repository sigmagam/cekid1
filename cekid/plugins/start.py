"""/start — kartu user + keyboard menu utama."""

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from cekid import bot, rich, store
from cekid.keyboards import main_menu
from cekid.utils import reply_chat_card, reply_user_card

HELP = (
    "🤖 <b>CekID Bot</b>\n\n"
    "Tekan tombol di keyboard — sekali tekan langsung buka dialog pilih:\n"
    "👤 <b>User</b> · ⭐️ <b>Premium</b> · 🤖 <b>Bot</b>\n"
    "💬 <b>Forum</b> · 👥 <b>Group</b> · 📢 <b>Channel</b>\n"
    "🗂 <b>My Group</b> · 📚 <b>My Channel</b> (chat milikmu sendiri)\n\n"
    "Perintah: /start · /id · /cek · /help"
)


@Client.on_message(filters.private, group=-1)
async def record_user(_, message: Message):
    """Catat semua user yang pernah berinteraksi (untuk broadcast)."""
    store.save_user(message.from_user)


@Client.on_message(filters.command("start") & filters.private)
async def start(_, message: Message):
    return await reply_user_card(bot, message, message.from_user, badge="👋 <b>Halo!</b>")


@Client.on_message(filters.command("help"))
async def help_cmd(_, message: Message):
    return await rich.reply(
        bot, message,
        blocks=[
            rich.heading("🤖 CekID Bot", 2),
            rich.para(
                "Tekan tombol di keyboard — sekali tekan langsung buka dialog pilih:\n"
                "👤 User · ⭐️ Premium · 🤖 Bot\n"
                "💬 Forum · 👥 Group · 📢 Channel\n"
                "🗂 My Group · 📚 My Channel (chat milikmu sendiri)"
            ),
            rich.para("Perintah: /start · /id · /cek · /help"),
            rich.buttons([rich.rbtn("❌ Tutup", style=rich.DANGER, callback_data="close")]),
        ],
        fallback=HELP,
    )


@Client.on_message(filters.command("start") & ~filters.private)
async def start_chat(_, message: Message):
    """ /start di group/channel -> kartu info chat itu. """
    return await reply_chat_card(bot, message, message.chat)


@Client.on_callback_query(filters.regex("^close$"))
async def close(_, cq: CallbackQuery):
    try:
        return await cq.message.delete()
    except Exception:
        return await cq.answer("Tidak bisa ditutup.", show_alert=True)
