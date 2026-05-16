#!/bin/bash

# Finds the directory where this script lives (~/doutrina-content/scripts) 
# and goes up one level to the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

INPUT_DIR="$PROJECT_ROOT/books/md/1-lde/parts"
OUTPUT_DIR="$PROJECT_ROOT/books/md/1-lde/full"
OUTPUT="$OUTPUT_DIR/lde-full.md"

echo "🔄 Concatenating split parts into $OUTPUT ..."

# Find and sort files numerically (0 to 6) inside the root parts directory
files=($(ls -v "$INPUT_DIR"/lde-*.md 2>/dev/null | grep -E 'lde-[0-6]\.md'))

if [ ${#files[@]} -eq 0 ]; then
    echo "❌ No split files found matching lde-[0-6].md in $INPUT_DIR"
    echo "Current directory contents of $INPUT_DIR:"
    ls -la "$INPUT_DIR" 2>/dev/null || echo "Directory does not exist or permission denied."
    exit 1
fi

echo "✅ Found ${#files[@]} parts."

# Clear/create output file
> "$OUTPUT"

for file in "${files[@]}"; do
    # Extract just the filename for a cleaner echo log
    filename=$(basename "$file")
    echo "📄 Adding: $filename"
    
    cat "$file" >> "$OUTPUT"
    echo "" >> "$OUTPUT" # Optional: add blank line between parts
done

echo "🎉 Done! Full file created: $OUTPUT"
echo "Size: $(wc -c < "$OUTPUT") bytes"