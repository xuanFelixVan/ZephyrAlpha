# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.ops_governance.interrupt_handler
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.services.adapter;zephyr.trading
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 硬中断必须立即生效;紧急覆盖必须审计记录
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_interrupt_handler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Interrupt Handler — D-022-06 硬中断处理器: Owner紧急中断+优雅停止+状态保存。
"""

from __future__ import annotations

from enum import Enum


class InterruptSignal(Enum):
    OWNER_OVERRIDE = "owner_override"
    SAFETY_BREACH = "safety_breach"
    HARD_TIMEOUT = "hard_timeout"


class InterruptHandler:
    def __init__(self):
        self._interrupted = False
        self._signal: InterruptSignal | None = None

    def interrupt(self, signal: InterruptSignal) -> None:
        self._interrupted = True
        self._signal = signal

    @property
    def interrupted(self) -> bool:
        return self._interrupted

    def save_state(self) -> dict:
        return {"interrupted": self._interrupted, "signal": self._signal.value if self._signal else None}

    def resume(self) -> bool:
        self._interrupted = False
        self._signal = None
        return True
