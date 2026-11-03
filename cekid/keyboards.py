"""Semua keyboard bot (reply keyboard berwarna + inline)."""

from pyrogram import enums
from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                            KeyboardButton, KeyboardButtonRequestChat,
                            KeyboardButtonRequestUsers, ReplyKeyboardMarkup)

PRIMARY = enums.ButtonStyle.PRIMARY
SUCCESS = enums.ButtonStyle.SUCCESS
DANGER = enums.ButtonStyle.DANGER
DEFAULT = enums.ButtonStyle.DEFAULT

REQ_USER = 701
REQ_CHANNEL = 702
REQ_GROUP = 703
REQ_FORUM = 704

TXT_USER = "👤 User"
TXT_PREMIUM = "⭐️ Premium"
TXT_BOT = "🤖 Bot"
TXT_GROUP = "👥 Group"
TXT_CHANNEL = "📢 Channel"
TXT_FORUM = "💬 Forum"
TXT_MYGROUP = "🗂 My Group"
TXT_MYCHANNEL = "📚 My Channel"

MAIN_BUTTONS = {
    TXT_USER, TXT_PREMIUM, TXT_BOT, TXT_GROUP,
    TXT_CHANNEL, TXT_FORUM, TXT_MYGROUP, TXT_MYCHANNEL,
}


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(TXT_USER, style=PRIMARY),
             KeyboardButton(TXT_PREMIUM, style=SUCCESS)],
            [KeyboardButton(TXT_BOT, style=DEFAULT),
             KeyboardButton(TXT_FORUM, style=DEFAULT)],
            [KeyboardButton(TXT_GROUP, style=PRIMARY),
             KeyboardButton(TXT_CHANNEL, style=PRIMARY)],
            [KeyboardButton(TXT_MYGROUP, style=SUCCESS),
             KeyboardButton(TXT_MYCHANNEL, style=SUCCESS)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def user_picker() -> ReplyKeyboardMarkup:
    """Reply keyboard: pilih user lewat dialog native Telegram."""
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(
                "🔍 Pilih User",
                style=PRIMARY,
                request_users=KeyboardButtonRequestUsers(
                    button_id=REQ_USER,
                    request_name=True,
                    request_username=True,
                    max_quantity=1,
                ),
            )
        ]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def chat_picker(channel: bool = True, group: bool = True, forum: bool = False) -> ReplyKeyboardMarkup:
    row = []
    if channel:
        row.append(
            KeyboardButton(
                "📢 Pilih Channel",
                style=PRIMARY,
                request_chat=KeyboardButtonRequestChat(
                    button_id=REQ_CHANNEL if not forum else REQ_FORUM,
                    chat_is_channel=True,
                    request_title=True,
                    request_username=True,
                ),
            )
        )
    if group:
        row.append(
            KeyboardButton(
                "👥 Pilih Group",
                style=SUCCESS,
                request_chat=KeyboardButtonRequestChat(
                    button_id=REQ_GROUP if not forum else REQ_FORUM,
                    chat_is_channel=False,
                    request_title=True,
                    request_username=True,
                ),
            )
        )
    return ReplyKeyboardMarkup(
        keyboard=[row] if row else None,
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def close_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Tutup", callback_data="close", style=DANGER)]]
    )


def back_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Kembali", callback_data="back", style=PRIMARY)]]
    )
