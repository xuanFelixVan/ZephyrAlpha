#!/usr/bin/env python3
import os, re, sys, json
from pathlib import Path
from collections import defaultdict

DOCS = Path(r'D:\ZephyrAlpha\docs')
SRC = Path(r'D:\ZephyrAlpha\src')
ROOT = Path(r'D:\ZephyrAlpha')

results = {}

# ====== DIMENSION 1: Path Compliance ======
print("=" * 70)
print("DIMENSION 1: Path Compliance Scan")
print("=" * 70)
d1_violations = []
for root, dirs, files in os.walk(DOCS):
    for d in dirs:
        full = os.path.join(root, d)
        rel = os.path.relpath(full, DOCS).replace("\\", "/")
        has_non_ascii = any(ord(c) > 127 for c in d)
        has_space = " " in d
        has_bracket = any(c in d for c in "[](){}")
        has_special = any(c in d for c in "!@#$%^&*+=|<>?,;")
        issues = []
        if has_non_ascii:
            issues.append("Non-ASCII")
        if has_space:
            issues.append("Space")
        if has_bracket:
            issues.append("Bracket")
        if has_special:
            issues.append("Special")
        if issues:
            d1_violations.append({"path": rel, "issues": issues})

for v in sorted(d1_violations, key=lambda x: x["path"]):
    print(f'  [{" | ".join(v["issues"])}] {v["path"]}')
print(f"\nTotal D1 violations: {len(d1_violations)}")
results["d1"] = d1_violations

