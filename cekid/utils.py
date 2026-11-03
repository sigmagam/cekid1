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
    t = text.strip()
    return t.lstrip("-").isdigit()


async def resolve_user(client, msg):
    """Ambil User dari pesan (picker / balas pesan / id / @username)."""
    shared = getattr(msg, "users_shared", None)
    if shared and shared.users:
        try:
            return await client.get_users(shared.users[0].id)
        except Exception:
            return None

    if getattr(msg, "reply_to_message", None) and msg.reply_to_message.from_user:
        return msg.reply_to_message.from_user

    text = (msg.text or "").strip()
    if _looks_like_id(text):
        try:
            return await client.get_users(int(text))
        except Exception:
            return None
    if text.startswith("@") or text:
        try:
            return await client.get_users(text)
        except Exception:
            return None
    return None


async def resolve_chat(client, msg, expect_forum: bool = False):
    """Ambil Chat dari pesan (picker / balas pesan / id / @username)."""
    shared = getattr(msg, "chat_shared", None)
    chat_id = None
    if shared and shared.chat:
        chat_id = shared.chat.id
    elif getattr(msg, "reply_to_message", None):
        chat_id = msg.reply_to_message.chat.id
    else:
        text = (msg.text or "").strip()
        if _looks_like_id(text):
            chat_id = int(text)
        elif text.startswith("@"):
            chat_id = text

    if chat_id is None:
        return None
    try:
        chat = await client.get_chat(chat_id)
    except Exception:
        return None
    if expect_forum and not getattr(chat, "is_forum", False):
        return chat
    return chat


def chat_kind(chat) -> str:
    t = str(getattr(chat, "type", ""))
    if t.endswith("CHANNEL"):
        return "channel"
    if t.endswith("SUPERGROUP"):
        return "supergroup"
    if t.endswith("GROUP"):
        return "group"
    return "user"
