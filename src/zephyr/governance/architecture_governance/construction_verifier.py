# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.architecture_governance.construction_verifier
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 施工验证不可跳过;验证checklist必须完整
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Construction Verifier — 施工验证器: 任务卡完成度+蓝图一致性检查。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: construction_verifier.py
# 层: 算法
# - id: A1
#   name_zh: ① ConstructionVerifier
#   name_en: ConstructionVerifier
#   intro: class ConstructionVerifier 源码 L51-L67
#   desc: 公共方法（定义序）: verify_card, blueprint_consistency；源码 L51-L67
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ConstructionVerifier
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
