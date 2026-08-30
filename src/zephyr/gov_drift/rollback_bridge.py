# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.rollback_bridge
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/gov_drift/_analysis.py ; tests/rollback/test_rollback_bridge.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 漂移->回滚桥接不可禁用
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] BridgeError;RollbackTriggerFailed
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
G-CT-006 契约：Drift -> Rollback 漂移触发回滚.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: rollback_bridge.py
# 层: 算法
# - id: A1
#   name_zh: ① DriftRollbackBridge
#   name_en: DriftRollbackBridge
#   intro: 行为漂移->回滚触发.
#   desc: 行为漂移->回滚触发.；公共方法（定义序）: on_drift_detected；源码 L51-L60
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: DriftRollbackBridge
#   downstream: src/zephyr/gov_drift/_analysis.py ; tests/rollback/test_rollback_bridge.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class DriftRollbackBridge:
    """行为漂移->回滚触发."""

    def on_drift_detected(self, agent_id: str, drift_type: str, severity: str) -> dict:
        return {
            "triggered": severity in {"HIGH", "CRITICAL"},
            "agent_id": agent_id,
            "drift_type": drift_type,
            "action": "ROLLBACK" if severity in {"HIGH", "CRITICAL"} else "OBSERVE",
        }
