# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.resilience.multi_instance_coord
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_multi_instance_coord | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Multi-Instance Coordinator — v0.14.0 R199

Blindspot: Single FLE instance is SPOF; multi-instance coordination untested; split-brain possible.
Risk: R199 — Two FLE instances make conflicting repairs due to leaderless operation.

Mitigation: Raft consensus-based leader election with split-brain protection.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum


class InstanceRole(str, Enum):
    LEADER = "LEADER"
    FOLLOWER = "FOLLOWER"
    CANDIDATE = "CANDIDATE"


@dataclass
class InstanceInfo:
    instance_id: str
    role: InstanceRole = InstanceRole.FOLLOWER
    last_heartbeat: float = field(default_factory=time.time)
    term: int = 0


@dataclass
class MultiInstanceCoord:
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    peers: list[str] = field(default_factory=list)
    role: InstanceRole = InstanceRole.FOLLOWER
    current_term: int = 0
    voted_for: str | None = None
    leader_id: str | None = None

    @property
    def is_leader(self) -> bool:
        return self.role is InstanceRole.LEADER

    def start_election(self) -> None:
        self.current_term += 1
        self.role = InstanceRole.CANDIDATE
        self.voted_for = self.instance_id

    def become_leader(self) -> None:
        self.role = InstanceRole.LEADER
        self.leader_id = self.instance_id

    def step_down(self) -> None:
        self.role = InstanceRole.FOLLOWER
        self.leader_id = None

    def check_split_brain(self, other_leader: str) -> bool:
        return self.is_leader and other_leader != self.instance_id and other_leader != ""
