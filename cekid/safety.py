"""Guard so a handler error replies instead of failing silently."""

import functools
import logging

log = logging.getLogger("cekid.safe")

def safe(func):
    """Log the traceback and tell the user, instead of dying quietly."""
    @functools.wraps(func)
    async def wrapper(client, update, *args, **kwargs):
        try:
            return await func(client, update, *args, **kwargs)
        except Exception as err:
            log.exception("Handler %s failed: %s", func.__name__, err)
            notice = "⚠️ Something went wrong. Please try again."
            try:
                if hasattr(update, "reply_text"):
                    await update.reply_text(notice)
                elif getattr(update, "message", None) is not None:
                    await update.message.reply_text(notice)
                else:
                    await update.answer("Something went wrong.", show_alert=True)
            except Exception:
                pass
    return wrapper
