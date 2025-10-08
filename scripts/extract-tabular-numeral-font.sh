#!/bin/bash

# Script to extract tabular number glyphs (tnum) from an OTF font
# and create a new font with those glyphs mapped to standard digits

set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_font.otf> <output_font.otf>"
    echo "Example: $0 MyFont.otf MyFont-Tabular.otf"
    exit 1
fi

INPUT_FONT="$1"
OUTPUT_FONT="$2"

# Check if input font exists
if [ ! -f "$INPUT_FONT" ]; then
    echo "Error: Input font '$INPUT_FONT' not found"
    exit 1
fi

# Check if fonttools is installed
if ! python3 -c "import fontTools" 2>/dev/null; then
    echo "fonttools not found. Installing..."
    pip3 install fonttools --break-system-packages
fi

# Create Python script to do the extraction
PYTHON_SCRIPT=$(cat <<'PYSCRIPT'
import sys
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeatures
import os

def extract_tnum_glyphs(input_path, output_path):
    """Extract tnum glyphs and create new font with them mapped to digits"""
    
    print(f"Loading font: {input_path}")
    font = TTFont(input_path)
    
    # Find the tnum feature substitutions
    tnum_mapping = {}
    
    if 'GSUB' in font:
        gsub = font['GSUB']
        
        # Look for tnum feature
        for feature_record in gsub.table.FeatureList.FeatureRecord:
            if feature_record.FeatureTag == 'tnum':
                print("Found 'tnum' feature")
                feature = feature_record.Feature
                
                # Get lookup indices
                for lookup_index in feature.LookupListIndex:
                    lookup = gsub.table.LookupList.Lookup[lookup_index]
                    
                    # Process each subtable
                    for subtable in lookup.SubTable:
                        if hasattr(subtable, 'mapping'):
                            # Single substitution
                            for glyph_in, glyph_out in subtable.mapping.items():
                                tnum_mapping[glyph_in] = glyph_out
                                print(f"  Mapping: {glyph_in} -> {glyph_out}")
    
    if not tnum_mapping:
        print("Error: Could not find any tabular number glyphs")
        sys.exit(1)
    
    print(f"\nFound {len(tnum_mapping)} tabular substitutions")
    
    # Get the character map
    cmap = font.getBestCmap()
    
    # Create reverse mapping to find which Unicode points map to our source glyphs
    # Include digits (0-9), period (.), and degree symbol (°)
    target_chars = {}
    for code_point, glyph_name in cmap.items():
        char = chr(code_point)
        # Check if this is a digit (0-9)
        if 0x30 <= code_point <= 0x39:  # Unicode for '0' to '9'
            if glyph_name in tnum_mapping:
                target_chars[char] = tnum_mapping[glyph_name]
                print(f"Character '{char}' will use tabular glyph: {tnum_mapping[glyph_name]}")
        # Always include period and degree symbol (use tabular if available, otherwise regular)
        elif code_point == 0x2E:  # period '.'
            if glyph_name in tnum_mapping:
                target_chars[char] = tnum_mapping[glyph_name]
                print(f"Character '{char}' will use tabular glyph: {tnum_mapping[glyph_name]}")
            else:
                target_chars[char] = glyph_name
                print(f"Character '{char}' will use regular glyph: {glyph_name}")
        elif code_point == 0xB0:  # degree symbol '°'
            if glyph_name in tnum_mapping:
                target_chars[char] = tnum_mapping[glyph_name]
                print(f"Character '{char}' will use tabular glyph: {tnum_mapping[glyph_name]}")
            else:
                target_chars[char] = glyph_name
                print(f"Character '{char}' will use regular glyph: {glyph_name}")
    
    if not target_chars:
        print("Error: Could not map characters to tabular glyphs")
        sys.exit(1)
    
    # Now modify the cmap to point characters directly to tabular glyphs
    for table in font['cmap'].tables:
        for char, tnum_glyph in target_chars.items():
            code_point = ord(char)
            if code_point in table.cmap:
                old_glyph = table.cmap[code_point]
                table.cmap[code_point] = tnum_glyph
                print(f"Remapped U+{code_point:04X} ('{char}'): {old_glyph} -> {tnum_glyph}")
    
    # Remove GSUB table since we've baked in the substitutions
    if 'GSUB' in font:
        print("\nRemoving GSUB table (substitutions are now baked in)")
        del font['GSUB']
    
    # Save the modified font
    print(f"\nSaving modified font to: {output_path}")
    font.save(output_path)
    print("Done!")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_font.otf> <output_font.otf>")
        sys.exit(1)
    
    extract_tnum_glyphs(sys.argv[1], sys.argv[2])

PYSCRIPT
)

# Run the Python script
echo "$PYTHON_SCRIPT" | python3 - "$INPUT_FONT" "$OUTPUT_FONT"

echo ""
echo "Successfully created $OUTPUT_FONT with tabular numbers as default"