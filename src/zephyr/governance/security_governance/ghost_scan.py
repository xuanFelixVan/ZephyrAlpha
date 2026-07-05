# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.ghost_scan
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 幽灵进程检测不可禁用;内核级验证不可绕过
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_ghost_scan | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Ghost Scan — v0.8.0 幽灵进程检测: lingering process扫描+资源泄漏检测。
"""

from __future__ import annotations


class GhostScanner:
    def __init__(self):
        self._registered_pids: set[str] = set()

    def register(self, pid: str):
        self._registered_pids.add(pid)

    def detect_ghosts(self, active_pids: set[str]) -> list[str]:
        return list(self._registered_pids - active_pids)

    def cleanup(self, pid: str) -> bool:
        self._registered_pids.discard(pid)
        return True
