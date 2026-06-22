# [A_module] module_id=MOD-GOV__base_server | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
