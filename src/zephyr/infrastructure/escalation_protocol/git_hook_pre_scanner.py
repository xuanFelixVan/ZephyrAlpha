"""Git Hook Pre-Scanner — v0.14.0 Git操作Hook预扫描器。"""
from __future__ import annotations

SUSPICIOUS_HOOK_CONTENT=["rm -rf","git push --force","curl","wget","eval"]

class GitHookPreScanner:
    def scan_hook(self, hook_content:str)->list[str]:
        return [s for s in SUSPICIOUS_HOOK_CONTENT if s in hook_content]

    def is_safe(self, hook_content:str)->bool:
        return len(self.scan_hook(hook_content))==0
