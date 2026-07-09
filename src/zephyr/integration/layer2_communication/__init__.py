# [A_module] module_id=MOD-ORC_layer2_communication | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Re-export from shared protocols
# 5.93.6 修复：import * → 显式导入
from zephyr.shared.protocols.a2a.a2a_schemas import (
    A2AMessage,
    A2AMessagePart,
    A2AStateMachine,
    A2ATask,
    A2ATaskStatus,
    ContextPackage,
    HandoffManagerProtocol,
    HandoffRecord,
    MessageRouterProtocol,
    PartType,
    PushNotifierProtocol,
)

__all__ = [
    "A2AMessage",
    "A2AMessagePart",
    "A2AStateMachine",
    "A2ATask",
    "A2ATaskStatus",
    "ContextPackage",
    "HandoffManagerProtocol",
    "HandoffRecord",
    "MessageRouterProtocol",
    "PartType",
    "PushNotifierProtocol",
]

__version__ = "0.10.0"
