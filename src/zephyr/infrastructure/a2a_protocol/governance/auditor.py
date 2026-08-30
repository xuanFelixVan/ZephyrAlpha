# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.governance.auditor
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
G-CT-008 契约：A2A -> Audit 审计 Agent 间通信.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: auditor.py
# 层: 算法
# - id: A1
#   name_zh: ① A2AAuditor
#   name_en: A2AAuditor
#   intro: Agent-to-Agent 通信审计.
#   desc: Agent-to-Agent 通信审计.；公共方法（定义序）: log_message；源码 L63-L81
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: A2AAuditor
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

# STUB: from zephyr.governance.escalation.contracts import AuditWriter
# Reason: zephyr.infrastructure.rollback.contracts does not export AuditWriter yet
try:
    import importlib as _il

    _mod = _il.import_module("zephyr.infrastructure.rollback.contracts")
    AuditWriter = _mod.AuditWriter
except (ImportError, AttributeError):

    class AuditWriter:
        @staticmethod
        def write(**kwargs):
            return kwargs


class A2AAuditor:
    """Agent-to-Agent 通信审计."""

    def log_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        session_id: str = "",
    ) -> dict:
        return AuditWriter.write(
            agent_id=from_agent,
            permission="a2a_message",
            resource=f"a2a://{to_agent}",
            decision_basis=f"A2A->Audit: {message_type}",
            session_id=session_id,
            granted=True,
            metadata={"from": from_agent, "to": to_agent, "type": message_type},
        )
