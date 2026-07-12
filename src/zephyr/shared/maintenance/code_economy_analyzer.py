# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.maintenance.code_economy_analyzer
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.gov_enforcement.rule_enforcement.gate_engine; tests.unit.shared.test_orphan_integration
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
class EconomyReport:
    total_lines: int
    active_lines: int
    dead_lines: int
    reuse_ratio: float
    redundancy_ratio: float


class CodeEconomyAnalyzer:
    def __init__(self):
        self._modules: dict[str, int] = {}
        self._imports: dict[str, int] = {}

    def register_module(self, name: str, lines: int) -> None:
        self._modules[name] = lines

    def register_import(self, module_name: str) -> None:
        self._imports[module_name] = self._imports.get(module_name, 0) + 1

    def analyze(self) -> EconomyReport:
        total = sum(self._modules.values())
        active = sum(v for k, v in self._modules.items() if self._imports.get(k, 0) > 0)
        dead = total - active
        reuse = sum(v for v in self._imports.values() if v > 1) / max(len(self._imports), 1)
        redundancy = dead / total if total > 0 else 0.0
        return EconomyReport(total, active, dead, reuse, redundancy)
