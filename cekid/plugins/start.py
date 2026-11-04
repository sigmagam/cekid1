"""/start — user card + main menu keyboard."""

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from cekid import bot, rich, store
from cekid.keyboards import main_menu
from cekid.utils import reply_chat_card, reply_user_card
from cekid.safety import safe

HELP = (
    "🤖 <b>CekID Bot</b>\n\n"
    "Tap a button on the keyboard — one tap opens the native Telegram picker:\n"
    "👤 <b>User</b> · ⭐️ <b>Premium</b> · 🤖 <b>Bot</b>\n"
    "💬 <b>Forum</b> · 👥 <b>Group</b> · 📢 <b>Channel</b>\n"
    "🗂 <b>My Group</b> · 📚 <b>My Channel</b> (chats you created)\n\n"
    "Commands: /start · /id · /cek · /help"
)

@Client.on_message(filters.private, group=-1)
@safe(gate=False)
async def record_user(_, message: Message):
    """Store every user that interacts with the bot (used by /broadcast)."""
    store.save_user(message.from_user)

@Client.on_message(filters.command("start") & filters.private)
@safe
async def start(_, message: Message):
    return await reply_user_card(
        bot, message, message.from_user,
        badge=["👋 ", rich.bold("Hello!"), " Here is your account info."],
        reply_markup=main_menu(),
    )

@Client.on_message(filters.command("help"))
@safe
async def help_cmd(_, message: Message):
    return await rich.reply(
        bot, message,
        blocks=[
            rich.title("🤖 CekID Bot"),
            rich.para(rich.italic("Look up IDs for users, bots, groups, channels and forums.")),
            rich.divider(),
            rich.heading("How to use", 3),
            rich.bullets([
                [rich.bold("👤 User"), " — any regular user (never a bot)"],
                [rich.bold("⭐️ Premium"), " — premium users only"],
                [rich.bold("🤖 Bot"), " — bot accounts only"],
                [rich.bold("💬 Forum"), " — groups with topics enabled"],
                [rich.bold("👥 Group"), " — regular groups"],
                [rich.bold("📢 Channel"), " — channels"],
                [rich.bold("🗂 My Group"), " / ", rich.bold("📚 My Channel"),
                 " — chats you created yourself"],
            ]),
            rich.heading("Commands", 3),
            rich.bullets([
                [rich.code("/start"), " — your own account info"],
                [rich.code("/cek <id|@username>"), " — look up a user"],
                [rich.code("/id"), " — ID of the current chat"],
                [rich.code("/help"), " — this message"],
            ]),
            rich.footer("Fields Telegram does not expose are hidden from cards."),
            rich.buttons([
                rich.rbtn("❌ Close", style=rich.DANGER, callback_data="close"),
            ]),
        ],
        fallback=HELP,
    )

@Client.on_message(filters.command("start") & ~filters.private)
@safe
async def start_chat(_, message: Message):
    """ /start in a group/channel -> card for that chat. """
    return await reply_chat_card(bot, message, message.chat)

@Client.on_callback_query(filters.regex("^close$"))
@safe
async def close(_, cq: CallbackQuery):
    try:
        return await cq.message.delete()
    except Exception:
        return await cq.answer("Cannot close this message.", show_alert=True)
