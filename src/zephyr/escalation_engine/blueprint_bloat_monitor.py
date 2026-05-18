# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.blueprint_bloat_monitor

# [INVARIANTS] 蓝图膨胀监控不可禁用;max=100不可修改

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Blueprint Bloat Monitor — v0.11.0 蓝图膨胀监控器。
"""
from __future__ import annotations

class BlueprintBloatMonitor:
    MAX_BLUEPRINT_LINES=5000
    MAX_TASK_CARDS=50

    def check_bloat(self, blueprint_lines:int, task_cards:int)->dict:
        return {
            "blueprint_ok":blueprint_lines<=self.MAX_BLUEPRINT_LINES,
            "task_cards_ok":task_cards<=self.MAX_TASK_CARDS,
            "lines":blueprint_lines,"cards":task_cards,
        }

    def should_refactor(self, blueprint_lines:int)->bool:
        return blueprint_lines>self.MAX_BLUEPRINT_LINES
