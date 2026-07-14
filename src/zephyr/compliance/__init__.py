# [A_module] module_id=MOD-CMP_compliance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L10-001 | docs/03_modules/_domain_compliance/blueprint.md
# [MODULE] zephyr.compliance
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""D_COMPLIANCE Compliance — Re-export wrapper (DM-291)

All modules have been migrated to zephyr.governance.
This package re-exports for backward compatibility.
"""

from __future__ import annotations

__all__ = [
    "AISGSandbox",
    "ArtifactFinding",
    "ArtifactScanner",
    "AuditAction",
    "AuditDecision",
    "ComplianceEngine",
    "ComplianceManagerBase",
    "ComplianceRule",
    "DefaultSecurityGateway",
    "ScanFinding",
    "ScanReport",
    "SecurityContext",
    "SecurityGateway",
    "aisg_sandbox",
    "artifact_scanner",
    "compliance_manager",
    "default_security_gateway",
    "evidence_pack",
    "financial_compliance",
    "integrity",
    "merkle_hourly",
    "security_gateway_base",
]

_LAZY_IMPORTS = {
    "AISGSandbox": ("zephyr.governance.intelligence_governance.aisg_sandbox", "AISGSandbox"),
    "ArtifactFinding": ("zephyr.gov_drift.artifact_scanner", "ArtifactFinding"),
    "ArtifactScanner": ("zephyr.gov_drift.artifact_scanner", "ArtifactScanner"),
    "ScanReport": ("zephyr.gov_drift.artifact_scanner", "ScanReport"),
    "ComplianceManagerBase": ("zephyr.governance.compliance_gate_a6.compliance_manager", "ComplianceManagerBase"),
    "ComplianceRule": ("zephyr.governance.compliance_gate_a6.compliance_manager", "ComplianceRule"),
    "DefaultSecurityGateway": ("zephyr.governance.security_governance.default_security_gateway", "DefaultSecurityGateway"),
    "ScanFinding": ("zephyr.governance.security_governance.default_security_gateway", "ScanFinding"),
    "SecurityContext": ("zephyr.governance.security_governance.default_security_gateway", "SecurityContext"),
    "AuditAction": ("zephyr.governance.security_governance.security_gateway_base", "AuditAction"),
    "AuditDecision": ("zephyr.governance.security_governance.security_gateway_base", "AuditDecision"),
    "ComplianceEngine": ("zephyr.governance.security_governance.security_gateway_base", "ComplianceEngine"),
    "SecurityGateway": ("zephyr.governance.security_governance.security_gateway_base", "SecurityGateway"),
}

_SUBMODULES = [
    "aisg_sandbox",
    "artifact_scanner",
    "compliance_manager",
    "default_security_gateway",
    "security_gateway_base",
]


def __getattr__(name):
    if name in _LAZY_IMPORTS:
        import importlib

        mod_path, attr_name = _LAZY_IMPORTS[name]
        mod = importlib.import_module(mod_path)
        value = getattr(mod, attr_name)
        globals()[name] = value
        return value
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(f"zephyr.governance.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
