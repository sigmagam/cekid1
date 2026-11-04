"""Rich message helper (Telegram rich message) + efek animasi pesan.

Semua kiriman teks bot lewat sini. Kalau server/DC menolak rich message,
otomatis jatuh ke HTML biasa — bot tidak pernah mati karena fitur baru.
"""

import logging
import os
import random

from pyrogram import enums
from pyrogram.errors import MessageNotModified
from pyrogram.types import (CopyTextButton, DisabledButton, InputMediaPhoto,
                            InputRichBlockBlockQuotation,
                            InputRichBlockButtons, InputRichBlockDetails,
                            InputRichBlockDivider, InputRichBlockFooter,
                            InputRichBlockList, InputRichBlockListItem,
                            InputRichBlockMathematicalExpression,
                            InputRichBlockParagraph, InputRichBlockPhoto,
                            InputRichBlockPreformatted,
                            InputRichBlockSectionHeading, InputRichBlockTable,
                            InputRichMessage, LinkPreviewOptions,
                            ReplyParameters, RichBlockTableCell,
                            RichBlockCaption, RichMessageButton, RichText,
                            RichTextBold,
                            RichTextCode, RichTextCustomEmoji,
                            RichTextItalic, RichTextMarked, RichTextSpoiler,
                            RichTextSubscript, RichTextSuperscript, RichTextUrl)

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

# ---------- teks bergaya ----------

def _t(text):
    """RichText hanya menerima str / RichText / list-nya."""
    if isinstance(text, (str, RichText, list, tuple)):
        return text
    return str(text)

def bold(text) -> RichTextBold:
    return RichTextBold(_t(text))

def italic(text) -> RichTextItalic:
    return RichTextItalic(_t(text))

def code(text) -> RichTextCode:
    return RichTextCode(_t(text))

def mark(text) -> RichTextMarked:
    return RichTextMarked(_t(text))

def spoiler(text) -> RichTextSpoiler:
    return RichTextSpoiler(_t(text))

def sub(text) -> RichTextSubscript:
    return RichTextSubscript(_t(text))

def sup(text) -> RichTextSuperscript:
    return RichTextSuperscript(_t(text))

def link(text, url: str) -> RichTextUrl:
    """Teks yang bisa diklik."""
    return RichTextUrl(text, url)

html_link = link

def emoji(custom_emoji_id: str, alt: str) -> RichTextCustomEmoji:
    return RichTextCustomEmoji(custom_emoji_id, alt)

# ---------- blok ----------

def heading(text, size: int = 3) -> InputRichBlockSectionHeading:
    return InputRichBlockSectionHeading(text, size)

def title(text) -> InputRichBlockSectionHeading:
    return InputRichBlockSectionHeading(text, 1)

def para(text) -> InputRichBlockParagraph:
    return InputRichBlockParagraph(text)

def quote(blocks, credit=None) -> InputRichBlockBlockQuotation:
    if not isinstance(blocks, (list, tuple)):
        blocks = [blocks]
    return InputRichBlockBlockQuotation(list(blocks), credit=credit)

def pre(text, language: str | None = None) -> InputRichBlockPreformatted:
    return InputRichBlockPreformatted(text, language=language)

def math(expression: str) -> InputRichBlockMathematicalExpression:
    return InputRichBlockMathematicalExpression(expression)

def caption(text, credit=None) -> RichBlockCaption:
    return RichBlockCaption(text, credit=credit)

def photo(file_id: str, caption_text=None, credit=None,
          has_spoiler: bool = False) -> InputRichBlockPhoto:
    """Blok foto di dalam rich message (PP user / foto chat)."""
    cap = caption(caption_text, credit=credit) if caption_text else None
    return InputRichBlockPhoto(
        InputMediaPhoto(file_id, has_spoiler=has_spoiler or None), cap
    )

def divider() -> InputRichBlockDivider:
    return InputRichBlockDivider()

def footer(text) -> InputRichBlockFooter:
    return InputRichBlockFooter(text)

