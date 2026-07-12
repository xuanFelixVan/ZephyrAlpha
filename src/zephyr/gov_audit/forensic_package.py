# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.gov_audit.forensic_package
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 证据包不可篡改;因果图必须完整
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_forensic_package | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Forensic Package — v0.8.0 取证就绪: escalation event bundle+hash chain+timestamp。
"""

from __future__ import annotations
from zephyr.shared.io.serialization import dumps

import hashlib
from datetime import UTC, datetime


class ForensicPackage:
    def __init__(self):
        self._events: list[dict] = []
        self._chain: list[str] = []

    def bundle(self, event: dict) -> str:
        serialized = dumps(event, sort_keys=True)
        h = hashlib.sha256(serialized.encode()).hexdigest()
        self._events.append({"hash": h, "timestamp": datetime.now(UTC).isoformat(), "event": event})
        if self._chain:
            prev = self._chain[-1]
            h = hashlib.sha256((prev + serialized).encode()).hexdigest()
        self._chain.append(h)
        return h

    def verify_chain(self) -> bool:
        for i in range(1, len(self._chain)):
            prev = self._chain[i - 1]
            curr_event = dumps(self._events[i]["event"], sort_keys=True)
            expected = hashlib.sha256((prev + curr_event).encode()).hexdigest()
            if expected != self._chain[i]:
                return False
        return True
