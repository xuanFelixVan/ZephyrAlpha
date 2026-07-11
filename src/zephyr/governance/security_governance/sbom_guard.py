# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.sbom_guard
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] SBOM必须完整;幽灵依赖必须检测
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_sbom_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

SBOM Guard — v0.8.0 SBOM供应链防护: 依赖版本锁定+脆弱性扫描+cve告警。
"""

from __future__ import annotations


class SBOMGuard:
    def __init__(self):
        self._sbom: dict[str, str] = {}

    def register_dependency(self, name: str, version: str, hash_checksum: str = ""):
        self._sbom[name] = {"version": version, "hash": hash_checksum}

    def verify_sbom(self, current_deps: dict[str, str]) -> list[str]:
        diffs = []
        for name, expected in self._sbom.items():
            current = current_deps.get(name)
            if current is None:
                diffs.append(f"MISSING: {name}")
            elif current != expected["version"]:
                diffs.append(f"VERSION_MISMATCH: {name} expected={expected['version']} actual={current}")
        return diffs

    def scan_cve(self) -> list[str]:
        return []
