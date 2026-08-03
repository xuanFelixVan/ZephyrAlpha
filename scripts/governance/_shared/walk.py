# [BLUEPRINT] MOD-INF-005 | scripts/governance/_shared/walk.py | §
# [MODULE] scripts.governance._shared.walk
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.__init__
# [CONSUMERS] iter_staged_files → check_encoding/detect_direct_llm_calls/scan_debt/check_pure_shim（pre-commit --staged 变更检测）；iter_files → 60+ governance 脚本（全量遍历）
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
"""

from __future__ import annotations

import fnmatch
import os
import subprocess
from pathlib import Path

from _shared.constants import EXCLUDE_DIRS, REPO_ROOT


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


def iter_staged_files(
    extensions: frozenset[str] | None = None,
    path_prefix: str | None = None,
) -> list[Path]:
    """返回当前 staged（新增/修改，排除删除）文件列表（变更检测优化）。

    用 ``git diff --cached --diff-filter=d --name-only`` 从 git 索引读取，
    供 pre-commit 钩子只校验本次变更文件，避免全量扫描 35K 文件仓库。
    对标 audit_broken_links._get_basename_cache 的 git ls-files 优化模式：
    O(1) 读 git 索引 vs os.walk/rglob O(N) 遍历文件系统。

    命名说明：本函数返回 ``list[Path]``（不含变更状态），与
    ``zephyr.shared.security.ssot_guard.staged_files``（返回 ``dict[str,str]``
    含 A/M/D/R 状态字符）语义不同——后者服务运行时 SSoT 守卫需要区分变更类型，
    本函数服务 governance 扫描器只需"扫哪些文件"。命名加 ``iter_`` 前缀与
    同模块 ``iter_files()`` 对称，消除同名碰撞导致的 AI 误用风险。

    语义安全：未变更文件在历史提交时已过 gate；本次提交只会引入已变更
    文件的新违规。全量审计由 CI（不带 --staged）或手动 --scan/--dir 路径覆盖。

    Args:
        extensions: 允许的扩展名集合（含点号，如 frozenset({'.py'})），None 不限。
        path_prefix: 仅保留以该前缀开头的仓库相对路径（如 'src/zephyr/'），None 不限。

    Returns:
        已排序去重的绝对 Path 列表（仅含仍存在于工作区的文件）。
        git 不可用或无 staged 文件时返回空列表（pre-commit 无变更 = 无事可做）。
    """
    r = subprocess.run(
        ["git", "diff", "--cached", "--diff-filter=d", "--name-only"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0:
        return []
    result: list[Path] = []
    for line in r.stdout.splitlines():
        rel = line.strip().replace("\\", "/")
        if not rel:
            continue
        if path_prefix and not rel.startswith(path_prefix):
            continue
        fp = REPO_ROOT / rel
        if extensions and fp.suffix.lower() not in extensions:
            continue
        if fp.exists():
            result.append(fp)
    return sorted(set(result))
