import re
import unicodedata
from pathlib import Path

FILE_PATH = Path("1-lde-full.md")


def remove_diacritics(text):
    """Removes Portuguese accents (í -> i, ç -> c, ã -> a, etc.) dynamically."""
    normalized = unicodedata.normalize("NFD", text)
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


def fix_file_links(file_path):
    if not file_path.exists():
        print(f"❌ File {file_path} not found.")
        return

    content = file_path.read_text(encoding="utf-8")

    # This regex isolates group 2 (the anchor slug itself)
    pattern = re.compile(r"(🏷️\s*\[[^\]]+\]\s*\(\s*#)([^)]+)(\s*\))")

    # The lambda function applies 'remove_diacritics' ONLY to group 2
    fixed_content = pattern.sub(
        lambda m: f"{m.group(1)}{remove_diacritics(m.group(2))}{m.group(3)}",
        content,
    )

    file_path.write_text(fixed_content, encoding="utf-8")
    print("✨ Accent normalization complete for all 🏷️ link anchors!")


if __name__ == "__main__":
    fix_file_links(FILE_PATH)
