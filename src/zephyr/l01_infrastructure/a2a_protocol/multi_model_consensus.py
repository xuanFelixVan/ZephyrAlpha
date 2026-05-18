# [BLUEPRINT] MOD-INF-025 | docs/03_modules/l01_infrastructure/a2a-protocol/blueprint.md
# [MODULE] zephyr.l01_infrastructure.a2a_protocol
# [INVARIANTS] Agent间通信;冲突解决;四级委托约束
# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/a2a-protocol/blueprint.md;src/zephyr/l01_infrastructure/a2a_protocol/__init__.py
# [CONSUMERS] MOD-INF-027;MOD-INF-018;MOD-INF-022
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CommunicationError;ConflictError;DelegationError
# [TESTS] tests/test_a2a_protocol/

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
    return f"ESCALATED: {reason} → Owner"
