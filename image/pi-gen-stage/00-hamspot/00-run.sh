#!/bin/bash -e
install -d "${ROOTFS_DIR}/opt/hamspot/app" "${ROOTFS_DIR}/opt/hamspot/radio" "${ROOTFS_DIR}/etc/hamspot" "${ROOTFS_DIR}/etc/systemd/system"
cp -a "${STAGE_DIR}/00-hamspot/files/app/." "${ROOTFS_DIR}/opt/hamspot/app/"
cp -a "${STAGE_DIR}/00-hamspot/files/radio/." "${ROOTFS_DIR}/opt/hamspot/radio/"
cp "${STAGE_DIR}"/00-hamspot/files/*.service "${ROOTFS_DIR}/etc/systemd/system/"
# Build from pinned upstream revisions; keep sources/license notices in the image.
on_chroot <<'CHROOT'
set -eu
id hamspot >/dev/null 2>&1 || useradd --system --home /nonexistent --shell /usr/sbin/nologin hamspot
usermod -a -G dialout,systemd-journal hamspot
install -d /usr/local/src/hamspot /usr/share/hamspot
python3 - <<'PY'
import json,subprocess
from pathlib import Path
sources=json.loads(Path('/opt/hamspot/radio/sources.json').read_text())
for name,source in sources.items():
    directory='/usr/local/src/hamspot/'+name
    subprocess.run(['git','clone',source['url'],directory],check=True)
    subprocess.run(['git','-C',directory,'checkout','--detach',source['commit']],check=True)
    subprocess.run(['make','-j2'],cwd=directory,check=True)
    subprocess.run(['install','-m','755',directory+'/'+name,'/usr/local/bin/'+name],check=True)
PY
# Optional lookup databases do not block RF use. Empty files suppress missing-file errors.
touch /usr/share/hamspot/DMRIds.dat /usr/share/hamspot/NXDN.csv
PYTHONPATH=/opt/hamspot/app python3 - <<'PY'
import json
from pathlib import Path
from radio import render
state=Path('/etc/hamspot')
c=json.loads(Path('/opt/hamspot/radio/defaults.json').read_text())
(state/'config.json').write_text(json.dumps(c,indent=2)+'\n')
for name,data in render(c).items(): (state/name).write_text(data)
PY
chown -R root:hamspot /etc/hamspot
chmod 750 /etc/hamspot
chmod 640 /etc/hamspot/*
printf '%s\n' 'hamspot ALL=(root) NOPASSWD: /usr/bin/python3 -I /opt/hamspot/app/control-entry.py' > /etc/sudoers.d/hamspot
chmod 440 /etc/sudoers.d/hamspot
visudo -cf /etc/sudoers.d/hamspot
# First boot credential file is available on the FAT boot partition and at local console.
printf '\nHamSpot: https://hamspot.local:8443\nLogin: /boot/firmware/HAMSPOT-LOGIN.txt\n' >> /etc/issue
systemctl enable hamspot-firstboot hamspot hamspot-radio hamspot-gateway mosquitto avahi-daemon
CHROOT
# Pi 5 GPIO UART is distinct from the debug UART exposed as serial0.
cat >> "${ROOTFS_DIR}/boot/firmware/config.txt" <<'CONFIG'

# HamSpot GPIO modem UART
[pi5]
dtoverlay=uart0-pi5
[pi4]
enable_uart=1
dtoverlay=disable-bt
[all]
CONFIG
# Do not run a serial login on the modem pins.
sed -i -E 's/console=(serial0|ttyAMA0),[0-9]+ ?//g' "${ROOTFS_DIR}/boot/firmware/cmdline.txt"
