# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.drift_detection.vigil_runtime
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] VIGIL运行时不可禁用;Core Identity不可修改
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_vigil_runtime | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Vigil Runtime — v0.6.0 VIGIL维护运行时: 运维token预算+手动override窗口。
"""

from __future__ import annotations

import time


class VigilRuntime:
    def __init__(self):
        self._token_budget = 2000
        self._tokens_used = 0
        self._override_window_open = False
        self._override_expiry = 0.0

    def consume(self, tokens: int) -> bool:
        if self._tokens_used + tokens > self._token_budget:
            return False
        self._tokens_used += tokens
        return True

    def open_override_window(self, duration_s: float = 600):
        self._override_window_open = True
        self._override_expiry = time.time() + duration_s

    @property
    def override_active(self) -> bool:
        return self._override_window_open and time.time() < self._override_expiry

    def remaining_tokens(self) -> int:
        return max(0, self._token_budget - self._tokens_used)
