#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析 Option B 发现的 46 个重复 module_id
建议是否需要修复
"""
import json, sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path

L1_SCAN = Path('docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.json')

with open(L1_SCAN, encoding='utf-8') as f:
    l1 = json.load(f)

dups = l1['module_ids'].get('duplicates', {})

print("重复 module_id 分析\n" + "="*70)
print()

# Categorize by archive status
archive_groups = {}
active_groups = {}
for mid, files in dups.items():
    archive_count = sum(1 for f in files if '99_ARCHIVE' in f or '06_ARCHIVE' in f or 'DEPRECATED' in f)
    if archive_count > 0:
        archive_groups[mid] = (files, archive_count)
    else:
        active_groups[mid] = files

print(f"📊 重复 module_id 分布:")
print(f"  总重复组数        : {len(dups)}")
print(f"  至少含 1 个归档文件: {len(archive_groups)} 组 ({100*len(archive_groups)//len(dups)}%)")
print(f"  全是活跃文件      : {len(active_groups)} 组 ({100*len(active_groups)//len(dups)}%)")
print()

if archive_groups:
    print("🗂️  含归档的重复组（可安全消解）:")
    for mid, (files, arch_cnt) in sorted(archive_groups.items(), key=lambda x: -x[1][1])[:10]:
        print(f"\n  module_id: '{mid}'")
        print(f"    总文件数  : {len(files)}")
        print(f"    归档文件  : {arch_cnt}")
        print(f"    活跃文件  : {len(files) - arch_cnt}")
        for f in files:
            is_arch = '🗃️ ARCHIVE' if ('99_ARCHIVE' in f or '06_ARCHIVE' in f or 'DEPRECATED' in f) else '✅ ACTIVE '
            print(f"      {is_arch}  {f}")

if active_groups:
    print()
    print("⚠️  全活跃重复组（需人工审查）:")
    for mid, files in sorted(active_groups.items(), key=lambda x: -len(x[1]))[:5]:
        print(f"\n  module_id: '{mid}'")
        print(f"    文件数: {len(files)}")
        for f in files:
            print(f"      - {f}")

print()
print("="*70)
print("💡 建议:")
print()
print("1. 含 ARCHIVE 的 35 组：")
print("   → 可安全消解：保留活跃版本，删除或重新命名归档版本的 module_id")
print()
print("2. 全活跃的 11 组：")
print("   → 需人工审查：判断是否真的需要两个不同路径下的重复 ID")
print()
print("建议优先级：")
print("  ① 消解含 ARCHIVE 的 35 组（自动消解）→ Haiku 4.5")
print("  ② 人工审查全活跃的 11 组（高优先级）→ Sonnet 4.6")
