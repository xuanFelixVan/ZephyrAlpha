# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer2_communication.message_router
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.layer2_communication.a2a_schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Message Router — A2A 消息路由"""

from collections.abc import Callable

from .a2a_schemas import A2AMessage, PartType


class MessageRouter:
    def __init__(self):
        self._handlers: dict[PartType, list[Callable]] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def handlers(self) -> dict[PartType, list[Callable]]:
        """只读：handlers（Stage 4 公共化）。"""
        return self._handlers

    @handlers.setter
    def handlers(self, value):
        """写入：handlers（Stage 4 公共化）。"""
        self._handlers = value

    def register_handler(self, part_type: PartType, handler: Callable):
        self._handlers.setdefault(part_type, []).append(handler)

    def route(self, message: A2AMessage) -> dict[str, list]:
        results: dict[str, list] = {}
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
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    results[part.part_type.value].append({"error": str(e)})
        return results
