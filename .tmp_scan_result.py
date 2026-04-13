import json
from pathlib import Path
d = json.loads(Path('docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.json').read_text(encoding='utf-8'))
stats = d['links']['stats']
print('After SKIP_PARTS update (excluded .audit_fix_backup, .trae, review_materials_package):')
for k, v in stats.items():
    print(f'  {k}: {v}')
md_cnt = d.get('md_file_count', '?')
print(f'  md_file_count: {md_cnt}')
