# [A_module] module_id=MOD-INF_a2a_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md

# [MODULE] zephyr.infrastructure.a2a_protocol.layer1_discovery.a2a_registry

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] stable

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""A2A Registry — Agent Card 注册与发现"""


from typing import Dict, List, Optional
from pathlib import Path
import yaml

from .agent_card import AgentCard


class A2ARegistry:
    """Agent Card 注册中心"""

    def __init__(self, registry_path: Optional[Path] = None):
        self._cards: Dict[str, AgentCard] = {}
        self._path = registry_path

    def register(self, card: AgentCard) -> AgentCard:
        self._cards[card.agent_id] = card
        return card

    def discover(self, capability: Optional[str] = None) -> List[AgentCard]:
        if capability:
            return [c for c in self._cards.values() if capability in c.capabilities]
        return list(self._cards.values())

    def get(self, agent_id: str) -> Optional[AgentCard]:
        return self._cards.get(agent_id)

    def unregister(self, agent_id: str) -> bool:
        if agent_id in self._cards:
            del self._cards[agent_id]
            return True
        return False
