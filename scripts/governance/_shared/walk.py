"""
walk.py — 目录遍历共享工具

对标 SCRIPT-QUALITY-001 D-D-05（禁止跨脚本复制粘贴逻辑）
10+ 个脚本各自复制了 os.walk() + EXCLUDE_DIRS 过滤模式。
"""

from __future__ import annotations

import os
from pathlib import Path

from _shared.constants import EXCLUDE_DIRS


def iter_files(
    root: Path,
    extensions: frozenset[str] | None = None,
    exclude_dirs: frozenset[str] | None = None,
    exclude_files: frozenset[str] | None = None,
) -> list[Path]:
    """递归遍历目录，返回符合条件的文件路径列表。

    Args:
        root: 遍历根目录。
        extensions: 允许的文件扩展名集合（含点号，如 '.md'），None 表示不限制。
        exclude_dirs: 排除的目录名集合，默认使用共享 EXCLUDE_DIRS。
        exclude_files: 排除的文件名集合。

    Returns:
        符合条件的文件路径列表（已排序）。
    """
    excl = exclude_dirs or EXCLUDE_DIRS
    excl_files = exclude_files or frozenset()
    result: list[Path] = []

    if not root.exists():
        return result

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if d not in excl and not d.startswith(".")
        ]
        for filename in sorted(filenames):
            if filename in excl_files:
                continue
            filepath = Path(dirpath) / filename
            if extensions and filepath.suffix.lower() not in extensions:
                continue
            result.append(filepath)

    return result
