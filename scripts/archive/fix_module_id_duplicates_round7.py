#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
修复第七轮发现的module_id重复问题

处理的重复组:
1. INDEX_FACTOR_LIBRARY_001 - 2个文件
2. KNOWLEDGE_MANAGEMENT_001 - 2个文件
3. INDEX_99_ARCHIVE_001 - 2个文件
4. INDEX_BEST_PRACTICES_001 - 2个文件
"""

import re
from pathlib import Path


def fix_yaml_module_id(file_path: Path, new_module_id: str) -> bool:
    """修复文件的module_id"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        if not content.startswith("---"):
            print(f"[SKIP] {file_path} - 无YAML头部")
            return False

        lines = content.split("\n")
        new_lines = []
        replaced = False

        for line in lines:
            if line.strip().startswith("module_id:"):
                indent = len(line) - len(line.lstrip())
                indent_str = line[:indent]
                new_lines.append(f"{indent_str}module_id: {new_module_id}")
                replaced = True
            else:
                new_lines.append(line)

        if not replaced:
            print(f"[SKIP] {file_path} - 未找到module_id字段")
            return False

        new_content = "\n".join(new_lines)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"[OK] {file_path} -> {new_module_id}")
        return True

    except Exception as e:
        print(f"[ERROR] {file_path} - {str(e)}")
        return False


def main():
    print("=" * 80)
    print("Module ID重复修复工具 - 第七轮")
    print("=" * 80)
    print()

    fixes = [
        # 1. INDEX_FACTOR_LIBRARY_001
        {
            "file": "docs/02_FACTOR_LIBRARY/INDEX.md",
            "new_id": "INDEX_FACTOR_LIBRARY_MAIN_001"
        },
        {
            "file": "docs/08_KNOWLEDGE/FACTOR_LIBRARY/INDEX.md",
            "new_id": "INDEX_FACTOR_LIBRARY_KNOWLEDGE_001"
        },

        # 2. KNOWLEDGE_MANAGEMENT_001
        {
            "file": "docs/02_FACTOR_LIBRARY/KNOWLEDGE_MANAGEMENT.md",
            "new_id": "KNOWLEDGE_MANAGEMENT_FACTOR_001"
        },
        {
            "file": "docs/10_AI_WORKFLOW/KNOWLEDGE_MANAGEMENT_BLUEPRINT.md",
            "new_id": "KNOWLEDGE_MANAGEMENT_AI_001"
        },

        # 3. INDEX_99_ARCHIVE_001
        {
            "file": "docs/03_TRADING_TACTICS/99_ARCHIVE/INDEX.md",
            "new_id": "INDEX_ARCHIVE_TRADING_001"
        },
        {
            "file": "docs/05_IMPLEMENTATION/99_ARCHIVE/INDEX.md",
            "new_id": "INDEX_ARCHIVE_IMPLEMENTATION_001"
        },

        # 4. INDEX_BEST_PRACTICES_001
        {
            "file": "docs/05_IMPLEMENTATION/07_OPERATIONS/knowledge_base/best_practices/INDEX.md",
            "new_id": "INDEX_BEST_PRACTICES_OPS_001"
        },
        {
            "file": "docs/08_KNOWLEDGE/BEST_PRACTICES/INDEX.md",
            "new_id": "INDEX_BEST_PRACTICES_KNOWLEDGE_001"
        },
    ]

    success_count = 0
    error_count = 0

    for fix in fixes:
        file_path = Path(fix["file"])
        new_id = fix["new_id"]

        if not file_path.exists():
            print(f"[SKIP] {file_path} - 文件不存在")
            continue

        if fix_yaml_module_id(file_path, new_id):
            success_count += 1
        else:
            error_count += 1

    print()
    print("=" * 80)
    print("修复统计")
    print("=" * 80)
    print(f"成功修复: {success_count}")
    print(f"失败数: {error_count}")
    print()


if __name__ == "__main__":
    main()
