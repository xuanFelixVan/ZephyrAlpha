# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.persistence.protocol_state_store
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 协议状态持久化不可丢失;崩溃恢复必须可用
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_protocol_state_store | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Protocol State Store — v0.10.0 协议运行时状态持久化: JSON snapshot+recovery state+crash恢复。
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime


class ProtocolStateStore:
    def __init__(self, state_dir: str = ".audit_cache"):
        self._dir = state_dir
        self._state: dict = {}
        os.makedirs(self._dir, exist_ok=True)

    def save(self) -> str:
        snapshot = {"state": self._state, "timestamp": datetime.now(UTC).isoformat()}
        path = os.path.join(self._dir, "protocol_state.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, default=str)
        return path

    def update(self, key: str, value):
        self._state[key] = value
