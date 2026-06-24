# [BLUEPRINT] MOD-GOVERNANCE
# [MODULE] zephyr.infrastructure.a2a_protocol.governance._base_server
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
import logging

logger = logging.getLogger(__name__)


class BaseMCPServer:
    def __init__(self, name=None):
        self.name = name or "base"
        self._tools = {}

    def register_tool(self, name, handler):
        self._tools[name] = handler

    async def handle_request(self, request):
        method = request.get("method", "")
        handler = self._tools.get(method)
        if handler:
            return await handler(request)
        return {"error": f"Unknown method: {method}"}


class MCPError(Exception):
    def __init__(self, code=-1, message="", data=None):
        self.code = code
        self.message = message
        self.data = data or {}
        super().__init__(message)
