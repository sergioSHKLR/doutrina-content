#!/usr/bin/env python3
"""
Roman numerals → "Cap. NN" (leading zero for 1-9)
"""

import re
from pathlib import Path
import sys

roman_to_arabic = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9,
    'X': 10, 'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15, 'XVI': 16,
    'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20, 'XXI': 21, 'XXII': 22,
    'XXIII': 23, 'XXIV': 24, 'XXV': 25, 'XXVI': 26, 'XXVII': 27, 'XXVIII': 28,
    'XXIX': 29, 'XXX': 30, 'XXXI': 31, 'XXXII': 32, 'XXXIII': 33, 'XXXIV': 34,
    'XXXV': 35, 'XXXVI': 36
}

def roman_to_cap(text):
    def replace(match):
        roman = match.group(1).upper()
        num = roman_to_arabic.get(roman)
        if num is not None:
            # Add leading zero for numbers 1-9
            formatted = f"{num:02d}" if num < 10 else str(num)
            return f"Cap. {formatted}"
        return match.group(0)

    # Match standalone Roman numerals
    pattern = r'\b([IVXLCDM]+)\b'
    return re.sub(pattern, replace, text, flags=re.IGNORECASE3


def process_file(input_path, output_path=None):
    content = Path(input_path).read_text(encoding="utf-8")
    new_content = roman_to_cap(content)

    if output_path:
        Path(output_path).write_text(new_content, encoding="utf-8")
        print(f"✅ Converted Roman numerals → Cap. NN (with leading zero for 1-9)")
        print(f"   Saved to: {output_path}")
    else:
        print(new_content[:1000])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python roman_to_cap.py <input.md> [output.md]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file

    process_file(input_file, output_file)