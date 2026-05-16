#!/bin/bash

# Finds the directory where this script lives (~/doutrina-content/scripts) 
# and goes up one level to the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

INPUT_DIR="$PROJECT_ROOT/books/md/1-lde/parts"
OUTPUT_DIR="$PROJECT_ROOT/books/md/1-lde/full"
OUTPUT="$OUTPUT_DIR/lde-full.md"

# Define dedicated, structured backup directories inside root
BACKUP_PARTS_DIR="$PROJECT_ROOT/backup/parts"
BACKUP_FULL_DIR="$PROJECT_ROOT/backup/full"

# Generate a uniform timestamp format for this entire compilation run (e.g., 20260516_074419)
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "🔄 Starting deep archival concatenation into $OUTPUT ..."

# Ensure both backup destination subfolders exist
mkdir -p "$BACKUP_PARTS_DIR"
mkdir -p "$BACKUP_FULL_DIR"

# Find and sort files numerically (0 to 6) inside the root parts directory
files=($(ls -v "$INPUT_DIR"/lde-*.md 2>/dev/null | grep -E 'lde-[0-6]\.md'))

if [ ${#files[@]} -eq 0 ]; then
    echo "❌ No split files found matching lde-[0-6].md in $INPUT_DIR"
    echo "Current directory contents of $INPUT_DIR:"
    ls -la "$INPUT_DIR" 2>/dev/null || echo "Directory does not exist or permission denied."
    exit 1
fi

echo "✅ Found ${#files[@]} parts to back up and process."

# --- 1. FULL FILE BACKUP STEP ---
if [ -f "$OUTPUT" ]; then
    # Strip pathing and extension to isolate "lde-full"
    BASE_FULL_NAME=$(basename "$OUTPUT" .md)
    BACKUP_FULL_FILE="$BACKUP_FULL_DIR/${BASE_FULL_NAME}.${TIMESTAMP}.old"
    
    echo "🗄️  Archiving previous master to: backup/full/$(basename "$BACKUP_FULL_FILE")"
    mv "$OUTPUT" "$BACKUP_FULL_FILE"
fi

# Clear/create a fresh output file for the new compilation stream
> "$OUTPUT"

# --- 2. PARTS BACKUP & PROCESSING LOOP ---
for file in "${files[@]}"; do
    filename=$(basename "$file")
    
    # Strip extension to isolate part name (e.g., "lde-0")
    part_base_name="${filename%.md}"
    BACKUP_PART_FILE="$BACKUP_PARTS_DIR/${part_base_name}.${TIMESTAMP}.old"
    
    echo "📄 Archiving and processing part: $filename"
    
    # Secure a physical copy of the original part file right now in backup/parts/
    cp "$file" "$BACKUP_PART_FILE"
    
    # Streams the content, swapping local "> expand " markers for native Eleventy "::: expand "
    # Also handles converting a closing line-starting ">" back to ":::" if needed
    sed -e 's/^> expand /::: expand /g' \
        -e 's/^>:::/:::/g' "$file" >> "$OUTPUT"
        
    echo "" >> "$OUTPUT" # Optional: add blank line between parts
done

echo "🎉 Done! Full file created: $OUTPUT"
echo "Size: $(wc -c < "$OUTPUT") bytes"

# alias is concat