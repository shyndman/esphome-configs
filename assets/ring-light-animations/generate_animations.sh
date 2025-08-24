#!/bin/bash
# Generate sliding text animations for office ring light display
# Usage: ./generate_animations.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="../../scripts/create_sliding_text_gif.py"

# Display dimensions for the SSD1306 72x40 display
WIDTH=72
HEIGHT=40

# Font settings to match current config
FONT_LARGE="gfonts://Lexend Zetta@400"
FONT_MEDIUM="gfonts://Lexend Zetta@400"

# Animation timing (18fps with single pause frame)
SLIDE_IN=9
PAUSE=1  
SLIDE_OUT=9
DURATION=56  # ~56ms per frame = 18fps

# Position adjustment - raise text up a bit from center
VERTICAL_OFFSET=-4  # Negative moves text up

echo "Generating animations for office ring light display..."
echo "Display: ${WIDTH}x${HEIGHT}"
echo "Timing: ${SLIDE_IN} slide-in + ${PAUSE} pause + ${SLIDE_OUT} slide-out frames (total: $((SLIDE_IN + PAUSE + SLIDE_OUT)))"
echo "Frame duration: ${DURATION}ms"
echo "Vertical offset: ${VERTICAL_OFFSET}px"
echo

cd "$SCRIPT_DIR"

# Power state animations (medium font, similar to current config)
echo "Creating power state animations..."
uv run "$PYTHON_SCRIPT" "ON" \
  --font "$FONT_MEDIUM" --size 26 \
  --width "$WIDTH" --height "$HEIGHT" \
  --slide-in "$SLIDE_IN" --pause "$PAUSE" --slide-out "$SLIDE_OUT" \
  --duration "$DURATION" --vertical-offset "$VERTICAL_OFFSET" \
  --output "on.gif"

uv run "$PYTHON_SCRIPT" "OFF" \
  --font "$FONT_MEDIUM" --size 26 \
  --width "$WIDTH" --height "$HEIGHT" \
  --slide-in "$SLIDE_IN" --pause "$PAUSE" --slide-out "$SLIDE_OUT" \
  --duration "$DURATION" --vertical-offset "$VERTICAL_OFFSET" \
  --output "off.gif"

# Brightness level animations (large font for numbers)
echo "Creating brightness level animations..."
for i in {1..10}; do
  uv run "$PYTHON_SCRIPT" "$i" \
    --font "$FONT_LARGE" --size 32 \
    --width "$WIDTH" --height "$HEIGHT" \
    --slide-in "$SLIDE_IN" --pause "$PAUSE" --slide-out "$SLIDE_OUT" \
    --duration "$DURATION" --vertical-offset "$VERTICAL_OFFSET" \
    --output "${i}.gif"
done

# Color mode animations (large font for single characters)
echo "Creating color mode animations..."
uv run "$PYTHON_SCRIPT" "W" \
  --font "$FONT_LARGE" --size 32 \
  --width "$WIDTH" --height "$HEIGHT" \
  --slide-in "$SLIDE_IN" --pause "$PAUSE" --slide-out "$SLIDE_OUT" \
  --duration "$DURATION" --vertical-offset "$VERTICAL_OFFSET" \
  --output "w.gif"

uv run "$PYTHON_SCRIPT" "W+Y" \
  --font "$FONT_LARGE" --size 23 \
  --width "$WIDTH" --height "$HEIGHT" \
  --slide-in "$SLIDE_IN" --pause "$PAUSE" --slide-out "$SLIDE_OUT" \
  --duration "$DURATION" --vertical-offset "$VERTICAL_OFFSET" \
  --output "a.gif"

uv run "$PYTHON_SCRIPT" "Y" \
  --font "$FONT_LARGE" --size 32 \
  --width "$WIDTH" --height "$HEIGHT" \
  --slide-in "$SLIDE_IN" --pause "$PAUSE" --slide-out "$SLIDE_OUT" \
  --duration "$DURATION" --vertical-offset "$VERTICAL_OFFSET" \
  --output "y.gif"

echo
echo "Animation generation complete!"
echo "Generated files:"
ls -la *.gif | awk '{print "  " $9 " (" $5 " bytes)"}'

echo
echo "Total size:"
du -sh *.gif | tail -1