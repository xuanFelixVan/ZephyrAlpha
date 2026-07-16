# [BLUEPRINT] MOD-INF-005 | scripts/governance/task_summary.py | §
# [MODULE] scripts.governance.task_summary
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.persistence.task_repo; zephyr.governance.persistence.sqlite_schema
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
task_summary.py — 任务系统全局摘要 CLI
=======================================
Blueprint: MOD-TASK_SYSTEM (infrastructure_runtime_integration/task-system) OPS-003
依赖: TaskRepository + SQLite metadata DB



Usage:
    python scripts/governance/task_summary.py                  # 全部透视
    python scripts/governance/task_summary.py --by-phase       # 仅 Phase 分组
    python scripts/governance/task_summary.py --by-blueprint   # 仅蓝图分组
    python scripts/governance/task_summary.py --by-status      # 仅状态分布
    python scripts/governance/task_summary.py --json           # JSON 输出
    python scripts/governance/task_summary.py --quiet          # 安静模式，仅摘要行
"""

from __future__ import annotations

from _shared.constants import EXIT_ERROR, EXIT_PASS, REPO_ROOT as _PROJECT_ROOT

__manifest__ = """
args: []
description: ⚠ __manifest__ 缺失——请添加元数据块
dimensions: []
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from zephyr.governance.persistence.sqlite_schema import init_db
from zephyr.governance.persistence.task_repo import TaskRepository

_STATUS_ICON: dict[str, str] = {
    "pending": "⬜",
    "ready": "🟡",
    "in_progress": "🔵",
    "completed": "✅",
    "verified": "🌟",
    "failed": "❌",
    "blocked": "🔴",
    "waiting": "⏳",
    "retry": "🔄",
    "cancelled": "🚫",
}

_STATUS_ORDER = (
    "pending",
    "ready",
    "in_progress",
    "completed",
    "verified",
    "blocked",
    "waiting",
    "failed",
    "retry",
    "cancelled",
)

_PRIORITY_WEIGHT: dict[str, int] = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
_PRIORITY_LABEL: dict[str, str] = {
    "P0": "🔴 P0",
    "P1": "🟠 P1",
    "P2": "🟡 P2",
    "P3": "🟢 P3",
    "P4": "⚪ P4",
}

_PHASE_LABELS: dict[int, str] = {
    0: "Phase 0 - 规划",
    1: "Phase 1 - 核心骨架",
    2: "Phase 2 - 聚合/基础设施",
    3: "Phase 3 - 治理/健壮性",
    4: "Phase 4 - 业务层",
    5: "Phase 5 - 集成",
}


def _sv(card) -> str:
    """_sv implementation."""
    return card.status.value.lower()


def _bar(ratio: float, width: int = 20) -> str:
    """_bar implementation."""
    filled = max(0, min(width, int(ratio * width)))
    return "█" * filled + "░" * (width - filled)


def _icon(s: str) -> str:
    """_icon implementation."""
    return _STATUS_ICON.get(s, "❓")


