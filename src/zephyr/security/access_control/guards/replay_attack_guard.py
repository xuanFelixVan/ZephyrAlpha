# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.guards.replay_attack_guard
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] check returns dict {"allowed": bool, "reason": str}; first-seen nonce -> allowed=True; repeated nonce -> allowed=False
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check never raises; returns {"allowed": False, "reason": ...} on invalid input
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_replay_attack_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ReplayAttackGuard — 重放攻击防护.

依据蓝图 MOD-INF-018 §3:
- 维护已见 nonce 集合
- 第一次出现的 nonce 允许通过
- 重复 nonce 判定为重放攻击并拒绝
"""

from __future__ import annotations

from typing import Any


class ReplayAttackGuard:
    """重放攻击防护器."""

    def __init__(self) -> None:
        self._seen_nonces: set[Any] = set()

    def check(self, nonce: object, timestamp: float | None = None) -> dict:
        """检查重放攻击.

        返回 {"allowed": bool, "reason": str}。
        第一次 nonce -> allowed=True; 重复 nonce -> allowed=False。
        """
        if nonce is None:
            return {
                "allowed": False,
                "reason": "replay_blocked: nonce is None",
            }
        if nonce in self._seen_nonces:
            return {
                "allowed": False,
                "reason": (
                    f"replay_blocked: duplicate nonce={nonce!r} "
                    f"timestamp={timestamp}"
                ),
            }
        self._seen_nonces.add(nonce)
        return {
            "allowed": True,
            "reason": (
                f"replay_allowed: first-seen nonce={nonce!r} "
                f"timestamp={timestamp}"
            ),
        }


__all__ = [
    "ReplayAttackGuard",
]
