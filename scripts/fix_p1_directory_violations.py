#!/usr/bin/env python3
"""
P1 级目录命名违规修复脚本
修复活跃区的关键目录违规
"""

import io
import os
import sys
import shutil
from pathlib import Path

# Windows UTF-8 支持
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"

# P1 级修复: 活跃区的关键目录
P1_RENAMES = [
    # (原路径, 新名称, 说明)
    ("02_FACTOR_LIBRARY/05_BACKTEST", "05_BACKTESTING", "回测引擎目录"),
    ("08_HUMAN_AI_INTERFACE/05_BACKTEST_UI", "05_BT_UI", "回测界面目录"),
    ("09_AUDIT/TEMPLATES", "TEMPLATE_LIBRARY", "审计模板目录"),
]

def rename_directory(old_rel_path: str, new_name: str, description: str) -> dict:
    """重命名单个目录"""
    result = {
        "old_path": old_rel_path,
        "new_name": new_name,
        "description": description,
        "status": "pending",
        "error": None
    }
    
    old_path = DOCS_DIR / old_rel_path
    parent_dir = old_path.parent
    new_path = parent_dir / new_name
    
    # 检查原目录是否存在
    if not old_path.exists():
        result["status"] = "skipped"
        result["error"] = "原目录不存在"
        return result
    
    # 检查新目录是否已存在
    if new_path.exists():
        result["status"] = "failed"
        result["error"] = f"目标目录已存在: {new_name}"
        return result
    
    try:
        # 执行重命名
        old_path.rename(new_path)
        result["status"] = "success"
        print(f"[OK] 已重命名: {old_rel_path} -> {new_name}")
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        print(f"[FAIL] 失败: {old_rel_path} -> {new_name}: {e}")
    
    return result

def main():
    print("=" * 70)
    print("P1 级目录命名违规修复")
    print("=" * 70)
    print()
    
    results = []
    for old_path, new_name, desc in P1_RENAMES:
        result = rename_directory(old_path, new_name, desc)
        results.append(result)
    
    # 统计
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
    
    print()
    print("注意: 请运行以下命令更新文件引用:")
    print("  python scripts/batch_fix_invalid_links_v2.py")

if __name__ == "__main__":
    main()
