#!/usr/bin/env python3
"""
修复 Python 脚本编码问题，防止 Windows 控制台乱码。

本脚本会遍历指定目录下的所有 .py 文件，在文件开头（shebang 之后）插入编码修复代码，
确保在 Windows 环境下 stdout/stderr 使用 UTF-8 编码。

用法：
    python scripts/fix_python_encoding.py --dry-run
    python scripts/fix_python_encoding.py --execute --target scripts
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# 要插入的代码块（在 shebang 之后）
ENCODING_FIX = '''# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
'''

def needs_fix(content: str) -> bool:
    """检查文件是否已包含编码修复代码。"""
    # 检查是否已有 sys.stdout 重配置
    if 'sys.stdout = io.TextIOWrapper' in content:
        return False
    # 检查是否已有 PYTHONUTF8 注释？忽略
    return True

def insert_fix(content: str) -> str:
    """在 shebang 行之后插入编码修复代码。"""
    lines = content.splitlines(keepends=True)
    new_lines = []
    inserted = False
    for i, line in enumerate(lines):
        new_lines.append(line)
        if not inserted and line.startswith('#!'):
            # 在 shebang 行后插入
            new_lines.append('\n')
            new_lines.append(ENCODING_FIX)
            inserted = True
    # 如果没有 shebang，则在文件开头插入
    if not inserted:
        new_lines.insert(0, ENCODING_FIX + '\n')
    return ''.join(new_lines)

def process_file(filepath: Path, dry_run: bool = True):
    """处理单个文件。"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"警告：无法以 UTF-8 读取 {filepath}，跳过")
        return
    
    if not needs_fix(content):
        print(f"跳过 {filepath}（已修复）")
        return
    
    new_content = insert_fix(content)
    if dry_run:
        print(f"[dry-run] 将修改 {filepath}")
        # 显示差异（可选）
        # print(new_content[:200])
    else:
        # 备份原文件
        backup = filepath.with_suffix(filepath.suffix + '.bak')
        try:
            with open(backup, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"备份失败：{e}")
            return
        # 写入新内容
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"已修复 {filepath}")
        except Exception as e:
            print(f"写入失败：{e}")
            # 恢复备份
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
            except:
                pass

def main():
    parser = argparse.ArgumentParser(description='修复 Python 脚本编码')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='只显示分析结果，不实际修改文件（默认）')
    parser.add_argument('--execute', action='store_true',
                        help='实际修改文件')
    parser.add_argument('--force', action='store_true',
                        help='跳过确认，直接执行')
    parser.add_argument('--target', type=str, default='scripts',
                        help='目标目录（默认 scripts）')
    parser.add_argument('--exclude', action='append', default=[],
                        help='排除模式（如 **/test_*.py）')
    args = parser.parse_args()

    if args.execute:
        args.dry_run = False
        if not args.force:
            confirm = input("确认修改文件？(yes/no): ")
            if confirm.lower() != 'yes':
                print("取消操作")
                sys.exit(0)
    else:
        print("干燥运行模式（不修改文件）")

    target_dir = Path(args.target)
    if not target_dir.is_dir():
        print(f"目标目录不存在：{target_dir}")
        sys.exit(1)

    # 收集所有 .py 文件
    py_files = list(target_dir.rglob('*.py'))
    print(f"找到 {len(py_files)} 个 Python 文件")

    for py_file in py_files:
        # 检查排除模式
        skip = False
        for pattern in args.exclude:
            if py_file.match(pattern):
                skip = True
                break
        if skip:
            continue
        process_file(py_file, args.dry_run)

    print("\n操作完成。")
    if args.dry_run:
        print("请使用 --execute 参数实际应用修复。")

if __name__ == '__main__':
    main()