#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
补齐缺失 module_id 的 22 个文件
为临时报告、快照和过期文件添加 module_id frontmatter
"""
import json, sys, io, re, uuid
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
from datetime import datetime, timezone

REPO = Path(".")
L1_SCAN = REPO / "docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.json"

with open(L1_SCAN, encoding="utf-8") as f:
    l1 = json.load(f)

no_id_files = l1["module_ids"].get("files_without_module_id_sample", [])

print("补齐缺失 module_id 的文件\n" + "="*70)
print(f"共 {len(no_id_files)} 个文件需要补齐\n")

# 规则：根据文件路径和用途分配 module_id
def generate_module_id(file_path):
    """根据文件路径生成合适的 module_id"""
    p = file_path.lower()
    basename = Path(file_path).stem
    
    # 临时报告
    if "reports/" in p or "report" in p:
        return f"AUTO_REPORT_{basename.upper()}"
    
    # 审计状态快照
    if "audit" in p and "state" in p:
        return f"AUDIT_STATE_{basename.upper()}"
    
    # 自动生成日志
    if "analysis" in p or "generated" in p:
        return f"AUTO_GENERATED_{basename.upper()}"
    
    # 顶层索引
    if basename == "index":
        return f"INDEX_{Path(file_path).parent.name.upper()}"
    
    # 根目录文件
    if "/" not in file_path:
        return f"ROOT_{basename.upper()}"
    
    # 默认格式
    return f"AUTO_{basename.upper()}"

def add_module_id_to_file(file_path):
    """为文件添加 module_id frontmatter"""
    p = REPO / file_path
    
    if not p.exists():
        return {"file": file_path, "status": "SKIP", "reason": "file_not_found"}
    
    try:
        content = p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"file": file_path, "status": "ERROR", "reason": f"read_error: {e}"}
    
    # 检查是否已有 frontmatter
    if content.startswith("---"):
        fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if fm_match and "module_id" in fm_match.group(1):
            return {"file": file_path, "status": "SKIP", "reason": "already_has_module_id"}
        
        # 有 frontmatter 但没 module_id，插入到第一个 ---之后
        lines = content.split("\n")
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                mid = generate_module_id(file_path)
                lines.insert(i, f"module_id: {mid}")
                new_content = "\n".join(lines)
                break
        else:
            # frontmatter 未正确关闭，跳过
            return {"file": file_path, "status": "SKIP", "reason": "malformed_frontmatter"}
    else:
        # 无 frontmatter，添加新的
        mid = generate_module_id(file_path)
        new_content = f"---\nmodule_id: {mid}\nstatus: Auto-generated\ngenerated_date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n---\n\n{content}"
    
    try:
        p.write_text(new_content, encoding="utf-8")
        mid = generate_module_id(file_path)
        return {
            "file": file_path,
            "status": "ADDED",
            "module_id": mid
        }
    except Exception as e:
        return {"file": file_path, "status": "ERROR", "reason": f"write_error: {e}"}

# 处理所有缺失文件
results = []
for fpath in no_id_files:
    result = add_module_id_to_file(fpath)
    results.append(result)
    status = result.get("status", "?")
    if status == "ADDED":
        print(f"[ADDED]  {fpath}")
        print(f"         module_id: {result.get('module_id')}")
    elif status == "SKIP":
        print(f"[SKIP]   {fpath}  ({result.get('reason')})")
    elif status == "ERROR":
        print(f"[ERROR]  {fpath}  ({result.get('reason')})")

# 统计
added = sum(1 for r in results if r["status"] == "ADDED")
skipped = sum(1 for r in results if r["status"] == "SKIP")
errors = sum(1 for r in results if r["status"] == "ERROR")

print()
print("="*70)
print(f"完成: {added} 个文件补齐 module_id")
print(f"      {skipped} 个文件跳过")
print(f"      {errors} 个文件出错")

# 保存报告
ts = datetime.now(timezone.utc).strftime("%Y%m%d")
report_path = REPO / "docs/09_AUDIT/STATE" / f"ADD_MISSING_MODULEIDS_{ts}.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump({
        "timestamp": ts,
        "total_files": len(no_id_files),
        "added": added,
        "skipped": skipped,
        "errors": errors,
        "results": results
    }, f, indent=2, ensure_ascii=False)

print(f"报告: {report_path.relative_to(REPO)}")
