# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.context_governance.command_chain_length_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 命令体积门控max=20不可修改;超限必须阻断
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Command Chain Length Gate — v0.13.0 命令体积Deny退化防御器。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: command_chain_length_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① CommandChainGate
#   name_en: CommandChainGate
#   intro: class CommandChainGate 源码 L51-L61
#   desc: 公共方法（定义序）: evaluate；源码 L51-L61
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: CommandChainGate
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class CommandChainGate:
    MAX_LENGTH = 5000
    MAX_COMMANDS = 20

    def evaluate(self, command_chain: list[str]) -> tuple[bool, str]:
        total_len = sum(len(c) for c in command_chain)
        if total_len > self.MAX_LENGTH:
            return False, f"Chain length {total_len} > {self.MAX_LENGTH}"
        if len(command_chain) > self.MAX_COMMANDS:
            return False, f"Command count {len(command_chain)} > {self.MAX_COMMANDS}"
        return True, "OK"
