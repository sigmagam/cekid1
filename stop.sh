#!/bin/bash
screen -S cekid1 -X quit 2>/dev/null
pkill -f '/root/cekid1/run.sh' 2>/dev/null
pkill -f '/root/cekid1/venv/bin/python3' 2>/dev/null
echo "✅ cekid1 dihentikan"
