"""Rich message helper (Telegram rich message) + efek animasi pesan.

Semua kiriman teks bot lewat sini. Kalau server/DC menolak rich message,
otomatis jatuh ke HTML biasa — bot tidak pernah mati karena fitur baru.
"""

import logging
import os
import random

from pyrogram import enums
from pyrogram.errors import MessageNotModified
from pyrogram.types import (DisabledButton, InputRichBlockButtons,
                            InputRichBlockParagraph,
                            InputRichBlockSectionHeading, InputRichBlockTable,
                            InputRichMessage, LinkPreviewOptions,
                            RichBlockCaption, RichBlockTableCell,
                            RichMessageButton, RichText, RichTextUrl)

logger = logging.getLogger("cekid.rich")

PRIMARY = enums.ButtonStyle.PRIMARY
SUCCESS = enums.ButtonStyle.SUCCESS
DANGER = enums.ButtonStyle.DANGER
DEFAULT = enums.ButtonStyle.DEFAULT
LINK = enums.ButtonStyle.LINK

# ID efek animasi pesan Telegram (private chat). Bebas dipakai dari mana saja.
EFFECTS = [
    5104841245755180586,  # 🔥
    5107584321108051014,  # 👍
    5046509860389126442,  # 🎉
    5159385139981059251,  # ❤️
    5104858069142078462,  # 🎊
]

_ENABLED = os.getenv("RICH_MESSAGE", "1").strip().lower() not in ("0", "false", "off", "no")
_EFFECTS = os.getenv("EFFECTS", "1").strip().lower() not in ("0", "false", "off", "no")
_FAILS = 0
_MAX_FAILS = 3


def rich_available() -> bool:
    return _ENABLED and _FAILS < _MAX_FAILS


def _note_fail() -> None:
    global _FAILS
    _FAILS += 1
    if _FAILS == _MAX_FAILS:
        logger.warning("Rich message tidak didukung server -> pakai HTML biasa.")


def effect_id() -> int | None:
    return random.choice(EFFECTS) if (_EFFECTS and EFFECTS) else None


def heading(text: str, size: int = 3) -> InputRichBlockSectionHeading:
    return InputRichBlockSectionHeading(text, size)


def para(text: str) -> InputRichBlockParagraph:
    return InputRichBlockParagraph(text)


def html_link(text: str, url: str) -> RichTextUrl:
    """Teks yang bisa diklik di dalam blok rich."""
    return RichTextUrl(text, url)


def _cell(value):
    if value is None:
        return "-"
    if isinstance(value, RichText):
        return value
    return str(value)


def table(rows, header: bool = False, striped: bool = True,
          bordered: bool = False) -> InputRichBlockTable:
    cells = [
        [
            RichBlockTableCell(text=_cell(c), is_header=bool(header and i == 0),
                               align="left")
            for c in row
        ]
        for i, row in enumerate(rows)
    ]
    return InputRichBlockTable(cells, is_bordered=bordered, is_striped=striped)


def rbtn(text: str, style=DEFAULT, callback_data=None, url=None,
         disabled: bool = False) -> RichMessageButton:
    kwargs = {}
    if disabled:
        kwargs["disabled"] = DisabledButton()
    elif callback_data is not None:
        kwargs["callback_data"] = callback_data
    elif url is not None:
        kwargs["url"] = url
    else:
        kwargs["callback_data"] = "noop"
    return RichMessageButton(text, style=style, **kwargs)


def buttons(row, align: str | None = "center") -> InputRichBlockButtons:
    return InputRichBlockButtons(list(row), align=align)


def rich(blocks) -> InputRichMessage:
    return InputRichMessage(blocks=list(blocks))


def _text_of(msg: InputRichMessage, text: str | None) -> str:
    return text or msg.html or msg.markdown or "⚠️ (pesan kosong)"


async def _send_plain(client, chat_id, text, reply_markup, effect, **kwargs):
    for eff in (effect, None):
        try:
            return await client.send_message(
                chat_id,
                text,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.DEFAULT,
                link_preview_options=LinkPreviewOptions(is_disabled=True),
                effect_id=eff,
                **kwargs,
            )
        except Exception as err:
            if eff is None:
                logger.warning("Gagal kirim pesan: %s", err)
    return None


async def reply(client, message, *, blocks=None, html: str | None = None,
                fallback: str | None = None, reply_markup=None,
                effect: int | None = None, with_effect: bool = True, **kwargs):
    """Balas pesan dengan rich message; fallback otomatis ke HTML."""
    msg = InputRichMessage(blocks=blocks, html=html)
    text = _text_of(msg, fallback)
    chat_id = message.chat.id
    private = str(getattr(message.chat, "type", "")).endswith("PRIVATE")
    eff = effect if effect is not None else (effect_id() if (with_effect and private) else None)

    if rich_available():
        try:
            return await client.send_rich_message(
                chat_id, msg, reply_markup=reply_markup,
                effect_id=eff, reply_parameters=_reply_params(message),
            )
        except Exception as err:
            _note_fail()
            logger.warning("Rich message gagal (%s) -> fallback HTML.", err)
    return await _send_plain(client, chat_id, text, reply_markup, eff, **kwargs)


async def edit(client, message, *, blocks=None, html: str | None = None,
               fallback: str | None = None, reply_markup=None):
    msg = InputRichMessage(blocks=blocks, html=html)
    if rich_available():
        try:
            return await message.edit(rich_message=msg, reply_markup=reply_markup)
        except MessageNotModified:
            return message
        except Exception as err:
            _note_fail()
            logger.warning("Rich edit gagal (%s) -> fallback HTML.", err)
    try:
        return await message.edit_text(
            _text_of(msg, fallback), reply_markup=reply_markup,
            parse_mode=enums.ParseMode.DEFAULT,
        )
    except MessageNotModified:
        return message
    except Exception:
        return message


def _reply_params(message):
    from pyrogram.types import ReplyParameters

    return ReplyParameters(message_id=message.id)
