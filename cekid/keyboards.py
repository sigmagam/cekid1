"""Every bot keyboard (colored reply keyboard + inline).

Menu buttons are Telegram *request* buttons: one tap opens the native
picker (user / channel / group / forum) with no intermediate keyboard.
"""

from pyrogram import enums
from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                            KeyboardButton, KeyboardButtonRequestChat,
                            KeyboardButtonRequestUsers, ReplyKeyboardMarkup)

PRIMARY = enums.ButtonStyle.PRIMARY
SUCCESS = enums.ButtonStyle.SUCCESS
DANGER = enums.ButtonStyle.DANGER
DEFAULT = enums.ButtonStyle.DEFAULT

# Unique button_id per feature (used when users_shared / chat_shared arrive).
REQ_USER = 701
REQ_PREMIUM = 702
REQ_BOT = 703
REQ_GROUP = 704
REQ_CHANNEL = 705
REQ_FORUM = 706
REQ_MYGROUP = 707
REQ_MYCHANNEL = 708


def _user_button(text: str, button_id: int, *, is_bot: bool | None = None,
                 is_premium: bool | None = None,
                 style: enums.ButtonStyle = PRIMARY) -> KeyboardButton:
    return KeyboardButton(
        text,
        style=style,
        request_users=KeyboardButtonRequestUsers(
            button_id=button_id,
            user_is_bot=is_bot,
            user_is_premium=is_premium,
            request_name=True,
            request_username=True,
            max_quantity=1,
        ),
    )


def _chat_button(text: str, button_id: int, *, is_channel: bool,
                 is_forum: bool | None = None, created: bool | None = None,
                 style: enums.ButtonStyle = PRIMARY) -> KeyboardButton:
    return KeyboardButton(
        text,
        style=style,
        request_chat=KeyboardButtonRequestChat(
            button_id=button_id,
            chat_is_channel=is_channel,
            chat_is_forum=is_forum,
            chat_is_created=created,
            request_title=True,
            request_username=True,
            request_photo=True,
        ),
    )


def main_menu() -> ReplyKeyboardMarkup:
    """One tap opens the native user/chat picker."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                _user_button("👤 User", REQ_USER, is_bot=False),
                _user_button("⭐️ Premium", REQ_PREMIUM, is_bot=False,
                             is_premium=True, style=SUCCESS),
            ],
            [
                _user_button("🤖 Bot", REQ_BOT, is_bot=True),
                _chat_button("💬 Forum", REQ_FORUM, is_channel=False, is_forum=True),
            ],
            [
                _chat_button("👥 Group", REQ_GROUP, is_channel=False, is_forum=False),
                _chat_button("📢 Channel", REQ_CHANNEL, is_channel=True),
            ],
            [
                # chat_is_created=True -> only chats the user created (owner).
                _chat_button("🗂 My Group", REQ_MYGROUP, is_channel=False,
                             is_forum=None, created=True, style=SUCCESS),
                _chat_button("📚 My Channel", REQ_MYCHANNEL, is_channel=True,
                             created=True, style=SUCCESS),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def close_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Tutup", callback_data="close", style=DANGER)]]
    )
