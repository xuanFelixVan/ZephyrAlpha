# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.bare_repo_scanner
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 裸仓库检测不可跳过;pre_clone检查必须执行
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_bare_repo_scanner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Bare Repo Scanner — v0.14.0 嵌入式裸仓库检测器。
"""

from __future__ import annotations

import os


class BareRepoScanner:
    def scan_directory(self, root_path: str) -> list[str]:
        found = []
        if not os.path.exists(root_path):
            return found
        for root, dirs, _ in os.walk(root_path):
            for d in dirs:
                if d == ".git":
                    full = os.path.join(root, d)
                    head_path = os.path.join(full, "HEAD")
                    config_path = os.path.join(full, "config")
                    if not os.path.exists(head_path) and os.path.exists(config_path):
                        found.append(root)
        return found
