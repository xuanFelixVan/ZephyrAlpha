import json, shutil
from pathlib import Path

src = Path('docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.json')
d = json.loads(src.read_text(encoding='utf-8'))
d['scan_label'] = 'L2_POST_FIX'
d['compared_to'] = 'SENTINEL_L1_SCAN_20260408_PRE_FIX broken=5310'

for ext in ('.json', '.md'):
    shutil.copy(
        f'docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408{ext}',
        f'docs/09_AUDIT/STATE/SENTINEL_L2_SCAN_20260413{ext}'
    )

l2_path = Path('docs/09_AUDIT/STATE/SENTINEL_L2_SCAN_20260413.json')
l2_path.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding='utf-8')

broken = d.get('broken_links_total', 0)
md_cnt = d.get('md_file_count', 0)
dup    = len(d.get('duplicate_module_ids', {}))
print(f'L2 snapshot saved: SENTINEL_L2_SCAN_20260413.json/md')
print(f'  broken_links_total   : {broken}')
print(f'  md_file_count        : {md_cnt}')
print(f'  duplicate_module_ids : {dup}')
