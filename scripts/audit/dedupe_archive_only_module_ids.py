#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
消解 13 组 Archive-Archive 重复 module_id
策略：保留较新的归档版本，删除较旧版本的 module_id（改为 _DELETED 标记）
或标记为 DEPRECATED
"""
import json, sys, io, re
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
from datetime import datetime, timezone

REPO = Path(".")
L1_SCAN = REPO / "docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.json"

with open(L1_SCAN, encoding="utf-8") as f:
    l1 = json.load(f)

dups = l1["module_ids"].get("duplicates", {})

# 筛选 Archive-only 重复组
archive_only = {}
for mid, files in dups.items():
    is_all_archive = all(
        any(x in f.lower() for x in ['99_archive', '06_archive', 'deprecated'])
        for f in files
    )
    if is_all_archive:
        archive_only[mid] = files

print("消解 Archive-Archive 重复 module_id\n" + "="*70)
print(f"共 {len(archive_only)} 组 Archive-only 重复\n")

# 策略：按文件名日期排序，保留最新，标记其他为 DEPRECATED
def extract_date_from_path(path_str):
    """从路径中提取日期（_YYYYMMDD_ 格式）"""
    match = re.search(r"_(\d{8})_", path_str)
    return match.group(1) if match else "0000-00-00"

results = []
for mid, files in sorted(archive_only.items()):
    # 按日期排序，最新的放在最后
    files_with_dates = [(f, extract_date_from_path(f)) for f in files]
    files_with_dates.sort(key=lambda x: x[1])
    
    # 保留最新版本，其他标记为 DEPRECATED
    canonical = files_with_dates[-1][0]
    to_deprecate = [f for f, _ in files_with_dates[:-1]]
    
    for fpath in to_deprecate:
        p = REPO / fpath
        if not p.exists():
            results.append({
                "module_id": mid,
                "file": fpath,
                "status": "SKIP",
                "reason": "file_not_found"
            })
            continue
        
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
            
            # 在 module_id 行后添加 status: DEPRECATED 注释
            new_content = re.sub(
                rf"(module_id:\s*['\"]?{re.escape(mid)}['\"]?)",
                rf"\1\n# [DEPRECATED] Archive duplicate - canonical version in {canonical}",
                content,
                count=1,
                flags=re.IGNORECASE | re.MULTILINE
            )
            
            # 也可选择改 status 字段
            if "status:" in new_content:
                new_content = re.sub(
                    r"(status:\s*)(\w+)",
                    r"\1DEPRECATED",
                    new_content,
                    count=1,
                    flags=re.MULTILINE
                )
            
            p.write_text(new_content, encoding="utf-8")
            
            results.append({
                "module_id": mid,
                "file": fpath,
                "status": "MARKED_DEPRECATED",
                "canonical": canonical
            })
            
        except Exception as e:
            results.append({
                "module_id": mid,
                "file": fpath,
                "status": "ERROR",
                "reason": str(e)
            })

# 显示结果
for i, (mid, files) in enumerate(sorted(archive_only.items()), 1):
    print(f"{i}. module_id: '{mid}'")
    for r in results:
        if r["module_id"] == mid and r["status"] == "MARKED_DEPRECATED":
            print(f"   ❌ {r['file']} → DEPRECATED")
            print(f"      (canonical: {Path(r['canonical']).name})")
    print()

# 统计
marked = sum(1 for r in results if r["status"] == "MARKED_DEPRECATED")
errors = sum(1 for r in results if r["status"] == "ERROR")
skipped = sum(1 for r in results if r["status"] == "SKIP")

print("="*70)
print(f"完成: {marked} 个文件标记为 DEPRECATED")
print(f"      {errors} 个文件出错")
print(f"      {skipped} 个文件跳过")

# 保存报告
ts = datetime.now(timezone.utc).strftime("%Y%m%d")
report_path = REPO / "docs/09_AUDIT/STATE" / f"DEDUPE_ARCHIVE_ONLY_MODULEIDS_{ts}.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump({
        "timestamp": ts,
        "total_duplicate_groups": len(archive_only),
        "marked_deprecated": marked,
        "errors": errors,
        "skipped": skipped,
        "results": results
    }, f, indent=2, ensure_ascii=False)

print(f"报告: {report_path.relative_to(REPO)}")
