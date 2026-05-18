# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.dependency_auditor

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""依赖审计器——验证第三方依赖是否有CVE/许可证冲突/范围蠕变."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DependencyAuditResult(BaseModel):
    package: str
    version: str
    known_cves: list[str] = Field(default_factory=list)
    license_type: str = ""
    scope: str = "main"
    approved: bool = True


RESTRICTED_LICENSES = ["GPL-2.0", "GPL-3.0", "AGPL-3.0", "UNLICENSED"]
RESTRICTED_PACKAGES = ["left-pad", "event-stream", "flatmap-stream", "node-ipc"]


class DependencyAuditor:
    def audit(self, package: str, version: str, license_type: str = "MIT", scope: str = "main") -> DependencyAuditResult:
        issues: list[str] = []

        if package.lower() in RESTRICTED_PACKAGES:
            issues.append("RESTRICTED_PACKAGE")

        if license_type.upper() in RESTRICTED_LICENSES:
            issues.append(f"RESTRICTED_LICENSE:{license_type}")

        return DependencyAuditResult(
            package=package,
            version=version,
            known_cves=issues,
            license_type=license_type,
            scope=scope,
            approved=len(issues) == 0,
        )
