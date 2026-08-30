# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.resilience_governance.account_isolator
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 多账户隔离不可绕过;per-account熔断必须独立
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Account Isolator — v0.10.0 多账户升级隔离器。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: account_isolator.py
# 层: 算法
# - id: A1
#   name_zh: ① AccountIsolator
#   name_en: AccountIsolator
#   intro: class AccountIsolator 源码 L51-L62
#   desc: 公共方法（定义序）: bind, get_policy, isolate_account；源码 L51-L62
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: AccountIsolator
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class AccountIsolator:
    def __init__(self):
        self._bindings: dict[str, str] = {}

    def bind(self, account_id: str, escalation_policy: str):
        self._bindings[account_id] = escalation_policy

    def get_policy(self, account_id: str) -> str:
        return self._bindings.get(account_id, "default_blocked")

    def isolate_account(self, account_id: str) -> bool:
        return account_id in self._bindings
