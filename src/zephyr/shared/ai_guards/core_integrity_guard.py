# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.ai_guards.core_integrity_guard
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.governance.__init__; zephyr.gov_enforcement.rule_enforcement.gate_engine; tests.unit.shared.test_orphan_integration
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IntegrityCheck:
    component: str
    is_valid: bool
    intact: bool
    message: str


class CoreIntegrityGuard:
    def __init__(self):
        self._frozen_components: set[str] = set()
        self._checksums: dict[str, str] = {}

    def freeze(self, component: str, checksum: str) -> None:
        self._frozen_components.add(component)
        self._checksums[component] = checksum

    def register_frozen(self, component: str, checksum: str) -> None:
        self.freeze(component, checksum)

    def check(self, component: str, current_checksum: str) -> IntegrityCheck:
        if component not in self._frozen_components:
            return IntegrityCheck(
                component, False, False, "not_frozen: integrity check requires component to be frozen first"
            )
        expected = self._checksums.get(component, "")
        valid = current_checksum == expected
        msg = "checksum_match" if valid else f"expected {expected}, got {current_checksum}"
        return IntegrityCheck(component, valid, valid, msg)

    def is_frozen(self, component: str) -> bool:
        return component in self._frozen_components
