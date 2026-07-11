# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.hooks_integrity_guard
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Hooks自编辑防护不可禁用;外部hash必须验证
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_hooks_integrity_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Hooks Integrity Guard — v0.11.0 Hooks自编辑防护器。
"""

from __future__ import annotations


class HooksIntegrityGuard:
    def __init__(self):
        self._hooks_hashes: dict[str, str] = {}

    def register(self, hook_path: str, hash_value: str):
        self._hooks_hashes[hook_path] = hash_value

    def verify(self, hook_path: str, current_hash: str) -> bool:
        expected = self._hooks_hashes.get(hook_path)
        return expected is None or expected == current_hash
