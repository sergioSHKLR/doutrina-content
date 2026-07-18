#!/bin/bash

# 1. Configuration
INPUT_FILE="books/md/1-lde/full/1-lde-full.md" # Change this to your filename
OUTPUT_FILE="html/1-lde-toc.html"


if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: $INPUT_FILE not found!"
    exit 1
fi

# 1. Convert
markdown-to-standalone-html "$INPUT_FILE" -o "$OUTPUT_FILE"

# 2. Strip Custom Anchors
sed -i 's/{#[^}]*}//g' "$OUTPUT_FILE"

# 3. Aggressive CSS Injection
# This targets every possible TOC container and forces a scrollbar
CSS_FIX="
<style>
  /* Force scrolling on common TOC containers */
  #toc, .toc, .sidebar, .navigation, #sidebar {
    position: fixed !important;
    top: 20px !important;
    bottom: 20px !important;
    overflow-y: auto !important;
    max-height: calc(100vh - 40px) !important;
  }
  /* Ensure the body has space for the fixed sidebar */
  body {
    margin-left: 280px !important; /* Adjust if your TOC width is different */
  }
</style>"

# Injects the fix before the closing head tag
sed -i "/<\/head>/i $CSS_FIX" "$OUTPUT_FILE"

echo "Build complete. Check $OUTPUT_FILE."
