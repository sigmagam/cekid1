"""CekID bot entry point."""

import fcntl
import sys
from pathlib import Path

from cekid import bot

LOCK = Path("/root/cekid1/.bot.lock")


def single_instance():
    """Cuma satu proses bot. Exit diam-diam kalau sudah ada yang jalan."""
    handle = open(LOCK, "w")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("Another cekid1 instance is already running.")
        sys.exit(0)
    return handle


if __name__ == "__main__":
    _lock = single_instance()
    bot.run()
