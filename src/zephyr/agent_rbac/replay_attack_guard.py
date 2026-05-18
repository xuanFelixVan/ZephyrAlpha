# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.replay_attack_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""重放攻击守卫——检测+防御API/Token/请求重放攻击(nonce+窗口)."""
from __future__ import annotations

import hashlib
import time
from typing import Any


class ReplayAttackGuard:
    _WINDOW_SECONDS: int = 300
    _MAX_NONCES: int = 10000

    def __init__(self) -> None:
        self._seen_nonces: dict[str, float] = {}
        self._blocked_count: int = 0

    def check(self, nonce: str, timestamp: float) -> dict[str, Any]:
        now = time.time()
        if abs(now - timestamp) > self._WINDOW_SECONDS:
            return {"allowed": False, "reason": "timestamp_outside_window", "age_seconds": abs(now - timestamp)}

        nonce_hash = hashlib.sha256(nonce.encode()).hexdigest()[:16]
        if nonce_hash in self._seen_nonces:
            self._blocked_count += 1
            return {"allowed": False, "reason": "replay_detected", "nonce_hash": nonce_hash}

        self._seen_nonces[nonce_hash] = now
        self._cleanup()
        return {"allowed": True, "nonce_hash": nonce_hash}

    def _cleanup(self) -> None:
        if len(self._seen_nonces) > self._MAX_NONCES:
            cutoff = time.time() - self._WINDOW_SECONDS
            self._seen_nonces = {k: v for k, v in self._seen_nonces.items() if v > cutoff}
