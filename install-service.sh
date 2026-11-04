#!/bin/bash
# Pasang auto-restart: systemd kalau ada, kalau tidak pakai cron @reboot.
cd /root/cekid1 || exit 1
NAME=cekid1

if systemctl is-system-running >/dev/null 2>&1 || systemctl --version >/dev/null 2>&1; then
    if [ -d /run/systemd/system ] && systemctl daemon-reload >/dev/null 2>&1; then
        cp deploy/$NAME.service /etc/systemd/system/$NAME.service
        systemctl daemon-reload
        systemctl enable --now $NAME
        echo "✅ systemd: $NAME aktif (auto-restart + hidup lagi setelah reboot)"
        systemctl --no-pager -l status $NAME | head -12
        exit 0
    fi
fi

# Fallback: cron @reboot + supervisor run.sh (auto-restart kalau crash).
if command -v crontab >/dev/null 2>&1; then
    ( crontab -l 2>/dev/null | grep -v '/root/cekid1/start.sh'
      echo "@reboot /root/cekid1/start.sh >> /root/cekid1/cekid.log 2>&1" ) | crontab -
    echo "✅ cron @reboot dipasang (bot hidup lagi setelah reboot)"
fi
/root/cekid1/start.sh
