# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.git_hook_pre_scanner
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Git Hook预扫描不可跳过;risky_patterns必须匹配
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_git_hook_pre_scanner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Git Hook Pre-Scanner — v0.14.0 Git操作Hook预扫描器。
"""

from __future__ import annotations

from typing import Final
SUSPICIOUS_HOOK_CONTENT: Final[list] = ["rm -rf", "git push --force", "curl", "wget", "eval"]


class GitHookPreScanner:
    def scan_hook(self, hook_content: str) -> list[str]:
        return [s for s in SUSPICIOUS_HOOK_CONTENT if s in hook_content]

    def is_safe(self, hook_content: str) -> bool:
        return len(self.scan_hook(hook_content)) == 0
