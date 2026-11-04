#!/bin/bash
# Jalankan bot. Prioritas: systemd unit -> screen -> nohup.
cd /root/cekid1 || exit 1

if systemctl list-unit-files 2>/dev/null | grep -q "^cekid1.service"; then
    systemctl start cekid1
    systemctl --no-pager -l status cekid1 | head -6
    exit 0
fi

if screen -ls 2>/dev/null | grep -q "\.cekid1"; then
    echo "Screen cekid1 sudah jalan."
    exit 0
fi
if fuser /root/cekid1/.bot.lock >/dev/null 2>&1; then
    echo "Bot cekid1 sudah jalan."
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

nohup /root/cekid1/run.sh >> /root/cekid1/cekid.log 2>&1 &
echo "✅ cekid1 jalan via nohup (log: /root/cekid1/cekid.log)"
