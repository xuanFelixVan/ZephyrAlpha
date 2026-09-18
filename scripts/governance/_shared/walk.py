# [BLUEPRINT] MOD-INF-005 | scripts/governance/_shared/walk.py | §
# [MODULE] scripts.governance._shared.walk
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.__init__, scripts.governance._shared.staged_files
# [CONSUMERS] iter_staged_files → check_encoding/detect_direct_llm_calls/scan_debt/check_pure_shim/check_any_abuse（pre-commit --staged 变更检测，真源在 _shared/staged_files.py）；iter_files → 60+ governance 脚本（全量遍历）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/scripts_governance/test_staged_walk.py（iter_staged_files 单元测试）
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
walk.py — 目录遍历共享工具

对标 SCRIPT-QUALITY-001 D-D-05（禁止跨脚本复制粘贴逻辑）
10+ 个脚本各自复制了 os.walk() + EXCLUDE_DIRS 过滤模式。

iter_staged_files 真源在 _shared/staged_files.py（轻量模块，不 import _shared.constants
避免 psycopg2 传递依赖）。本模块 re-export 供已有消费方（check_encoding/
detect_direct_llm_calls/scan_debt/check_pure_shim）向后兼容。check_any_abuse.py
因 commit-time gate 零重依赖约束，直接 import _shared.staged_files（不经过本模块）。
"""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path

from _shared.constants import EXCLUDE_DIRS, REPO_ROOT
from _shared.staged_files import (
    iter_staged_files,  # noqa: F401  re-export 真源在 _shared/staged_files.py（轻量模块无 psycopg2 传递依赖）
)


def iter_files(
    root: Path,
    extensions: frozenset[str] | None = None,
    exclude_dirs: frozenset[str] | None = None,
    exclude_files: frozenset[str] | None = None,
    name_pattern: str | None = None,
) -> list[Path]:
    """递归遍历目录，返回符合条件的文件路径列表。

    Args:
        root: 遍历根目录。
        extensions: 允许的文件扩展名集合（含点号，如 '.md'），None 表示不限制。
        exclude_dirs: 排除的目录名集合，默认使用共享 EXCLUDE_DIRS。
        exclude_files: 排除的文件名集合。
        name_pattern: fnmatch 文件名模式（如 "blueprint.md"、"g*.yaml"），None 表示不按名称过滤。

    Returns:
        符合条件的文件路径列表（已排序）。
    """
    excl = exclude_dirs or EXCLUDE_DIRS
    excl_files = exclude_files or frozenset()
    result: list[Path] = []

    if not root.exists():
        return result

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in excl and not d.startswith(".")]
        for filename in sorted(filenames):
            if filename in excl_files:
                continue
            if name_pattern and not fnmatch.fnmatch(filename, name_pattern):
                continue
            filepath = Path(dirpath) / filename
            if extensions and filepath.suffix.lower() not in extensions:
                continue
            result.append(filepath)

    return result


# ─── 扫描目录入参口径（治本 2026-09-19 CF1 F2-F6，单一真源，禁止各检测器复制）─────
# 病根：五个检测器（detect_temp_files / detect_shell_true / detect_threading_lock /
# detect_vague_terms / detect_ruins_references）在遍历循环里写
#     try: rel = filepath.relative_to(REPO_ROOT)
#     except ValueError: continue
# 展示路径算不出来就把"发现"整条丢掉，而 files_scanned 照常计数（或不计数后
# 0==0 通过）——于是 `--scan-dir src`（相对口径）永远报"扫了 N 文件 / 0 发现 /
# exit 0"。传错目录、目录不存在、目录不在仓内同样 exit 0＝君子协定式假绿。


def resolve_scan_dir(raw: str | Path | None) -> Path | None:
    """把扫描目录入参归一为绝对路径；空/None 入参返回 None（调用方走默认全库口径）。

    Args:
        raw: CLI `--scan-dir` 原值或调用方传入的 Path（可能是相对路径）。

    Returns:
        绝对化后的 Path；入参为空时返回 None。
    """
    if raw is None:
        return None
    text = str(raw).strip()
    if not text:
        return None
    return Path(text).expanduser().resolve()


def rel_for_display(path: Path) -> str:
    """仓内文件给相对路径（正斜杠），仓外文件给绝对路径——绝不因算不出相对就丢发现。"""
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def zero_scan_error(
    explicit_dir: Path | None, files_scanned: int, label: str, found_count: int = 0
) -> str | None:
    """显式传了扫描目录、却 0 文件进入统计且 0 发现 → 返回错误文案；否则 None。

    0 文件进入统计只有三种成因，全部必须出声：
    目录不存在 / 目录下无可扫扩展名文件 / 目录不在 REPO_ROOT 相对口径内。
    found_count>0 时不报（例如目录下只有子目录、无文件，但临时目录本身已被计入发现）。
    """
    if explicit_dir is not None and files_scanned == 0 and found_count == 0:
        return (
            f"ERROR [{label}] 显式扫描目录 {explicit_dir} 下 0 个文件进入统计"
            "（目录不存在 / 无可扫文件 / 不在仓内口径）——入参口径失效，拒绝按通过处理"
        )
    return None


# iter_staged_files 实现已移至 _shared/staged_files.py（轻量模块，无 psycopg2 传递依赖）
# 本模块通过上方 `from _shared.staged_files import iter_staged_files` re-export
# 治本（2026-08-03）：消除 check_any_abuse.py 23 行内联 git diff 重复代码
