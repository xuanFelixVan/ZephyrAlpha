# AI-generated: pre-commit 钩子共享工具（Batch A2 / 红蓝融合）
"""Git 暂存区与仓库根解析，供 scripts/hooks/ 下各检查脚本复用。"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable
from pathlib import Path


def resolve_repo_root() -> Path:
    """自本文件或任意调用方路径向上查找含 pyproject.toml 的目录。"""
    here = Path(__file__).resolve().parent
    for parent in [here, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("无法定位仓库根目录（未找到 pyproject.toml）")


def git_staged_paths(repo_root: Path | None = None) -> list[Path]:
    """返回 git 暂存区文件路径（相对仓库根，POSIX 风格）。"""
    root = repo_root or resolve_repo_root()
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "-z"],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    raw = result.stdout.decode("utf-8", errors="replace")
    if not raw:
        return []
    parts = raw.split("\0")
    out: list[Path] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        out.append(root / p)
    return out


def main_wrapper(run_check: Callable[[Path, list[Path]], int]) -> None:
    """CLI 入口：有 argv 路径则用 argv，否则用暂存区全集。"""
    repo = resolve_repo_root()
    args = [a for a in sys.argv[1:] if a]
    if args:
        paths = [repo / a if not Path(a).is_absolute() else Path(a) for a in args]
    else:
        paths = git_staged_paths(repo)
    sys.exit(run_check(repo, paths))
