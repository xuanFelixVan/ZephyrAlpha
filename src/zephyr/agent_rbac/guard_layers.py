# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.guard_layers

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
防护层模块集合 — ColdStartLock, EscalationHandler, AutoGuard

MOD-INF-018 guard_layers package
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from zephyr.shared.contracts.identity.agent_identity import AgentIdentity
from zephyr.agent_rbac.immutable_core import ImmutableCore


class AutoGuardMode(str, Enum):
    OFF = "off"
    LAX = "lax"
    STRICT = "strict"


@dataclass
class AutoGuardResult:
    decision: str = "ALLOW"
    timeout: int = 300
    post_hook_registered: bool = False


class ColdStartLock:
    def __init__(self, immutable_core: Optional[ImmutableCore] = None) -> None:
        self._immutable_core = immutable_core or ImmutableCore()
        self._locked: bool = True
        self._verified_at: float = 0.0

    def verify_and_unlock(self) -> bool:
        result = self._immutable_core.verify_immutable_core_integrity()
        if result.intact:
            self._locked = False
            self._verified_at = time.time()
            return True
        return False

    @property
    def is_locked(self) -> bool:
        return self._locked

    def owner_bypass(self) -> None:
        self._locked = False
        self._verified_at = time.time()


class EscalationHandler:
    LEVELS = ["P0_OWNER", "P1_URGENT", "P2_HIGH", "P3_MEDIUM", "P4_LOW"]

    def __init__(self) -> None:
        self._escalated: list[dict] = []
        self._cooldowns: dict[str, float] = {}

    def escalate(
        self,
        agent_id: str,
        level: str,
        reason: str,
        detail: str = "",
    ) -> str:
        event = {
            "agent_id": agent_id,
            "level": level,
            "reason": reason,
            "detail": detail,
            "timestamp": time.time(),
        }
        self._escalated.append(event)

        if level == "P0_OWNER":
            return "P0_TRIGGERED_NOTIFY_OWNER"
        if level in ("P1_URGENT", "P2_HIGH"):
            return "ESCALATED_AUDIT_ONLY"
        return "LOGGED"

    def should_throttle(self, agent_id: str, window: float = 60.0, max_count: int = 5) -> bool:
        cutoff = time.time() - window
        count = sum(1 for e in self._escalated if e["agent_id"] == agent_id and e["timestamp"] > cutoff)
        return count >= max_count

    def reset_agent(self, agent_id: str) -> None:
        self._escalated = [e for e in self._escalated if e["agent_id"] != agent_id]
        self._cooldowns.pop(agent_id, None)


class AutoGuard:
    def __init__(self) -> None:
        self._mode: AutoGuardMode = AutoGuardMode.LAX
        self._guarded: dict[str, list] = {}

    def allow_with_guard(self, agent: AgentIdentity, operation: str) -> AutoGuardResult:
        timeout = agent.get_auto_guard_timeout()
        self._guarded.setdefault(agent.session_id, []).append({
            "operation": operation,
            "since": time.time(),
            "timeout": timeout,
        })
        return AutoGuardResult(
            decision="AUTO_GUARD",
            timeout=timeout,
            post_hook_registered=True,
        )

    def verify(self, agent_id: str, operation: str, expected: str, actual: str) -> bool:
        return expected == actual

    def get_active_guards(self, agent_id: str) -> list[dict]:
        now = time.time()
        guards = self._guarded.get(agent_id, [])
        active = [g for g in guards if now - g["since"] <= g["timeout"]]
        self._guarded[agent_id] = active
        return active
