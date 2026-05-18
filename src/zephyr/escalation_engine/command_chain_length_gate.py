# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.command_chain_length_gate

# [INVARIANTS] 命令体积门控max=20不可修改;超限必须阻断

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Command Chain Length Gate — v0.13.0 命令体积Deny退化防御器。
"""
from __future__ import annotations

class CommandChainGate:
    MAX_LENGTH=5000
    MAX_COMMANDS=20

    def evaluate(self, command_chain:list[str])->tuple[bool,str]:
        total_len=sum(len(c) for c in command_chain)
        if total_len>self.MAX_LENGTH:
            return False,f"Chain length {total_len} > {self.MAX_LENGTH}"
        if len(command_chain)>self.MAX_COMMANDS:
            return False,f"Command count {len(command_chain)} > {self.MAX_COMMANDS}"
        return True,"OK"
