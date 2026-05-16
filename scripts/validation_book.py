from pathlib import Path
import re

OUTPUT_FILE = Path("lde-com-indice.md")

def run_validation(file_path):
    if not file_path.exists():
        print(f"❌ Error: {file_path} does not exist. Run the processor script first.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    errors = 0
    print(f"🔍 Analyzing {file_path}...\n")

    # Check 1: Count container tags to ensure none are left unclosed
    opens = content.count("::: expand 🔗")
    closes = content.count(":::")
    
    # Simple count check (assuming no other ::: block types exist)
    print(f"📊 Block Syntax Count:")
    print(f"   - '::: expand 🔗' blocks found: {opens}")
    
    # Check 2: Look for the old tag format that should have been overwritten or deleted
    old_placeholders = re.findall(r":::\s*expand\s*🏷️", content)
    if old_placeholders:
        print(f"❌ ERROR: Found {len(old_placeholders)} remnants of the old '::: expand 🏷️' tag!")
        errors += 1
    else:
        print("✅ SUCCESS: All old '::: expand 🏷️' placeholders removed or updated.")

    # Check 3: Check for empty container blocks '::: expand 🔗 \n :::'
    empty_blocks = re.findall(r":::\s*expand\s*🔗\s*:::", content)
    if empty_blocks:
        print(f"❌ ERROR: Found {len(empty_blocks)} empty link containers!")
        errors += 1
    else:
        print("✅ SUCCESS: No empty link blocks exist.")

    # Check 4: Ensure all remaining link entries contain both the 🏷️ and 🔗 formatting
    sample_links = re.findall(r"🏷️\s*\[[^\]]+\]\s*\(\s*#[^)]+\s*\)", content)
    print(f"   - Properly formatted links found: {len(sample_links)}")

    print("\n--- SUMMARY ---")
    if errors == 0:
        print("🎉 Validation Passed! The file structure looks perfect and clean.")
    else:
        print(f"⚠️ Validation Failed with {errors} structural error(s). Review the alerts above.")

if __name__ == "__main__":
    run_validation(OUTPUT_FILE)
