"""Card formatting (rich blocks + HTML fallback) and chat resolving."""

import logging
import os

import html

log = logging.getLogger("cekid.utils")

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


def _about(info):
    """Bio user / deskripsi chat / about bot."""
    for attr in ("bio", "description", "about"):
        value = getattr(info, attr, None)
        if value:
            return value
    return None


async def _enrich(client, obj):
    """Ambil data terbaru dari server (id dulu, lalu @username)."""
    targets = []
    if getattr(obj, "id", None) is not None:
        targets.append(obj.id)
    if getattr(obj, "username", None):
        targets.append(f"@{obj.username}")
    for target in targets:
        try:
            got = await client.get_chat(target)
        except Exception:
            continue
        if got is not None:
            return got
    return None


def _retype(fid, file_type):
    """Re-encode a file id with a different FileType (PHOTO -> VIDEO/ANIMATION)."""
    if not fid:
        return None
    try:
        from pyrogram.file_id import FileId
        info = FileId.decode(fid)
        return FileId(
            major=info.major, minor=info.minor, file_type=file_type,
            dc_id=info.dc_id, file_reference=info.file_reference, url=info.url,
            media_id=info.media_id, access_hash=info.access_hash,
        ).encode()
    except Exception:
        return None


async def _profile_video(client, chat_id):
    """Video/gif profile photo (Telegram animated avatar), kalau ada."""
    try:
        async for ph in client.get_chat_photos(chat_id, limit=1):
            anim = getattr(ph, "animation", None)
            video = getattr(anim, "animation", None) if anim else None
            if video is not None:
                return video
    except Exception:
        pass
    return None


async def attach_video(client, sent, blocks, text, video):
    """Kartu sudah terkirim; sekarang sunting biar videonya ikut (unggah belakangan)."""
    from cekid import rich

    if sent is None or video is None:
        return sent
    path = None
    try:
        path = await client.download_media(video)
        if not path:
            return sent
        block = rich.video(
            path,
            duration=int(getattr(video, "duration", 0) or 0),
            width=int(getattr(video, "width", 0) or 512),
            height=int(getattr(video, "height", 0) or 512),
        )
        return await rich.edit(client, sent, blocks=[block] + list(blocks),
                               fallback=text)
    except Exception as err:
        log.warning("Gagal menempelkan video ke kartu: %s", err)
        return sent
    finally:
        if path:
            try:
                os.remove(path)
            except OSError:
                pass


async def send_profile_video(client, chat_id, video, caption=None):
    """Kirim foto profil video sebagai video/animation (gif)."""
    from pyrogram.file_id import FileType

    fid = getattr(video, "file_id", None)
    for kind, retype in (("animation", FileType.ANIMATION), ("video", FileType.VIDEO)):
        fixed = _retype(fid, retype)
        if not fixed:
            continue
        try:
            if kind == "animation":
                return await client.send_animation(chat_id, fixed, caption=caption)
            return await client.send_video(chat_id, fixed, caption=caption,
                                           supports_streaming=True)
        except Exception:
            continue
    # Jalan terakhir: unduh lalu unggah ulang.
    path = None
    try:
        path = await client.download_media(video)
        if path:
            try:
                return await client.send_animation(chat_id, path, caption=caption)
            except Exception:
                return await client.send_video(chat_id, path, caption=caption,
                                               supports_streaming=True)
    except Exception:
        return None
    finally:
        if path:
            try:
                os.remove(path)
            except OSError:
                pass
    return None


async def user_card(client, user):
    """-> (blocks, html_text, photo_file_id). Plain bordered table (variant 10)."""
    from cekid import rich

    info = await _enrich(client, user)
    bio = _about(info) if info is not None else None
    if info is not None:
        for attr in ("dc_id", "photo", "is_premium", "is_bot", "first_name",
                     "last_name", "username"):
            mine, theirs = getattr(user, attr, None), getattr(info, attr, None)
            if mine is None and theirs is not None:
                try:
                    setattr(user, attr, theirs)
                except Exception:
                    pass

    raw_photo = _photo_id(user)
    name = full_name(user)
    dc = getattr(user, "dc_id", None)
    photos = await _photo_ids(client, user.id, raw_photo)
    video = await _profile_video(client, user.id)

    rows = [("ID", rich.code(user.id))]
    if getattr(user, "first_name", None):
        rows.append(("FIRST NAME", user.first_name))
    if getattr(user, "last_name", None):
        rows.append(("LAST NAME", user.last_name))
    if getattr(user, "username", None):
        rows.append(("USERNAME", f"@{user.username}"))
    if user.is_premium is not None:
        rows.append(("PREMIUM", "YES" if user.is_premium else "NO"))
    if user.is_bot is not None:
        rows.append(("BOT", "YES" if user.is_bot else "NO"))
    if dc:
        rows.append(("DC", str(dc)))
    if photos:
        rows.append(("PHOTOS", str(len(photos))))
    rows.append(("LINK", rich.spoiler(rich.link(name, perm_link(user)))))

    blocks = []
    if video is None:
        media = rich.photos(photos)
        if media is not None:
            blocks.append(media)
    blocks.append(rich.table(rows, header=True, bordered=True,
                             striped=False, compact=True))
    if bio:
        blocks += [rich.divider(), rich.quote([rich.para(bio)], credit=name)]

    text = f"👤 <b>{esc(name)}</b>\n"
    for label, value in rows:
        if label == "LINK":
            continue
        text += f"<b>{label}:</b> {esc(value if isinstance(value, str) else rich.plain(value))}\n"
    if bio:
        text += f"📝 <b>Bio:</b> {esc(bio)}\n"
    text += f'🔗 <a href="{perm_link(user)}">{esc(name)}</a>'

    return blocks, text, raw_photo, video


