# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.license_compliance
# [DOMAIN] D_FBL_VERIFICATION
# [DEPENDENCIES] zephyr.feedback_loop.gates.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_license_compliance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""License Compliance — v0.14.0 R198

Blindspot: Third-party library licenses unchecked; copyleft contamination of proprietary codebase.
Risk: R198 — GPL dependency introduced; legal liability from auto-generated code.

Mitigation: SPDX license audit with copyleft alert and dependency policy enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class LicenseRisk(str, Enum):
    PERMISSIVE = "PERMISSIVE"
    COPYLEFT = "COPYLEFT"
    UNKNOWN = "UNKNOWN"
    FORBIDDEN = "FORBIDDEN"


@dataclass
class DependencyLicense:
    package: str
    version: str
    license_spdx: str
    risk: LicenseRisk


@dataclass
class LicenseCompliance:
    dependencies: list[DependencyLicense] = field(default_factory=list)
    forbidden_licenses: set[str] = field(default_factory=lambda: {"AGPL-3.0", "GPL-3.0"})
    copyleft_licenses: set[str] = field(
        default_factory=lambda: {
            "GPL-2.0",
            "GPL-3.0",
            "LGPL-3.0",
            "AGPL-3.0",
            "MPL-2.0",
        }
    )

    def register(self, package: str, version: str, spdx: str) -> LicenseRisk:
        if spdx in self.forbidden_licenses:
            risk = LicenseRisk.FORBIDDEN
        elif spdx in self.copyleft_licenses:
            risk = LicenseRisk.COPYLEFT
        elif spdx in ("MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC"):
            risk = LicenseRisk.PERMISSIVE
        else:
            risk = LicenseRisk.UNKNOWN
        self.dependencies.append(DependencyLicense(package=package, version=version, license_spdx=spdx, risk=risk))
        return risk

    def copyleft_alerts(self) -> list[DependencyLicense]:
        return [d for d in self.dependencies if d.risk in (LicenseRisk.COPYLEFT, LicenseRisk.FORBIDDEN)]
