# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.collectors.feedback_collector
# [DOMAIN] D_OPS
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_feedback_collector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from collections import deque
from dataclasses import dataclass, field
from enum import Enum


class FeedbackChannel(str, Enum):
    ACTION_RESULT = "action_result"
    OWNER_ACK = "owner_ack"


class OwnerResponse(str, Enum):
    ACK = "ack"
    OVERRIDE = "override"
    IGNORE = "ignore"


@dataclass
class ActionResult:
    action_type: str
    anomaly_id: str
    pre_value: float
    post_value: float
    success_flag: bool
    timestamp: float
    delta: float = 0.0

    def __post_init__(self):
        self.delta = self.post_value - self.pre_value


@dataclass
class OwnerAck:
    anomaly_id: str
    response: OwnerResponse
    timestamp: float
    note: str = ""


@dataclass
class FeedbackCollector:
    window_seconds: float = 300.0
    action_results: deque[ActionResult] = field(default_factory=deque)
    owner_acks: deque[OwnerAck] = field(default_factory=deque)

    def collect_action_result(self, result: ActionResult) -> None:
        self.action_results.append(result)
        self._trim_window()

    def collect_owner_ack(self, ack: OwnerAck) -> None:
        self.owner_acks.append(ack)
        self._trim_window()

    def _trim_window(self) -> None:
        now = max(
            (r.timestamp for r in self.action_results),
            default=0.0,
        )
        cutoff = now - self.window_seconds
        while self.action_results and self.action_results[0].timestamp < cutoff:
            self.action_results.popleft()
        while self.owner_acks and self.owner_acks[0].timestamp < cutoff:
            self.owner_acks.popleft()

    def repair_failure_rate(self) -> float:
        if not self.action_results:
            return 0.0
        failures = sum(1 for r in self.action_results if not r.success_flag)
        return failures / len(self.action_results)

    def owner_override_rate(self) -> float:
        if not self.owner_acks:
            return 0.0
        overrides = sum(1 for a in self.owner_acks if a.response == OwnerResponse.OVERRIDE)
        return overrides / len(self.owner_acks)
