"""Batch delete FIXED_FILE_DELETED entries from debt registry.
Refined: only match real file paths (no wildcards/glob patterns)."""
import re
from pathlib import Path

REGISTRY = Path(r"D:\ZephyrAlpha\docs\02_enterprise_architecture\architecture_debt_registry.md")
REPO = Path(r"D:\ZephyrAlpha")

content = REGISTRY.read_text(encoding="utf-8")
lines = content.splitlines(keepends=True)

# Find all #### entries and their line ranges (0-indexed)
entries = []
i = 0
while i < len(lines):
    if lines[i].startswith("#### "):
        start = i
        j = i + 1
        while j < len(lines) and not lines[j].startswith("#### ") and not lines[j].startswith("### "):
            j += 1
        entry_text = "".join(lines[start:j])
        entries.append((start, j, lines[start], entry_text))
        i = j
    else:
        i += 1

print(f"Total #### entries: {len(entries)}")

# Markdown link pattern: [text](file:///D:/ZephyrAlpha/path) or file:///d:/ZephyrAlpha/path
md_link_pattern = re.compile(r'file:///[Dd]:/[Zz]ephyr[Aa]lpha/([^)\\]+)')

# Backtick paths: only match real paths (no wildcards, curly braces, or ** patterns)
# Must start with a known directory prefix and end with a file extension
backtick_pattern = re.compile(r'`((?:src/|scripts/|tests/|docs/|config/)[^`{}*?\[\]]+\.(?:py|yaml|yml|json|md|sql))`')

def clean_path(p: str) -> str:
    """Clean a path: remove #L123 anchors, :123 line numbers, leading/trailing whitespace."""
    p = p.split("#")[0]  # Remove markdown anchors
    p = p.split(":")[0] if ":" in p and not p[1:3] == ":/" else p  # Remove :123 line refs (but not :// in URLs)
    return p.strip()

def file_exists(p: str) -> bool:
    """Check if a file exists at the given relative path."""
    clean = clean_path(p)
    if not clean or "*" in clean or "{" in clean or "?" in clean:
        return False  # Skip glob patterns
    return (REPO / clean).exists()

# Identify entries to delete (ALL referenced files deleted)
entries_to_delete = set()
delete_info = []

for start, end, title_line, entry_text in entries:
    # Extract all file paths from markdown links
    md_paths = md_link_pattern.findall(entry_text)
    # Extract backtick paths (real paths only, no wildcards)
    bt_paths = backtick_pattern.findall(entry_text)

    all_paths = list(set(md_paths + bt_paths))
    if not all_paths:
        continue

    # Check if ALL files are deleted
    all_deleted = True
    has_existing = False
    for p in all_paths:
        clean = clean_path(p)
        if not clean or "*" in clean or "{" in clean:
            continue  # Skip glob patterns
        if (REPO / clean).exists():
            has_existing = True
            all_deleted = False
            break

    if all_deleted and not has_existing:
        # Verify at least one path was actually checked (not all globs)
        checked = [p for p in all_paths if not ("*" in clean_path(p) or "{" in clean_path(p))]
        if checked:
            entries_to_delete.add((start, end))
            delete_info.append((title_line.strip()[:100], len(checked)))

print(f"\nEntries to delete (ALL files deleted): {len(delete_info)}")
for title, path_count in delete_info[:30]:
    print(f"  [{path_count} paths] {title}")
if len(delete_info) > 30:
    print(f"  ... and {len(delete_info) - 30} more")

# Build new content: keep lines that are NOT in deleted entries
new_lines = []
deleted_count = 0
i = 0
while i < len(lines):
    in_deleted = False
    for start, end in entries_to_delete:
        if start <= i < end:
            in_deleted = True
            if i == start:
                deleted_count += 1
            break
    if not in_deleted:
        new_lines.append(lines[i])
    i += 1

print(f"\nDeleted {deleted_count} entries")
print(f"Old line count: {len(lines)}")
print(f"New line count: {len(new_lines)}")

# Verify new entry count
new_content = "".join(new_lines)
new_entry_count = len(re.findall(r'^#### ', new_content, re.MULTILINE))
print(f"New #### entry count: {new_entry_count}")

# Write updated file
REGISTRY.write_text(new_content, encoding="utf-8")
print(f"\nUpdated registry written to {REGISTRY}")
