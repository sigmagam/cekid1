"""Card formatting (rich blocks + HTML fallback) and chat resolving."""

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
    if value is None:
        return UNKNOWN  # peers from the picker are sometimes partial
    return "Yes" if value else "No"


def _photo_id(user):
    photo = getattr(user, "photo", None)
    return photo.big_file_id if photo else None


def _as_photo_id(fid):
    """Convert a CHAT_PHOTO file id to PHOTO (Telegram rejects CHAT_PHOTO here)."""
    if not fid:
        return None
    try:
        from pyrogram.file_id import FileId, FileType
        info = FileId.decode(fid)
        if info.file_type == FileType.PHOTO:
            return fid
        if info.file_type != FileType.CHAT_PHOTO:
            return None
        return FileId(
            major=info.major, minor=info.minor, file_type=FileType.PHOTO,
            dc_id=info.dc_id, file_reference=info.file_reference, url=info.url,
            media_id=info.media_id, access_hash=info.access_hash,
            volume_id=info.volume_id, thumbnail_source=info.thumbnail_source,
            thumbnail_file_type=info.thumbnail_file_type,
            thumbnail_size=info.thumbnail_size, secret=info.secret,
            local_id=info.local_id, chat_id=info.chat_id,
            chat_access_hash=info.chat_access_hash,
            sticker_set_id=info.sticker_set_id,
            sticker_set_access_hash=info.sticker_set_access_hash,
            sticker_set_version=info.sticker_set_version,
        ).encode()
    except Exception:
        return None


async def _photo_ids(client, chat_id, fallback=None, limit: int = 4) -> list[str]:
    """Collect photos for the slideshow; falls back to the object photo."""
    ids: list[str] = []
    try:
        async for ph in client.get_chat_photos(chat_id, limit=limit):
            fid = getattr(ph, "big_file_id", None) or getattr(ph, "file_id", None)
            fid = _as_photo_id(fid)
            if fid and fid not in ids:
                ids.append(fid)
    except Exception:
        pass
    if not ids:
        fid = _as_photo_id(fallback)
        if fid:
            ids = [fid]
    return ids


async def user_card(client, user):
    """-> (blocks, html_text, photo_file_id). Clean card, details collapsed."""
    from cekid import rich

    bio = None
    try:
        bio = (await client.get_chat(user.id)).bio
    except Exception:
        bio = None

    raw_photo = _photo_id(user)
    name = full_name(user)
    dc = getattr(user, "dc_id", None)
    photos = await _photo_ids(client, user.id, raw_photo)

    blocks = [rich.title(f"👤 {name}")]
    line = [rich.code(user.id)]
    if getattr(user, "username", None):
        line += ["  ·  ", f"@{user.username}"]
    blocks.append(rich.para(line))

    media = rich.photos(photos, rich.bold(name), credit=f"ID {user.id}")
    if media is not None:
        blocks += [rich.divider(), media]

    badges = []
    if user.is_bot is not None:
        badges.append("🤖 Bot account" if user.is_bot else "👤 Human")
    if user.is_premium:
        badges.append("⭐️ Premium")
    if dc:
        badges.append(f"🌐 DC {dc}")
    if len(photos) > 1:
        badges.append(f"🖼 {len(photos)} photos")
    if badges:
        blocks.append(rich.para([rich.bold(" · ".join(badges))]))

    rows = [("🆔 ID", rich.code(user.id))]
    if getattr(user, "first_name", None):
        rows.append(("👤 First name", user.first_name))
    if getattr(user, "last_name", None):
        rows.append(("👥 Last name", user.last_name))
    if getattr(user, "username", None):
        rows.append(("🔗 Username", f"@{user.username}"))
    if user.is_premium is not None:
        rows.append(("⭐️ Premium", "Yes" if user.is_premium else "No"))
    if user.is_bot is not None:
        rows.append(("🤖 Bot", "Yes" if user.is_bot else "No"))
    if dc:
        rows.append(("🌐 DC ID", str(dc)))
    if photos:
        rows.append(("🖼 Photos", str(len(photos))))
    rows.append(("🔗 Permanent link", rich.spoiler(rich.link(name, perm_link(user)))))
    blocks.append(rich.details("📄 Full details",
                               [rich.table(rows, striped=True, compact=True)]))

    if bio:
        blocks += [rich.divider(), rich.heading("📝 Bio", 3),
                   rich.quote([rich.para(bio)], credit=name)]

    text = f"👤 <b>{esc(name)}</b>\n🆔 <code>{user.id}</code>"
    for label, value in rows[1:]:
        if label.startswith("🔗 Permanent"):
            continue
        text += f"\n<b>{label}:</b> {esc(value if isinstance(value, str) else rich.plain(value))}"
    if bio:
        text += f"\n📝 <b>Bio:</b> {esc(bio)}"
    text += f"\n🔗 <a href=\"{perm_link(user)}\">{esc(name)}</a>"

    return blocks, text, raw_photo


