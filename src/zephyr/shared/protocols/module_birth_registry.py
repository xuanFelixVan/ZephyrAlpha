# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.protocols.module_birth_registry
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.governance.__init__; tests.unit.shared.test_orphan_integration
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

import time
from dataclasses import dataclass


@dataclass
class BirthRecord:
    module_id: str
    created_at: float
    parent_module: str
    scaffold_method: str


class ModuleBirthRegistry:
    def __init__(self):
        self._records: dict[str, BirthRecord] = {}

    def register(self, module_id: str, parent_module: str = "", scaffold_method: str = "scaffold.py") -> BirthRecord:
        record = BirthRecord(module_id, time.time(), parent_module, scaffold_method)
        self._records[module_id] = record
        return record

    def get(self, module_id: str) -> BirthRecord | None:
        return self._records.get(module_id)

    def get_children(self, parent_module: str) -> list[BirthRecord]:
        return [r for r in self._records.values() if r.parent_module == parent_module]

    def list_all(self) -> list[BirthRecord]:
        return list(self._records.values())
