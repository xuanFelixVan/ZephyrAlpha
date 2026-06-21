# [A_module] module_id=MOD-ORC_context_optimizer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md

# [MODULE] zephyr.orchestration.agent_lifecycle.context_optimizer

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
MOD-INF-019: Agent Spec — Context Optimizer
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.1.0
"""


from typing import Dict, Any


class ContextOptimizer:
    """零上下文启动优化器——前三轮加载Onboarding Skill，第4轮起跳过"""

    ONBOARDING_MAX_ROUNDS = 3

    _conversation_round: Dict[str, int] = {}

    @classmethod
    def should_load_onboarding(cls, session_id: str) -> bool:
        round_num = cls._conversation_round.get(session_id, 0)
        return round_num < cls.ONBOARDING_MAX_ROUNDS

    @classmethod
    def increment_round(cls, session_id: str) -> int:
        cls._conversation_round[session_id] = cls._conversation_round.get(session_id, 0) + 1
        return cls._conversation_round[session_id]
