"""Gate (wajib join) + guard supaya error handler balas pesan, tidak diam."""

import functools
import logging

from cekid import config, fsub

log = logging.getLogger("cekid.safe")

NOTICE = "⚠️ Something went wrong. Please try again."


async def _notify(update) -> None:
    try:
        if hasattr(update, "reply_text"):
            await update.reply_text(NOTICE)
        elif getattr(update, "message", None) is not None:
            await update.message.reply_text(NOTICE)
        else:
            await update.answer("Something went wrong.", show_alert=True)
    except Exception:
        pass


def safe(func=None, *, gate: bool = True):
    """Decorator: cek wajib join dulu, lalu jaga error handler."""
    def decorate(fn):
        @functools.wraps(fn)
        async def wrapper(client, update, *args, **kwargs):
            user = getattr(update, "from_user", None)
            if gate and user is not None and user.id not in config.ADMIN_IDS:
                try:
                    missing = await fsub.missing(client, user.id)
                    if missing:
                        return await fsub.send_gate(client, update, missing)
                except Exception as err:  # jangan pernah blokir karena error cek
                    log.warning("Force-subscribe check failed: %s", err)
            try:
                return await fn(client, update, *args, **kwargs)
            except Exception as err:
                log.exception("Handler %s failed: %s", fn.__name__, err)
                await _notify(update)
        return wrapper
    return decorate if func is None else decorate(func)
