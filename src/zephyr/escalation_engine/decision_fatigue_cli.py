# [BLUEPRINT] MOD-INF-022 | docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md
# [MODULE] zephyr.escalation_engine
# [INVARIANTS] 升级裁决;四级约束;Kill Switch
# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md;src/zephyr/escalation_engine/__init__.py
# [CONSUMERS] MOD-INF-027;MOD-INF-020;MOD-INF-018
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] EscalationError;TimeoutError
# [TESTS] tests/test_escalation_engine/

from __future__ import annotations

import argparse

from .decision_fatigue import EisenhowerPriority, TaskTriage, triage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="zephyr-priorities", description="Eisenhower Matrix 优先级分类看板")
    parser.add_argument("--filter", type=str, default="ALL", help="按优先级筛选: P0/P1/P2/P3/ALL")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sample = [
        TaskTriage(task_id="T01", description="Lock协议检查", urgent=True, important=True),
        TaskTriage(task_id="T02", description="重构性能优化", urgent=False, important=True),
        TaskTriage(task_id="T03", description="格式化文档", urgent=True, important=False),
    ]
    classified = triage(sample)
    if args.filter == "ALL":
        for p in EisenhowerPriority:
            items = classified.get(p, [])
            print(f"{p.value}: {len(items)} tasks")
    else:
        try:
            lvl = EisenhowerPriority(args.filter)
            for t in classified.get(lvl, []):
                print(f"  [{t.priority.value}] {t.task_id}: {t.description}")
        except ValueError:
            print(f"Unknown filter: {args.filter} — use P0/P1/P2/P3/ALL")


if __name__ == "__main__":
    main()
