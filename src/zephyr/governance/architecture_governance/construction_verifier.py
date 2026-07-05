# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.architecture_governance.construction_verifier
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 施工验证不可跳过;验证checklist必须完整
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_construction_verifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Construction Verifier — 施工验证器: 任务卡完成度+蓝图一致性检查。
"""

from __future__ import annotations


class ConstructionVerifier:
    def verify_card(self, task_id: str, produced_files: list[str], expected_files: list[str]) -> dict:
        missing = set(expected_files) - set(produced_files)
        extra = set(produced_files) - set(expected_files)
        return {
            "task_id": task_id,
            "match": len(missing) == 0 and len(extra) == 0,
            "missing": list(missing),
            "extra": list(extra),
        }

    def blueprint_consistency(self, blueprint_refs: list[str], actual_files: list[str]) -> float:
        bp_set = set(blueprint_refs)
        actual_set = set(actual_files)
        if not bp_set:
            return 0.0
        return len(bp_set & actual_set) / len(bp_set)
