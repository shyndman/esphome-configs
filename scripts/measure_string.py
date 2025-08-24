#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "freetype-py>=2.5.1",
#   "requests>=2.32.5",
# ]
# ///
"""
Font string measurement utility.

Measures the pixel dimensions of a string when rendered with a specific font,
using the same algorithms as ESPHome's font rendering system.
"""

import argparse
import os
import re
import sys
from pathlib import Path

import requests
from freetype import FT_LOAD_RENDER, Face

__version__ = "0.1.0"


def pt_to_px(pt):
    """Convert a point size to pixels, rounding up to the nearest pixel."""
    return (pt + 63) // 64


def download_google_font(
    family: str, weight: str = "regular", italic: bool = False
) -> str:
    """
    Download a Google Font and return the path to the cached file.

    Replicates ESPHome's download_gfont logic from:
    esphome/components/font/__init__.py:310-346
    """
    # Map weight names to numbers
    font_weights = {
        "thin": 100,
        "extra-light": 200,
        "light": 300,
        "regular": 400,
        "medium": 500,
        "semi-bold": 600,
        "bold": 700,
        "extra-bold": 800,
        "black": 900,
    }

    # Convert weight name to number if necessary
    if isinstance(weight, str) and weight in font_weights:
        weight = font_weights[weight]

    # Create Google Fonts API URL
    name = f"{family}:ital,wght@{int(italic)},{weight}"
    url = f"https://fonts.googleapis.com/css2?family={name}"

    # Create cache directory
    cache_dir = Path.home() / ".cache" / "esp_measure_string"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Generate cache file name
    cache_file = cache_dir / f"{family}@{weight}@{italic}@v1.ttf"

    # Return cached file if it exists
    if cache_file.exists():
        return str(cache_file)

    print(
        f"Downloading Google Font: {family} (weight: {weight}, italic: {italic})",
        file=sys.stderr,
    )

    try:
        # Get the CSS file
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Extract the TTF URL from the CSS
        match = re.search(r"src:\s+url\((.+)\)\s+format\('truetype'\);", response.text)
        if not match:
            raise ValueError(
                f"Could not extract TTF file from Google Fonts response for {name}"
            )

        ttf_url = match.group(1)

        # Download the TTF file
        ttf_response = requests.get(ttf_url, timeout=30)
        ttf_response.raise_for_status()

        # Save to cache
        with open(cache_file, "wb") as f:
            f.write(ttf_response.content)

        return str(cache_file)

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Could not download Google Font {family}: {e}")


def parse_font_spec(font_spec: str) -> str:
    """
    Parse font specification and return path to font file.

    Supports:
    - Local file paths: "/path/to/font.ttf"
    - Google Fonts shorthand: "gfonts://Roboto" or "gfonts://Roboto@bold"
    - Google Fonts with italic: "gfonts://Roboto@400@true"
    """
    if font_spec.startswith("gfonts://"):
        # Parse Google Fonts shorthand
        match = re.match(r"^gfonts://([^@]+)(@([^@]+))?(@(true|false))?$", font_spec)
        if not match:
            raise ValueError(
                "Invalid Google Fonts syntax. Use: gfonts://FontName[@weight][@italic]"
            )

        family = match.group(1)
        weight = match.group(3) or "regular"
        italic = match.group(5) == "true" if match.group(5) else False

        return download_google_font(family, weight, italic)

    # Assume it's a local file path
    if not os.path.exists(font_spec):
        raise ValueError(f"Font file not found: {font_spec}")

    return font_spec


def measure_string(font_path: str, size: int, text: str):
    """
    Measure the pixel dimensions of a string using the specified font.

    Replicates ESPHome's Font::measure() logic from:
    esphome/components/font/font.cpp:78-109

    Returns:
        dict: Contains width, height, baseline, and x_offset measurements
    """
    try:
        # Load the font face
        face = Face(font_path)

        # Set pixel size (ESPHome uses set_pixel_sizes)
        face.set_pixel_sizes(size, 0)

        # Initialize measurement variables
        baseline = pt_to_px(face.size.ascender)
        height = pt_to_px(face.size.height)

        # Handle cases where metrics aren't available (like bitmap fonts)
        if baseline == 0:
            if not face.is_scalable:
                baseline = size
            else:
                print(
                    f"Warning: Unable to determine baseline of font {font_path}",
                    file=sys.stderr,
                )

        if height == 0:
            if not face.is_scalable:
                height = size
            else:
                print(
                    f"Warning: Unable to determine height of font {font_path}",
                    file=sys.stderr,
                )

        # Process each character in the string
        x = 0
        min_x = 0
        has_char = False

        # Convert string to bytes for proper UTF-8 handling
        text_bytes = text.encode("utf-8")
        i = 0

        while i < len(text_bytes):
            # Handle UTF-8 character decoding
            try:
                char = text_bytes[i:].decode("utf-8")[0]
                char_bytes = char.encode("utf-8")
                i += len(char_bytes)
            except UnicodeDecodeError:
                # Skip invalid characters
                i += 1
                continue

            try:
                # Load the glyph for this character
                face.load_char(char, FT_LOAD_RENDER)
                glyph = face.glyph

                if not has_char:
                    min_x = glyph.bitmap_left
                else:
                    min_x = min(min_x, x + glyph.bitmap_left)

                # Add the advance width
                x += pt_to_px(glyph.metrics.horiAdvance)
                has_char = True

            except Exception:
                # Character not found in font, use default advance
                # ESPHome uses the first glyph's advance as fallback
                if has_char:
                    # Just continue without this character
                    continue

        # Calculate final measurements
        x_offset = min_x
        width = x - min_x if has_char else 0

        return {
            "width": width,
            "height": height,
            "baseline": baseline,
            "x_offset": x_offset,
        }

    except Exception as e:
        print(f"Error measuring string: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Measure pixel dimensions of a string using a specified font"
    )
    parser.add_argument(
        "--font",
        required=True,
        help="Font specification: local file path, or Google Fonts (gfonts://FontName[@weight][@italic])",
    )
    parser.add_argument("--size", type=int, required=True, help="Font size in pixels")
    parser.add_argument("string", help="String to measure")

    args = parser.parse_args()

    # Parse font specification and get font path
    try:
        font_path = parse_font_spec(args.font)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Measure the string
    measurements = measure_string(font_path, args.size, args.string)

    # Output the results
    print(f'String: "{args.string}"')
    print(f"Width: {measurements['width']}px")
    print(f"Height: {measurements['height']}px")
    print(f"Baseline: {measurements['baseline']}px")
    print(f"X-offset: {measurements['x_offset']}px")


if __name__ == "__main__":
    main()