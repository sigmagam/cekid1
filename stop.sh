#!/bin/bash
# Hentikan bot (systemd kalau ada, kalau tidak kill manual).
if systemctl list-unit-files 2>/dev/null | grep -q "^cekid1.service"; then
    systemctl stop cekid1
    echo "✅ cekid1 (systemd) dihentikan"
    exit 0
fi

screen -S cekid1 -X quit 2>/dev/null
for lock in /root/cekid1/.bot.lock /root/cekid1/.cekid.lock; do
    pids=$(fuser $lock 2>/dev/null)
    [ -n "$pids" ] && kill -9 $pids 2>/dev/null
done
pkill -f '/root/cekid1/run.sh' 2>/dev/null
pkill -f '/root/cekid1/venv/bin/python3 main.py' 2>/dev/null
sleep 1
echo "✅ cekid1 dihentikan"
