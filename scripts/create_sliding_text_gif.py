#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "Pillow>=10.0.0",
#   "requests>=2.25.0"
# ]
# ///

"""
Create animated GIF for binary ESPHome displays.
Generates sliding text animation suitable for monochrome displays.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import requests


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


def load_font(font_spec: str, font_size: int) -> ImageFont.ImageFont:
    """Load font with error handling."""
    try:
        font_path = parse_font_spec(font_spec)
        return ImageFont.truetype(font_path, font_size)
    except (OSError, ValueError) as e:
        print(f"Warning: Could not load font '{font_spec}': {e}, using default font")
        try:
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()


def get_text_bbox(text: str, font: ImageFont.ImageFont) -> tuple[int, int, int, int]:
    """Get bounding box for text with the given font."""
    temp_img = Image.new('1', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)
    return temp_draw.textbbox((0, 0), text, font=font)


def create_sliding_animation(
    text: str,
    font_spec: str,
    font_size: int,
    width: int,
    height: int,
    slide_in_frames: int,
    pause_frames: int,
    slide_out_frames: int,
    frame_duration: int,
    output_file: str,
    vertical_offset: int = 0
) -> None:
    """Create sliding text animation for binary display."""
    
    font = load_font(font_spec, font_size)
    
    # Get text dimensions
    bbox = get_text_bbox(text, font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate positions
    text_x = (width - text_width) // 2
    center_y = (height - text_height) // 2 + vertical_offset
    
    # Starting position (completely off-screen above)
    start_y = -text_height
    # Ending position (completely off-screen below)
    end_y = height
    
    frames = []
    total_frames = slide_in_frames + pause_frames + slide_out_frames
    
    print(f"Creating animation with {total_frames} frames:")
    print(f"  Text: '{text}'")
    print(f"  Font: {font_spec} at {font_size}pt")
    print(f"  Display: {width}x{height}")
    print(f"  Text size: {text_width}x{text_height}")
    print(f"  Timing: {slide_in_frames} slide-in + {pause_frames} pause + {slide_out_frames} slide-out")
    
    frame_num = 0
    
    # Slide-in frames
    for i in range(slide_in_frames):
        img = Image.new('1', (width, height), color=0)  # Black background
        draw = ImageDraw.Draw(img)
        
        # Interpolate Y position from start to center
        progress = i / (slide_in_frames - 1) if slide_in_frames > 1 else 1
        y_pos = int(start_y + (center_y - start_y) * progress)
        
        draw.text((text_x, y_pos), text, font=font, fill=1)  # White text
        frames.append(img)
        frame_num += 1
    
    # Pause frames
    for i in range(pause_frames):
        img = Image.new('1', (width, height), color=0)  # Black background
        draw = ImageDraw.Draw(img)
        draw.text((text_x, center_y), text, font=font, fill=1)  # White text
        frames.append(img)
        frame_num += 1
    
    # Slide-out frames  
    for i in range(slide_out_frames):
        img = Image.new('1', (width, height), color=0)  # Black background
        draw = ImageDraw.Draw(img)
        
        # Interpolate Y position from center to end
        progress = i / (slide_out_frames - 1) if slide_out_frames > 1 else 1
        y_pos = int(center_y + (end_y - center_y) * progress)
        
        draw.text((text_x, y_pos), text, font=font, fill=1)  # White text
        frames.append(img)
        frame_num += 1
    
    # Save animated GIF
    frames[0].save(
        output_file,
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration,
        loop=0,  # Infinite loop
        optimize=True
    )
    
    print(f"Saved '{output_file}' with {len(frames)} frames")
    print(f"Frame duration: {frame_duration}ms per frame")


def main():
    parser = argparse.ArgumentParser(
        description="Create sliding text animation GIF for binary ESPHome displays"
    )
    
    parser.add_argument("text", help="Text to animate")
    parser.add_argument("--font", required=True, help="Font specification: local file path or Google Fonts (gfonts://FontName[@weight][@italic])")
    parser.add_argument("--size", type=int, required=True, help="Font size in points")
    parser.add_argument("--width", type=int, default=128, help="Display width in pixels (default: 128)")
    parser.add_argument("--height", type=int, default=64, help="Display height in pixels (default: 64)")
    parser.add_argument("--slide-in", type=int, default=8, help="Number of slide-in frames (default: 8)")
    parser.add_argument("--pause", type=int, default=12, help="Number of pause frames (default: 12)")
    parser.add_argument("--slide-out", type=int, default=8, help="Number of slide-out frames (default: 8)")
    parser.add_argument("--duration", type=int, default=100, help="Frame duration in ms (default: 100)")
    parser.add_argument("--output", default="sliding_text.gif", help="Output filename (default: sliding_text.gif)")
    parser.add_argument("--vertical-offset", type=int, default=0, help="Vertical offset for center position in pixels (negative = up, positive = down)")
    
    args = parser.parse_args()
    
    try:
        create_sliding_animation(
            args.text,
            args.font,
            args.size,
            args.width,
            args.height,
            args.slide_in,
            args.pause,
            args.slide_out,
            args.duration,
            args.output,
            args.vertical_offset
        )
        print("Animation created successfully!")
    except Exception as e:
        print(f"Error creating animation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
