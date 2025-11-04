#!/usr/bin/env bash
# Regenerate the action-bar fan animation frames by rotating the base glyph.

set -euo pipefail

OUTPUT_DIR="${1:-assets/spinning-fan-animation}"
SVG_SOURCE="${2:-${OUTPUT_DIR}/fan.svg}"
TARGET_SIZE="${3:-58}"
FRAME_COUNT="${4:-30}"
ANGLE_STEP="${5:-12}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CAIROSVG_BIN=""
if command -v cairosvg >/dev/null 2>&1; then
  CAIROSVG_BIN="$(command -v cairosvg)"
elif [[ -x "${SCRIPT_DIR}/../.venv/bin/cairosvg" ]]; then
  CAIROSVG_BIN="${SCRIPT_DIR}/../.venv/bin/cairosvg"
fi
if [[ -z "${CAIROSVG_BIN}" ]]; then
  echo "Error: 'cairosvg' is required to rasterize ${SVG_SOURCE}. Install it (pip install cairosvg) or adjust the script to use a PNG base." >&2
  exit 1
fi
if ! command -v convert >/dev/null 2>&1; then
  echo "Error: ImageMagick 'convert' binary is required." >&2
  exit 1
fi

if [[ ! -f "${SVG_SOURCE}" ]]; then
  echo "Error: Source SVG '${SVG_SOURCE}' not found." >&2
  exit 1
fi

mkdir -p "${OUTPUT_DIR}"
rm -f "${OUTPUT_DIR}"/fan-*.png

BASE_FRAME="${OUTPUT_DIR}/fan-0.png"
printf 'Rendering base frame %s at %sx%s\n' "${BASE_FRAME}" "${TARGET_SIZE}" "${TARGET_SIZE}"
"${CAIROSVG_BIN}" \
  "${SVG_SOURCE}" \
  -f png \
  -W "${TARGET_SIZE}" \
  -H "${TARGET_SIZE}" \
  -o "${BASE_FRAME}" \
  --background=transparent

for index in $(seq 1 "${FRAME_COUNT}"); do
  angle=$((index * ANGLE_STEP))
  printf 'Generating %s/fan-%d.png\n' "${OUTPUT_DIR}" "${angle}"
  convert "${BASE_FRAME}" \
    -background none \
    -distort SRT "${angle}" \
    "${OUTPUT_DIR}/fan-${angle}.png"
done

if command -v optipng >/dev/null 2>&1; then
  printf 'Optimizing generated frames with optipng\n'
  optipng -quiet "${OUTPUT_DIR}"/fan-*.png
else
  printf 'optipng not found; skipping PNG optimization\n'
fi
