# [A_module] module_id=MOD-SHR_core_integrity_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
