"""Lookup user / premium / bot (request buttons -> rich card instantly)."""

from pyrogram import Client, filters
from pyrogram.types import Message

from cekid import bot, rich, store
from cekid.keyboards import REQ_BOT, REQ_PREMIUM, REQ_USER
from cekid.utils import full_name, reply_user_card

CEK_HELP = (
    "🔎 <b>How to use /cek</b>\n\n"
    "• <code>/cek 123456789</code>\n"
    "• <code>/cek @username</code>\n"
    "• reply to a user message and type <code>/cek</code>\n"
    "• or tap 👤 User / 🤖 Bot / ⭐️ Premium on the menu."
)

@Client.on_message(filters.users_shared)
async def on_user_shared(_, message: Message):
    """From the 👤 User / ⭐️ Premium / 🤖 Bot buttons."""
    store.save_user(message.from_user)
    shared = message.users_shared
    if not shared or not shared.users:
        return await rich.reply(bot, message, fallback="❌ No user was selected.")
    peer = shared.users[0]
    # A peer from the picker may only carry an ID (no access_hash), so
    # get_users() is only used to enrich the data we already have.
    user = peer
    try:
        fetched = await bot.get_users(peer.id)
        if fetched is not None:
            user = fetched
    except Exception:
        user = peer

    # 👤 User means regular users only. If the client still sends a bot,
    # never render a bot card for that button.
    if shared.button_id in (REQ_USER, REQ_PREMIUM) and user.is_bot:
        return await rich.reply(
            bot, message,
            blocks=[
                rich.heading("⚠️ That is a bot", 3),
                rich.para([f"{full_name(user)} is a bot. Use the ",
                           rich.bold("🤖 Bot"), " button instead."]),
            ],
            fallback=f"⚠️ {full_name(user)} is a bot. Use the 🤖 Bot button.",
        )

    if shared.button_id == REQ_BOT and not user.is_bot:
        return await rich.reply(
            bot, message,
            blocks=[
                rich.heading("⚠️ That is not a bot", 3),
                rich.para([f"{full_name(user)} is not a bot. Use the ",
                           rich.bold("👤 User"), " button instead."]),
            ],
            fallback=f"⚠️ {full_name(user)} is not a bot. Use the 👤 User button.",
        )

    badge = None
    if shared.button_id == REQ_PREMIUM:
        badge = ("⭐️ Premium user" if user.is_premium
                 else "⭐️ Not a premium user")
    elif shared.button_id == REQ_BOT:
        badge = "🤖 Bot account"
    if badge:
        badge = [rich.bold(badge)]
    return await reply_user_card(bot, message, user, badge=badge)

@Client.on_message(filters.command("cek"))
async def cek_cmd(_, message: Message):
    store.save_user(message.from_user)
    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target = await bot.get_users(message.command[1])
        except Exception:
            target = None

    if target is None:
        return await rich.reply(
            bot, message,
            blocks=[
                rich.title("🔎 How to use /cek"),
                rich.divider(),
                rich.bullets([
                    rich.code("/cek 123456789"),
                    rich.code("/cek @username"),
                    ["reply to a user message and type ", rich.code("/cek")],
                    "or tap 👤 User / 🤖 Bot / ⭐️ Premium on the menu",
                ]),
            ],
            fallback=CEK_HELP,
        )
    return await reply_user_card(bot, message, target)
