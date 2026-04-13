import json
from pathlib import Path

d = json.loads(Path('docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.json').read_text(encoding='utf-8'))
mod = d.get('module_ids', {})

unique = mod.get('unique_module_ids', 0)
dup_cnt = mod.get('duplicate_ids_count', 0)
dup_rate = 100 * dup_cnt / (dup_cnt + unique) if (dup_cnt + unique) > 0 else 0

print('验证 Path C1 后的 module_id 唯一性:')
print(f'  唯一 module_id 数    : {unique}')
print(f'  重复 module_id 数    : {dup_cnt}')
print(f'  重复率              : {dup_rate:.2f}%')
print()
print('变化:')
print(f'  重复组: 46 → {dup_cnt}')
print(f'  消解效果: {46 - dup_cnt} 组')
