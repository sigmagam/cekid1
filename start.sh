#!/bin/bash
# Jalankan bot di screen "cekid1" (auto-restart via run.sh).
# Kalau screen tidak tersedia/gagal, fallback ke nohup.
cd /root/cekid1 || exit 1

if screen -ls 2>/dev/null | grep -q "\.cekid1"; then
    echo "Screen cekid1 sudah jalan."
    exit 0
fi

if command -v screen >/dev/null 2>&1; then
    screen -dmS cekid1 /root/cekid1/run.sh
    sleep 2
    if screen -ls 2>/dev/null | grep -q "\.cekid1"; then
        echo "✅ cekid1 jalan di screen (lihat: screen -r cekid1)"
        exit 0
    fi
    echo "⚠️ screen gagal dibuat, pakai nohup..."
fi

if pgrep -f '/root/cekid1/run.sh' >/dev/null; then
    echo "run.sh sudah jalan."
    exit 0
fi
nohup /root/cekid1/run.sh >> /root/cekid1/cekid.log 2>&1 &
echo "✅ cekid1 jalan via nohup (log: /root/cekid1/cekid.log)"
