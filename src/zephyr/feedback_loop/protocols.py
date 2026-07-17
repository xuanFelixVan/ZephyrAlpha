# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.protocols
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.__init__
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

# 治本（裁定#18 G8）：AgentCapability 原为桩类（name/level/description），与测试契约
# (agent_id/capabilities/version + Pydantic model_dump) 完全不符。现改为从
# zephyr.shared.contracts.protocols 重新导出正确的 Pydantic BaseModel 版本。
from zephyr.shared.contracts.protocols import AgentCapability  # noqa: F401 — re-export


class ActionType(str, Enum):
    NOTIFY_OWNER = "NOTIFY_OWNER"
    ADJUST_THRESHOLD = "ADJUST_THRESHOLD"
    REPAIR = "REPAIR"
    DEPLOY = "DEPLOY"
    SELF_UPGRADE = "SELF_UPGRADE"
    REBALANCE = "REBALANCE"


class FeedbackProtocolAdapter(Protocol):
    def dispatch_action(self, action_type: ActionType, payload: dict[str, Any]) -> bool: ...
