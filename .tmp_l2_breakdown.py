import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path
from collections import Counter

d = json.loads(Path('docs/09_AUDIT/STATE/SENTINEL_L2_SCAN_20260413.json').read_text(encoding='utf-8'))
invalid = d['links']['invalid_details_sample']

print(f'Total invalid links: {len(invalid)}')
print()

# Break down by top-level source directory
prefixes = Counter()
for item in invalid:
    src = item['source'].replace('\\','/')
    parts = src.split('/')
    if src.startswith('.audit_fix_backup'):
        prefixes['.audit_fix_backup/'] += 1
    elif src.startswith('docs/'):
        prefixes['/'.join(parts[:3]) + '/'] += 1
    else:
        prefixes[parts[0] + '/'] += 1

print('Source breakdown:')
for p, cnt in prefixes.most_common():
    print(f'  {cnt:4d}  {p}')

# Docs-only breakdown
docs_only = [item for item in invalid if item['source'].startswith('docs/')]
backup_only = [item for item in invalid if item['source'].startswith('.audit_fix_backup/')]

print(f'\n--- docs/ only: {len(docs_only)} ---')
docs_prefixes = Counter()
for item in docs_only:
    src = item['source'].replace('\\','/')
    parts = src.split('/')
    docs_prefixes['/'.join(parts[:3]) + '/'] += 1
for p, cnt in docs_prefixes.most_common():
    print(f'  {cnt:4d}  {p}')

print(f'\n--- .audit_fix_backup/: {len(backup_only)} ---')
print('  (backup directory - expected, these files are unmanaged copies)')

# Sample 10 docs/ invalid links
print(f'\nSample of docs/ broken links:')
for item in docs_only[:15]:
    print(f'  src: {item["source"][-65:]}')
    print(f'  url: {item["url"]}')
    print(f'  resolved: {item["resolved"]}')
    print()
