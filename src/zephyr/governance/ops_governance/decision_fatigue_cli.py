# [BLUEPRINT] SRC-057 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] zephyr.governance.decision_fatigue_cli
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.ops_governance.decision_fatigue
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_decision_fatigue_cli | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

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
