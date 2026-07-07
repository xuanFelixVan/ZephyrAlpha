# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.governance._base_server
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
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
# [TTL] permanent
# [A_module] module_id=MOD-INF_a2a_base_server | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
import logging

logger = logging.getLogger(__name__)


# class-name-alias: a2a_protocol governance MCP 基类（极简 stub），区别于 infrastructure/_base_server.py 和 integration/mcp/_base_server.py 的完整实现
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
    error_code = "ZA-IF-0012"

    def __init__(self, code=-1, message="", data=None, error_code: str | None = None):
        self.code = code
        self.message = message
        self.data = data or {}
        super().__init__(message)
        if error_code is not None:
            self.error_code = error_code
