#!/usr/bin/env bash
# Build a prototype HamSpot SD-card image with official pi-gen.
# Requires Linux, git, Docker and sufficient disk space. Not a production release.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${ROOT}/image/work"
mkdir -p "$OUT"
if [ ! -d "$OUT/pi-gen/.git" ]; then
  git clone --depth 1 --branch arm64 https://github.com/RPi-Distro/pi-gen.git "$OUT/pi-gen"
fi
PI="$OUT/pi-gen"
STAGE="$PI/stage-hamspot"
mkdir -p "$STAGE/00-hamspot/files"
cp "$ROOT/image/pi-gen-stage/00-hamspot/00-packages" "$STAGE/00-hamspot/00-packages"
cp "$ROOT/image/pi-gen-stage/00-hamspot/00-run.sh" "$STAGE/00-hamspot/00-run.sh"
chmod +x "$STAGE/00-hamspot/00-run.sh"
for name in server.py index.html hdmi.html settings.html; do
  cp "$ROOT/app/$name" "$STAGE/00-hamspot/files/$name"
done
cp "$ROOT/config.example.json" "$STAGE/00-hamspot/files/config.example.json"
cp "$ROOT/image/hamspot.service" "$STAGE/00-hamspot/files/hamspot.service"
touch "$STAGE/EXPORT_IMAGE"
touch "$PI/stage2/SKIP_IMAGES"
touch "$PI/stage3/SKIP" "$PI/stage4/SKIP" "$PI/stage5/SKIP"
cat > "$PI/config" <<'EOF'
IMG_NAME='HamSpot-arm64-prototype'
RELEASE='trixie'
DEPLOY_COMPRESSION='xz'
STAGE_LIST='stage0 stage1 stage2 stage-hamspot'
TARGET_HOSTNAME='hamspot'
ENABLE_SSH=0
EOF
echo 'Building Raspberry Pi OS 64-bit prototype image; this can take substantial time.'
cd "$PI"
./build-docker.sh
echo "Check output in $PI/deploy/"
