#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
预提交钩子：检查索引文件完整性。
当前版本仅检查指定目录下是否存在 INDEX.md，并验证其基本格式。
后续可扩展为检查索引条目与实际文件的对应关系。
"""

import os
import sys
from pathlib import Path

# 需要检查索引的目录列表（相对路径）
DIRS_TO_CHECK = [
    "docs",
    "docs/00_OVERVIEW",
    "docs/00_RESOURCES",
    "docs/01_FRAMEWORK",
    "docs/02_FACTOR_LIBRARY",
    "docs/03_TRADING_TACTICS",
    "docs/04_EXECUTION",
    "docs/05_IMPLEMENTATION",
    "docs/06_CONSTRUCTION_DOCS",
    "docs/07_RESEARCH",
    "docs/08_HUMAN_AI_INTERFACE",
    "docs/08_KNOWLEDGE",
    "docs/09_AUDIT",
    "docs/10_AI_WORKFLOW",
    "docs/10_GOVERNANCE_COMPLIANCE",
    "docs/11_STRATEGIC_DECISION",
]

def check_index_existence(dir_path: Path) -> list:
    """检查目录下是否有 INDEX.md，如果没有则返回错误信息。"""
    errors = []
    index_file = dir_path / "INDEX.md"
    if not index_file.exists():
        errors.append(f"目录 {dir_path} 缺少 INDEX.md 文件")
    else:
        # 可选：检查文件是否为空或仅包含空白行
        content = index_file.read_text(encoding="utf-8", errors="ignore").strip()
        if not content:
            errors.append(f"INDEX.md 文件为空: {index_file}")
        # 可以进一步检查是否有列表条目，但暂时跳过
    return errors

def main():
    errors = []
    for dir_rel in DIRS_TO_CHECK:
        dir_path = Path(dir_rel)
        if dir_path.exists() and dir_path.is_dir():
            errors.extend(check_index_existence(dir_path))
        # 如果目录不存在，则跳过（可能是项目结构差异）
    
    if errors:
        print("❌ 索引完整性检查失败：")
        for err in errors:
            print(f"   - {err}")
        print("\n请补充缺失的 INDEX.md 文件，或更新现有索引内容。")
        sys.exit(1)
    else:
        print("✅ 索引完整性检查通过。")
        sys.exit(0)

if __name__ == "__main__":
    main()