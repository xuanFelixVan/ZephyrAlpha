# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.protocols
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.__init__
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
# [A_module] module_id=MOD-UNK_protocols | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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
    def dispatch_action(self, action_type: ActionType, payload: dict[str, Any]) -> bool: ...


class AgentCapability:
    def __init__(self, name="", level=0, description=""):
        self.name = name
        self.level = level
        self.description = description

    def __repr__(self):
        return f"AgentCapability({self.name}, level={self.level})"
