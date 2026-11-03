#!/bin/bash
# Supervisor ringan: restart cuma kalau proses python keluar (crash/exit).
cd /root/cekid1 || exit 1
ulimit -n 65536

LOG=/root/cekid1/cekid.log
PY=/root/cekid1/venv/bin/python3

# Kunci: cuma boleh ada 1 supervisor (cegah 2 bot rebutan session -> "database is locked").
exec 9>/root/cekid1/.cekid.lock
if ! flock -n 9; then
    echo "[$(date '+%F %T')] run.sh sudah jalan, keluar." | tee -a "$LOG"
    exit 0
fi

while true; do
    find /root/cekid1/cekid -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
    echo "[$(date '+%F %T')] cekid starting..." | tee -a "$LOG"
    "$PY" main.py 2>&1 | tee -a "$LOG"
    code=${PIPESTATUS[0]}
    echo "[$(date '+%F %T')] cekid exit code=$code, restart in 5s..." | tee -a "$LOG"
    if [ -f "$LOG" ] && [ "$(stat -c%s "$LOG")" -gt 5242880 ]; then
        tail -n 1000 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
    fi
    sleep 5
done
