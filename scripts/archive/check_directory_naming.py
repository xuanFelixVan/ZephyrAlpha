#!/usr/bin/env python3
"""目录命名规范检查脚本

用途: 检查 docs/ 下所有目录的命名是否符合规范
功能:
  - 检测目录命名格式违规
  - 检测禁止关键词（temp/tmp/backup/old等）
  - 检测目录深度超限
  - 支持 pre-commit 集成

使用:
  python scripts/check_directory_naming.py              # 全量检查
  python scripts/check_directory_naming.py --staged     # 只检查变更的目录
  python scripts/check_directory_naming.py --verbose    # 详细输出

返回码:
  0 - 全部通过
  1 - 发现违规

作者: 外部审计安全评估后新增
日期: 2026-04-13
"""

from __future__ import annotations

import io
import os
import re
import sys
from pathlib import Path

# Windows UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

DOCS_ROOT = Path(__file__).resolve().parent.parent / "docs"

# 命名规范配置
NAMING_RULES = {
    # Layer主目录: 数字前缀+大写下划线
    "layer_dirs": re.compile(r"^\d{2}_[A-Z_]+$"),
    # 归档目录: XX_ARCHIVE
    "archive_dirs": re.compile(r"^\d{2}_ARCHIVE$"),
    # 知识目录: XX_KNOWLEDGE 或 XX_KNOWLEDGE_BASE
    "knowledge_dirs": re.compile(r"^\d{2}_KNOWLEDGE(_BASE)?$"),
    # 子目录: 小写下划线 或 全大写下划线
    "sub_dirs": re.compile(r"^[a-z0-9_]+|[A-Z0-9_]+$"),
}

# 禁止的关键词（大小写不敏感）
PROHIBITED_KEYWORDS = {
    "temp", "tmp", "backup", "old", "test", "new",
    "draft", "copy", "副本", "备份", "临时", "测试",
    "untitled", "无标题", "新建文件夹"
}

# 最大目录深度（从 docs/ 开始）
MAX_DEPTH = 6


class DirectoryNamingChecker:
    """目录命名规范检查器"""

    def __init__(self, docs_root: Path = DOCS_ROOT, verbose: bool = False):
        self.docs_root = docs_root
        self.verbose = verbose
        self.violations: list[dict] = []

    def check_all_directories(self) -> bool:
        """检查所有目录，返回是否全部通过"""
        if self.verbose:
            print(f"🔍 扫描目录: {self.docs_root}")
            print("-" * 70)

        for dir_path in self.docs_root.rglob("*"):
            if dir_path.is_dir():
                self._check_single_directory(dir_path)

        return len(self.violations) == 0

    def check_staged_directories(self) -> bool:
        """检查 git 暂存区中涉及的目录"""
        import subprocess

        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
                capture_output=True,
                text=True,
                cwd=self.docs_root.parent,
            )
            staged_files = result.stdout.strip().split("\n") if result.stdout else []
        except subprocess.SubprocessError:
            staged_files = []

        # 提取目录路径
        dirs_to_check = set()
        for file_path in staged_files:
            if file_path.startswith("docs/"):
                full_path = self.docs_root.parent / file_path
                if full_path.is_dir():
                    dirs_to_check.add(full_path)
                elif full_path.parent.is_dir():
                    dirs_to_check.add(full_path.parent)

        for dir_path in dirs_to_check:
            self._check_single_directory(dir_path)

        return len(self.violations) == 0

    def _check_single_directory(self, dir_path: Path) -> None:
        """检查单个目录"""
        dir_name = dir_path.name
        rel_path = dir_path.relative_to(self.docs_root)
        depth = len(rel_path.parts)

        # 1. 检查目录深度
        if depth > MAX_DEPTH:
            self.violations.append({
                "path": str(rel_path),
                "name": dir_name,
                "type": "深度超限",
                "detail": f"当前深度 {depth} 层，超过最大限制 {MAX_DEPTH} 层",
            })
            if self.verbose:
                print(f"❌ [{rel_path}] 深度超限: {depth} > {MAX_DEPTH}")
            return

        # 2. 检查是否为Layer主目录（特殊规则）
        if depth == 1:
            if not (
                NAMING_RULES["layer_dirs"].match(dir_name)
                or NAMING_RULES["archive_dirs"].match(dir_name)
                or NAMING_RULES["knowledge_dirs"].match(dir_name)
            ):
                self.violations.append({
                    "path": str(rel_path),
                    "name": dir_name,
                    "type": "Layer目录命名违规",
                    "detail": f"'{dir_name}' 不符合 Layer 目录命名规范（应为 '数字_大写下划线' 格式）",
                })
                if self.verbose:
                    print(f"❌ [{rel_path}] Layer目录命名违规")
                return

        # 3. 检查禁止关键词
        dir_name_lower = dir_name.lower()
        for keyword in PROHIBITED_KEYWORDS:
            if keyword in dir_name_lower:
                self.violations.append({
                    "path": str(rel_path),
                    "name": dir_name,
                    "type": "禁止关键词",
                    "detail": f"目录名包含禁止词 '{keyword}'",
                })
                if self.verbose:
                    print(f"❌ [{rel_path}] 禁止关键词: {keyword}")
                return

        # 4. 检查子目录命名规范
        if depth > 1:
            if not NAMING_RULES["sub_dirs"].match(dir_name):
                self.violations.append({
                    "path": str(rel_path),
                    "name": dir_name,
                    "type": "子目录命名违规",
                    "detail": f"'{dir_name}' 应使用小写下划线或全大写下划线格式",
                })
                if self.verbose:
                    print(f"❌ [{rel_path}] 子目录命名违规")
                return

        if self.verbose:
            print(f"✅ [{rel_path}] 通过")

    def print_report(self) -> None:
        """打印检查报告"""
        if not self.violations:
            print("\n✅ 所有目录命名符合规范")
            return

        print(f"\n❌ 发现 {len(self.violations)} 个目录命名违规:")
        print("-" * 70)

        for i, v in enumerate(self.violations, 1):
            print(f"\n{i}. [{v['type']}] {v['path']}")
            print(f"   问题: {v['detail']}")

        print("\n" + "-" * 70)
        print("修复建议:")
        print("  1. 使用描述性名称，避免 temp/tmp/backup 等临时性词汇")
        print("  2. Layer主目录使用格式: 数字_大写下划线（如 02_FACTOR_LIBRARY）")
        print("  3. 子目录使用小写下划线（如 config_management）")
        print("  4. 目录深度不超过6层")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="目录命名规范检查",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python check_directory_naming.py --verbose          # 详细检查所有目录
  python check_directory_naming.py --staged           # 只检查暂存区变更
  python check_directory_naming.py --staged --verbose # 详细检查暂存区
        """,
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出模式",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="只检查 git 暂存区中的变更",
    )

    args = parser.parse_args()

    checker = DirectoryNamingChecker(verbose=args.verbose)

    if args.staged:
        passed = checker.check_staged_directories()
    else:
        passed = checker.check_all_directories()

    checker.print_report()

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
