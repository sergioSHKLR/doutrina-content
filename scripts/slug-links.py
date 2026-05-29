import re
import unicodedata

def clean_slug(text):
    """Generates a clean markdown anchor from heading text."""
    text = text.replace('🆕', '').replace('🔖', '').replace('📑', '')
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text).strip('-')
    return text

def process_markdown_index(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex constraints:
    # 1. Lookbehind (?<=\s) ensures there is a space directly to the left.
    # 2. Group 1 parses digits, Group 2 parses optional lowercase suffix letter.
    # 3. Lookahead (?=\s|,|$) ensures a space, a comma, or the end of the line is directly to the right.
    num_pattern = re.compile(r'(?<=\s)\b([0-9]+)([a-z])?\b(?=\s|,|$)')

    def replace_numbers_in_text(text):
        def match_handler(match):
            num_str = match.group(1)
            letter_str = match.group(2) or ""
            val = int(num_str)
            
            # Strict validation range check
            if 1 <= val <= 1019:
                if letter_str:
                    return f"[Q.{num_str}.{letter_str}](#q{num_str}{letter_str})"
                return f"[Q.{num_str}](#q{num_str})"
            return match.group(0)

        return num_pattern.sub(match_handler, text)

    updated_lines = []
    lines = content.splitlines()

    for line in lines:
        # Match EXACTLY h6 (######) tags with an optional trailing {#anchor} block
        heading_match = re.match(r'^(######)\s+(.*?)(?:\s*\{#.*?\})?$', line)
        
        if heading_match:
            hashes = heading_match.group(1)
            heading_text = heading_match.group(2).strip()
            
            # Recompute and replace anchor cleanly
            slug = clean_slug(heading_text)
            updated_lines.append(f"{hashes} {heading_text} {{#{slug}}}")
            
        else:
            # Process text lines. Pad line with a temporary leading space 
            # to capture standalone numbers positioned at the very start of a line.
            padded_line = " " + line
            processed_padded = replace_numbers_in_text(padded_line)
            # Remove the padding space before saving
            updated_line = processed_padded[1:]
            updated_lines.append(updated_line)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(updated_lines))

# Execution Path Configuration
input_path = "books/md/1-lde/partial/06.md"
output_path = "books/md/1-lde/partial/06-slugged-linked.md"

process_markdown_index(input_path, output_path)
print("Index updated successfully with strict spacing rules!")
