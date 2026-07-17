# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_agent_blocklist
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/a2a/test_a2a_agent_blocklist.py
# [A_module] module_id=MOD-INF_a2a_agent_blocklist | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
A2A Agent 黑名单管理（重命名自 a2a_protocol_security.py，AI-14 审计 P5 修复）

治本修复(2026-07-17): 重命名自 a2a_protocol_security.py，消除与 a2a_security.py
（A2A 消息 payload 内容威胁扫描器）的命名混淆。原命名导致两个"security"模块
易被 AI 误判为重复责任。

责任边界（命名治本后清晰分离）:
    - 本模块 (a2a_agent_blocklist): agent 级黑名单管理（block/is_blocked）
    - a2a_security.py: A2A 消息 payload 内容威胁扫描（6类威胁：prompt_injection/
      code_execution/credential_leak/path_traversal/denylist_content/oversized_payload）

接口: A2AAgentBlocklist.block(agent_id, reason) / is_blocked(agent_id)
"""


class A2AAgentBlocklist:
    """A2A Agent 黑名单管理器。

    提供 agent 级别的拉黑与查询，用于治理违规 agent 的通信隔离。
    """

    def __init__(self):
        self._blocked_agents: set = set()

    def block(self, agent_id: str, reason: str) -> dict:
        """拉黑指定 agent。

        :param agent_id: agent 标识
        :param reason: 拉黑原因
        :return: 操作结果字典
        """
        self._blocked_agents.add(agent_id)
        return {"agent": agent_id, "blocked": True, "reason": reason}

    def is_blocked(self, agent_id: str) -> bool:
        """查询 agent 是否被拉黑。

        :param agent_id: agent 标识
        :return: True=已拉黑，False=未拉黑
        """
        return agent_id in self._blocked_agents
