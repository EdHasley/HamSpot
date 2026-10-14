#!/bin/sh
# Run as root on a spare Raspberry Pi OS test installation.
set -eu
test "$(id -u)" -eq 0 || { echo "Run as root"; exit 1; }
SRC="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
id hamspot >/dev/null 2>&1 || useradd --system --home /nonexistent --shell /usr/sbin/nologin hamspot
mkdir -p /opt/hamspot/app
install -m 0644 "$SRC/app/server.py" /opt/hamspot/app/server.py
install -m 0644 "$SRC/app/index.html" /opt/hamspot/app/index.html
install -m 0644 "$SRC/config.example.json" /opt/hamspot/config.example.json
install -m 0644 "$SRC/image/hamspot.service" /etc/systemd/system/hamspot.service
systemctl daemon-reload
systemctl enable hamspot.service
echo "Prototype installed. Start with: systemctl start hamspot"
