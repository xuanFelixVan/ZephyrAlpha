#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
Module ID重复手动修复脚本

专门处理剩余的5组特殊情况:
1. BENCHMARK_MANAGEMENT_BLUEPRINT_001 - 2个文件
2. FRAMEWORK_001_L01_DOC - 3个文件
3. MODULE_RESPONSIBILITY_BOUNDARIES_001 - 2个文件
4. MARKET_REGIME_DETECTION_001 - 2个文件
5. {MODULE_ID} - 2个文件
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
    print("Module ID重复手动修复工具")
    print("=" * 80)
    print()

    fixes = [
        # 1. BENCHMARK_MANAGEMENT_BLUEPRINT_001
        {
            "file": "docs/01_FRAMEWORK/BENCHMARK_MANAGEMENT_BLUEPRINT.md",
            "new_id": "BENCHMARK_MANAGEMENT_FRAMEWORK_001"
        },
        {
            "file": "docs/11_STRATEGIC_DECISION/BENCHMARK_MANAGEMENT_BLUEPRINT.md",
            "new_id": "BENCHMARK_MANAGEMENT_STRATEGIC_001"
        },

        # 2. FRAMEWORK_001_L01_DOC - 修复上一轮产生的新重复
        {
            "file": "docs/01_FRAMEWORK/DOCUMENT_CREATION_CHECKLIST.md",
            "new_id": "DOCUMENT_CREATION_CHECKLIST_001"
        },
        {
            "file": "docs/01_FRAMEWORK/DOCUMENT_CREATION_REVIEW_PROCESS.md",
            "new_id": "DOCUMENT_CREATION_REVIEW_PROCESS_001"
        },
        {
            "file": "docs/01_FRAMEWORK/DOCUMENT_RESPONSIBILITY_BOUNDARIES.md",
            "new_id": "DOCUMENT_RESPONSIBILITY_BOUNDARIES_001"
        },

        # 3. MODULE_RESPONSIBILITY_BOUNDARIES_001
        {
            "file": "docs/01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md",
            "new_id": "MODULE_RESPONSIBILITY_BOUNDARIES_FRAMEWORK_001"
        },
        {
            "file": "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MODULE_RESPONSIBILITY_BOUNDARIES_BLUEPRINT.md",
            "new_id": "MODULE_RESPONSIBILITY_BOUNDARIES_001"
        },

        # 4. MARKET_REGIME_DETECTION_001
        {
            "file": "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MARKET_REGIME_DETECTION_BLUEPRINT.md",
            "new_id": "MARKET_REGIME_DETECTION_001"
        },
        {
            "file": "docs/11_STRATEGIC_DECISION/MARKET_REGIME_BLUEPRINT.md",
            "new_id": "MARKET_REGIME_STRATEGIC_001"
        },

        # 5. {MODULE_ID} - 模板文件，需要特殊处理
        {
            "file": "docs/09_AUDIT/STANDARDS/DOC_GOVERNANCE_MECHANISM.md",
            "new_id": "DOC_GOVERNANCE_MECHANISM_001"
        },
        {
            "file": "docs/09_AUDIT/WORKFLOWS/DOC_CREATION_WORKFLOW.md",
            "new_id": "DOC_CREATION_WORKFLOW_001"
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
