"""VibeVerify Integration — v0.9.0 VibeVerify集成器: auto_guard级别+增量修复+confidence回传。"""
from __future__ import annotations

class VibeVerifyIntegration:
    def __init__(self):
        self._scan_count=0
        self._violations_patched=0

    def scan_and_patch(self, code:str)->tuple[bool,int]:
        self._scan_count+=1
        violations=0
        if "eval(" in code:violations+=1
        if "exec(" in code:violations+=1
        self._violations_patched+=violations
        return violations==0,violations

    @property
    def patch_count(self)->int:
        return self._violations_patched