def render_all(cards: list) -> None:
    """render_all implementation."""
    out = sys.stdout
    now_utc = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    total = len(cards)

    status_counts: dict[str, int] = defaultdict(int)
    phase_counts: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    bp_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    priority_counts: dict[str, int] = defaultdict(int)

    for c in cards:
        sv = _sv(c)
        status_counts[sv] += 1
        phase_counts[c.phase][sv] += 1
        bp = c.source_blueprint or "?"
        bp_counts[bp][sv] += 1
        priority_counts[c.priority.value] += 1

    completed = status_counts.get("completed", 0) + status_counts.get("verified", 0)
    in_progress = status_counts.get("in_progress", 0)
    failed = status_counts.get("failed", 0)
    blocked = status_counts.get("blocked", 0) + status_counts.get("waiting", 0)
    pending = status_counts.get("pending", 0) + status_counts.get("ready", 0)
    cancelled = status_counts.get("cancelled", 0)
    overall_ratio = completed / max(total, 1)

    print(f"\n{'=' * 60}", file=out)
    print("  ZephyrAlpha 任务系统 — 全局进度", file=out)
    print(f"  {now_utc}", file=out)
    print(f"{'=' * 60}", file=out)

    print("\n-- 全局概览 --", file=out)
    print(f"  总计 {total} 张任务卡  [{_bar(overall_ratio)}] {overall_ratio:.0%}", file=out)
    print(f"  ✅ 已完成: {completed:>4}    🔵 进行中: {in_progress:>4}", file=out)
    print(f"  ⬜ 待开始: {pending:>4}    🔴 阻塞/等待: {blocked:>4}", file=out)
    print(f"  ❌ 失败:   {failed:>4}    🚫 已取消: {cancelled:>4}", file=out)

    print("\n-- 按 Phase 分组 --", file=out)
    for ph in sorted(phase_counts):
        pc = phase_counts[ph]
        ph_total = sum(pc.values())
        ph_done = pc.get("completed", 0) + pc.get("verified", 0)
        r = ph_done / max(ph_total, 1)
        label = _PHASE_LABELS.get(ph, f"Phase {ph}")
        detail = "  ".join(f"{_icon(s)}:{pc.get(s, 0)}" for s in _STATUS_ORDER if pc.get(s, 0) > 0)
        print(f"  Phase {ph} [{label[:24]:<24}] {_bar(r)} {r:.0%} ({ph_done}/{ph_total})", file=out)
        if detail:
            print(f"    {detail}", file=out)

    print(f"\n-- 按蓝图分组 ({len(bp_counts)} 个蓝图) --", file=out)
    for bp in sorted(bp_counts, key=lambda b: -sum(bp_counts[b].values())):
        bc = bp_counts[bp]
        bp_total = sum(bc.values())
        bp_done = bc.get("completed", 0) + bc.get("verified", 0)
        r = bp_done / max(bp_total, 1)
        detail = "  ".join(f"{_icon(s)}:{bc.get(s, 0)}" for s in _STATUS_ORDER if bc.get(s, 0) > 0)
        print(f"  {bp:<24} {_bar(r, 15)} {r:.0%} ({bp_done}/{bp_total})", file=out)
        if detail:
            print(f"    {detail}", file=out)

    print("\n-- 状态分布 --", file=out)
    for sv in _STATUS_ORDER:
        n = status_counts.get(sv, 0)
        if n == 0:
            continue
        bar_w = min(30, max(1, int(n / max(total, 1) * 30)))
        print(f"  {_icon(sv)} {sv:<14} {'█' * bar_w} {n:>4}  ({n / max(total, 1):.0%})", file=out)

    print("\n-- 优先级分布 --", file=out)
    for pv in sorted(priority_counts, key=lambda p: _PRIORITY_WEIGHT.get(p, 99)):
        n = priority_counts[pv]
        label = _PRIORITY_LABEL.get(pv, pv)
        bar_w = min(30, max(1, int(n / max(total, 1) * 30)))
        print(f"  {label:<8} {'█' * bar_w} {n:>4}", file=out)

    active_p0 = [
        c
        for c in cards
        if c.priority.value == "P0" and _sv(c) in ("pending", "ready", "in_progress", "blocked", "waiting")
    ]
    if active_p0:
        print(f"\n-- 活跃 P0 任务 ({len(active_p0)} 个) --", file=out)
        for c in sorted(active_p0, key=lambda x: x.task_id):
            print(f"  {_icon(_sv(c))} {c.task_id}  [{_sv(c)}] {c.title}", file=out)

    print(f"\n{'─' * 60}", file=out)
    print(f"  刷新: {datetime.now(UTC).strftime('%H:%M:%S UTC')}", file=out)
    print(f"{'─' * 60}\n", file=out)


def render_json(cards: list) -> None:
    """render_json implementation."""
    status_counts: dict[str, int] = defaultdict(int)
    for c in cards:
        status_counts[_sv(c)] += 1

    output = {
        "total": len(cards),
        "by_status": dict(status_counts),
        "tasks": [
            {
                "task_id": c.task_id,
                "title": c.title,
                "status": _sv(c),
                "priority": c.priority.value,
                "phase": c.phase,
                "source_blueprint": c.source_blueprint,
            }
            for c in sorted(cards, key=lambda x: x.task_id)
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2), file=sys.stdout)


