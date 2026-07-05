# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.detectors.false_completion_detector
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] check_false_completion returns non-None CompletionClaim with .detected/.reason; detected=True when actual_size < expected_size
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check_false_completion never raises; returns CompletionClaim(detected=False) on equal/greater size
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_false_completion_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FalseCompletionDetector — 虚假完成检测.

依据蓝图 MOD-INF-018 §3:
- 检测 agent 声称完成但实际产出不足的情况
- 当 actual_size < expected_size 时判定为虚假完成
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CompletionClaim:
    """完成声明检测结果."""

    detected: bool
    reason: str
    agent_id: str
    expected_size: int
    actual_size: int


class FalseCompletionDetector:
    """虚假完成检测器."""

    def __init__(self) -> None:
        self._claims: list[dict] = []

    def record_claim(self, agent_id: str, claimed: str, actual: str) -> bool:
        """记录完成声明.

        Args:
            agent_id: agent ID
            claimed: 声称的完成状态
            actual: 实际的完成状态

        Returns:
            bool: True 当声明与实际匹配（非虚假完成）
        """
        is_valid = claimed == actual
        self._claims.append({
            "agent_id": agent_id,
            "claimed": claimed,
            "actual": actual,
            "valid": is_valid,
        })
        return is_valid

    def check_false_completion(
        self,
        agent_id: str,
        expected_size: int,
        actual_size: int,
    ) -> CompletionClaim:
        """检测虚假完成.

        当 actual_size < expected_size 时判定为虚假完成。
        """
        if actual_size < expected_size:
            return CompletionClaim(
                detected=True,
                reason=(
                    f"false_completion: agent={agent_id} "
                    f"expected={expected_size} actual={actual_size} "
                    f"deficit={expected_size - actual_size}"
                ),
                agent_id=agent_id,
                expected_size=expected_size,
                actual_size=actual_size,
            )
        return CompletionClaim(
            detected=False,
            reason=(
                f"ok: agent={agent_id} "
                f"expected={expected_size} actual={actual_size}"
            ),
            agent_id=agent_id,
            expected_size=expected_size,
            actual_size=actual_size,
        )


__all__ = [
    "CompletionClaim",
    "FalseCompletionDetector",
]
