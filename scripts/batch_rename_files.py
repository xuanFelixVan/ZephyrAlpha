#!/usr/bin/env python3

# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
批量文件名规范化脚本。

将文件名统一为小写连字符格式（kebab-case），去除空格和特殊字符，
确保扩展名正确（.md），并保留 Git 历史。

用法：
    python scripts/batch_rename_files.py --dry-run
    python scripts/batch_rename_files.py --execute --pattern "*.md"
    python scripts/batch_rename_files.py --docs-root docs --exclude "**/node_modules/**"

参数：
    --dry-run           只显示分析结果，不执行重命名（默认）
    --execute           实际执行重命名（危险！请先 dry-run）
    --pattern GLOB      文件匹配模式（默认 "**/*.md"）
    --docs-root PATH    docs 根目录（默认 'docs'）
    --exclude GLOB      排除模式（可多次使用）
    --skip-git          不使用 git mv，直接使用 os.rename（不推荐）
    --verbose           输出详细信息
"""

import argparse
import fnmatch
import logging
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Optional

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def normalize_filename(name: str, is_dir: bool = False) -> str:
    """将文件名规范化为小写连字符格式。
    
    规则：
    1. 转换为全小写。
    2. 将下划线、空格替换为连字符。
    3. 删除除连字符、数字、字母、点以外的字符。
    4. 合并连续的连字符。
    5. 确保扩展名 .md 小写（如果是文件）。
    6. 目录名不应包含点（除非是特殊前缀如 .git）。
    
    注意：保留前导数字前缀（如 00_）中的下划线？我们选择保留数字前缀，
    但将下划线替换为连字符（例如 00_governance -> 00-governance）。
    """
    # 分离扩展名
    stem = name
    ext = ''
    if not is_dir and '.' in name:
        stem, ext = os.path.splitext(name)
        ext = ext.lower()
        # 确保 markdown 文件扩展名为 .md
        if ext == '.markdown':
            ext = '.md'
    
    # 转换小写
    stem = stem.lower()
    
    # 替换下划线和空格为连字符
    stem = re.sub(r'[_\s]+', '-', stem)
    
    # 删除非字母数字、非连字符、非点的字符（目录不允许有点）
    if is_dir:
        stem = re.sub(r'[^a-z0-9\-]', '', stem)
    else:
        # 文件允许有点（用于其他扩展名）
        stem = re.sub(r'[^a-z0-9\-.]', '', stem)
    
    # 合并连续的连字符
    stem = re.sub(r'-+', '-', stem)
    
    # 去除首尾连字符
    stem = stem.strip('-')
    
    # 重新组合
    if ext:
        # 如果扩展名是 .md，确保 stem 不以连字符结尾
        if stem.endswith('-') and ext == '.md':
            stem = stem[:-1]
        new_name = stem + ext
    else:
        new_name = stem
    
    # 特殊处理：如果名称为空（极不可能），恢复为 original
    if not new_name:
        return name
    
    return new_name


def should_skip(path: Path, exclude_patterns: List[str]) -> bool:
    """检查路径是否匹配排除模式。"""
    posix_path = path.as_posix()
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(posix_path, pattern):
            return True
    return False


def find_files(root: Path, pattern: str, exclude_patterns: List[str]) -> List[Path]:
    """递归查找匹配模式的文件。"""
    files = []
    for filepath in root.rglob(pattern):
        if filepath.is_file():
            if should_skip(filepath, exclude_patterns):
                continue
            files.append(filepath)
    return files


def git_mv(src: Path, dst: Path, dry_run: bool = True, skip_git: bool = False) -> bool:
    """使用 git mv 移动文件（保留历史）。"""
    if dry_run:
        logger.info(f"[dry-run] git mv {src} -> {dst}")
        return True
    
    if skip_git:
        try:
            src.rename(dst)
            logger.info(f"重命名 {src} -> {dst}")
            return True
        except OSError as e:
            logger.error(f"重命名失败：{e}")
            return False
    
    # 使用 git mv
    cmd = ['git', 'mv', str(src), str(dst)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"git mv {src} -> {dst}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"git mv 失败：{e.stderr}")
        return False


def analyze_rename(filepath: Path, docs_root: Path) -> Tuple[Path, Path, str]:
    """分析文件的重命名目标路径。"""
    relative = filepath.relative_to(docs_root)
    parent = relative.parent
    old_name = filepath.name
    is_dir = filepath.is_dir()
    new_name = normalize_filename(old_name, is_dir)
    new_relative = parent / new_name
    new_path = docs_root / new_relative
    return filepath, new_path, new_name


def main():
    parser = argparse.ArgumentParser(description='批量文件名规范化')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='只显示分析结果，不执行重命名（默认）')
    parser.add_argument('--execute', action='store_true',
                        help='实际执行重命名（危险！请先 dry-run）')
    parser.add_argument('--pattern', type=str, default='**/*.md',
                        help='文件匹配模式（默认 "**/*.md"）')
    parser.add_argument('--docs-root', type=str, default='docs',
                        help='docs 根目录（默认 docs）')
    parser.add_argument('--exclude', action='append', default=[],
                        help='排除模式（可多次使用），例如 "**/node_modules/**"')
    parser.add_argument('--skip-git', action='store_true',
                        help='不使用 git mv，直接使用 os.rename（不推荐）')
    parser.add_argument('--verbose', action='store_true',
                        help='输出详细信息')
    args = parser.parse_args()

    if args.execute:
        args.dry_run = False
        logger.warning("执行模式已启用，将实际重命名文件！")
    else:
        logger.info("干燥运行模式（不实际重命名文件）。")

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    docs_root = Path(args.docs_root)
    if not docs_root.is_dir():
        logger.error(f"docs 根目录不存在：{docs_root}")
        sys.exit(1)

    # 默认排除 .git 目录和任何隐藏目录
    default_exclude = ['**/.git/**', '**/.*/**']
    exclude_patterns = default_exclude + args.exclude

    logger.info(f"扫描文件，模式：{args.pattern} ...")
    files = find_files(docs_root, args.pattern, exclude_patterns)
    logger.info(f"找到 {len(files)} 个文件。")

    rename_plan = []
    skipped = []
    for f in files:
        src, dst, new_name = analyze_rename(f, docs_root)
        if src.name == new_name:
            skipped.append((src, "文件名已规范"))
            continue
        if dst.exists():
            skipped.append((src, f"目标文件已存在：{dst}"))
            continue
        rename_plan.append((src, dst))

    # 打印分析结果
    print("\n" + "="*80)
    print("文件名规范化分析报告")
    print("="*80)
    print(f"待重命名文件数：{len(rename_plan)}")
    print(f"跳过文件数：{len(skipped)}")
    if rename_plan:
        print("\n以下文件将被重命名：")
        for src, dst in rename_plan:
            print(f"  {src.relative_to(docs_root)}  ->  {dst.relative_to(docs_root)}")
    if skipped and args.verbose:
        print("\n跳过的文件：")
        for src, reason in skipped:
            print(f"  {src.relative_to(docs_root)}  ({reason})")

    # 执行重命名
    if not args.dry_run:
        logger.info("开始执行重命名...")
        success_count = 0
        for src, dst in rename_plan:
            success = git_mv(src, dst, dry_run=False, skip_git=args.skip_git)
            if success:
                success_count += 1
            else:
                logger.error(f"重命名失败：{src}")
        logger.info(f"重命名完成，成功 {success_count}/{len(rename_plan)} 个文件。")
    else:
        print("\n本次为干燥运行，未实际重命名文件。")
        print("若要执行重命名，请使用 --execute 参数（务必先备份）。")

    # 生成摘要
    print("\n" + "="*80)
    print("总结")
    print("="*80)
    print(f"扫描文件总数：{len(files)}")
    print(f"待重命名文件数：{len(rename_plan)}")
    print(f"跳过文件数：{len(skipped)}")
    if args.dry_run:
        print("\n干燥运行完成。")
    else:
        print("\n重命名执行完成。")
    print("="*80)


if __name__ == '__main__':
    main()