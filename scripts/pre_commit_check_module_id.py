#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
Git pre-commit hook: module_id重复检查

功能:
- 在Git提交前自动检查module_id重复
- 如果发现重复，阻止提交并提示

安装方法:
    cp scripts/pre_commit_check_module_id.py .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
"""

import os
import sys
from pathlib import Path
from collections import defaultdict


def check_module_id_duplicates():
    """检查module_id重复"""
    docs_root = Path("docs")
    if not docs_root.exists():
        print("[INFO] docs目录不存在，跳过检查")
        return True

    module_id_map = defaultdict(list)

    # 扫描所有.md文件
    for root, dirs, files in os.walk(docs_root):
        # 排除特定目录
        if any(exclude in root for exclude in ["audit_state", "archive", "__pycache__", ".git"]):
            continue

        for file in files:
            if not file.endswith(".md"):
                continue

            file_path = Path(root) / file
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("module_id:"):
                            module_id = line.split(":", 1)[1].strip()
                            module_id_map[module_id].append(str(file_path))
                            break
            except Exception:
                pass

    # 检查重复
    duplicates = {k: v for k, v in module_id_map.items() if len(v) > 1}

    if duplicates:
        print("\n[ERROR] 发现重复的module_id，提交被阻止！\n")
        print("=" * 80)
        for module_id, files in duplicates.items():
            print(f"\n重复的module_id: {module_id}")
            print(f"涉及文件数: {len(files)}")
            for file in files:
                print(f"  - {file}")
        print("\n" + "=" * 80)
        print("\n请修复以上问题后重新提交。")
        print("建议:")
        print("  1. 为重复的文档分配不同的module_id")
        print("  2. 如果是归档文档，使用ARCHIVED_前缀")
        print("  3. 参考docs/09_AUDIT/STATE/MODULE_ID_REGISTRY.md\n")
        return False

    print("[OK] module_id检查通过")
    return True


if __name__ == "__main__":
    success = check_module_id_duplicates()
    sys.exit(0 if success else 1)
