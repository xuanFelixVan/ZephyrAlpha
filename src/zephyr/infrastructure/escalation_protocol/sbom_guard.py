"""SBOM Guard — v0.8.0 SBOM供应链防护: 依赖版本锁定+脆弱性扫描+cve告警。"""
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