def details(summary, blocks, is_open: bool = False) -> InputRichBlockDetails:
    if not isinstance(blocks, (list, tuple)):
        blocks = [blocks]
    return InputRichBlockDetails(summary, list(blocks), is_open=is_open)

def _item(text, **kwargs) -> InputRichBlockListItem:
    return InputRichBlockListItem([para(text)], **kwargs)

def bullets(items) -> InputRichBlockList:
    return InputRichBlockList([_item(t) if not isinstance(t, InputRichBlockListItem)
                               else t for t in items])

def checklist(items) -> InputRichBlockList:
    """items: list of (checked: bool, teks)."""
    out = []
    for checked, text in items:
        out.append(_item(text, has_checkbox=True, is_checked=bool(checked)))
    return InputRichBlockList(out)

def _cell(value):
    if value is None:
        return "-"
    if isinstance(value, (RichText, list, tuple)):
        return value
    return str(value)

def table(rows, header: bool = False, striped: bool = True,
          bordered: bool = False, compact: bool = False,
          align: str = "left") -> InputRichBlockTable:
    cells = [
        [
            RichBlockTableCell(text=_cell(c), is_header=bool(header and i == 0),
                               align=align)
            for c in row
        ]
        for i, row in enumerate(rows)
    ]
    return InputRichBlockTable(cells, is_bordered=bordered, is_striped=striped,
                               is_compact=compact)

def kv_table(rows, value_align: str = "left") -> InputRichBlockTable:
    """Tabel 2 kolom label/nilai; label di-bold, tanpa header."""
    cells = [
        [
            RichBlockTableCell(text=RichTextBold(k), align="left"),
            RichBlockTableCell(text=_cell(v), align=value_align),
        ]
        for k, v in rows
    ]
    return InputRichBlockTable(cells, is_bordered=False, is_striped=True)

def rbtn(text, style=DEFAULT, callback_data=None, url=None,
         copy: str | None = None, disabled: bool = False,
         web_app=None, switch_inline_query: str | None = None) -> RichMessageButton:
    kwargs = {}
    if disabled:
        kwargs["disabled"] = DisabledButton()
    elif callback_data is not None:
        kwargs["callback_data"] = callback_data
    elif url is not None:
        kwargs["url"] = url
    elif copy is not None:
        kwargs["copy_text"] = CopyTextButton(text=str(copy))
    elif web_app is not None:
        kwargs["web_app"] = web_app
    elif switch_inline_query is not None:
        kwargs["switch_inline_query"] = switch_inline_query
    else:
        kwargs["callback_data"] = "noop"
    return RichMessageButton(text, style=style, **kwargs)

def buttons(row, align: str | None = "center") -> InputRichBlockButtons:
    return InputRichBlockButtons(list(row), align=align)

def rich(blocks, media=None) -> InputRichMessage:
    return InputRichMessage(blocks=list(blocks), media=media)

# ---------- kirim / edit ----------

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

async def reply(client, message, *, blocks=None, media=None, html: str | None = None,
                fallback: str | None = None, reply_markup=None,
                effect: int | None = None, with_effect: bool = True, **kwargs):
    """Balas pesan dengan rich message; fallback otomatis ke HTML."""
    msg = InputRichMessage(blocks=blocks, html=html, media=media)
    text = _text_of(msg, fallback)
    chat_id = message.chat.id
    private = str(getattr(message.chat, "type", "")).endswith("PRIVATE")
    eff = effect if effect is not None else (effect_id() if (with_effect and private) else None)

    if (blocks or html or media) and rich_available():
        try:
            return await client.send_rich_message(
                chat_id, msg, reply_markup=reply_markup,
                effect_id=eff, reply_parameters=ReplyParameters(message_id=message.id),
            )
        except Exception as err:
            _note_fail()
            logger.warning("Rich message gagal (%s) -> fallback HTML.", err)
    return await _send_plain(client, chat_id, text, reply_markup, eff, **kwargs)

async def edit(client, message, *, blocks=None, html: str | None = None,
               fallback: str | None = None, reply_markup=None):
    msg = InputRichMessage(blocks=blocks, html=html)
    if (blocks or html) and rich_available():
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
