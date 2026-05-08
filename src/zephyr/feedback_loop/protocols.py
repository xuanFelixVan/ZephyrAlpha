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
