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
