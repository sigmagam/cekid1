"""Force subscribe gate: wajib join (plus satu opsional) sebelum pakai bot."""

import logging
import os

from pyrogram.errors import UserNotParticipant

from cekid import config

log = logging.getLogger("cekid.fsub")

# chat_id -> link, bisa dipaksa lewat env: FSUB_LINKS="-100123=https://t.me/x,..."
_ENV_LINKS = {}
for _pair in os.getenv("FSUB_LINKS", "").split(","):
    if "=" in _pair:
        _k, _v = _pair.split("=", 1)
        _ENV_LINKS[int(_k.strip())] = _v.strip()

_INFO: dict[int, dict] = {}

JOINED = {"ChatMemberStatus.OWNER", "ChatMemberStatus.ADMINISTRATOR",
          "ChatMemberStatus.MEMBER"}


async def info(client, chat_id: int) -> dict:
    """Judul + link chat (di-cache)."""
    if chat_id in _INFO:
        return _INFO[chat_id]
    title, url, username = None, _ENV_LINKS.get(chat_id), None
    try:
        chat = await client.get_chat(chat_id)
        title = getattr(chat, "title", None) or getattr(chat, "first_name", None)
        username = getattr(chat, "username", None)
        if url is None and username:
            url = f"https://t.me/{username}"
        if url is None:
            url = getattr(chat, "invite_link", None)
    except Exception as err:
        log.warning("Cannot read chat %s: %s", chat_id, err)
    if url is None:
        try:
            url = await client.export_chat_invite_link(chat_id)
        except Exception as err:
            log.warning("Cannot export invite link for %s: %s", chat_id, err)
    _INFO[chat_id] = {"title": title or str(chat_id), "url": url,
                      "username": username}
    return _INFO[chat_id]


async def member(client, chat_id: int, user_id: int):
    """True = member, False = not a member, None = unknown."""
    try:
        status = str((await client.get_chat_member(chat_id, user_id)).status)
        return status in JOINED
    except UserNotParticipant:
        return False
    except Exception as err:
        log.warning("Member check %s in %s failed: %s", user_id, chat_id, err)
        return None


async def missing(client, user_id: int) -> list[int]:
    """Required chats the user has not joined (unknown counts as passed)."""
    out = []
    for chat_id in config.FSUB_REQUIRED:
        if await member(client, chat_id, user_id) is False:
            out.append(chat_id)
    return out


async def blocks(client, missing_ids: list[int]):
    """Blok pesan gate (dipakai untuk kirim maupun edit)."""
    from cekid import rich

    chats = [(cid, True) for cid in config.FSUB_REQUIRED]
    chats += [(cid, False) for cid in config.FSUB_OPTIONAL]
    for chat_id, _ in chats:
        await info(client, chat_id)

    lines = []
    buttons = []
    for chat_id, required in chats:
        meta = _INFO.get(chat_id) or {}
        title = meta.get("title") or str(chat_id)
        username = meta.get("username")
        url = meta.get("url")
        label = title + (f" (@{username})" if username else "")
        shown = (rich.link(label, url) if url else label)
        lines.append([rich.bold("Wajib: " if required else "Opsional: "), shown])
        prefix = "❗️ " if (required and chat_id in missing_ids) else ("📢 " if required else "💬 ")
        buttons.append(rich.rbtn(prefix + label,
                                 style=rich.PRIMARY if required else rich.DEFAULT,
                                 url=url or "https://t.me"))
    buttons.append(rich.rbtn("🔄 Try again", style=rich.SUCCESS,
                             callback_data="fsub:check"))

    return [
        rich.title("🔒 Join required"),
        rich.para(rich.italic("Join the channel below, then tap Try again.")),
        rich.divider(),
        rich.bullets(lines),
        rich.para("The group is optional — join it only if you want to."),
        rich.buttons(buttons),
    ]


GATE_TEXT = ("🔒 <b>Join required</b>\n\n"
             "Join the channel below, then tap Try again.\n"
             "The group is optional.")


async def send_gate(client, update, missing_ids: list[int]):
    from cekid import rich

    data = await blocks(client, missing_ids)
    target = update if hasattr(update, "reply_text") else getattr(update, "message", None)
    if target is None:
        return None
    try:
        return await rich.reply(client, target, blocks=data, fallback=GATE_TEXT)
    except Exception as err:
        log.warning("Cannot send gate: %s", err)
        return None