# ====== DIMENSION 2: module_id duplicates ======
print("\n" + "=" * 70)
print("DIMENSION 2: module_id Uniqueness Check")
print("=" * 70)
module_ids = defaultdict(list)
for md_file in DOCS.rglob("*.md"):
    try:
        with open(md_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(2000)
        rel = str(md_file.relative_to(DOCS)).replace("\\", "/")
        in_fm = False
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped == "---":
                in_fm = not in_fm
                continue
            if in_fm and stripped.startswith("module_id:"):
                mid = stripped.split(":", 1)[1].strip()
                module_ids[mid].append(rel)
                break
    except:
        pass

d2_duplicates = {k: v for k, v in module_ids.items() if len(v) > 1}
for mid, paths in sorted(d2_duplicates.items()):
    print(f'  DUPLICATE module_id="{mid}":')
    for p in paths:
        print(f"    -> {p}")
print(f"\nTotal D2 duplicates: {len(d2_duplicates)}")
results["d2"] = {k: v for k, v in d2_duplicates.items()}

# ====== DIMENSION 3: YAML Frontmatter Completeness ======
print("\n" + "=" * 70)
print("DIMENSION 3: YAML Frontmatter Completeness")
print("=" * 70)
required_fields = ["module_id", "version", "status", "owner"]
d3_issues = []
md_count = 0
for md_file in DOCS.rglob("*.md"):
    md_count += 1
    try:
        with open(md_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(2000)
        rel = str(md_file.relative_to(DOCS)).replace("\\", "/")
        if not content.startswith("---"):
            d3_issues.append({"path": rel, "issue": "No YAML frontmatter"})
            continue
        end = content.find("---", 3)
        if end == -1:
            d3_issues.append({"path": rel, "issue": "YAML frontmatter not closed"})
            continue
        yaml_block = content[3:end]
        missing = [f for f in required_fields if f + ":" not in yaml_block]
        if missing:
            d3_issues.append({"path": rel, "issue": f"Missing fields: {', '.join(missing)}"})
    except:
        pass

for v in sorted(d3_issues, key=lambda x: x["path"]):
    print(f'  {v["issue"]} -> {v["path"]}')
print(f"\nTotal D3 issues: {len(d3_issues)} / {md_count} files scanned")
results["d3"] = d3_issues

# ====== DIMENSION 4: INDEX link cross-check ======
print("\n" + "=" * 70)
print("DIMENSION 4: INDEX Link Integrity")
print("=" * 70)
d4_dead_links = []
d4_orphans = []

all_md_files = set()
for md_file in DOCS.rglob("*.md"):
    rel = str(md_file.relative_to(DOCS)).replace("\\", "/")
    all_md_files.add(rel)

index_files = list(DOCS.rglob("INDEX.md"))
for idx_file in index_files:
    try:
        with open(idx_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        idx_rel = str(idx_file.relative_to(DOCS)).replace("\\", "/")
        links = re.findall(r"\[([^\]]*)\]\(([^)]+\.md)\)", content)
        for text, link in links:
            if link.startswith(("http", "https", "#", "mailto:")):
                continue
            link_clean = link.split("#")[0]
            if not link_clean:
                continue
            target = (idx_file.parent / link_clean).resolve()
            try:
                target_rel = str(target.relative_to(DOCS)).replace("\\", "/")
            except ValueError:
                continue
            if target_rel not in all_md_files:
                d4_dead_links.append({"index": idx_rel, "dead_link": link_clean, "resolved": target_rel})
    except:
        pass

indexed_files = set()
for idx_file in index_files:
    try:
        with open(idx_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        idx_rel = str(idx_file.relative_to(DOCS)).replace("\\", "/")
        links = re.findall(r"\]\(([^)]+\.md)\)", content)
        for link in links:
            if link.startswith(("http", "https")):
                continue
            link_clean = link.split("#")[0]
            if not link_clean:
                continue
            target = (idx_file.parent / link_clean).resolve()
            try:
                target_rel = str(target.relative_to(DOCS)).replace("\\", "/")
                indexed_files.add(target_rel)
            except ValueError:
                pass
    except:
        pass

for f in sorted(all_md_files):
    if f not in indexed_files and f != "INDEX.md":
        d4_orphans.append(f)

for dl in sorted(d4_dead_links, key=lambda x: x["index"]):
    print(f'  DEAD LINK in {dl["index"]}: {dl["dead_link"]} -> {dl["resolved"]}')
print(f"\nDead links: {len(d4_dead_links)}")
print(f"Orphan files (not indexed): {len(d4_orphans)}")
if d4_orphans[:20]:
    for o in d4_orphans[:20]:
        print(f"  ORPHAN: {o}")
    if len(d4_orphans) > 20:
        print(f"  ... and {len(d4_orphans) - 20} more")
results["d4_dead"] = d4_dead_links
results["d4_orphans"] = d4_orphans

# ====== DIMENSION 6: Double YAML bomb ======
print("\n" + "=" * 70)
print("DIMENSION 6: Double YAML / module_id in body")
print("=" * 70)
d6_issues = []
for md_file in DOCS.rglob("*.md"):
    try:
        with open(md_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        rel = str(md_file.relative_to(DOCS)).replace("\\", "/")
        dash_count = 0
        for line in content.split("\n"):
            if line.strip() == "---":
                dash_count += 1
        if dash_count > 2:
            d6_issues.append({"path": rel, "issue": f"Extra --- markers: {dash_count} total"})

        body_module_ids = re.findall(r"^module_id:\s*\S+", content, re.MULTILINE)
        if len(body_module_ids) > 1:
            d6_issues.append({"path": rel, "issue": f"Multiple module_id declarations: {len(body_module_ids)}"})
    except:
        pass

for v in sorted(d6_issues, key=lambda x: x["path"]):
    print(f'  {v["issue"]} -> {v["path"]}')
print(f"\nTotal D6 issues: {len(d6_issues)}")
results["d6"] = d6_issues

# ====== DIMENSION 7: L5 hardcoded global params ======
print("\n" + "=" * 70)
print("DIMENSION 7: L5 Hardcoded Global Parameters")
print("=" * 70)
d7_issues = []
l5_dirs = ["05_IMPLEMENTATION", "04_EXECUTION"]
hardcoded_patterns = [
    (r"threshold\s*[:=]\s*[\d.]+", "hardcoded threshold"),
    (r"fee_rate\s*[:=]\s*[\d.]+", "hardcoded fee rate"),
    (r"slippage\s*[:=]\s*[\d.]+", "hardcoded slippage"),
    (r"risk_limit\s*[:=]\s*[\d.]+", "hardcoded risk limit"),
    (r"MAX_POSITION\s*[:=]\s*[\d.]+", "hardcoded max position"),
]
for md_file in DOCS.rglob("*.md"):
    rel = str(md_file.relative_to(DOCS)).replace("\\", "/")
    if not any(rel.startswith(d) for d in l5_dirs):
        continue
    try:
        with open(md_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for pattern, desc in hardcoded_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                d7_issues.append({"path": rel, "issue": f"{desc}: {matches}"})
    except:
        pass

for v in sorted(d7_issues, key=lambda x: x["path"]):
    print(f'  {v["issue"]} -> {v["path"]}')
print(f"\nTotal D7 issues: {len(d7_issues)}")
results["d7"] = d7_issues

# ====== DIMENSION 9: SOP closure - missing DoD ======
print("\n" + "=" * 70)
print("DIMENSION 9: SOP Closure - Missing Definition of Done")
print("=" * 70)
d9_issues = []
for md_file in DOCS.rglob("*.md"):
    try:
        with open(md_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        rel = str(md_file.relative_to(DOCS)).replace("\\", "/")
        has_steps = bool(re.search(r"步骤|Step|步骤\s*\d", content, re.IGNORECASE))
        has_dod = bool(re.search(r"验收标准|Definition of Done|DoD|完成标准|Done条件", content, re.IGNORECASE))
        if has_steps and not has_dod:
            d9_issues.append(rel)
    except:
        pass

for v in sorted(d9_issues):
    print(f"  Missing DoD: {v}")
print(f"\nTotal D9 issues: {len(d9_issues)}")
results["d9"] = d9_issues

# ====== DIMENSION 10: Orphan trend ======
print("\n" + "=" * 70)
print("DIMENSION 10: Orphan Trend Assessment")
print("=" * 70)
total_md = len(all_md_files)
indexed_count = len(indexed_files)
orphan_count = len(d4_orphans)
governance_rate = round((total_md - orphan_count) / total_md * 100, 2) if total_md else 0
print(f"Total .md files: {total_md}")
print(f"Indexed files: {indexed_count}")
print(f"Orphan files: {orphan_count}")
print(f"Governance rate: {governance_rate}%")

prev_reports = list(DOCS.rglob("09_AUDIT/STATE/orphan_scan_result_*.json"))
if prev_reports:
    latest = max(prev_reports, key=lambda p: p.stat().st_mtime)
    try:
        with open(latest, "r", encoding="utf-8") as f:
            prev_data = json.load(f)
        prev_rate = prev_data.get("orphan_rate", "N/A")
        print(f"Previous scan orphan rate: {prev_rate}%")
        print(f"Previous scan file: {latest.name}")
    except:
        pass
else:
    print("No previous orphan scan reports found")

results["d10"] = {
    "total_md": total_md,
    "indexed": indexed_count,
    "orphans": orphan_count,
    "governance_rate": governance_rate,
}

# Save full results
with open(ROOT / "audit_10d_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("\n\nFull results saved to audit_10d_results.json")
