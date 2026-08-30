# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.governance._base_server
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: name 参数
#   fields: 参数 name（无注解）
#   code: _base_server.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① BaseMCPServer
#   name_en: BaseMCPServer
#   intro: class BaseMCPServer 源码 L54-L67
#   desc: 公共方法（定义序）: register_tool, handle_request；源码 L54-L67
#   inputs: name
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: BaseMCPServer
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
