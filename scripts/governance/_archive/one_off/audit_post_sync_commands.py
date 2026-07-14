# [BLUEPRINT] MOD-INF-005 | scripts/governance/audit_post_sync_commands.py | §post_sync-validation
# [MODULE] scripts.governance.audit_post_sync_commands
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__; zephyr.governance.persistence.sqlite_schema
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只读诊断，不修改 governance.db；扫描所有任务的 post_sync_standard 命令并校验可执行性
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""audit_post_sync_commands.py — post_sync_standard 命令可执行性巡检（防幻觉/CLI漂移）

扫描 governance.db 中所有任务的 post_sync_standard 命令，逐条机械校验：
  - shell 可解析（shlex）
  - .py 脚本存在
  - argparse flag 已注册（通过 --help 输出 grep）

主动发现两类问题（而非被动等 transition(COMPLETED) 死锁）：
  1. 建卡 AI 幻觉：臆造不存在的脚本或 flag（如 D-SIGNAL 改名 20 卡死锁事故根因）
  2. CLI 漂移：脚本后续重构删除了 flag，导致已建卡的 post_sync_standard 失效

用法:
    python scripts/governance/audit_post_sync_commands.py            # 全量扫描报告
    python scripts/governance/audit_post_sync_commands.py --quiet    # 仅输出 broken，供 CI 门禁

返回码:
    0 = CLEAN（所有命令可解析、脚本存在、flag 已注册）
    1 = 发现 broken 命令（臆造脚本/flag 或 CLI 漂移）

设计基线:
    与 TaskRepository._validate_post_sync_executable（create 时校验）互补——
    create() 拦截新建卡，本脚本巡检已落库卡 + 检测后续 CLI 漂移。
    建议改名/重构后、CI 流水线中定期运行。
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

# 治本(2026-06-30): REPO_ROOT 真源来自 _shared.constants (SSoT), 消除 parents[N] 硬编码
from _shared.constants import DB_PATH, REPO_ROOT as _REPO_ROOT  # noqa: E402

