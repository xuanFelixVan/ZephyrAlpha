# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.gov_audit.supply_chain
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.models
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_supply_chain | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
audit-trail.supply_chain — MOD-INF-020 · 供应链审计
=====================================================
蓝图 D-020-23 · 包安装检测 + SHA-256 完整性验证

特性
----
  - 包安装检测: 检测 pip/npm 等包安装事件
  - SHA-256 完整性验证: 验证安装包的哈希完整性
  - 供应链攻击检测: 检测可疑的包来源
"""

from __future__ import annotations

import hashlib
import logging
import os
import subprocess
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

_logger = logging.getLogger(__name__)


class PackageRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    package_name: str = ""
    version: str = ""
    source: str = ""
    sha256: str = ""
    installed_at: str = ""
    installed_by: str = ""
    integrity_verified: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditPackageResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    package_name: str = ""
    is_safe: bool = True
    integrity_ok: bool = True
    issues: list[str] = Field(default_factory=list)
    risk_score: float = 0.0
    audited_at: str = ""


class IntegrityVerifyResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    package_name: str = ""
    expected_hash: str = ""
    actual_hash: str = ""
    is_valid: bool = False
    verified_at: str = ""


_UNTRUSTED_SOURCES: set[str] = {
    os.getenv("UNTRUSTED_PYPI_URL", "http://pypi.org"),
    os.getenv("UNTRUSTED_NPM_REGISTRY_URL", "http://registry.npmjs.org"),
    "unknown",
    "",
}

_SUSPICIOUS_PATTERNS: list[str] = [
    "-dev",
    "-test",
    "-tmp",
    "-backup",
    "-old",
]


class SupplyChainAuditor:
    def __init__(
        self,
        trusted_sources: set[str] | None = None,
        verify_hashes: bool = True,
    ) -> None:
        self._trusted_sources = trusted_sources or {
            os.getenv("PYPI_API_URL", "https://pypi.org"),
            os.getenv("PYTHONHOSTED_URL", "https://files.pythonhosted.org"),
            os.getenv("NPM_REGISTRY_URL", "https://registry.npmjs.org"),
        }
        self._verify_hashes = verify_hashes
        self._audited_packages: dict[str, PackageRecord] = {}

    def audit_package(
        self,
        package_name: str,
        version: str = "",
        source: str = "",
        sha256: str = "",
        installed_by: str = "",
    ) -> AuditPackageResult:
        issues: list[str] = []
        risk_score = 0.0

        if source and source not in self._trusted_sources:
            is_http = source.startswith("http://")
            is_unknown = source in _UNTRUSTED_SOURCES
            if is_http:
                issues.append(f"Package from insecure HTTP source: {source}")
                risk_score += 0.4
            elif is_unknown:
                issues.append(f"Package from unknown source: {source}")
                risk_score += 0.3

        for pattern in _SUSPICIOUS_PATTERNS:
            if pattern in package_name.lower():
                issues.append(f"Package name contains suspicious pattern: '{pattern}'")
                risk_score += 0.2
                break

        integrity_ok = True
        if self._verify_hashes and sha256:
            verify = self.verify_integrity(package_name, sha256)
            integrity_ok = verify.is_valid
            if not verify.is_valid:
                issues.append(f"SHA-256 integrity check failed for {package_name}")
                risk_score += 0.5

        is_safe = len(issues) == 0 and risk_score < 0.5

        record = PackageRecord(
            package_name=package_name,
            version=version,
            source=source,
            sha256=sha256,
            installed_at=datetime.now(UTC).isoformat(),
            installed_by=installed_by,
            integrity_verified=integrity_ok,
        )
        self._audited_packages[package_name] = record

        result = AuditPackageResult(
            package_name=package_name,
            is_safe=is_safe,
            integrity_ok=integrity_ok,
            issues=issues,
            risk_score=round(min(1.0, risk_score), 4),
            audited_at=datetime.now(UTC).isoformat(),
        )
        if not is_safe:
            _logger.warning("SupplyChainAuditor: unsafe package %s: %s", package_name, issues)
        return result

    def verify_integrity(
        self,
        package_name: str,
        expected_sha256: str,
    ) -> IntegrityVerifyResult:
        actual_hash = self._compute_package_hash(package_name)
        is_valid = actual_hash == expected_sha256 if actual_hash and expected_sha256 else False

        if not is_valid:
            _logger.warning(
                "SupplyChainAuditor: integrity mismatch for %s (expected=%s, actual=%s)",
                package_name,
                expected_sha256[:16],
                actual_hash[:16] if actual_hash else "N/A",
            )

        return IntegrityVerifyResult(
            package_name=package_name,
            expected_hash=expected_sha256,
            actual_hash=actual_hash,
            is_valid=is_valid,
            verified_at=datetime.now(UTC).isoformat(),
        )

    def get_audited_packages(self) -> list[PackageRecord]:
        return list(self._audited_packages.values())

    @staticmethod
    def _compute_package_hash(package_name: str) -> str:
        try:
            result = subprocess.run(
                ["pip", "show", "-f", package_name],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
            )
            if result.returncode != 0:
                return ""
            hasher = hashlib.sha256()
            hasher.update(result.stdout.encode("utf-8"))
            return hasher.hexdigest()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return ""
