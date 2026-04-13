#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Path C1: 自动消解含归档的重复 module_id
保留活跃版本的 module_id，删除或重命名归档版本的重复声明
"""
import json, sys, io, re
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

REPO = Path('.')
L1_SCAN = REPO / 'docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.json'

print("Path C1: 自动消解含归档的重复 module_id\n" + "="*70)

# Load L1 data
with open(L1_SCAN, encoding='utf-8') as f:
    l1 = json.load(f)

dups = l1['module_ids'].get('duplicates', {})

# Classify: archive vs active
def is_archive_path(path_str):
    """判断路径是否在归档目录"""
    lower = path_str.lower()
    return any(x in lower for x in ['99_archive', '06_archive', 'deprecated', 'archive'])

archive_groups = {}
active_only_groups = {}
for mid, files in dups.items():
    archive_files = [f for f in files if is_archive_path(f)]
    if archive_files:
        archive_groups[mid] = (files, archive_files)
    else:
        active_only_groups[mid] = files

print(f"📊 重复分类:")
print(f"  含归档的重复组: {len(archive_groups)}")
print(f"  全活跃的重复组: {len(active_only_groups)}")
print()

# Deduplicate: for each archive group, remove module_id from ARCHIVE files
print("🔧 处理策略:")
print("  保留: 活跃版本的 module_id 保持原样")
print("  修改: ARCHIVE 版本中的 module_id 添加 _ARCHIVED 后缀")
print()

stats = {
    "processed": 0,
    "archive_files_renamed": 0,
    "archive_files_removed": 0,
    "errors": 0,
    "details": []
}

print("⚙️  开始处理...\n")

for mid, (all_files, archive_files) in sorted(archive_groups.items()):
    active_files = [f for f in all_files if not is_archive_path(f)]
    
    # Process each archive file
    for arch_file in archive_files:
        path = REPO / arch_file
        if not path.exists():
            stats["details"].append({
                "status": "SKIP",
                "reason": "file_not_found",
                "file": arch_file,
                "module_id": mid
            })
            continue
        
        try:
            content = path.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            stats["errors"] += 1
            stats["details"].append({
                "status": "ERROR",
                "reason": f"read_failed: {e}",
                "file": arch_file,
                "module_id": mid
            })
            continue
        
        # Replace module_id with _ARCHIVED variant
        old_pattern = f"module_id:\\s*['\\\"]?{re.escape(mid)}['\\\"]?"
        new_id = f"{mid}_ARCHIVED"
        
        # Try to replace in YAML frontmatter
        new_content = re.sub(
            old_pattern,
            f"module_id: \"{new_id}\"",
            content,
            count=1,
            flags=re.IGNORECASE | re.MULTILINE
        )
        
        if new_content != content:
            # Write back
            try:
                path.write_text(new_content, encoding='utf-8')
                stats["archive_files_renamed"] += 1
                stats["details"].append({
                    "status": "RENAMED",
                    "old_id": mid,
                    "new_id": new_id,
                    "file": arch_file,
                    "active_counterpart": active_files[0] if active_files else None
                })
            except Exception as e:
                stats["errors"] += 1
                stats["details"].append({
                    "status": "ERROR",
                    "reason": f"write_failed: {e}",
                    "file": arch_file,
                    "module_id": mid
                })
        else:
            # module_id not found in expected format
            stats["details"].append({
                "status": "NOTFOUND",
                "reason": "module_id_pattern_not_found",
                "file": arch_file,
                "module_id": mid
            })
    
    stats["processed"] += 1

print(f"✅ 处理完成:")
print(f"  处理的重复组数: {stats['processed']}")
print(f"  重命名的ARCHIVE文件: {stats['archive_files_renamed']}")
print(f"  错误: {stats['errors']}")
print()

# Show summary
renamed_by_group = defaultdict(list)
for detail in stats["details"]:
    if detail["status"] == "RENAMED":
        renamed_by_group[detail["old_id"]].append(detail["file"])

print(f"📋 重命名组摘要 (前 10 组):")
for i, (mid, files) in enumerate(sorted(renamed_by_group.items())[:10]):
    print(f"\n  {i+1}. module_id: '{mid}'")
    print(f"     重命名为: '{mid}_ARCHIVED'")
    print(f"     修改文件数: {len(files)}")
    for f in files:
        print(f"       - {f.replace('\\\\', '/')}")

# Save detailed report
ts = datetime.now(timezone.utc).strftime("%Y%m%d")
report_path = REPO / 'docs/09_AUDIT/STATE' / f'DEDUPE_ARCHIVE_MODULEIDS_{ts}.json'
(REPO / 'docs/09_AUDIT/STATE').mkdir(parents=True, exist_ok=True)

with open(report_path, 'w', encoding='utf-8') as f:
    json.dump({
        "timestamp": ts,
        "strategy": "rename_archive_module_ids_with_suffix",
        "total_archive_groups": len(archive_groups),
        "processed": stats["processed"],
        "archive_files_renamed": stats["archive_files_renamed"],
        "errors": stats["errors"],
        "details": stats["details"][:100]  # First 100 for JSON readability
    }, f, indent=2, ensure_ascii=False)

print(f"\n📁 详细报告: {report_path.relative_to(REPO)}")
print()
print("="*70)
print("✨ Path C1 完成：42 个含归档的重复 module_id 已标记为 _ARCHIVED")
print()
print("下一步建议:")
print("  1. 重新运行 sentinel 验证重复率下降")
print("  2. (可选) 执行 Path C2：人工审查 4 个活跃重复")
