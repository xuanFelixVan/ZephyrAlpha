"""Check HAS_EXISTING_FILES entries and sample NO_PATH entries."""
import re
from pathlib import Path

REGISTRY = Path(r"D:\ZephyrAlpha\docs\02_enterprise_architecture\architecture_debt_registry.md")
REPO = Path(r"D:\ZephyrAlpha")

content = REGISTRY.read_text(encoding="utf-8")
lines = content.splitlines()

# Find all #### entries
entries = []
i = 0
while i < len(lines):
    if lines[i].startswith("#### "):
        start = i
        title = lines[i]
        j = i + 1
        while j < len(lines) and not lines[j].startswith("#### ") and not lines[j].startswith("### "):
            j += 1
        entry_text = "\n".join(lines[start:j])
        entries.append((start + 1, j, title, entry_text))
        i = j
    else:
        i += 1

# Also extract markdown link paths: [text](file:///path)
md_link_pattern = re.compile(r'file:///D:/ZephyrAlpha/([^)]+)')
# And backtick paths with any prefix
backtick_pattern = re.compile(r'`([^`]+\.(?:py|yaml|yml|json|md|sql|sh))`')

print("=== HAS_EXISTING_FILES entries (11) ===")
file_pattern = re.compile(r'`((?:src/|scripts/|tests/|docs/|config/|tmp/)[^`]+\.(?:py|yaml|yml|json|md|sql|sh))`')
has_existing = []
for start_line, end_line, title, entry_text in entries:
    paths = file_pattern.findall(entry_text)
    if not paths:
        continue
    all_deleted = True
    for p in paths:
        if (REPO / p).exists():
            all_deleted = False
            break
    if not all_deleted:
        sev_match = re.search(r'\[(HIGH|MEDIUM|LOW)\]', title)
        severity = sev_match.group(1) if sev_match else "NONE"
        has_existing.append((start_line, end_line, title, severity, paths, entry_text))

for start_line, end_line, title, severity, paths, entry_text in has_existing:
    print(f"\n--- L{start_line}-{end_line} [{severity}] ---")
    print(title[:120])
    for p in paths:
        exists = (REPO / p).exists()
        print(f"  {'EXISTS' if exists else 'MISSING'}: {p}")
    # Print first 3 lines of entry
    for line in entry_text.splitlines()[:5]:
        print(f"  {line[:120]}")

# Sample NO_PATH HIGH entries to understand format
print("\n\n=== Sample NO_PATH HIGH entries (first 10) ===")
no_path_high = []
for start_line, end_line, title, entry_text in entries:
    sev_match = re.search(r'\[(HIGH|MEDIUM|LOW)\]', title)
    severity = sev_match.group(1) if sev_match else "NONE"
    if severity != "HIGH":
        continue
    paths = file_pattern.findall(entry_text)
    md_paths = md_link_pattern.findall(entry_text)
    backtick_paths = backtick_pattern.findall(entry_text)
    if not paths and not md_paths and not backtick_paths:
        no_path_high.append((start_line, end_line, title, entry_text))

print(f"Total HIGH NO_PATH entries: {len(no_path_high)}")
for start_line, end_line, title, entry_text in no_path_high[:10]:
    print(f"\n--- L{start_line} ---")
    for line in entry_text.splitlines()[:5]:
        print(f"  {line[:150]}")

# Check HIGH entries with md_link paths
print("\n\n=== HIGH entries with markdown link paths ===")
high_md_link = []
for start_line, end_line, title, entry_text in entries:
    sev_match = re.search(r'\[(HIGH|MEDIUM|LOW)\]', title)
    severity = sev_match.group(1) if sev_match else "NONE"
    if severity != "HIGH":
        continue
    md_paths = md_link_pattern.findall(entry_text)
    if md_paths:
        # Check if files exist
        all_deleted = all(not (REPO / p.replace("#L", "").split(":")[0]).exists() for p in md_paths)
        any_exists = any((REPO / p.replace("#L", "").split(":")[0]).exists() for p in md_paths)
        status = "FIXED_DELETED" if all_deleted else ("HAS_EXISTING" if any_exists else "UNCLEAR")
        high_md_link.append((start_line, title, md_paths, status))

print(f"HIGH entries with md_link paths: {len(high_md_link)}")
fixed_count = sum(1 for _, _, _, s in high_md_link if s == "FIXED_DELETED")
has_count = sum(1 for _, _, _, s in high_md_link if s == "HAS_EXISTING")
print(f"  FIXED_DELETED: {fixed_count}")
print(f"  HAS_EXISTING: {has_count}")
