"""Delete verified FIXED entries from debt registry by title matching."""
import re
from pathlib import Path

REGISTRY = Path(r"D:\ZephyrAlpha\docs\02_enterprise_architecture\architecture_debt_registry.md")

content = REGISTRY.read_text(encoding="utf-8")
lines = content.splitlines(keepends=True)

# Titles to delete (#### level entries)
fixed_titles_4 = [
    "#### 5.5.6 AGENTS.md声明make_ttl_reconciler",
    "#### 5.6.2 make_ttl_reconciler宪法级不符",
    "#### 5.11.5 doc_type operational_rule指向真空目录",
    "#### 5.22.7 llm_security与llm_security_01整套包重复",
]

# 5.174 HIGH group - special: delete the group header and all 9 items until MEDIUM
# Title: "#### HIGH（9个） [✓ FIXED"
fixed_group_5_174 = "#### HIGH（9个） [✓ FIXED"

# ##### level subsections to delete (5.1.1 B, D, E)
fixed_titles_5 = [
    "##### B. semantic_vocabulary.yaml",
    "##### D. module_lifecycle_status_vocabulary.yaml",
    "##### E. contract_status_vocabulary.yaml",
]

# Find line ranges to delete
# Each entry starts at a #### or ##### line and ends at the next #### or ##### line
# (or ### line for #### entries)
deletions = []  # list of (start_idx, end_idx, title)

i = 0
while i < len(lines):
    line = lines[i]
    # Check #### level entries
    if line.startswith("#### "):
        for title in fixed_titles_4:
            if title in line:
                start = i
                j = i + 1
                while j < len(lines) and not lines[j].startswith("#### ") and not lines[j].startswith("### "):
                    j += 1
                deletions.append((start, j, line.strip()[:100]))
                i = j
                break
        else:
            # Check 5.174 HIGH group
            if fixed_group_5_174 in line:
                start = i
                j = i + 1
                # End at next #### (MEDIUM group)
                while j < len(lines) and not lines[j].startswith("#### "):
                    j += 1
                deletions.append((start, j, line.strip()[:100]))
                i = j
            else:
                i += 1
    # Check ##### level entries
    elif line.startswith("##### "):
        for title in fixed_titles_5:
            if title in line:
                start = i
                j = i + 1
                while j < len(lines) and not lines[j].startswith("##### ") and not lines[j].startswith("#### ") and not lines[j].startswith("### "):
                    j += 1
                deletions.append((start, j, line.strip()[:100]))
                i = j
                break
        else:
            i += 1
    else:
        i += 1

print(f"Found {len(deletions)} entries to delete:")
for start, end, title in deletions:
    print(f"  L{start+1}-L{end} ({end-start} lines): {title}")

# Build deletion set
delete_lines = set()
for start, end, _ in deletions:
    for k in range(start, end):
        delete_lines.add(k)

# Build new content
new_lines = [lines[k] for k in range(len(lines)) if k not in delete_lines]
deleted_count = len(lines) - len(new_lines)

print(f"\nDeleted {deleted_count} lines")
print(f"Old line count: {len(lines)}")
print(f"New line count: {len(new_lines)}")

# Verify new entry count
new_content = "".join(new_lines)
new_entry_count_4 = len(re.findall(r'^#### ', new_content, re.MULTILINE))
new_entry_count_5 = len(re.findall(r'^##### ', new_content, re.MULTILINE))
print(f"New #### entry count: {new_entry_count_4}")
print(f"New ##### entry count: {new_entry_count_5}")

# Write updated file
REGISTRY.write_text(new_content, encoding="utf-8")
print(f"\nUpdated registry written to {REGISTRY}")
