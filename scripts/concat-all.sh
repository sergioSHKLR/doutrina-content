#!/bin/bash

# =============================================
# concat-all.sh - Robust > expand replacement
# =============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

BACKUP_ROOT="$PROJECT_ROOT/backup"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "🔄 Starting full archival concatenation for all books..."

mkdir -p "$BACKUP_ROOT"

BOOKS=($(ls -d "$PROJECT_ROOT/books/md/"[0-9]-* 2>/dev/null | sort -V))

if [ ${#BOOKS[@]} -eq 0 ]; then
    echo "❌ No book folders found in books/md/"
    exit 1
fi

echo "📚 Found ${#BOOKS[@]} books to process."

for book_dir in "${BOOKS[@]}"; do
    BOOK_NAME=$(basename "$book_dir")
    PARTIAL_DIR="$book_dir/partial"
    FULL_DIR="$book_dir/full"
    OUTPUT="$FULL_DIR/${BOOK_NAME}-full.md"
    
    BACKUP_BOOK_FULL="$BACKUP_ROOT/full/$BOOK_NAME"
    BACKUP_BOOK_PARTIAL="$BACKUP_ROOT/partial/$BOOK_NAME"
    mkdir -p "$BACKUP_BOOK_FULL"
    mkdir -p "$BACKUP_BOOK_PARTIAL"
    
    echo -e "\n────────────────────────────────────"
    echo "📖 Processing: $BOOK_NAME"
    
    if [ ! -d "$PARTIAL_DIR" ]; then
        echo "   ⚠️  Skipping - no 'partial' folder"
        continue
    fi

    files=($(ls -v "$PARTIAL_DIR"/*.md 2>/dev/null | sort -V))

    if [ ${#files[@]} -eq 0 ]; then
        echo "   ⚠️  No .md files found"
        continue
    fi

    echo "   ✅ Found ${#files[@]} parts"

    # Create a safe temporary file for compiling text to prevent self-referencing file locks
    TMP_OUTPUT=$(mktemp)

    for file in "${files[@]}"; do
        filename=$(basename "$file")
        part_base="${filename%.md}"
        
        BACKUP_PART="$BACKUP_BOOK_PARTIAL/${part_base}.${TIMESTAMP}.old"
        cp "$file" "$BACKUP_PART"
        
        echo "   📄 Processing: $filename"
        
        # Stream formatting edits directly into the temporary output holder
        sed -E '
            s/^>\s*expand\s+/::: expand /g;
            s/^>expand\s+/::: expand /g;
            s/^>\s*:::/:::/g;
            s/^>:::/:::/g
        ' "$file" >> "$TMP_OUTPUT"
        
        echo "" >> "$TMP_OUTPUT"
    done

    # Ensure the destination folder exists before moving files in
    mkdir -p "$FULL_DIR"

    # Safely clear out or back up the pre-existing target file
    if [ -f "$OUTPUT" ]; then
        BASE_NAME=$(basename "$OUTPUT" .md)
        BACKUP_FULL="$BACKUP_BOOK_FULL/${BASE_NAME}.${TIMESTAMP}.old"
        # Using force move guarantees overwrite success on the old backup path
        mv -f "$OUTPUT" "$BACKUP_FULL"
        echo "   🗄️  Backed up existing full file"
    fi

    # Swap the completely built temporary file to the final destination path
    mv -f "$TMP_OUTPUT" "$OUTPUT"

    echo "   🎉 Created: ${BOOK_NAME}-full.md  ($(wc -c < "$OUTPUT" | numfmt --to=iec) bytes)"
done

echo -e "\n✅ All books processed successfully!"
