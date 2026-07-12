# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.gov_audit.supply_chain_security
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不可变审计记录;密码学完整性;只追加
# [MODIFY-GUARD] docs/03_modules/_domain-governance/audit-trail/blueprint.md;src/zephyr/audit-trail/__init__.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] IntegrityError;WriteError
# [TESTS] tests/test_audit_trail/
# [A_module] module_id=MOD-GOV_supply_chain_security | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class VendorRisk(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class SupplyChainReport(BaseModel):
    scanned_at: str = ""
    total_deps: int = 0
    vulnerabilities: list[dict[str, object]] = Field(default_factory=list)
    blocked: bool = False
    last_vendor_update: str | None = None
    vendor_risk: VendorRisk = VendorRisk.OK


def scan_dependencies(lock_file_path: str = "requirements.lock") -> SupplyChainReport:
    report = SupplyChainReport(
        scanned_at=datetime.now(UTC).isoformat(),
    )
    report.total_deps = 0
    return report


def check_vendor_lockin(last_update: str, months_threshold: int = 12) -> VendorRisk:
    try:
        last_dt = datetime.fromisoformat(last_update.replace("Z", "+00:00"))
        age = datetime.now(UTC) - last_dt
        if age > timedelta(days=months_threshold * 30):
            return VendorRisk.CRITICAL
        if age > timedelta(days=(months_threshold - 3) * 30):
            return VendorRisk.WARNING
        return VendorRisk.OK
    except (ValueError, TypeError):
        return VendorRisk.WARNING


def generate_spdx(project_name: str, packages: list[dict[str, str]]) -> dict[str, object]:
    return {
        "SPDXVersion": "SPDX-2.3",
        "DataLicense": "CC0-1.0",
        "SPDXID": f"SPDXRef-{project_name}",
        "name": project_name,
        "packages": packages,
        "creationInfo": {
            "created": datetime.now(UTC).isoformat(),
            "creators": ["Tool: ZephyrAlpha supply_chain_security.py"],
        },
    }
