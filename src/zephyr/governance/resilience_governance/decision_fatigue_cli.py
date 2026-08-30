# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.resilience_governance.decision_fatigue_cli
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.resilience_governance.decision_fatigue
# [CONSUMERS] MOD-INF-027;MOD-INF-020;MOD-INF-018
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 升级裁决;四级约束;Kill Switch
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md;src/zephyr/escalation-engine/__init__.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] EscalationError;TimeoutError
# [TESTS] tests/test_escalation_engine/
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: decision_fatigue_cli.py
# 层: 算法
# - id: A1
#   name_zh: ① build_parser
#   name_en: build_parser
#   intro: build_parser() 源码 L67-L70
#   desc: 源码 L67-L70
#   inputs: 无参数
#   outputs: argparse.ArgumentParser
# - id: A2
#   name_zh: ② main
#   name_en: main
#   intro: main() 源码 L73-L92
#   desc: 源码 L73-L92
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: argparse.ArgumentParser
#   name_en: argparse.ArgumentParser
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-020;MOD-INF-018
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import argparse

from zephyr.governance.resilience_governance.decision_fatigue import (
    EisenhowerPriority,
    TaskTriage,
    triage,
)


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
