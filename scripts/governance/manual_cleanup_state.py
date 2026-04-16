#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动清理 docs/09_AUDIT/STATE/ 目录，保留每种类型的最新版本。

清理规则：
1. 永久保留：文件名含 TRIAGE, RESOLUTION, DECISION, CANONICAL, REASONING, MASTER, SITEMAP, INDEX, LATEST
2. 按类型分组：去掉日期后缀后相同前缀的文件视为同一类型
3. 每类型只保留最新版本（按文件名中的日期或修改时间）
4. 删除旧版本
"""

import re
from datetime import datetime
from pathlib import Path

STATE_DIR = Path("docs/09_AUDIT/STATE")

# 永久保留关键词
PERMANENT_KEYWORDS = ["TRIAGE", "RESOLUTION", "DECISION", "CANONICAL", "REASONING",
                      "MASTER", "SITEMAP", "INDEX", "LATEST"]

def get_file_date(path: Path) -> datetime:
    """从文件名提取日期，或使用修改时间"""
    # 尝试提取 YYYYMMDD_HHMMSS 或 YYYY-MM-DD
    match = re.search(r"(\d{4}-?\d{2}-?\d{2})", path.name)
    if match:
        date_str = match.group(1).replace("-", "")
        try:
            return datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            pass
    return datetime.fromtimestamp(path.stat().st_mtime)

def get_type_prefix(name: str) -> str:
    """提取文件类型前缀（去掉日期和扩展名）"""
    name = name.upper()
    # 移除 _YYYYMMDD_HHMMSS 或 -YYYY-MM-DD-HHMMSS 后缀
    name = re.sub(r"[_-]\d{8}[_-]?\d{6}.*$", "", name)
    name = re.sub(r"[_-]\d{8}.*$", "", name)
    name = re.sub(r"\.\w+$", "", name)
    return name

def is_permanent(path: Path) -> bool:
    """检查是否永久保留"""
    name_upper = path.name.upper()
    return any(k in name_upper for k in PERMANENT_KEYWORDS)

def main(dry_run: bool = True):
    print(f"{'[DRY-RUN] ' if dry_run else ''}开始清理 STATE 目录...")
    print(f"目录: {STATE_DIR}")
    print("-" * 80)

    if not STATE_DIR.exists():
        print("错误: 目录不存在")
        return

    # 获取所有文件
    all_files = [p for p in STATE_DIR.iterdir() if p.is_file()]
    print(f"总文件数: {len(all_files)}")

    # 按类型分组
    files_by_type = {}
    for p in all_files:
        if is_permanent(p):
            continue
        prefix = get_type_prefix(p.name)
        if prefix not in files_by_type:
            files_by_type[prefix] = []
        files_by_type[prefix].append(p)

    # 找出需要删除的文件（保留每类型最新版）
    files_to_delete = []
    files_to_keep = []

    for prefix, paths in files_by_type.items():
        if len(paths) <= 1:
            files_to_keep.extend(paths)
            continue

        # 按日期排序，保留最新
        sorted_paths = sorted(paths, key=get_file_date, reverse=True)
        files_to_keep.append(sorted_paths[0])  # 最新版
        files_to_delete.extend(sorted_paths[1:])  # 旧版本

    # 永久保留的文件
    permanent_files = [p for p in all_files if is_permanent(p)]
    files_to_keep.extend(permanent_files)

    print(f"保留文件数: {len(files_to_keep)}")
    print(f"删除文件数: {len(files_to_delete)}")
    print()

    # 显示将要删除的文件
    if files_to_delete:
        print("将要删除的文件:")
        for p in sorted(files_to_delete):
            date = get_file_date(p)
            print(f"  - {p.name} (日期: {date.strftime('%Y-%m-%d')})")
        print()

    # 显示保留的文件
    print("保留的文件:")
    for p in sorted(files_to_keep):
        date = get_file_date(p)
        prefix = get_type_prefix(p.name)
        marker = "[永久]" if is_permanent(p) else "[最新]"
        print(f"  {marker} {p.name} (类型: {prefix[:40]})")

    # 执行删除
    if not dry_run and files_to_delete:
        print()
        print("执行删除...")
        for p in files_to_delete:
            try:
                p.unlink()
                print(f"  已删除: {p.name}")
            except Exception as e:
                print(f"  删除失败: {p.name} - {e}")

    print()
    print("-" * 80)
    if dry_run:
        print("[DRY-RUN] 完成。使用 --execute 参数执行实际删除。")
    else:
        print("清理完成!")

    # 统计
    final_count = len(list(STATE_DIR.iterdir()))
    print(f"清理后文件数: {final_count}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="手动清理 STATE 目录")
    parser.add_argument("--execute", action="store_true", help="执行实际删除（默认 dry-run）")
    args = parser.parse_args()
    main(dry_run=not args.execute)
