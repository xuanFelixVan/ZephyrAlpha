# [BLUEPRINT] MOD-INF-005 | scripts/governance/fix_broken_post_sync.py | §post_sync-repair
# [MODULE] scripts.governance.fix_broken_post_sync
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__; zephyr.governance.persistence.task_repo
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 一次性修复脚本：批量修正历史 broken post_sync_standard 命令
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""fix_broken_post_sync.py — 批量修复历史 broken post_sync_standard 命令

DM-210625 #205-D 裁定执行脚本：
  20 个 OPS-20260626xx 任务：apply_depgraph.py --diagnose → diagnose_depgraph.py
  3 个 OPS-20260625xx 任务：sync_rule_registry.py --warn-only → sync_rule_registry.py（移除臆造 flag）

修复策略：
  - 仅修复活跃任务（PENDING/IN_PROGRESS/READY/BLOCKED/WAITING/RETRY）
  - 终态任务（COMPLETED/VERIFIED/FAILED/CANCELLED）不修复（不会再次 transition）
  - 使用 TaskRepository.update(post_sync_standard=...) 触发机械校验
  - 拒绝写入仍含臆造 flag/不存在脚本的命令（PostSyncValidationError）

用法:
    python scripts/governance/fix_broken_post_sync.py            # 执行修复
    python scripts/governance/fix_broken_post_sync.py --dry-run  # 仅预览，不写入

