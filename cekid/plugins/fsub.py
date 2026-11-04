"""Tombol Try again untuk verifikasi wajib join."""

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from cekid import bot, fsub, rich
from cekid.safety import safe

@Client.on_callback_query(filters.regex("^fsub:"))
@safe(gate=False)
async def check_join(_, cq: CallbackQuery):
    missing = await fsub.missing(bot, cq.from_user.id)
    if not missing:
        await cq.answer("✅ Verified")
        return await rich.edit(
            bot, cq.message,
            blocks=[
                rich.title("✅ Verified"),
                rich.para(rich.italic("You can use the bot now.")),
                rich.divider(),
                rich.para("Send /start to begin."),
            ],
            fallback="✅ <b>Verified</b>\n\nYou can use the bot now. Send /start.",
        )
    await cq.answer("❌ You have not joined yet", show_alert=True)
    data = await fsub.blocks(bot, missing)
    return await rich.edit(bot, cq.message, blocks=data, fallback=fsub.GATE_TEXT)
