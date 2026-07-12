# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.actors.action_selector
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.__init__
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
# [A_module] module_id=MOD-UNK_action_selector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import time
from dataclasses import dataclass, field
from typing import Any

from zephyr.feedback_loop.protocols import ActionType, FeedbackProtocolAdapter


@dataclass
class ActionRecord:
    action_type: ActionType
    timestamp: float
    success: bool


@dataclass
class ActionSelector:
    protocol_adapter: FeedbackProtocolAdapter
    action_priority: list[ActionType] = field(
        default_factory=lambda: [
            ActionType.NOTIFY_OWNER,
            ActionType.ADJUST_THRESHOLD,
            ActionType.REPAIR,
            ActionType.DEPLOY,
            ActionType.SELF_UPGRADE,
            ActionType.REBALANCE,
        ]
    )
    history: list[ActionRecord] = field(default_factory=list)
    retired_actions: dict[str, float] = field(default_factory=dict)
    consecutive_failures: dict[str, int] = field(default_factory=dict)
    RETIRE_SECONDS: int = 7 * 24 * 3600
    MAX_CONSECUTIVE_FAILURES: int = 3
    learning_rate: float = 0.1
    discount_factor: float = 0.9

    def select_action(self, diagnosis: Any) -> ActionType | None:
        now = time.time()
        for at in self.action_priority:
            if at.value in self.retired_actions:
                if now - self.retired_actions[at.value] > self.RETIRE_SECONDS:
                    del self.retired_actions[at.value]
                else:
                    continue
            return at
        return None

    def record_result(self, action_type: ActionType, success: bool) -> None:
        record = ActionRecord(action_type=action_type, timestamp=time.time(), success=success)
        self.history.append(record)
        if success:
            self.consecutive_failures[action_type.value] = 0
        else:
            self.consecutive_failures[action_type.value] = self.consecutive_failures.get(action_type.value, 0) + 1
            if self.consecutive_failures[action_type.value] >= self.MAX_CONSECUTIVE_FAILURES:
                self.retired_actions[action_type.value] = time.time()
                self.consecutive_failures[action_type.value] = 0

    def execute_action(self, action_type: ActionType, payload: dict[str, Any]) -> bool:
        return self.protocol_adapter.dispatch_action(action_type, payload)
