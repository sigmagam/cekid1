"""Format kartu (rich + teks fallback) dan resolve chat."""

import html

NA = "N/A"
UNKNOWN = "Unknown"


def esc(value) -> str:
    return html.escape(str(value)) if value is not None else NA


def full_name(user) -> str:
    name = " ".join(x for x in (user.first_name, user.last_name) if x)
    return name or NA


def perm_link(user) -> str:
    if getattr(user, "username", None):
        return f"https://t.me/{user.username}"
    return f"tg://user?id={user.id}"


def yesno(value) -> str:
    return "Yes" if value else "No"


def _photo_id(user):
    photo = getattr(user, "photo", None)
    return photo.big_file_id if photo else None


async def user_card(client, user):
    """-> (blocks, teks_html, file_id_foto)."""
    from cekid import rich

    try:
        bio = (await client.get_chat(user.id)).bio
    except Exception:
        bio = None

    photo = _photo_id(user)
    name = full_name(user)
    rows = [
        ("🆔 ID", rich.code(user.id)),
        ("👤 First Name", user.first_name or NA),
        ("👥 Last Name", user.last_name or NA),
        ("🔗 Username", f"@{user.username}" if user.username else NA),
        ("🌐 DC ID", getattr(user, "dc_id", None) or UNKNOWN),
        ("🖼 Photo", "✅ ada" if photo else "none"),
        ("⭐️ Premium", rich.bold(yesno(user.is_premium))),
        ("🤖 Bot", rich.bold(yesno(user.is_bot))),
        ("🔗 Permanent Link", rich.link(name, perm_link(user))),
    ]

    text = (
        "👤 <b>User Information</b>\n"
        "<i>Semua detail akun Telegram yang bisa dibaca bot.</i>\n\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"👤 <b>First Name:</b> {esc(user.first_name)}\n"
        f"👥 <b>Last Name:</b> {esc(user.last_name) if user.last_name else NA}\n"
        f"🔗 <b>Username:</b> {'@' + user.username if user.username else NA}\n"
        f"🌐 <b>DC ID:</b> {getattr(user, 'dc_id', None) or UNKNOWN}\n"
        f"🖼 <b>Photo:</b> {'✅ ada' if photo else 'none'}\n"
        f"⭐️ <b>Premium:</b> {yesno(user.is_premium)}\n"
        f"🤖 <b>Bot:</b> {yesno(user.is_bot)}\n"
        f"🔗 <b>Permanent Link:</b> <a href=\"{perm_link(user)}\">{esc(name)}</a>"
    )

    blocks = [
        rich.title("👤 User Information"),
        rich.para(rich.italic("Semua detail akun Telegram yang bisa dibaca bot.")),
        rich.divider(),
        rich.kv_table(rows),
    ]
    if bio:
        blocks += [
            rich.divider(),
            rich.heading("📝 Bio", 3),
            rich.quote([rich.para(bio)]),
        ]
    else:
        blocks.append(rich.footer("📝 Bio: tidak ada"))

    return blocks, text, photo


async def chat_card(client, chat):
    """-> (blocks, teks_html)."""
    from cekid import rich

    username = f"@{chat.username}" if getattr(chat, "username", None) else NA
    members = getattr(chat, "members_count", None)
    if members is None:
        try:
            members = await client.get_chat_members_count(chat.id)
        except Exception:
            members = None
    description = getattr(chat, "description", None) or None
    title = getattr(chat, "title", None) or full_name(chat)
    is_forum = getattr(chat, "is_forum", None)
    ctype = str(getattr(chat, "type", NA)).replace("ChatType.", "")

    rows = [
        ("🆔 ID", rich.code(chat.id)),
        ("👤 Title", title),
        ("🔗 Username", username),
        ("💬 Type", ctype),
        ("🧵 Forum", yesno(is_forum) if is_forum is not None else NA),
        ("🔄 Members", members if members is not None else NA),
        ("🌐 DC ID", getattr(chat, "dc_id", None) or UNKNOWN),
    ]
    text = (
        "💬 <b>Chat Information</b>\n"
        "<i>Detail channel / group / forum.</i>\n\n"
        f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
        f"👤 <b>Title:</b> {esc(title)}\n"
        f"🔗 <b>Username:</b> {username}\n"
        f"💬 <b>Type:</b> {ctype}\n"
        f"🧵 <b>Forum:</b> {yesno(is_forum) if is_forum is not None else NA}\n"
        f"🔄 <b>Members:</b> {members if members is not None else NA}\n"
        f"🌐 <b>DC ID:</b> {getattr(chat, 'dc_id', None) or UNKNOWN}"
    )
    blocks = [
        rich.title("💬 Chat Information"),
        rich.para(rich.italic("Detail channel / group / forum.")),
        rich.divider(),
        rich.kv_table(rows),
    ]
    if description:
        blocks += [
            rich.divider(),
            rich.heading("📝 Description", 3),
            rich.quote([rich.para(description)]),
        ]
        text += f"\n📝 <b>Description:</b> {esc(description)}"
    else:
        blocks.append(rich.footer("📝 Description: tidak ada"))

    return blocks, text


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


def user_buttons(user):
    """Tombol rich message: salin ID + buka profil."""
    from cekid import rich

    row = [rich.rbtn("📋 Salin ID", style=rich.PRIMARY, copy=str(user.id))]
    if getattr(user, "username", None):
        row.append(rich.rbtn("🔗 Buka Profil", style=rich.SUCCESS,
                             url=perm_link(user)))
    return rich.buttons(row)


async def reply_user_card(client, message, user, badge: str | None = None,
                          reply_markup=None):
    """Kirim kartu user: foto+caption kalau ada PP, kalau tidak rich message."""
    from cekid import rich

    blocks, text, photo = await user_card(client, user)
    if badge:
        blocks.insert(1, rich.para(badge))
        text = f"{badge}\n\n{text}"
    blocks.append(user_buttons(user))
    if photo:
        try:
            private = str(getattr(message.chat, "type", "")).endswith("PRIVATE")
            return await message.reply_photo(
                photo, caption=text, reply_markup=reply_markup,
                effect_id=rich.effect_id() if private else None,
            )
        except Exception:
            pass
    return await rich.reply(
        client, message, blocks=blocks, fallback=text, reply_markup=reply_markup
    )


async def reply_chat_card(client, message, chat):
    from cekid import rich

    blocks, text = await chat_card(client, chat)
    blocks.append(rich.buttons([
        rich.rbtn("📋 Salin ID", style=rich.PRIMARY, copy=str(chat.id)),
    ]))
    return await rich.reply(client, message, blocks=blocks, fallback=text)
