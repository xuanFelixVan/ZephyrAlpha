# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.context_governance.command_chain_length_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 命令体积门控max=20不可修改;超限必须阻断
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_command_chain_length_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Command Chain Length Gate — v0.13.0 命令体积Deny退化防御器。
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
