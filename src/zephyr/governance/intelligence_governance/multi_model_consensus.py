# [BLUEPRINT] SRC-046 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.intelligence_governance.multi_model_consensus
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.intelligence_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_multi_model_consensus | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from enum import Enum


class ConsensusProtocol(str, Enum):
    MAJORITY = "Majority"
    WEIGHTED = "Weighted"
    UNANIMOUS = "Unanimous"


class DebateRound(str, Enum):
    R1_PROPOSAL = "R1_模型A解答"
    R2_CHALLENGE = "R2_模型B挑战"
    R3_REBUTTAL = "R3_模型A反驳"


def escalate_to_owner(reason: str) -> str:
    return f"ESCALATED: {reason} -> Owner"
