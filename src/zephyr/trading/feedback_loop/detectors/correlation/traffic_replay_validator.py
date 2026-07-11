# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.correlation.traffic_replay_validator
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.detectors.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_traffic_replay_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Traffic Replay Validator — v0.14.0 R202

Blindspot: FLE repairs untested against real production traffic patterns.
Risk: R202 — Repair works in sandbox but breaks under real traffic; shadow replay missing.

Mitigation: Production traffic shadow replay with behavior diffing before repair approval.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class ReplayVerdict(str, Enum):
    MATCH = "MATCH"
    DEVIATION = "DEVIATION"
    ERROR = "ERROR"


@dataclass
class ReplaySession:
    session_id: str
    source_endpoint: str
    replay_count: int = 0
    matches: int = 0
    deviations: int = 0
    errors: int = 0
    timestamp: float = field(default_factory=time.time)


@dataclass
class TrafficReplayValidator:
    sessions: list[ReplaySession] = field(default_factory=list)
    deviation_threshold_pct: float = 5.0

    def start_session(self, session_id: str, endpoint: str) -> ReplaySession:
        session = ReplaySession(session_id=session_id, source_endpoint=endpoint)
        self.sessions.append(session)
        return session

    def record_result(self, session_id: str, verdict: ReplayVerdict) -> None:
        for s in self.sessions:
            if s.session_id == session_id:
                s.replay_count += 1
                if verdict is ReplayVerdict.MATCH:
                    s.matches += 1
                elif verdict is ReplayVerdict.DEVIATION:
                    s.deviations += 1
                else:
                    s.errors += 1

    def deviation_rate(self, session_id: str) -> float:
        for s in self.sessions:
            if s.session_id == session_id and s.replay_count > 0:
                return (s.deviations + s.errors) / s.replay_count * 100.0
        return 0.0

    def should_abort(self, session_id: str) -> bool:
        return self.deviation_rate(session_id) > self.deviation_threshold_pct
