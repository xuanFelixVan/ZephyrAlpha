import json
from collections import Counter

d = json.load(open(r'D:\ZephyrAlpha\audit_10d_results.json', 'r', encoding='utf-8'))

print('=== D1: Path Violations (23 total) ===')
for v in d['d1']:
    issues_str = ' | '.join(v['issues'])
    print(f'  [{issues_str}] {v["path"]}')

print()

print('=== D3: Frontmatter Issues (1 total) ===')
for v in d['d3']:
    print(f'  {v["issue"]} -> {v["path"]}')

print()

print('=== D6: Double YAML Issues (782 total) ===')
extra_dash = sum(1 for v in d['d6'] if 'Extra' in v['issue'])
multi_mid = sum(1 for v in d['d6'] if 'Multiple module_id' in v['issue'])
print(f'  Extra --- markers: {extra_dash}')
print(f'  Multiple module_id: {multi_mid}')

print()
print('D6 samples (first 15):')
for v in d['d6'][:15]:
    print(f'  {v["issue"]} -> {v["path"]}')

print()

print('=== D7: L5 Hardcoded (56 total) ===')
types = Counter()
for v in d['d7']:
    t = v['issue'].split(':')[0] if ':' in v['issue'] else v['issue']
    types[t] += 1
for t, c in types.most_common():
    print(f'  {t}: {c}')

print()
print('D7 samples (first 10):')
for v in d['d7'][:10]:
    print(f'  {v["issue"]} -> {v["path"]}')

print()

# D2: deeper check - also check body module_ids
print('=== D2: module_id in body (not just frontmatter) ===')
import re
from pathlib import Path
from collections import defaultdict

DOCS = Path(r'D:\ZephyrAlpha\docs')
all_mids = defaultdict(list)
for md_file in DOCS.rglob("*.md"):
    try:
        with open(md_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        rel = str(md_file.relative_to(DOCS)).replace("\\", "/")
        matches = re.findall(r'^module_id:\s*(\S+)', content, re.MULTILINE)
        for mid in matches:
            all_mids[mid].append(rel)
    except:
        pass

dups = {k: v for k, v in all_mids.items() if len(v) > 1}
print(f'Total unique module_ids: {len(all_mids)}')
print(f'Duplicate module_ids: {len(dups)}')
for mid, paths in sorted(dups.items()):
    print(f'  "{mid}" appears in {len(paths)} files:')
    for p in paths:
        print(f'    -> {p}')

print()

# D4: orphan breakdown by layer
print('=== D4: Orphan breakdown by top-level directory ===')
layer_counts = Counter()
for o in d['d4_orphans']:
    layer = o.split('/')[0] if '/' in o else 'root'
    layer_counts[layer] += 1
for layer, count in layer_counts.most_common(20):
    print(f'  {layer}: {count} orphans')
