"""Resolve target (user/chat) + format kartu informasi."""

import html

from pyrogram import enums

NA = "N/A"
UNKNOWN = "Unknown"


def full_name(user) -> str:
    name = " ".join(x for x in (user.first_name, user.last_name) if x)
    return name or NA


def esc(text) -> str:
    return html.escape(str(text)) if text is not None else NA


def mention(user) -> str:
    """Nama yang bisa diklik (permanen walau tanpa username)."""
    return f'<a href="{perm_link(user)}">{esc(full_name(user))}</a>'


def perm_link(user) -> str:
    if getattr(user, "username", None):
        return f"https://t.me/{user.username}"
    return f"tg://user?id={user.id}"


def yesno(value) -> str:
    return "Yes" if value else "No"


def _photo_id(user):
    photo = getattr(user, "photo", None)
    return photo.big_file_id if photo else None


async def user_card(client, user, bio=None) -> tuple[str, str | None]:
    """-> (teks kartu, file_id foto atau None)."""
    if bio is None:
        try:
            bio = (await client.get_chat(user.id)).bio
        except Exception:
            bio = None

    # Catatan: Telegram (MTProto/TDLib) tidak menyimpan tanggal registrasi
    # akun, jadi nilainya "Unknown" — sama seperti DC/photo yang bisa kosong.
    text = (
        "👤 <b>User Information</b>\n\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"👤 <b>First Name:</b> {esc(user.first_name)}\n"
        f"👥 <b>Last Name:</b> {esc(user.last_name) if user.last_name else NA}\n"
        f"🔗 <b>Username:</b> {'@' + user.username if user.username else NA}\n"
        f"🌐 <b>DC ID:</b> {getattr(user, 'dc_id', None) or UNKNOWN}\n"
        f"🖼 <b>Photo:</b> {'✅' if _photo_id(user) else 'none'}\n"
        f"⭐️ <b>Premium:</b> {yesno(user.is_premium)}\n"
        f"🤖 <b>Bot:</b> {yesno(user.is_bot)}\n"
        f"🌍 <b>Language:</b> {user.language_code or UNKNOWN}\n"
        f"🗓 <b>Registration Date:</b> {UNKNOWN}\n"
        f"🔗 <b>Permanent Link:</b> {mention(user)}\n"
        f"📝 <b>Bio:</b> {esc(bio) if bio else NA}"
    )
    return text, _photo_id(user)


async def chat_card(client, chat) -> str:
    username = f"@{chat.username}" if getattr(chat, "username", None) else NA
    members = getattr(chat, "members_count", None)
    if members is None:
        try:
            members = await client.get_chat_members_count(chat.id)
        except Exception:
            members = None
    description = getattr(chat, "description", None) or NA
    is_forum = getattr(chat, "is_forum", None)
    return (
        "💬 <b>Chat Information</b>\n\n"
        f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
        f"👤 <b>Title:</b> {esc(getattr(chat, 'title', None) or full_name(chat))}\n"
        f"🔗 <b>Username:</b> {username}\n"
        f"💬 <b>Type:</b> {getattr(chat, 'type', NA)}\n"
        f"🧵 <b>Forum:</b> {yesno(is_forum) if is_forum is not None else NA}\n"
        f"🔄 <b>Members:</b> {members if members is not None else NA}\n"
        f"🌐 <b>DC ID:</b> {getattr(chat, 'dc_id', None) or UNKNOWN}\n"
        f"📝 <b>Description:</b> {esc(description)}"
    )


def _looks_like_id(text: str) -> bool:
    return text.strip().lstrip("-").isdigit()


async def resolve_chat(client, text: str):
    """Ambil Chat dari id atau @username."""
    text = (text or "").strip()
    if not text:
        return None
    if _looks_like_id(text):
        target = int(text)
    elif text.startswith("@"):
        target = text
    else:
        return None
    try:
        return await client.get_chat(target)
    except Exception:
        return None
