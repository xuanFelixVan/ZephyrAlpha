# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.blueprint_tools.blueprint_code_auditor
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
class DriftFinding:
    blueprint_section: str
    code_file: str
    drift_type: str
    description: str


@dataclass
class AuditReport:
    blueprint_path: str
    findings: list[DriftFinding]
    drift_count: int
    compliant: bool


DriftItem = DriftFinding


class BlueprintCodeAuditor:
    def __init__(self):
        self._findings: list[DriftFinding] = []

    def check_file_header(self, blueprint_id: str, code_file: str, header_blueprint_field: str) -> DriftFinding | None:
        if blueprint_id not in header_blueprint_field:
            finding = DriftFinding(
                blueprint_id, code_file, "header_mismatch", f"Blueprint {blueprint_id} not in [BLUEPRINT] field"
            )
            self._findings.append(finding)
            return finding
        return None

    def check_drift(
        self, blueprint_path: str, code_path: str, expected_field: str, actual_value: str | None
    ) -> DriftFinding | None:
        if actual_value is None:
            drift = DriftFinding(
                blueprint_path, code_path, "missing_field", f"Field '{expected_field}' not found in code"
            )
            self._findings.append(drift)
            return drift
        return None

    def audit(self, blueprint_path: str) -> AuditReport:
        return AuditReport(blueprint_path, list(self._findings), len(self._findings), len(self._findings) == 0)

    def get_drifts(self) -> list[DriftFinding]:
        return list(self._findings)

    def clear(self) -> None:
        self._findings.clear()
