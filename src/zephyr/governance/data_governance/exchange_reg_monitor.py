# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.data_governance.exchange_reg_monitor
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 交易所规则变更必须检测;API字段变更必须告警
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Exchange Reg Monitor — v0.11.0 交易所规则变更监控器。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: exchange_reg_monitor.py
# 层: 算法
# - id: A1
#   name_zh: ① ExchangeRegMonitor
#   name_en: ExchangeRegMonitor
#   intro: class ExchangeRegMonitor 源码 L51-L58
#   desc: 公共方法（定义序）: register_change, list_exchanges；源码 L51-L58
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ExchangeRegMonitor
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class ExchangeRegMonitor:
    EXCHANGES = ["SSE", "SZSE", "HKEX", "NYSE", "NASDAQ"]

    def register_change(self, exchange: str, rule_name: str, effective_date: str):
        return {"exchange": exchange, "rule": rule_name, "effective": effective_date, "requires_escalation": True}

    def list_exchanges(self) -> list[str]:
        return self.EXCHANGES
