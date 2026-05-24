#!/bin/bash

# =============================================
# concat-all.sh - Fixed Bound Token Injection
# =============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MD_ROOT="$PROJECT_ROOT/books/md"
SHARED_DIR="$MD_ROOT/shared"
BACKUP_ROOT="$PROJECT_ROOT/backup/full"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "🔄 Starting full compilation with clean bound tokens..."
mkdir -p "$BACKUP_ROOT"

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
    OUTPUT="$FULL_DIR/${BOOK_NAME}-full.md"
    
    if [ ! -d "$PARTIAL_DIR" ]; then continue; fi
    files=("$PARTIAL_DIR"/*.md)
    if [ ${#files[@]} -eq 0 ]; then continue; fi
    
    IFS=$'\n' files=($(sort -V <<<"${files[*]}")); unset IFS
    echo "📖 Processing: $BOOK_NAME"

    TMP_OUTPUT=$(mktemp)
    is_first_file=true

    for file in "${files[@]}"; do
        TMP_FILE_CONTENT=$(mktemp)
        
        sed -E 's/^>\s*expand\s+/::: expand /g; s/^>expand\s+/::: expand /g; s/^>\s*:::/:::/g; s/^>:::/:::/g' "$file" > "$TMP_FILE_CONTENT"

        if [ "$is_first_file" = true ]; then
            is_first_file=false
        else
            # Fix: Inject an explicit, non-clashing HTML part break comment
            echo -e "\n<!-- PART_BREAK -->\n" >> "$TMP_OUTPUT"

            if head -n 1 "$TMP_FILE_CONTENT" | grep -q '^---$'; then
                TMP_STRIPPED=$(mktemp)
                sed '1,/^---$/{ /^---$/d; d; }' "$TMP_FILE_CONTENT" > "$TMP_STRIPPED"
                mv -f "$TMP_STRIPPED" "$TMP_FILE_CONTENT"
            fi
        fi

        while IFS= read -r line; do
            if [[ "$line" =~ \<\!--[[:space:]]*INSERT_SHARED:([a-zA-Z0-9._-]+)[[:space:]]*--\> ]]; then
                shared_filename="${BASH_REMATCH}"
                shared_file_path="$SHARED_DIR/$shared_filename"
                
                echo "$line" >> "$TMP_OUTPUT" 
                if [ -f "$shared_file_path" ]; then
                    echo "   ➕ Injecting shared content: $shared_filename"
                    echo "<!-- START_SHARED -->" >> "$TMP_OUTPUT"
                    awk '1; END {if (NR && substr($0, length($0), 1) != "\n") print ""}' "$shared_file_path" >> "$TMP_OUTPUT"
                    echo "<!-- END_SHARED -->" >> "$TMP_OUTPUT"
                else
                    echo "   ⚠️ Shared content file not found: $shared_file_path"
                fi
            else
                echo "$line" >> "$TMP_OUTPUT"
            fi
        done < "$TMP_FILE_CONTENT"
        
        echo "" >> "$TMP_OUTPUT"
        rm -f "$TMP_FILE_CONTENT"
    done

    mkdir -p "$FULL_DIR"
    if [ -f "$OUTPUT" ]; then
        mv -f "$OUTPUT" "$BACKUP_ROOT/${BOOK_NAME}-full.${TIMESTAMP}.old"
    fi
    mv -f "$TMP_OUTPUT" "$OUTPUT"
    echo "   🎉 Created: ${BOOK_NAME}-full.md"
done

echo -e "\n✅ All master files compiled successfully!"
