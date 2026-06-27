# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.governance.audit_trail
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 不可变审计记录;密码学完整性;只追加
# [MODIFY-GUARD] docs/03_modules/_domain-governance/audit-trail/blueprint.md;src/zephyr/audit-trail/__init__.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] IntegrityError;WriteError
# [TESTS] tests/test_audit_trail/
# [A_module] module_id=MOD-UNK_sbom_generator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class LicenseType(str, Enum):
    MIT = "MIT"
    APACHE2 = "Apache-2.0"
    BSD = "BSD"
    PSF = "PSF"
    UNKNOWN = "UNKNOWN"


ALLOWED_LICENSES: set[LicenseType] = {
    LicenseType.MIT,
    LicenseType.APACHE2,
    LicenseType.BSD,
    LicenseType.PSF,
}


class DepInfo(BaseModel):
    name: str
    version: str
    license: LicenseType = LicenseType.UNKNOWN
    depth: int = 0
    cvss_score: float = 0.0
    cve_ids: list[str] = Field(default_factory=list)


class SBOMReport(BaseModel):
    format: str = "CycloneDX 1.4"
    generated_at: str = ""
    max_depth: int = 5
    dependencies: list[DepInfo] = Field(default_factory=list)
    blocked: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @property
    def depth_exceeded(self) -> list[DepInfo]:
        return [d for d in self.dependencies if d.depth > self.max_depth]

    @property
    def license_violations(self) -> list[DepInfo]:
        return [d for d in self.dependencies if d.license not in ALLOWED_LICENSES and d.license != LicenseType.UNKNOWN]

    @property
    def critical_cves(self) -> list[DepInfo]:
        return [d for d in self.dependencies if d.cvss_score >= 7.0]


def generate_sbom(deps: list[DepInfo]) -> SBOMReport:
    report = SBOMReport(
        generated_at=datetime.now(UTC).isoformat(),
        dependencies=deps,
    )
    for d in deps:
        if d.depth > 5:
            report.warnings.append(f"{d.name} depth={d.depth}>5")
        if d.license not in ALLOWED_LICENSES and d.license != LicenseType.UNKNOWN:
            report.warnings.append(f"{d.name} license={d.license.value} not allowed")
        if d.cvss_score >= 7.0:
            report.blocked.append(f"{d.name} CVSS={d.cvss_score}≥7.0")
    return report
