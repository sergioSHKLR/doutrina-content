#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MD_ROOT="$PROJECT_ROOT/books/md"

echo "🗑️  Wiping out all partial markdown files..."

shopt -s nullglob
BOOKS=("$MD_ROOT"/[0-9]-*)

for book_dir in "${BOOKS[@]}"; do
    BOOK_NAME=$(basename "$book_dir")
    PARTIAL_DIR="$book_dir/partial"
    
    if [ -d "$PARTIAL_DIR" ]; then
        # Deletes all markdown files inside this specific partial folder
        rm -f "$PARTIAL_DIR"/*.md
        echo "   🧹 Cleaned: $BOOK_NAME/partial/"
    fi
done

echo -e "\n✅ All partial markdown folders have been emptied!"