返回码:
    0 = 所有活跃任务已修复（或终态任务无需修复）
    1 = 部分任务修复失败（PostSyncValidationError 等）
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
_SRC_DIR = str(_SCRIPT_DIR.parents[2] / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from _shared.constants import DB_PATH, REPO_ROOT

from zephyr.governance.persistence.task_repo import PostSyncValidationError, TaskRepository

# ---------------------------------------------------------------------------
# 修复映射表：broken_command → correct_command
# ---------------------------------------------------------------------------

REPAIR_MAP: dict[str, list[str]] = {
    # ── 历史 #205-D 裁定（已修复，保留为文档；当前 DB 无匹配）──
    "python scripts/governance/apply_depgraph.py --diagnose": [
        "python scripts/governance/diagnose_depgraph.py",
    ],
    "python scripts/governance/sync_rule_registry.py --warn-only": [
        "python scripts/governance/sync_rule_registry.py",
    ],
    # ── OPS-D: 臆造 flag（脚本存在，flag 未注册）→ 移除臆造 flag ──
    "python D:/ZephyrAlpha/scripts/governance/sync_rule_registry.py --sync-yaml": [
        "python D:/ZephyrAlpha/scripts/governance/sync_rule_registry.py",
    ],
    "python scripts/governance/sync_rule_registry.py --sync-yaml": [
        "python scripts/governance/sync_rule_registry.py",
    ],
    f"python {REPO_ROOT / 'scripts' / 'governance' / 'sync_yaml_to_depgraph.py'} --warn-only": [
        f"python {REPO_ROOT / 'scripts' / 'governance' / 'sync_yaml_to_depgraph.py'}",
    ],
    "python scripts/governance/audit_registration.py --warn-only": [
        "python scripts/governance/audit_registration.py",
    ],
    "python scripts/governance/check_rule_four_way_alignment.py --warn-only": [
        "python scripts/governance/check_rule_four_way_alignment.py",
    ],
    "python scripts/governance/d3_metadata/check_naming_convention.py --full-scan && python scripts/governance/audit_registration.py": [
        "python scripts/governance/d3_metadata/check_naming_convention.py && python scripts/governance/audit_registration.py",
    ],
    "python scripts/governance/pre_write_gate.py --check": [
        "python scripts/governance/pre_write_gate.py",
    ],
    "python scripts/governance/session_startup_check.py --warn-only": [
        "python scripts/governance/session_startup_check.py",
    ],
    "python scripts/governance/sync_rule_registry.py --check": [
        "python scripts/governance/sync_rule_registry.py",
    ],
    "python scripts/governance/sync_rule_registry.py --dry-run": [
        "python scripts/governance/sync_rule_registry.py",
    ],
    # ── OPS-D: 已删除脚本/测试（终态任务，命令永不可执行）→ 清空 ──
    "python -m py_compile src/zephyr/autonomy_core/agent_rbac/__init__.py": [],
    "python -m py_compile src/zephyr/data/persistence/task_repo.py": [],
    "python -m pytest tests/test_rule_engine.py": [],
    "python -m pytest tests/test_rule_system_e2e.py -v": [],
    "python -m pytest tests/test_rule_system_red_blue.py -v": [],
    "python -m pytest tests/unit/test_dm400_stale_task_fix.py -v": [],
    "python D:/ZephyrAlpha/_yaml_to_md.py --all": [],
    f'python scripts/governance/check_cycle.py --db {os.getenv("DEPGRAPH_DB_CONN", "postgresql://localhost:5432/depgraph")} --max-depth 15 --warn-only 2>&1 | findstr /C:"cycle" /C:"TOTAL"': [],
    "python scripts/governance/d5_architecture/validators/validate_gate_discipline.py": [],
    "python scripts/governance/generate_rule_artifacts.py --l0": [],
    "python scripts/migration/verify_batch.py": [],
    "python scripts/migration/verify_batch.py --all": [],
}

# 活跃状态集合（需要修复的任务状态）
ACTIVE_STATUSES = frozenset({"PENDING", "IN_PROGRESS", "READY", "BLOCKED", "WAITING", "RETRY"})


def main() -> int:
    parser = argparse.ArgumentParser(
        description="批量修复历史 broken post_sync_standard 命令（DM-210625 #205-D 裁定）"
    )
    parser.add_argument(
        "--db",
        type=str,
        default=str(DB_PATH),
        help="governance.db 路径（默认: %(default)s）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅预览修复方案，不写入 DB",
    )
    parser.add_argument(
        "--include-terminal",
        action="store_true",
        help="同时修复终态任务（COMPLETED/CANCELLED 等）；默认仅修复活跃任务",
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"[ERROR] governance.db 不存在: {db_path}", file=sys.stderr)
        return 2

    repo = TaskRepository(db_path=db_path, enable_gate=False)

    # 1. 扫描所有任务，找出需要修复的活跃任务
    import sqlite3

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT task_id, status, post_sync_standard FROM tasks WHERE is_deleted = 0"
    ).fetchall()
    conn.close()

    # 2. 逐任务判定是否需要修复
    to_fix: list[tuple[str, str, list[str], list[str]]] = []  # (task_id, status, old, new)
    skipped_terminal: list[tuple[str, str]] = []  # (task_id, status)

    for row in rows:
        task_id = row["task_id"]
        status = row["status"]
        raw = row["post_sync_standard"] or "[]"
        import json

        try:
            cmds = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            cmds = []

        if not isinstance(cmds, list):
            continue

        # 检查是否有 broken 命令需要修复
        needs_fix = False
        new_cmds: list[str] = []
        for cmd in cmds:
            if isinstance(cmd, str) and cmd in REPAIR_MAP:
                needs_fix = True
                new_cmds.extend(REPAIR_MAP[cmd])
            elif isinstance(cmd, str):
                new_cmds.append(cmd)

        if not needs_fix:
            continue

        if status in ACTIVE_STATUSES or args.include_terminal:
            to_fix.append((task_id, status, cmds, new_cmds))
        else:
            skipped_terminal.append((task_id, status))

    # 3. 报告
    scope = "活跃+终态" if args.include_terminal else "活跃"
    print(f"扫描完成：{len(rows)} 个任务（修复范围：{scope}）")
    print(f"  需修复（{scope}）: {len(to_fix)} 个任务")
    print(f"  跳过（终态）: {len(skipped_terminal)} 个任务（不阻碍 transition，暂不修复）")
    print()

    if not to_fix:
        print("[DONE] 无活跃任务需要修复")
        repo.close()
        return 0

    # 4. 展示修复方案
    for task_id, status, old, new in to_fix:
        print(f"  {task_id} ({status})")
        print(f"    旧: {old}")
        print(f"    新: {new}")

    if args.dry_run:
        print(f"\n[DRY-RUN] 预览完成，未写入 DB。{len(to_fix)} 个任务待修复。")
        repo.close()
        return 0

    # 5. 执行修复
    print(f"\n执行修复...")
    success = 0
    failed: list[tuple[str, str]] = []  # (task_id, error_msg)

    for task_id, status, old, new in to_fix:
        try:
            repo.update(task_id, post_sync_standard=new)
            print(f"  [OK] {task_id}: {old} → {new}")
            success += 1
        except PostSyncValidationError as e:
            print(f"  [FAIL] {task_id}: PostSyncValidationError — {e}", file=sys.stderr)
            failed.append((task_id, str(e)))
        except Exception as e:
            print(f"  [FAIL] {task_id}: {type(e).__name__} — {e}", file=sys.stderr)
            failed.append((task_id, str(e)))

    repo.close()

    # 6. 汇总
    print(f"\n修复完成：成功 {success}/{len(to_fix)}，失败 {len(failed)}")
    if failed:
        print("\n失败详情：", file=sys.stderr)
        for tid, err in failed:
            print(f"  {tid}: {err}", file=sys.stderr)
        return 1

    print("[DONE] 所有活跃任务已修复")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
