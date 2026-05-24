#!/bin/bash

# =============================================
# split-all.sh - Synchronized Heading Segmenter
# =============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MD_ROOT="$PROJECT_ROOT/books/md"
BACKUP_ROOT="$PROJECT_ROOT/backup/partial"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "🔄 Running pure structural splitting pipeline..."

shopt -s nullglob
BOOKS=("$MD_ROOT"/[0-9]-*)

if [ ${#BOOKS[@]} -eq 0 ]; then
    echo "❌ No book folders found in books/md/"
    exit 1
fi

for book_dir in "${BOOKS[@]}"; do
    BOOK_NAME=$(basename "$book_dir")
    PARTIAL_DIR="$book_dir/partial"
    FULL_DIR="$book_dir/full"
    INPUT_FILE="$FULL_DIR/${BOOK_NAME}-full.md"

    if [ ! -f "$INPUT_FILE" ]; then 
        echo "⚠️  Skipping $BOOK_NAME - Full master file not found."
        continue
    fi
    echo "📖 Deconstructing: $BOOK_NAME"

    if [ -d "$PARTIAL_DIR" ]; then
        mkdir -p "$BACKUP_ROOT/$BOOK_NAME/split_${TIMESTAMP}"
        cp -r "$PARTIAL_DIR"/* "$BACKUP_ROOT/$BOOK_NAME/split_${TIMESTAMP}/" 2>/dev/null
        rm -rf "$PARTIAL_DIR"/*
    else
        mkdir -p "$PARTIAL_DIR"
    fi

    awk -v out_dir="$PARTIAL_DIR" '
        BEGIN {
            part_idx = 0
            current_file = sprintf("%s/%02d.md", out_dir, part_idx)
            skipping_shared = 0
            is_first_heading = 1
        }
        
        /^## / {
            # If it is the first heading encountered, do not step up the index.
            # This ensures ## 0. stays cleanly matched inside 00.md alongside its front matter.
            if (is_first_heading == 1) {
                is_first_heading = 0
            } else {
                if (current_file != "") close(current_file)
                part_idx++
                current_file = sprintf("%s/%02d.md", out_dir, part_idx)
            }
            skipping_shared = 0
        }
        
        # Look for the common start token to turn skipping ON
        /<!-- START_SHARED -->/ {
            skipping_shared = 1
            next
        }
        
        # Look for the common stop token to turn skipping OFF
        /<!-- END_SHARED -->/ {
            skipping_shared = 0
            next
        }
        
        # Ignore part break markers entirely during splitting
        /<!-- PART_BREAK -->/ {
            next
        }
        
        {
            if (skipping_shared == 0 && current_file != "") {
                print $0 >> current_file
            }
        }
    ' "$INPUT_FILE"

    generated_files=("$PARTIAL_DIR"/*.md)
    echo "   🎉 Split finished. Extracted ${#generated_files[@]} clean local chunks."
done

echo -e "\n✅ All source files segmented successfully!"
