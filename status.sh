#!/bin/bash
echo "— systemd —"
main=$(systemctl show -p MainPID --value cekid1 2>/dev/null)
if systemctl is-active --quiet cekid1 2>/dev/null; then
    echo "cekid1.service aktif (MainPID ${main:-?})"
    systemctl is-enabled cekid1 2>/dev/null | sed 's/^/enabled: /'
else
    echo "cekid1.service tidak aktif"
fi
echo "— proses —"
if [ -n "$main" ] && [ "$main" != "0" ]; then
    echo "$main $(tr '\0' ' ' < /proc/$main/cmdline 2>/dev/null)"
else
    echo "tidak ada proses cekid1"
fi
echo "— log —"
tail -n 12 /root/cekid1/cekid.log 2>/dev/null || echo "(belum ada log)"