async def chat_card(client, chat):
    """-> (blocks, html_text). Clean card, details collapsed."""
    from cekid import rich

    members = getattr(chat, "members_count", None)
    if members is None:
        try:
            members = await client.get_chat_members_count(chat.id)
        except Exception:
            members = None
    description = getattr(chat, "description", None) or None
    title = getattr(chat, "title", None) or full_name(chat)
    is_forum = getattr(chat, "is_forum", None)
    ctype = str(getattr(chat, "type", "")).replace("ChatType.", "") or None
    dc = getattr(chat, "dc_id", None)
    chat_photo = getattr(chat, "photo", None)
    fallback_photo = getattr(chat_photo, "big_file_id", None) if chat_photo else None
    photos = await _photo_ids(client, chat.id, fallback_photo, limit=4)

    blocks = [rich.title(f"💬 {title}")]
    line = [rich.code(chat.id)]
    if ctype:
        line += ["  ·  ", ctype.lower()]
    if getattr(chat, "username", None):
        line += ["  ·  ", f"@{chat.username}"]
    blocks.append(rich.para(line))

    media = rich.photos(photos, rich.bold(title), credit=f"ID {chat.id}")
    if media is not None:
        blocks += [rich.divider(), media]

    badges = []
    if members is not None:
        badges.append(f"🔄 {members:,} users")
    if is_forum:
        badges.append("🧵 Forum")
    if dc:
        badges.append(f"🌐 DC {dc}")
    if len(photos) > 1:
        badges.append(f"🖼 {len(photos)} photos")
    if badges:
        blocks.append(rich.para([rich.bold(" · ".join(badges))]))

    rows = [("🆔 ID", rich.code(chat.id))]
    if title:
        rows.append(("👤 Title", title))
    if getattr(chat, "username", None):
        rows.append(("🔗 Username", f"@{chat.username}"))
    if ctype:
        rows.append(("💬 Type", ctype))
    if is_forum is not None:
        rows.append(("🧵 Forum", "Yes" if is_forum else "No"))
    if members is not None:
        rows.append(("🔄 Members", f"{members:,}"))
    if dc:
        rows.append(("🌐 DC ID", str(dc)))

    raw_id = str(chat.id)
    if raw_id.startswith("-100"):
        inner = int(raw_id[4:])
        detail_blocks = [
            rich.table(rows, striped=True, compact=True),
            rich.divider(),
            rich.para(["Supergroup/channel IDs are ", rich.code("-100"),
                       " plus the real ID:"]),
            rich.math(f"{raw_id} = -(10^{{12}} + {inner})"),
            rich.para(["Real ID without prefix: ", rich.code(inner), "."]),
        ]
    else:
        detail_blocks = [rich.table(rows, striped=True, compact=True)]
    blocks.append(rich.details("📄 Full details", detail_blocks))

    if description:
        blocks += [rich.divider(), rich.heading("📝 Description", 3),
                   rich.quote([rich.para(description)], credit=title)]

    text = f"💬 <b>{esc(title)}</b>\n🆔 <code>{chat.id}</code>"
    for label, value in rows[1:]:
        text += f"\n<b>{label}:</b> {esc(value if isinstance(value, str) else rich.plain(value))}"
    if description:
        text += f"\n📝 <b>Description:</b> {esc(description)}"

    return blocks, text


def _looks_like_id(text: str) -> bool:
    return text.strip().lstrip("-").isdigit()


async def resolve_chat(client, text: str):
    """Resolve a Chat from an id or @username."""
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
    """Rich message buttons: copy ID + open profile."""
    from cekid import rich

    row = [rich.rbtn("📋 Copy ID", style=rich.PRIMARY, copy=str(user.id))]
    if getattr(user, "username", None):
        row.append(rich.rbtn("🔗 Open Profile", style=rich.SUCCESS,
                             url=perm_link(user)))
    return rich.buttons(row)


async def reply_user_card(client, message, user, badge=None, reply_markup=None):
    """Send the user card as a rich message (profile photo included inside)."""
    from cekid import rich

    blocks, text, photo = await user_card(client, user)
    if badge is not None:
        blocks.insert(0, rich.para([rich.bold(badge)]))
        text = f"{rich.plain(badge)}\n\n{text}"
    blocks.append(user_buttons(user))
    sent = await rich.reply(client, message, blocks=blocks, fallback=text,
                            reply_markup=reply_markup)
    pid = _as_photo_id(photo)
    if sent is None and pid:
        try:
            private = str(getattr(message.chat, "type", "")).endswith("PRIVATE")
            return await message.reply_photo(
                pid, caption=text, reply_markup=reply_markup,
                effect_id=rich.effect_id() if private else None,
            )
        except Exception:
            pass
    return sent


async def reply_chat_card(client, message, chat):
    from cekid import rich

    blocks, text = await chat_card(client, chat)
    blocks.append(rich.buttons([
        rich.rbtn("📋 Copy ID", style=rich.PRIMARY, copy=str(chat.id)),
    ]))
    return await rich.reply(client, message, blocks=blocks, fallback=text)
