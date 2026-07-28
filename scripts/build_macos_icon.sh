#!/bin/zsh

set -euo pipefail

SCRIPT_DIRECTORY="${0:A:h}"
PROJECT_DIRECTORY="${SCRIPT_DIRECTORY:h}"
SOURCE_SVG="${PROJECT_DIRECTORY}/assets/app-icon.svg"
OUTPUT_ICNS="${PROJECT_DIRECTORY}/assets/app-icon.icns"
TEMPORARY_DIRECTORY="$(mktemp -d)"
ICONSET_DIRECTORY="${TEMPORARY_DIRECTORY}/app-icon.iconset"

cleanup() {
    rm -rf "${TEMPORARY_DIRECTORY}"
}
trap cleanup EXIT

mkdir -p "${ICONSET_DIRECTORY}"

# Render one lossless 1024-pixel master using macOS Quick Look.
qlmanage \
    -t \
    -s 1024 \
    -o "${TEMPORARY_DIRECTORY}" \
    "${SOURCE_SVG}" \
    >/dev/null

MASTER_PNG="${TEMPORARY_DIRECTORY}/app-icon.svg.png"

# Generate every size required by the macOS iconset format.
sips -z 16 16 "${MASTER_PNG}" \
    --out "${ICONSET_DIRECTORY}/icon_16x16.png" >/dev/null
sips -z 32 32 "${MASTER_PNG}" \
    --out "${ICONSET_DIRECTORY}/icon_16x16@2x.png" >/dev/null
sips -z 32 32 "${MASTER_PNG}" \
    --out "${ICONSET_DIRECTORY}/icon_32x32.png" >/dev/null
sips -z 64 64 "${MASTER_PNG}" \
    --out "${ICONSET_DIRECTORY}/icon_32x32@2x.png" >/dev/null
sips -z 128 128 "${MASTER_PNG}" \
    --out "${ICONSET_DIRECTORY}/icon_128x128.png" >/dev/null
sips -z 256 256 "${MASTER_PNG}" \
    --out "${ICONSET_DIRECTORY}/icon_128x128@2x.png" >/dev/null
sips -z 256 256 "${MASTER_PNG}" \
    --out "${ICONSET_DIRECTORY}/icon_256x256.png" >/dev/null
sips -z 512 512 "${MASTER_PNG}" \
    --out "${ICONSET_DIRECTORY}/icon_256x256@2x.png" >/dev/null
sips -z 512 512 "${MASTER_PNG}" \
    --out "${ICONSET_DIRECTORY}/icon_512x512.png" >/dev/null
cp "${MASTER_PNG}" "${ICONSET_DIRECTORY}/icon_512x512@2x.png"

# Compile the iconset into the single file consumed by PyInstaller.
iconutil \
    -c icns \
    "${ICONSET_DIRECTORY}" \
    -o "${OUTPUT_ICNS}"

echo "Created ${OUTPUT_ICNS}"
