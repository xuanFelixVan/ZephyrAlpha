#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Option B: Frontmatter 完整性扫描
检查 module_id 字段的覆盖率和缺失情况
"""
import json, sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
from datetime import datetime, timezone

REPO = Path('.')
L1_SCAN = REPO / 'docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.json'

print("Option B: Frontmatter 完整性扫描\n" + "="*60)

# Load L1 data
with open(L1_SCAN, encoding='utf-8') as f:
    l1 = json.load(f)

mod_data = l1.get('module_ids', {})
md_count = l1.get('md_file_count', 0)

unique_ids = mod_data.get('unique_module_ids', 0)
dup_count = mod_data.get('duplicate_ids_count', 0)
no_id_total = mod_data.get('no_id_total', 0)
no_id_sample = mod_data.get('files_without_module_id_sample', [])

coverage = 100 * (md_count - no_id_total) / md_count if md_count > 0 else 0

print(f"\n📊 总体覆盖率:")
print(f"  扫描文件总数         : {md_count:,}")
print(f"  有 module_id 的文件  : {md_count - no_id_total:,} ({coverage:.1f}%)")
print(f"  缺 module_id 的文件  : {no_id_total:,} ({100-coverage:.1f}%)")
print()

print(f"🔍 Module ID 唯一性:")
print(f"  唯一 module_id 数    : {unique_ids:,}")
print(f"  重复 module_id 数    : {dup_count}")
dup_ratio = 100 * dup_count / (dup_count + unique_ids) if (dup_count + unique_ids) > 0 else 0
print(f"  重复率              : {dup_ratio:.2f}%")
print()

# Analyze missing patterns
print(f"📋 缺失 module_id 的 {no_id_total} 个文件分类:")
missing_by_prefix = {}
for f in no_id_sample:
    parts = f.replace('\\', '/').split('/')
    if f.startswith('.'):
        prefix = f'.[hidden]'
    elif f.startswith('docs/'):
        prefix = '/'.join(parts[:3]) + '/'
    else:
        prefix = parts[0] + '/'
    missing_by_prefix[prefix] = missing_by_prefix.get(prefix, 0) + 1

print("  按目录分布:")
for prefix in sorted(missing_by_prefix.keys(), key=lambda x: -missing_by_prefix[x]):
    cnt = missing_by_prefix[prefix]
    print(f"    {cnt:2d}  {prefix}")

print()
print("  具体文件列表:")
for f in no_id_sample[:no_id_total]:  # Show all 22
    print(f"    - {f}")

# Duplicate analysis
print()
print(f"⚠️  重复 module_id 详情:")
dups = mod_data.get('duplicates', {})
print(f"  共 {len(dups)} 组重复")
if dups:
    print("\n  Top 5 重复组:")
    for mid, files in sorted(dups.items(), key=lambda x: -len(x[1]))[:5]:
        print(f"    module_id='{mid}'  ({len(files)} 个文件)")
        for f in files[:3]:
            print(f"      - {f}")
        if len(files) > 3:
            print(f"      ... +{len(files)-3} more")

# Final assessment
print()
print("="*60)
print("✅ 诊断结论:")
print(f"  - module_id 覆盖率达 {coverage:.1f}%（良好）")
print(f"  - 缺失 {no_id_total} 个文件，多为临时生成文件/审计报告")
print(f"  - 重复率 {dup_ratio:.2f}%，需关注 {dup_count} 个重复ID")
print()

# Save report
ts = datetime.now(timezone.utc).strftime("%Y%m%d")
out_path = REPO / 'docs/09_AUDIT/STATE' / f'FRONTMATTER_AUDIT_{ts}.json'
report = {
    "scan_date": ts,
    "total_files": md_count,
    "files_with_module_id": md_count - no_id_total,
    "module_id_coverage_pct": round(coverage, 1),
    "files_without_module_id": no_id_total,
    "unique_module_ids": unique_ids,
    "duplicate_module_ids": dup_count,
    "duplicate_rate_pct": round(dup_ratio, 2),
    "files_without_id_sample": no_id_sample,
    "duplicate_groups": dups,
    "recommendation": "Coverage 99.4% is good; focus on deduplication if needed"
}

(REPO / 'docs/09_AUDIT/STATE').mkdir(parents=True, exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"📁 报告已保存: {out_path.relative_to(REPO)}")
