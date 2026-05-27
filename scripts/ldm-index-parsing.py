#!/usr/bin/env python3
"""
Manual LDM Index Extractor - Specify page range
"""

import fitz  # PyMuPDF
from pathlib import Path

def extract_from_pages(start_page=410, end_page=450):
    pdf_path = Path("books/pdf/2-Livro-dos-Mediuns.pdf")
    
    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    doc = fitz.open(pdf_path)
    index_text = []
    
    print(f"📖 Extracting from pages {start_page} to {end_page}...\n")
    
    for page_num in range(start_page-1, min(end_page, len(doc))):
        page = doc[page_num]
        text = page.get_text("text")
        index_text.append(f"--- Page {page_num+1} ---\n{text}")
        print(f"   Extracted page {page_num+1}")
    
    full_index = "\n".join(index_text)
    
    output_file = Path("reports/ldm_index_extracted.md")
    output_file.write_text(f"# LDM Index Extracted from PDF (Pages {start_page}-{end_page})\n\n{full_index}", encoding='utf-8')
    
    print(f"\n✅ Done! Saved to: {output_file}")
    doc.close()

if __name__ == "__main__":
    # Change these numbers if needed
    extract_from_pages(start_page=410, end_page=460)