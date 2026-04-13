import json
from pathlib import Path

c2_path = Path('docs/09_AUDIT/STATE/BASENAME_COLLISIONS_20260413.json')
with open(c2_path, encoding='utf-8') as f:
    data = json.load(f)

clusters = data.get('clusters', {})
index_cluster = clusters.get('index.md', {})
print('INDEX.md cluster:')
print(f"  Total: {index_cluster.get('count', 0)}")
paths = index_cluster.get('paths', [])
print(f'  Paths: {len(paths)}')
archive_cnt = len([p for p in paths if '/ARCHIVE/' in p or '.audit_fix_backup/' in p])
print(f'  Archive versions: {archive_cnt}')
if archive_cnt > 0:
    archive = [p for p in paths if '/ARCHIVE/' in p or '.audit_fix_backup/' in p]
    for p in archive[:3]:
        print(f'    {p}')
else:
    print('  (no archive versions in collision data)')
    print(f'  Sample paths:')
    for p in paths[:3]:
        print(f'    {p}')
