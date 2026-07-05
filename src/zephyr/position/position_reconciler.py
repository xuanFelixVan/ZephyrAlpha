# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.position.position_reconciler
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 持仓对账必须执行;P0-FATAL必须触发硬中断
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_position_reconciler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Position Reconciler — v0.10.0 持仓对账: execution report+book record+counterparty三方对账。
"""

from __future__ import annotations


class PositionReconciler:
    def __init__(self):
        self._positions: dict[str, dict] = {}

    def reconcile(self, internal: dict, external: dict) -> dict:
        diffs = {}
        all_keys = set(internal.keys()) | set(external.keys())
        for k in all_keys:
            i = internal.get(k, 0)
            e = external.get(k, 0)
            if i != e:
                diffs[k] = {"internal": i, "external": e, "diff": i - e}
        return {"match": len(diffs) == 0, "diffs": diffs, "count": len(diffs)}

    def should_escalate(self, diff_count: int, threshold: int = 3) -> bool:
        return diff_count >= threshold
