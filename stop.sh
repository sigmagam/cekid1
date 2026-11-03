#!/bin/bash
# Hentikan supervisor (run.sh) + bot-nya.
screen -S cekid1 -X quit 2>/dev/null

# Proses yang memegang lock = supervisor + anak-anaknya.
pids=$(fuser /root/cekid1/.cekid.lock 2>/dev/null)
if [ -n "$pids" ]; then
    kill -9 $pids 2>/dev/null
fi

pkill -f '/root/cekid1/run.sh' 2>/dev/null
pkill -f '/root/cekid1/venv/bin/python3 main.py' 2>/dev/null
sleep 1
echo "✅ cekid1 dihentikan"
