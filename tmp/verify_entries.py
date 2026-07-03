"""Batch verify debt registry entries: find entries referencing non-existent files."""
import re
import os
from pathlib import Path

REGISTRY = Path(r"D:\ZephyrAlpha\docs\02_enterprise_architecture\architecture_debt_registry.md")
REPO = Path(r"D:\ZephyrAlpha")

content = REGISTRY.read_text(encoding="utf-8")
lines = content.splitlines()

# Find all #### entries and their line ranges
entries = []
i = 0
while i < len(lines):
    if lines[i].startswith("#### "):
        start = i
        title = lines[i]
        # Find end of entry (next #### or ### or end of file)
        j = i + 1
        while j < len(lines) and not lines[j].startswith("#### ") and not lines[j].startswith("### "):
            j += 1
        entry_text = "\n".join(lines[start:j])
        entries.append((start + 1, j, title, entry_text))  # 1-indexed line numbers
        i = j
    else:
        i += 1

print(f"Total #### entries: {len(entries)}")

# For each entry, extract file paths and check existence
file_pattern = re.compile(r'`((?:src/|scripts/|tests/|docs/|config/|tmp/)[^`]+\.(?:py|yaml|yml|json|md|sql|sh))`')

fixed_deleted = []
fixed_deleted_severity = {"HIGH": [], "MEDIUM": [], "LOW": [], "NONE": []}
no_path = []
has_existing_files = []

for start_line, end_line, title, entry_text in entries:
    # Extract severity
    sev_match = re.search(r'\[(HIGH|MEDIUM|LOW)\]', title)
    severity = sev_match.group(1) if sev_match else "NONE"

    # Extract file paths
    paths = file_pattern.findall(entry_text)

    if not paths:
        no_path.append((start_line, end_line, title, severity))
        continue

    # Check if ALL referenced files don't exist
    all_deleted = True
    any_exists = False
    for p in paths:
        full_path = REPO / p
        if full_path.exists():
            any_exists = True
            all_deleted = False
        # Also check without the line number suffix
        # Some paths have :123 format

    if all_deleted and not any_exists:
        fixed_deleted.append((start_line, end_line, title, severity, paths))
        fixed_deleted_severity[severity].append((start_line, end_line, title, paths))
    else:
        has_existing_files.append((start_line, end_line, title, severity, paths))

print(f"\n=== FIXED_FILE_DELETED (all referenced files deleted) ===")
for sev in ["HIGH", "MEDIUM", "LOW", "NONE"]:
    print(f"  {sev}: {len(fixed_deleted_severity[sev])}")
print(f"  Total: {len(fixed_deleted)}")

print(f"\n=== NO_PATH (no file path referenced) ===")
for sev in ["HIGH", "MEDIUM", "LOW", "NONE"]:
    no_path_sev = [e for e in no_path if e[3] == sev]
    print(f"  {sev}: {len(no_path_sev)}")
print(f"  Total: {len(no_path)}")

print(f"\n=== HAS_EXISTING_FILES (needs manual check) ===")
for sev in ["HIGH", "MEDIUM", "LOW", "NONE"]:
    has_existing_sev = [e for e in has_existing_files if e[3] == sev]
    print(f"  {sev}: {len(has_existing_sev)}")
print(f"  Total: {len(has_existing_files)}")

# Output FIXED_FILE_DELETED entries for batch deletion
print(f"\n=== FIXED_FILE_DELETED entries (for deletion) ===")
for sev in ["HIGH", "MEDIUM", "LOW", "NONE"]:
    for start_line, end_line, title, paths in fixed_deleted_severity[sev]:
        # Clean title for display
        clean_title = title.replace("#### ", "").strip()[:100]
        print(f"  L{start_line}-{end_line} [{sev}] {clean_title}")
        print(f"    Files: {', '.join(paths[:3])}")
