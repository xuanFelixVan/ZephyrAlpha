# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer1_discovery.a2a_registry
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.layer1_discovery.agent_card
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

"""
A2A Registry — Agent Card 注册与发现

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: registry_path 参数
#   fields: 参数 registry_path（无注解）
#   code: a2a_registry.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① A2ARegistry
#   name_en: A2ARegistry
#   intro: Agent Card 注册中心
#   desc: Agent Card 注册中心；公共方法（定义序）: register, discover, get, unregister；源码 L53-L76
#   inputs: registry_path
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: A2ARegistry
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from pathlib import Path

from .agent_card import AgentCard


class A2ARegistry:
    """Agent Card 注册中心"""

    def __init__(self, registry_path: Path | None = None):
        self._cards: dict[str, AgentCard] = {}
        self._path = registry_path

    def register(self, card: AgentCard) -> AgentCard:
        self._cards[card.agent_id] = card
        return card

    def discover(self, capability: str | None = None) -> list[AgentCard]:
        if capability:
            return [c for c in self._cards.values() if capability in c.capabilities]
        return list(self._cards.values())

    def get(self, agent_id: str) -> AgentCard | None:
        return self._cards.get(agent_id)

    def unregister(self, agent_id: str) -> bool:
        if agent_id in self._cards:
            del self._cards[agent_id]
            return True
        return False