async def chat_card(client, chat):
    """-> (blocks, html_text). Plain bordered table (variant 10)."""
    from cekid import rich

    chat_id = chat.id
    info = await _enrich(client, chat)
    if info is not None:
        chat = info
    members = getattr(chat, "members_count", None)
    if members is None:
        try:
            members = await client.get_chat_members_count(chat_id)
        except Exception:
            members = None
    description = _about(chat)
    title = getattr(chat, "title", None) or full_name(chat)
    is_forum = getattr(chat, "is_forum", None)
    ctype = str(getattr(chat, "type", "")).replace("ChatType.", "") or None
    dc = getattr(chat, "dc_id", None)
    chat_photo = getattr(chat, "photo", None)
    fallback_photo = getattr(chat_photo, "big_file_id", None) if chat_photo else None
    photos = await _photo_ids(client, chat_id, fallback_photo, limit=4)
    video = await _profile_video(client, chat_id)

    rows = [("ID", rich.code(chat_id))]
    if title:
        rows.append(("TITLE", title))
    username = getattr(chat, "username", None)
    if username:
        rows.append(("USERNAME", f"@{username}"))
    if ctype:
        rows.append(("TYPE", ctype.upper()))
    if is_forum is not None:
        rows.append(("FORUM", "YES" if is_forum else "NO"))
    if members is not None:
        rows.append(("MEMBERS", f"{members:,}"))
    if dc:
        rows.append(("DC", str(dc)))
    if photos:
        rows.append(("PHOTOS", str(len(photos))))

    blocks = []
    if video is None:
        media = rich.photos(photos)
        if media is not None:
            blocks.append(media)
    blocks.append(rich.table(rows, header=True, bordered=True,
                             striped=False, compact=True))

    raw_id = str(chat_id)
    if raw_id.startswith("-100"):
        inner = int(raw_id[4:])
        blocks += [rich.divider(),
                   rich.math(f"{raw_id} = -(10^{{12}} + {inner})"),
                   rich.para(["Real ID without the -100 prefix: ",
                              rich.code(inner), "."])]
    if description:
        blocks += [rich.divider(), rich.quote([rich.para(description)], credit=title)]

    text = f"💬 <b>{esc(title)}</b>\n"
    for label, value in rows:
        text += f"<b>{label}:</b> {esc(value if isinstance(value, str) else rich.plain(value))}\n"
    if description:
        text += f"📝 <b>Description:</b> {esc(description)}"

    return blocks, text, video


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

    row = [rich.rbtn("Copy ID", style=rich.PRIMARY, copy=str(user.id))]
    if getattr(user, "username", None):
        row.append(rich.rbtn("Open Profile", style=rich.SUCCESS,
                             url=perm_link(user)))
    return rich.buttons(row)


async def reply_user_card(client, message, user, badge=None, reply_markup=None):
    """Send the user card as a rich message (profile photo included inside)."""
    from cekid import rich

    blocks, text, photo, video = await user_card(client, user)
    if badge is not None:
        blocks.insert(0, rich.para([rich.bold(badge)]))
        text = f"{rich.plain(badge)}\n\n{text}"
    blocks.append(user_buttons(user))
    sent = await rich.reply(client, message, blocks=blocks, fallback=text,
                            reply_markup=reply_markup)
    if sent is None:
        # Rich ditolak server -> kalau ada video, kirim sebagai pesan biasa.
        if video is not None:
            await send_profile_video(client, message.chat.id, video)
    elif video is not None:
        # Video diunggah setelah kartu tampil, lalu kartunya disunting.
        await attach_video(client, sent, blocks, text, video)
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

    blocks, text, video = await chat_card(client, chat)
    blocks.append(rich.buttons([
        rich.rbtn("Copy ID", style=rich.PRIMARY, copy=str(chat.id)),
    ]))
    sent = await rich.reply(client, message, blocks=blocks, fallback=text)
    if sent is None:
        if video is not None:
            await send_profile_video(client, message.chat.id, video)
    elif video is not None:
        await attach_video(client, sent, blocks, text, video)
    return sent
