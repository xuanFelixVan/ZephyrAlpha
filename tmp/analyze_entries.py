"""Analyze debt registry entries: count by pattern, identify deletion candidates."""
import re
from pathlib import Path
from collections import Counter

REGISTRY = Path(r"D:\ZephyrAlpha\docs\02_enterprise_architecture\architecture_debt_registry.md")
REPO = Path(r"D:\ZephyrAlpha")

content = REGISTRY.read_text(encoding="utf-8")
lines = content.splitlines(keepends=True)

# Find all #### entries
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

# Patterns
md_link_pattern = re.compile(r'file:///[Dd]:/[Zz]ephyr[Aa]lpha/([^)\\]+)')
backtick_pattern = re.compile(r'`((?:src/|scripts/|tests/|docs/|config/)[^`{}*?\[\]]+\.(?:py|yaml|yml|json|md|sql))`')

def clean_path(p: str) -> str:
    p = p.split("#")[0]
    # Strip :123 line refs but not ://
    if re.search(r':[0-9]+$', p):
        p = re.sub(r':[0-9]+$', '', p)
    return p.strip()

# Categorize entries
no_path = 0
has_md_only = 0
has_bt_only = 0
has_both = 0
md_all_deleted = 0  # entries where all md paths deleted
md_has_existing = 0  # entries where at least one md path exists
bt_all_deleted = 0
bt_has_existing = 0

# Track entries with md paths that all reference deleted files (deletion candidates)
md_deletion_candidates = []

for start, end, title_line, entry_text in entries:
    md_paths = md_link_pattern.findall(entry_text)
    bt_paths = backtick_pattern.findall(entry_text)

    md_paths_clean = [clean_path(p) for p in md_paths]
    bt_paths_clean = [clean_path(p) for p in bt_paths]
    md_paths_clean = [p for p in md_paths_clean if p and "*" not in p and "{" not in p]
    bt_paths_clean = [p for p in bt_paths_clean if p and "*" not in p and "{" not in p]

    has_md = bool(md_paths_clean)
    has_bt = bool(bt_paths_clean)

    if not has_md and not has_bt:
        no_path += 1
        continue

    if has_md and not has_bt:
        has_md_only += 1
    elif has_bt and not has_md:
        has_bt_only += 1
    else:
        has_both += 1

    # Check md paths
    if has_md:
        existing_md = [p for p in md_paths_clean if (REPO / p).exists()]
        if existing_md:
            md_has_existing += 1
        else:
            md_all_deleted += 1
            md_deletion_candidates.append((start, end, title_line.strip()[:120], "md", len(md_paths_clean)))

    # Check bt paths
    if has_bt:
        existing_bt = [p for p in bt_paths_clean if (REPO / p).exists()]
        if existing_bt:
            bt_has_existing += 1
        else:
            bt_all_deleted += 1
            md_deletion_candidates.append((start, end, title_line.strip()[:120], "bt", len(bt_paths_clean)))

print(f"\n=== Entry Categorization ===")
print(f"No file paths:                  {no_path}")
print(f"Has MD links only:              {has_md_only}")
print(f"Has backtick paths only:        {has_bt_only}")
print(f"Has both:                       {has_both}")
print(f"\n=== MD link analysis ===")
print(f"MD links - all files deleted:   {md_all_deleted}")
print(f"MD links - has existing file:   {md_has_existing}")
print(f"\n=== Backtick path analysis ===")
print(f"BT paths - all files deleted:   {bt_all_deleted}")
print(f"BT paths - has existing file:   {bt_has_existing}")

# Dedupe candidates (entry may be both md and bt all-deleted)
seen_starts = set()
unique_candidates = []
for start, end, title, src, cnt in md_deletion_candidates:
    if start not in seen_starts:
        seen_starts.add(start)
        unique_candidates.append((start, end, title, src, cnt))

print(f"\n=== Deletion candidates (all referenced files deleted) ===")
print(f"Unique entries: {len(unique_candidates)}")
for start, end, title, src, cnt in unique_candidates[:50]:
    print(f"  L{start+1} [{src}/{cnt}] {title}")
