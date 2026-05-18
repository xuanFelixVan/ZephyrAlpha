# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.micro_verifier

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""原子验证器——单次原子check(no-side-effects)用于高频快速验证."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AtomicResult(BaseModel):
    allowed: bool
    latency_us: int = 0
    cached: bool = False
    rule_id: str = ""
    layer: str = ""


class MicroVerifier:
    _CACHE: dict[str, AtomicResult] = {}

    def check(self, agent_id: str, action: str, resource: str) -> AtomicResult:
        cache_key = f"{agent_id}:{action}:{resource}"
        if cache_key in self._CACHE:
            result = self._CACHE[cache_key]
            result.cached = True
            return result

        allowed = action not in ("destroy", "meltdown", "sudo")
        result = AtomicResult(allowed=allowed, latency_us=1, cached=False, rule_id="MV-ATOMIC-001", layer="L0")
        self._CACHE[cache_key] = result
        return result

    def invalidate(self, agent_id: str = "") -> None:
        if agent_id:
            keys = [k for k in self._CACHE if k.startswith(agent_id)]
            for k in keys:
                del self._CACHE[k]
        else:
            self._CACHE.clear()
