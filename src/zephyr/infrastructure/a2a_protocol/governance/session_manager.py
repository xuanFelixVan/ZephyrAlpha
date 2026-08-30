# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.governance.session_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.governance.__init__
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
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: session_manager.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SessionManager
#   name_en: SessionManager
#   intro: class SessionManager 源码 L48-L64
#   desc: 公共方法（定义序）: create_session, get_session, end_session；源码 L48-L64
#   inputs: config
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SessionManager
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class SessionManager:
    def __init__(self, config=None):
        self.config = config or {}
        self._sessions = {}

    def create_session(self, agent_id):
        import uuid

        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {"agent_id": agent_id}
        return session_id

    def get_session(self, session_id):
        return self._sessions.get(session_id)

    def end_session(self, session_id):
        self._sessions.pop(session_id, None)
