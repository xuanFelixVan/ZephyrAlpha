# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.architecture_governance.blueprint_bloat_monitor
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 蓝图膨胀监控不可禁用;max=100不可修改
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_blueprint_bloat_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Blueprint Bloat Monitor — v0.11.0 蓝图膨胀监控器。
"""

from __future__ import annotations


class BlueprintBloatMonitor:
    MAX_BLUEPRINT_LINES = 5000
    MAX_TASK_CARDS = 50

    def check_bloat(self, blueprint_lines: int, task_cards: int) -> dict:
        return {
            "blueprint_ok": blueprint_lines <= self.MAX_BLUEPRINT_LINES,
            "task_cards_ok": task_cards <= self.MAX_TASK_CARDS,
            "lines": blueprint_lines,
            "cards": task_cards,
        }

    def should_refactor(self, blueprint_lines: int) -> bool:
        return blueprint_lines > self.MAX_BLUEPRINT_LINES
