# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.monotonic_clock
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] now() returns float >= previous now() call; monotonic non-decreasing across the instance lifetime
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] now() never raises; always returns a float >= last returned value
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_monotonic_clock | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MonotonicClock — 单调时钟.

依据蓝图 MOD-INF-018 §3:
- 提供单调递增的时间戳
- 防止系统时钟回拨导致的安全问题（如 token 重放）
- 基于 time.monotonic() + 内部计数器双保险
"""

from __future__ import annotations

import threading
import time


class MonotonicClock:
    """单调时钟.

    保证 now() 返回值非递减——即使系统时钟回拨也不影响。
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last: float = 0.0

    def now(self) -> float:
        """返回单调递增的时间戳.

        连续调用返回值 >= 前一次返回值。
        """
        with self._lock:
            current = time.monotonic()
            if current < self._last:
                # 系统时钟回拨（理论上 monotonic 不会，但作为防御）
                current = self._last
            self._last = current
            return current

    def verify(self, timestamp: float) -> dict:
        """验证时间戳是否存在漂移.

        检查给定时间戳是否 >= 上一次记录的时间戳（无回拨）。

        Args:
            timestamp: 待验证的时间戳

        Returns:
            dict: {"valid": bool, "reason": str}
        """
        with self._lock:
            if timestamp is None:
                return {"valid": False, "reason": "timestamp is None"}
            try:
                ts = float(timestamp)
            except (TypeError, ValueError):
                return {"valid": False, "reason": "invalid timestamp"}
            if ts < self._last:
                return {
                    "valid": False,
                    "reason": f"clock drift detected: {ts} < {self._last}",
                }
            return {"valid": True, "reason": "no drift"}


__all__ = [
    "MonotonicClock",
]