_SRC_DIR = str(_REPO_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

import sqlite3

from zephyr.shared.io.paths import DB_PATH
from zephyr.governance.architecture_governance.post_sync_validator import (
    validate_post_sync_command,
    validate_rollback_instructions,
)


@dataclass
class BrokenCommand:
    """一条 broken 命令/回滚说明及其受影响任务。

    W3 后覆盖三个字段：post_sync_standard / post_sync_specific（命令级校验）
    与 rollback_instructions（轻量语义校验）。command 字段为原始文本，
    broken_map 键用前缀区分来源（``[specific]`` / ``[rollback]{task_id}``）。
    """

    command: str
    reason: str
    affected_tasks: list[str] = field(default_factory=list)
    active_tasks: list[str] = field(default_factory=list)
    terminal_tasks: list[str] = field(default_factory=list)


# 活跃状态（会触发 transition(COMPLETED) 死锁的状态）
_ACTIVE_STATUSES = frozenset(
    {"PENDING", "IN_PROGRESS", "READY", "BLOCKED", "WAITING", "RETRY"}
)


def _resolve_script_path(script_token: str) -> Path:
    """解析脚本路径（相对路径基于 PROJECT_ROOT）。"""
    p = Path(script_token)
    if not p.is_absolute():
        p = _REPO_ROOT / p
    return p


def _validate_one_command(cmd: str) -> str | None:
    """校验单条 post_sync_standard 命令。

    返回 None 表示通过；返回字符串表示失败原因。
    仅校验含 .py 脚本的命令；非 .py（echo/git 等）跳过。

    校验逻辑真源：``zephyr.governance.architecture_governance.post_sync_validator.validate_post_sync_command``（SSoT）。
    与 task_repo._validate_post_sync_commands 复用同一逻辑，消除双份漂移风险
    （原 ~80 行重复逻辑已于 2026-06-26 抽取到 SSoT 模块）。
    """
    return validate_post_sync_command(cmd, _REPO_ROOT)


def _aggregate_broken(
    broken_map: dict[str, BrokenCommand],
    key: str,
    text: str,
    reason: str,
    task_id: str,
    status: str,
) -> None:
    """将一条 broken 命令/回滚文本聚合到 broken_map（三字段共用）。

    key 用前缀区分来源字段，避免不同字段的同名条目误合并；
    text 为原始内容（用于报告展示），reason 为 SSoT 失败归因。
    """
    if key not in broken_map:
        broken_map[key] = BrokenCommand(command=text, reason=reason)
    bc = broken_map[key]
    bc.affected_tasks.append(task_id)
    if status in _ACTIVE_STATUSES:
        bc.active_tasks.append(task_id)
    else:
        bc.terminal_tasks.append(task_id)


def scan_all_post_sync(db_path: Path) -> list[BrokenCommand]:
    """扫描 governance.db 所有任务的 post_sync 命令与回滚说明。

    W3 后覆盖三个字段（防孪生字段盲区）：
      - post_sync_standard（list[str]，命令级 SSoT 校验）
      - post_sync_specific（list[str]，同型同语义，复用 _validate_one_command）
      - rollback_instructions（str，轻量语义校验 validate_rollback_instructions）

    返回 broken 命令/回滚列表（含受影响任务 ID，按 active/terminal 分类）。
    active 任务 = 会触发 transition(COMPLETED) 死锁的活跃任务；
    terminal 任务 = 已 COMPLETED/CANCELLED/VERIFIED 等，不会再次 transition。
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT task_id, status, post_sync_standard, post_sync_specific, "
            "rollback_instructions FROM tasks WHERE is_deleted = 0"
        ).fetchall()
    finally:
        conn.close()

    # command -> {reason, affected_tasks}（key 用前缀区分来源字段）
    broken_map: dict[str, BrokenCommand] = {}

    for row in rows:
        task_id = row["task_id"]
        status = row["status"]

        # --- post_sync_standard（命令级校验，键无前缀，保持向后兼容）---
        raw = row["post_sync_standard"] or "[]"
        try:
            cmds = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            cmds = []
        if isinstance(cmds, list):
            for cmd in cmds:
                if not isinstance(cmd, str) or not cmd.strip():
                    continue
                reason = _validate_one_command(cmd)
                if reason is None:
                    continue
                _aggregate_broken(broken_map, cmd, cmd, reason, task_id, status)

        # --- W3: post_sync_specific（与 standard 同型同语义，复用 _validate_one_command；
        #     键加 [specific] 前缀区分来源字段）---
        raw_specific = row["post_sync_specific"] or "[]"
        try:
            specific_cmds = json.loads(raw_specific)
        except (json.JSONDecodeError, TypeError):
            specific_cmds = []
        if isinstance(specific_cmds, list):
            for cmd in specific_cmds:
                if not isinstance(cmd, str) or not cmd.strip():
                    continue
                reason = _validate_one_command(cmd)
                if reason is None:
                    continue
                _aggregate_broken(
                    broken_map, f"[specific]{cmd}", cmd, reason, task_id, status
                )

        # --- W3: rollback_instructions（str，轻量语义校验，非命令级；
        #     键加 [rollback]{task_id} 前缀，因回滚文本通常每任务唯一）---
        rollback_text = row["rollback_instructions"] or ""
        if rollback_text.strip():
            reason = validate_rollback_instructions(rollback_text, _REPO_ROOT)
            if reason is not None:
                _aggregate_broken(
                    broken_map,
                    f"[rollback]{task_id}",
                    rollback_text,
                    reason,
                    task_id,
                    status,
                )

    return list(broken_map.values())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="post_sync 命令与回滚说明可执行性巡检（防幻觉/CLI漂移；W3 覆盖 standard/specific/rollback 三字段）"
    )
    parser.add_argument(
        "--db",
        type=str,
        default=str(DB_PATH),
        help="governance.db 路径（默认: %(default)s）",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="仅输出活跃任务 broken 命令（供 CI 门禁，clean 时无输出）",
    )
    parser.add_argument(
        "--include-terminal",
        action="store_true",
        help="同时输出终态任务 broken 命令（默认仅输出活跃任务）",
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"[ERROR] governance.db 不存在: {db_path}", file=sys.stderr)
        return 2

    broken = scan_all_post_sync(db_path)

    # 分离活跃 vs 终态
    active_broken = [b for b in broken if b.active_tasks]
    terminal_broken = [b for b in broken if not b.active_tasks and b.terminal_tasks]

    if not active_broken and not terminal_broken:
        if not args.quiet:
            print(f"[CLEAN] 所有 post_sync 命令与回滚说明均合法（扫描 {db_path}）")
        return 0

    # 活跃任务 broken = ERROR（会死锁 transition(COMPLETED)）
    if active_broken:
        total_active = sum(len(b.active_tasks) for b in active_broken)
        print(
            f"[BROKEN] 发现 {len(active_broken)} 条命令影响 {total_active} 个活跃任务"
            f"（会阻断 transition(COMPLETED)）：",
            file=sys.stderr,
        )
        for b in active_broken:
            print(file=sys.stderr)
            print(f"  命令: {b.command}", file=sys.stderr)
            print(f"  原因: {b.reason}", file=sys.stderr)
            print(
                f"  活跃任务 ({len(b.active_tasks)}): "
                f"{', '.join(b.active_tasks[:10])}"
                + ("..." if len(b.active_tasks) > 10 else ""),
                file=sys.stderr,
            )
        print(file=sys.stderr)
        print(
            "修复建议：使用 TaskRepository.update(post_sync_standard=...) 批量修正，"
            "或运行 python scripts/governance/fix_broken_post_sync.py",
            file=sys.stderr,
        )

    # 终态任务 broken = WARNING（不会死锁，但数据不洁）
    if terminal_broken and (args.include_terminal or not args.quiet):
        total_terminal = sum(len(b.terminal_tasks) for b in terminal_broken)
        print(
            f"\n[WARN] {len(terminal_broken)} 条命令影响 {total_terminal} 个终态任务"
            f"（不会阻断流程，仅为数据清洁度问题）：",
            file=sys.stderr,
        )
        if args.include_terminal:
            for b in terminal_broken:
                print(file=sys.stderr)
                print(f"  命令: {b.command}", file=sys.stderr)
                print(f"  原因: {b.reason}", file=sys.stderr)
                print(
                    f"  终态任务 ({len(b.terminal_tasks)}): "
                    f"{', '.join(b.terminal_tasks[:10])}"
                    + ("..." if len(b.terminal_tasks) > 10 else ""),
                    file=sys.stderr,
                )
        else:
            print("  （使用 --include-terminal 查看详情）", file=sys.stderr)

    # 仅活跃任务 broken 时返回 1（阻断 CI）；终态 only 返回 0
    return 1 if active_broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
