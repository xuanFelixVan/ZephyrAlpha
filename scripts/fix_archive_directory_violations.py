#!/usr/bin/env python3
"""
归档区目录命名违规修复脚本
修复06_ARCHIVE和其他归档区的违规目录
"""

import io
import os
import sys
from pathlib import Path

# Windows UTF-8 支持
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"

# 归档区违规目录修复列表
ARCHIVE_RENAMES = [
    # (原路径, 新名称)
    ("06_ARCHIVE/20260407_old_layer_audit_reports", "20260407_LAYER_AUDIT_REPORTS"),
    ("06_ARCHIVE/20260410_c2_document_metadata_template", "20260410_C2_DOC_METADATA_TMPL"),
    ("06_ARCHIVE/20260410_system_manifest_backup", "20260410_SYSTEM_MANIFEST_BAK"),
    ("06_ARCHIVE/encoding_backups", "ENCODING_ARCHIVES"),
    ("06_ARCHIVE/temporary", "TEMP_HOLDING"),
    ("06_ARCHIVE/temp_pending", "PENDING_ITEMS"),
]

def rename_directory(old_rel_path: str, new_name: str) -> dict:
    """重命名单个目录"""
    result = {
        "old_path": old_rel_path,
        "new_name": new_name,
        "status": "pending",
        "error": None
    }
    
    old_path = DOCS_DIR / old_rel_path
    parent_dir = old_path.parent
    new_path = parent_dir / new_name
    
    if not old_path.exists():
        result["status"] = "skipped"
        result["error"] = "原目录不存在"
        return result
    
    if new_path.exists():
        result["status"] = "failed"
        result["error"] = f"目标目录已存在: {new_name}"
        return result
    
    try:
        old_path.rename(new_path)
        result["status"] = "success"
        print(f"[OK] {old_rel_path} -> {new_name}")
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        print(f"[FAIL] {old_rel_path} -> {new_name}: {e}")
    
    return result

def main():
    print("=" * 70)
    print("归档区目录命名违规修复")
    print("=" * 70)
    print()
    
    results = []
    for old_path, new_name in ARCHIVE_RENAMES:
        result = rename_directory(old_path, new_name)
        results.append(result)
    
    success_count = sum(1 for r in results if r["status"] == "success")
    skip_count = sum(1 for r in results if r["status"] == "skipped")
    fail_count = sum(1 for r in results if r["status"] == "failed")
    
    print()
    print("=" * 70)
    print("修复完成统计")
    print("=" * 70)
    print(f"[OK] 成功: {success_count}")
    print(f"[SKIP] 跳过: {skip_count}")
    print(f"[FAIL] 失败: {fail_count}")
    print()
    
    if fail_count > 0:
        print("失败详情:")
        for r in results:
            if r["status"] == "failed":
                print(f"  - {r['old_path']}: {r['error']}")

if __name__ == "__main__":
    main()
