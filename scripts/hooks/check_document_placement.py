#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
预提交钩子：检查文档放置位置是否符合 DOCUMENT_REPOSITORY_LAYOUT_STANDARD 标准。
当前版本仅检查根目录下的杂散文档文件，后续可扩展为全库扫描。
"""

import os
import sys
from pathlib import Path

# 允许保留在根目录的文件列表（支持通配符）
ALLOWED_PATTERNS = [
    # 配置文件
    ".editorconfig",
    ".env.*",
    ".gitignore",
    ".pre-commit-config.yaml",
    "pyproject.toml",
    # 项目元数据
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    # 依赖文件
    "requirements.txt",
    "requirements_extensions.txt",
    # 入口脚本
    "run_api.py",
    # 其他必要的项目根级别文件（可根据需要扩展）
]

# 目录映射：文件名/模式 -> 目标目录（用于识别错放的文件）
MAPPINGS = [
    # 已知文件精确匹配
    ("AI_CODE_EDITORS_COMPLETE_GUIDE.md", "docs/08_KNOWLEDGE_BASE/01_TECHNICAL_KNOWLEDGE/"),
    ("encoding_check_report.txt", "docs/09_AUDIT/REPORTS/"),
    ("CHANGELOG.md", "docs/00_OVERVIEW/"),
    ("ZephyrAlpha_Architecture.json", "docs/01_FRAMEWORK/"),
    # 基于关键词的匹配（支持通配符）
    ("*AI*", "docs/08_KNOWLEDGE_BASE/01_TECHNICAL_KNOWLEDGE/"),
    ("*指南*", "docs/08_KNOWLEDGE_BASE/01_TECHNICAL_KNOWLEDGE/"),
    ("*GUIDE*", "docs/08_KNOWLEDGE_BASE/01_TECHNICAL_KNOWLEDGE/"),
    ("*报告*", "docs/09_AUDIT/REPORTS/"),
    ("*report*", "docs/09_AUDIT/REPORTS/"),
    ("*检查*", "docs/09_AUDIT/REPORTS/"),
    ("*check*", "docs/09_AUDIT/REPORTS/"),
    ("*CHANGELOG*", "docs/00_OVERVIEW/"),
    ("*变更日志*", "docs/00_OVERVIEW/"),
    ("*架构*", "docs/01_FRAMEWORK/"),
    ("*architecture*", "docs/01_FRAMEWORK/"),
]

def matches_pattern(filename: str, pattern: str) -> bool:
    """简单通配符匹配，仅支持前缀/后缀通配符 *。"""
    if pattern.startswith("*") and pattern.endswith("*"):
        return pattern[1:-1] in filename
    elif pattern.startswith("*"):
        return filename.endswith(pattern[1:])
    elif pattern.endswith("*"):
        return filename.startswith(pattern[:-1])
    else:
        return filename == pattern

def is_allowed(filename: str) -> bool:
    """检查文件是否在允许列表中。"""
    for pattern in ALLOWED_PATTERNS:
        if matches_pattern(filename, pattern):
            return True
    return False

def get_target_directory(filename: str):
    """根据映射返回目标目录，如果没有匹配则返回 None。"""
    # 首先精确匹配
    for pattern, target in MAPPINGS:
        if pattern == filename:
            return target
    # 然后通配符匹配
    for pattern, target in MAPPINGS:
        if "*" in pattern and matches_pattern(filename, pattern):
            return target
    return None

def check_root_stray_files():
    """检查根目录下的杂散文档文件，返回错误列表。"""
    root = Path(".").resolve()
    errors = []
    for item in root.iterdir():
        if not item.is_file():
            continue  # 忽略目录
        filename = item.name
        if is_allowed(filename):
            continue
        target = get_target_directory(filename)
        if target is not None:
            errors.append((filename, target))
        else:
            # 没有匹配的映射，可能是未知的杂散文件
            errors.append((filename, None))
    return errors

def main():
    errors = check_root_stray_files()
    if errors:
        print("❌ 发现以下杂散文档文件，应移动到指定目录：")
        for filename, target in errors:
            if target:
                print(f"   {filename} -> {target}")
            else:
                print(f"   {filename} (未定义目标目录，请更新检查脚本)")
        print("\n请运行 scripts/clean_root_stray_files.py --execute 自动迁移，或手动移动文件。")
        sys.exit(1)
    else:
        print("✅ 根目录文档放置检查通过。")
        sys.exit(0)

if __name__ == "__main__":
    main()
