#!/bin/bash
echo "— screen —"
screen -ls 2>/dev/null | grep cekid1 || echo "tidak ada screen cekid1"
echo "— proses —"
if fuser /root/cekid1/.cekid.lock >/dev/null 2>&1; then
    fuser -v /root/cekid1/.cekid.lock 2>&1
else
    pgrep -af '/root/cekid1/run.sh|/root/cekid1/venv/bin/python3' || echo "tidak ada proses cekid1"
fi
echo "— log —"
tail -n 15 /root/cekid1/cekid.log 2>/dev/null || echo "(belum ada log)"
