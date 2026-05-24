#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MD_ROOT="$PROJECT_ROOT/books/md"

echo "🗑️  Deleting all full-compiled master files..."

shopt -s nullglob
BOOKS=("$MD_ROOT"/[0-9]-*)

for book_dir in "${BOOKS[@]}"; do
    BOOK_NAME=$(basename "$book_dir")
    FULL_DIR="$book_dir/full"
    
    if [ -d "$FULL_DIR" ]; then
        # Deletes the compiled -full.md file
        rm -f "$FULL_DIR"/*-full.md
        echo "   🧹 Removed master file from: $BOOK_NAME/full/"
    fi
done

echo -e "\n✅ All master full files have been removed!"
