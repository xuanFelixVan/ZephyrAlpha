# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.layer2_communication.message_router

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Message Router — A2A 消息路由"""

from typing import Dict, List, Callable
from .a2a_schemas import A2AMessage, PartType


class MessageRouter:
    def __init__(self):
        self._handlers: Dict[PartType, List[Callable]] = {}

    def register_handler(self, part_type: PartType, handler: Callable):
        self._handlers.setdefault(part_type, []).append(handler)

    def route(self, message: A2AMessage) -> Dict[str, List]:
        results: Dict[str, List] = {}
        for part in message.parts:
            handlers = self._handlers.get(part.part_type, [])
            results[part.part_type.value] = []
            for handler in handlers:
                try:
                    import inspect
                    sig = inspect.signature(handler)
                    params = list(sig.parameters.values())
                    if len(params) >= 1:
                        first_name = params[0].name.lower()
                        if first_name in ("msg", "message", "a2amessage"):
                            result = handler(message)
                        else:
                            result = handler(part.content, part.metadata)
                    else:
                        result = handler(message)
                    results[part.part_type.value].append(result)
                except Exception as e:
                    results[part.part_type.value].append({"error": str(e)})
        return results
