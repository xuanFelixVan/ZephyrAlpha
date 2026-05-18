# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.protocols

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from enum import Enum
from typing import Any, Protocol


class ActionType(str, Enum):
    NOTIFY_OWNER = "NOTIFY_OWNER"
    ADJUST_THRESHOLD = "ADJUST_THRESHOLD"
    REPAIR = "REPAIR"
    DEPLOY = "DEPLOY"
    SELF_UPGRADE = "SELF_UPGRADE"
    REBALANCE = "REBALANCE"


class FeedbackProtocolAdapter(Protocol):
    def dispatch_action(
        self, action_type: ActionType, payload: dict[str, Any]
    ) -> bool:
        ...
