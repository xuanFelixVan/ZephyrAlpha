# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.context_governance.protocol_self_context
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 协议自维护上下文不可丢失;session注入必须执行
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Protocol Self Context — v0.10.0 协议自维护上下文管理器。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: protocol_self_context.py
# 层: 算法
# - id: A1
#   name_zh: ① ProtocolSelfContext
#   name_en: ProtocolSelfContext
#   intro: class ProtocolSelfContext 源码 L51-L59
#   desc: 公共方法（定义序）: update_metrics, snapshot；源码 L51-L59
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ProtocolSelfContext
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class ProtocolSelfContext:
    def __init__(self):
        self._context: dict = {"version": "v0.10.0", "active_rules": 0, "last_reconcile": None}

    def update_metrics(self, active_rules: int):
        self._context["active_rules"] = active_rules

    def snapshot(self) -> dict:
        return dict(self._context)
