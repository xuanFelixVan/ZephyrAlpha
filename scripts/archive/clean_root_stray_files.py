#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
根目录杂散文档清理脚本。

扫描根目录，识别不符合R1层定义的杂散文档文件，并将它们迁移到合适的目录。
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Optional

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

# 目录映射：文件名/模式 -> 目标目录
# 优先匹配完全文件名，然后匹配关键词
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

def get_target_directory(filename: str) -> Optional[str]:
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

def ensure_directory_exists(dirpath: str) -> None:
    """确保目录存在，若不存在则创建。"""
    Path(dirpath).mkdir(parents=True, exist_ok=True)

def move_file(src: str, dst_dir: str, dry_run: bool = True) -> bool:
    """移动文件到目标目录，保留Git历史（如果已被跟踪）。"""
    dst = os.path.join(dst_dir, os.path.basename(src))
    if dry_run:
        print(f"[模拟] 移动 {src} -> {dst}")
        return True
    try:
        # 尝试使用 git mv（如果文件在Git中）
        result = subprocess.run(["git", "mv", src, dst], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[成功] git mv {src} -> {dst}")
            return True
        else:
            # 回退到 shutil.move
            shutil.move(src, dst)
            print(f"[成功] shutil.move {src} -> {dst}")
            return True
    except Exception as e:
        print(f"[错误] 移动 {src} 失败: {e}")
        return False

def update_index_file(target_dir: str, filename: str, dry_run: bool = True) -> None:
    """在目标目录的 INDEX.md 中添加条目（如果存在）。"""
    index_path = os.path.join(target_dir, "INDEX.md")
    if not os.path.exists(index_path):
        print(f"[信息] 目标目录下没有 INDEX.md，跳过索引更新")
        return
    # 简单追加一行（实际可能需要更智能的插入）
    entry = f"- [{filename}](./{filename})\n"
    if dry_run:
        print(f"[模拟] 将在 {index_path} 中添加条目: {entry.strip()}")
        return
    try:
        with open(index_path, "a", encoding="utf-8") as f:
            f.write(entry)
        print(f"[成功] 更新索引 {index_path}")
    except Exception as e:
        print(f"[错误] 更新索引失败: {e}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="清理根目录杂散文档")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="模拟运行，不实际移动文件（默认）")
    parser.add_argument("--execute", action="store_true",
                        help="实际执行移动操作（禁用 dry-run）")
    args = parser.parse_args()
    dry_run = not args.execute

    if dry_run:
        print("=== 模拟运行模式（不实际移动文件） ===")
    else:
        print("=== 执行模式（将实际移动文件） ===")

    root = Path(".").resolve()
    stray_files = []
    for item in root.iterdir():
        if not item.is_file():
            continue  # 忽略目录
        filename = item.name
        if is_allowed(filename):
            continue
        target = get_target_directory(filename)
        if target is None:
            # 没有匹配的映射，可能是未知的杂散文件
            print(f"[警告] 未分类的杂散文件: {filename}（未指定目标目录）")
            continue
        stray_files.append((str(item), target))

    if not stray_files:
        print("没有发现需要迁移的杂散文件。")
        return

    print(f"发现 {len(stray_files)} 个需要迁移的文件:")
    for src, target in stray_files:
        print(f"  {src} -> {target}")

    # 确认（仅在实际执行时）
    if not dry_run:
        response = input("是否继续移动？(y/N): ")
        if response.lower() != "y":
            print("取消操作。")
            return

    # 执行迁移
    moved = []
    for src, target in stray_files:
        ensure_directory_exists(target)
        if move_file(src, target, dry_run=dry_run):
            moved.append((src, target))
            update_index_file(target, os.path.basename(src), dry_run=dry_run)

    # 输出摘要
    print("\n=== 迁移摘要 ===")
    if dry_run:
        print("（模拟运行，未实际移动）")
    for src, target in moved:
        print(f"{src} -> {target}")
    print(f"总计 {len(moved)} 个文件已处理。")

if __name__ == "__main__":
    main()