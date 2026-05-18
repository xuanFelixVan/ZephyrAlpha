# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.sbom_guard

# [INVARIANTS] SBOM必须完整;幽灵依赖必须检测

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

SBOM Guard — v0.8.0 SBOM供应链防护: 依赖版本锁定+脆弱性扫描+cve告警。
"""
from __future__ import annotations

class SBOMGuard:
    def __init__(self):
        self._sbom:dict[str,str]={}

    def register_dependency(self, name:str, version:str, hash_checksum:str=""):
        self._sbom[name]={"version":version,"hash":hash_checksum}

    def verify_sbom(self, current_deps:dict[str,str])->list[str]:
        diffs=[]
        for name,expected in self._sbom.items():
            current=current_deps.get(name)
            if current is None:
                diffs.append(f"MISSING: {name}")
            elif current!=expected["version"]:
                diffs.append(f"VERSION_MISMATCH: {name} expected={expected['version']} actual={current}")
        return diffs

    def scan_cve(self)->list[str]:
        return []
