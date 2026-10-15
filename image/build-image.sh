#!/usr/bin/env bash
# Build a dmr-test HamSpot SD-card image with official pi-gen.
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
bash "$ROOT/image/prepare-stage.sh" "$STAGE"
touch "$STAGE/EXPORT_IMAGE"
touch "$PI/stage2/SKIP_IMAGES"
touch "$PI/stage3/SKIP" "$PI/stage4/SKIP" "$PI/stage5/SKIP"
cat > "$PI/config" <<'EOF'
IMG_NAME='HamSpot-arm64-dmr-test'
RELEASE='trixie'
DEPLOY_COMPRESSION='xz'
STAGE_LIST='stage0 stage1 stage2 stage-hamspot'
TARGET_HOSTNAME='hamspot'
ENABLE_SSH=0
EOF
echo 'Building Raspberry Pi OS 64-bit dmr-test image; this can take substantial time.'
cd "$PI"
./build-docker.sh
echo "Check output in $PI/deploy/"
