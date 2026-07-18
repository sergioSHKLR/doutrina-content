#!/bin/bash
# ==============================================================================
# LDE — Pandoc HTML + TOC
# ==============================================================================
# Compiles LDE full Markdown into HTML with a collapsible TOC template.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

INPUT="books/md/1-lde/full/1-lde-full.md"
OUTPUT="books/html/1-lde-toc.html"
TEMPLATE="books/html/template.html"

mkdir -p "books/html"

echo "======================================================================"
echo "🏗️  LDE pre-build audits..."
echo "======================================================================"
python3 scripts/audit_links.py "$INPUT"
python3 scripts/check_block_closures.py "$INPUT"

echo -e "\n======================================================================"
echo "🚀 Pandoc compile"
echo "  -> Source:   $INPUT"
echo "  -> Template: $TEMPLATE"
echo "  -> Output:   $OUTPUT"
echo "======================================================================"

pandoc "$INPUT" \
  --toc \
  --toc-depth=4 \
  --standalone \
  --template="$TEMPLATE" \
  --metadata pagetitle="O Livro dos Espíritos - Edição Digital" \
  -o "$OUTPUT"

echo -e "\n✅ LDE HTML ready: $OUTPUT"
