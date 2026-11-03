"""Task latar: backup database tiap jam 00:00 WIB ke admin."""

import asyncio
import logging
import os
import sqlite3
from datetime import datetime, timedelta, timezone

from cekid import config

log = logging.getLogger("cekid.tasks")

WIB = timezone(timedelta(hours=7), "WIB")


def snapshot(path: str) -> str | None:
    """Salinan konsisten DB (via sqlite backup API) — aman walau bot sedang jalan."""
    if not os.path.exists(path):
        return None
    tmp = f"{path}.backup"
    src = sqlite3.connect(path, timeout=30)
    dst = sqlite3.connect(tmp)
    try:
        with dst:
            src.backup(dst)
    finally:
        src.close()
        dst.close()
    return tmp


async def send_backup(client) -> None:
    path = await asyncio.to_thread(snapshot, config.DB_PATH)
    if not path:
        log.warning("Backup dilewati: %s tidak ada.", config.DB_PATH)
        return
    caption = f"🗄 <b>Backup database</b>\n{datetime.now(WIB):%Y-%m-%d %H:%M} WIB"
    try:
        for admin in config.ADMIN_IDS:
            try:
                await client.send_document(admin, path, caption=caption)
            except Exception as err:
                log.warning("Gagal kirim backup ke %s: %s", admin, err)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def _seconds_to_midnight() -> float:
    now = datetime.now(WIB)
    nxt = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return (nxt - now).total_seconds()


async def backup_loop(client) -> None:
    """Kirim backup tepat jam 00:00 WIB, lalu ulangi tiap hari."""
    while True:
        wait = _seconds_to_midnight()
        log.info("Backup DB berikutnya dalam %.0f detik (00:00 WIB).", wait)
        try:
            await asyncio.sleep(wait)
            await send_backup(client)
        except asyncio.CancelledError:
            raise
        except Exception as err:
            log.warning("Backup harian gagal: %s", err)
        await asyncio.sleep(60)  # lewati batas tengah malam, jangan dobel
