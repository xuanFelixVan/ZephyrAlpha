"""Extract HIGH severity entries with file references for verification."""
import re
from pathlib import Path

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
        title = lines[start].strip()
        entries.append((start, j, title, entry_text))
        i = j
    else:
        i += 1

# Find HIGH entries
md_link_pattern = re.compile(r'file:///[Dd]:/[Zz]ephyr[Aa]lpha/([^)\\]+)')

high_entries = []
for start, end, title, text in entries:
    # Check if HIGH severity
    if "[HIGH]" in title or "（HIGH）" in title or "【HIGH】" in title:
        # Extract file paths
        md_paths = md_link_pattern.findall(text)
        clean_paths = []
        for p in md_paths:
            p = p.split("#")[0].strip()
            if p and "*" not in p and "{" not in p:
                clean_paths.append(p)
        if clean_paths:
            high_entries.append((start, end, title, clean_paths))

print(f"Total #### entries: {len(entries)}")
print(f"HIGH entries with file refs: {len(high_entries)}")
print(f"\n=== HIGH entries (first 30) ===")
for start, end, title, paths in high_entries[:30]:
    # Check if files exist
    exists = [(REPO / p).exists() for p in paths]
    exist_count = sum(exists)
    print(f"\nL{start+1} [{exist_count}/{len(paths)} files exist] {title[:110]}")
    for p, e in zip(paths, exists):
        status = "✓" if e else "✗"
        print(f"  {status} {p}")
