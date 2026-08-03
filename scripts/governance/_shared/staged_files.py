# [BLUEPRINT] MOD-INF-005 | scripts/governance/_shared/staged_files.py | §
# [MODULE] scripts.governance._shared.staged_files
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib(subprocess/pathlib)
# [CONSUMERS] check_any_abuse.py（commit-time gate，零重依赖约束）；_shared/walk.py（re-export 给 check_encoding/detect_direct_llm_calls/scan_debt/check_pure_shim）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯 stdlib 实现，禁止 import _shared.constants（会间接 import psycopg2 导致 commit-time gate 崩溃）
# [MODIFY-GUARD] 修改需同步更新 _shared/walk.py（re-export 消费方）和 test_staged_walk.py（测试）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] git 不可用或无 staged 文件时返回空列表（不抛异常）
# [TESTS] tests/governance/scripts_governance/test_staged_walk.py（iter_staged_files 单元测试，通过 walk.py re-export 测试）
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
staged_files.py — staged 文件列表读取（轻量级，纯 stdlib）

治本背景（2026-08-03）：
  check_any_abuse.py 是 commit-time gate，必须零重依赖（仅 stdlib + PyYAML）。
  原方案在 check_any_abuse.py 内联 23 行 git diff 逻辑（与 _shared/walk.iter_staged_files 重复），
  原因是 import _shared.walk 会间接 import _shared.constants → psycopg2，导致 gate 崩溃。

  本模块是治本方案：将 iter_staged_files 抽取为独立轻量模块，只依赖 stdlib（subprocess + pathlib），
  不 import _shared.constants（避免 psycopg2 传递依赖）。
  - check_any_abuse.py 直接 import 本模块（零 psycopg2 依赖）
  - _shared/walk.py re-export 本模块函数（向后兼容已有 4 个消费方）

  根因分析：_shared/constants.py 混合了轻量常量（REPO_ROOT/EXCLUDE_DIRS/EXIT_*）
  与重 DB 基础设施（psycopg2/PgConnExecuteWrapper），违反单一职责原则。
  本模块是短期治本——长期治本应拆分 _shared/constants.py（影响 28+ 文件，单独任务处理）。

REPO_ROOT 说明：
  本模块内联计算 REPO_ROOT（Path(__file__).resolve().parents[3]），与 check_any_abuse.py
  原内联实现一致。未使用 zephyr.shared.io.paths SSoT 是因为 import 它需要 sys.path bootstrap
  （在 _shared.constants 中完成），而本模块的存在意义就是避免 import _shared.constants。
  parents[3] 路径推算：scripts/governance/_shared/staged_files.py → parents[0]=_shared, [1]=governance, [2]=scripts, [3]=repo root
"""

from __future__ import annotations

import subprocess
from pathlib import Path

# 内联计算 REPO_ROOT（不 import _shared.constants 以避免 psycopg2 传递依赖）
# 与 check_any_abuse.py 原内联实现一致：scripts/governance/_shared/staged_files.py → parents[3]
REPO_ROOT: Path = Path(__file__).resolve().parents[3]


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
    # CREATE_NO_WINDOW 防止 Windows 控制台窗口闪现（trae_067 铁律2）
    # getattr 跨平台：Windows 有 CREATE_NO_WINDOW 属性，非 Windows 返回 0
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    r = subprocess.run(  # noqa: bare-subprocess  轻量模块禁 import process_pool（会拉 psycopg2 传递依赖，打破 commit-time gate 零重依赖约束）
        ["git", "diff", "--cached", "--diff-filter=d", "--name-only"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        creationflags=creationflags,
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