def render_quiet(cards: list) -> None:
    """render_quiet implementation."""
    total = len(cards)
    status_counts: dict[str, int] = defaultdict(int)
    for c in cards:
        status_counts[_sv(c)] += 1
    done = status_counts.get("completed", 0) + status_counts.get("verified", 0)
    active = status_counts.get("in_progress", 0)
    failed = status_counts.get("failed", 0)
    blocked = status_counts.get("blocked", 0)
    print(f"tasks: {total} total | {done} done | {active} active | {failed} failed | {blocked} blocked")


def render_drift_check(repo: TaskRepository) -> int:
    """DM-362: 依赖漂移检测。返回漂移数（0=无漂移）。"""
    result = repo.drift_check()
    should_be_ready = result["should_be_ready"]
    should_be_blocked = result["should_be_blocked"]
    auto_promoted = result["auto_promoted_history"]
    total_drift = len(should_be_ready) + len(should_be_blocked)

    print(f"\n{'=' * 60}")
    print("  依赖漂移检测 (DM-362)")
    print(f"{'=' * 60}")

    if should_be_ready:
        print(f"\n-- 应提升为READY的任务 ({len(should_be_ready)} 个) --")
        for item in should_be_ready:
            print(f"  {item['task_id']}: {item['current_status']} → {item['expected_status']} | {item['details']}")
    else:
        print("\n-- 应提升为READY的任务: 无 --")

    if should_be_blocked:
        print(f"\n-- 应降为BLOCKED的任务 ({len(should_be_blocked)} 个) --")
        for item in should_be_blocked:
            print(f"  {item['task_id']}: {item['current_status']} → {item['expected_status']} | {item['details']}")
    else:
        print("\n-- 应降为BLOCKED的任务: 无 --")

    if auto_promoted:
        print(f"\n-- 最近auto_promoted事件 ({len(auto_promoted)} 条) --")
        for item in auto_promoted[:10]:
            payload = item.get("payload", {})
            print(
                f"  {item['task_id']}: {payload.get('from_status', '?')} → {payload.get('to_status', '?')} (触发: {payload.get('trigger_task', '?')}) @ {item['created_at'][:19]}"
            )
    else:
        print("\n-- 最近auto_promoted事件: 无 --")

    print(f"\n  漂移总计: {total_drift}")
    print(f"{'─' * 60}\n")
    return total_drift


def render_auto_close_dry_run(repo: TaskRepository) -> int:
    """DM-363: 已完成候选检测（dry-run）。返回候选数。"""
    candidates = repo.detect_completed_candidates()

    print(f"\n{'=' * 60}")
    print("  已完成候选检测 (DM-363 dry-run)")
    print(f"{'=' * 60}")

    if candidates:
        print(f"\n-- deliverables已存在但未关闭的任务 ({len(candidates)} 个) --")
        for item in candidates:
            print(f"  {item['task_id']}: status={item['status']}")
            for f in item["existing_files"]:
                print(f"    ✅ {f}")
    else:
        print("\n-- 无已完成未关闭的任务 --")

    print(f"\n  候选总计: {len(candidates)}")
    print(f"{'─' * 60}\n")
    return len(candidates)


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="任务系统全局进度摘要")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--quiet", "-q", action="store_true", help="安静模式")
    parser.add_argument("--warn-only", action="store_true", help="警告模式——不因未完成任务返回非零 exit code")
    parser.add_argument("--drift-check", action="store_true", help="DM-362: 依赖漂移检测")
    parser.add_argument("--auto-close-dry-run", action="store_true", help="DM-363: 已完成候选检测(dry-run)")
    args = parser.parse_args()

    init_db()
    repo = TaskRepository()

    if args.drift_check:
        drift_count = render_drift_check(repo)
        return EXIT_PASS if args.warn_only or drift_count == 0 else EXIT_ERROR

    if args.auto_close_dry_run:
        render_auto_close_dry_run(repo)
        return EXIT_PASS

    cards = repo.list_by_namespace("OPS")
    cards.sort(key=lambda c: c.seq)

    has_issues = any(_sv(c) in ("failed", "blocked") for c in cards)

    if args.json:
        render_json(cards)
    elif args.quiet:
        render_quiet(cards)
    else:
        render_all(cards)

    if args.warn_only:
        return EXIT_PASS
    if has_issues:
        return EXIT_ERROR
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
