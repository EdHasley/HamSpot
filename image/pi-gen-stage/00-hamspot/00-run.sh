#!/bin/bash -e
# pi-gen host-side stage; the build runner must execute this script.
install -d "${ROOTFS_DIR}/opt/hamspot/app" "${ROOTFS_DIR}/etc/systemd/system"
install -m 0644 "${STAGE_DIR}/files/server.py" "${ROOTFS_DIR}/opt/hamspot/app/server.py"
install -m 0644 "${STAGE_DIR}/files/index.html" "${ROOTFS_DIR}/opt/hamspot/app/index.html"
install -m 0644 "${STAGE_DIR}/files/hdmi.html" "${ROOTFS_DIR}/opt/hamspot/app/hdmi.html"
install -m 0644 "${STAGE_DIR}/files/settings.html" "${ROOTFS_DIR}/opt/hamspot/app/settings.html"
install -m 0644 "${STAGE_DIR}/files/config.example.json" "${ROOTFS_DIR}/opt/hamspot/config.example.json"
install -m 0644 "${STAGE_DIR}/files/hamspot.service" "${ROOTFS_DIR}/etc/systemd/system/hamspot.service"
on_chroot <<'EOF'
id hamspot >/dev/null 2>&1 || useradd --system --home /nonexistent --shell /usr/sbin/nologin hamspot
systemctl enable hamspot.service
EOF
