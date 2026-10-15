#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAGE="${1:?Usage: prepare-stage.sh stage-path}"
mkdir -p "$STAGE/00-hamspot/files/app" "$STAGE/00-hamspot/files/radio"
cp "$ROOT/image/pi-gen-stage/00-hamspot/00-packages" "$STAGE/00-hamspot/00-packages"
install -m 755 "$ROOT/image/pi-gen-stage/00-hamspot/00-run.sh" "$STAGE/00-hamspot/00-run.sh"
cp "$ROOT"/app/*.py "$ROOT"/app/*.html "$ROOT"/app/*.css "$ROOT"/app/*.js "$STAGE/00-hamspot/files/app/"
cp "$ROOT"/radio/* "$STAGE/00-hamspot/files/radio/"
cp "$ROOT"/image/hamspot*.service "$STAGE/00-hamspot/files/"
cat > "$STAGE/prerun.sh" <<'PRERUN'
#!/bin/bash -e
if [ ! -d "${ROOTFS_DIR}" ]; then
  copy_previous
fi
PRERUN
chmod +x "$STAGE/prerun.sh"
