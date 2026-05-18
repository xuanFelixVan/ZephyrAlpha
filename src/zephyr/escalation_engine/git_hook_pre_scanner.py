# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.git_hook_pre_scanner

# [INVARIANTS] Git Hook预扫描不可跳过;risky_patterns必须匹配

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Git Hook Pre-Scanner — v0.14.0 Git操作Hook预扫描器。
"""
from __future__ import annotations

SUSPICIOUS_HOOK_CONTENT=["rm -rf","git push --force","curl","wget","eval"]

class GitHookPreScanner:
    def scan_hook(self, hook_content:str)->list[str]:
        return [s for s in SUSPICIOUS_HOOK_CONTENT if s in hook_content]

    def is_safe(self, hook_content:str)->bool:
        return len(self.scan_hook(hook_content))==0
