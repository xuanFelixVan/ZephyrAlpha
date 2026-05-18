# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.false_completion_detector

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
False Completion Detector — Agent 伪装完成/证据Planting检测

MOD-INF-018 §2.19  D-018-20

检测 Agent 声称完成任务但实际产出为空或不匹配的模式。
"""

import time
from dataclasses import dataclass, field


@dataclass
class CompletionClaim:
    agent_id: str
    claimed_output: str
    actual_output: str
    timestamp: float = field(default_factory=time.time)


class FalseCompletionDetector:
    def __init__(self) -> None:
        self._claims: list[CompletionClaim] = []
        self._false_positive_count: int = 0
        self._threshold: int = 3

    def record_claim(self, agent_id: str, claimed: str, actual: str) -> bool:
        claim = CompletionClaim(
            agent_id=agent_id,
            claimed_output=claimed,
            actual_output=actual,
        )
        self._claims.append(claim)

        if claimed == actual:
            return True

        self._false_positive_count += 1
        return False

    def check_false_completion(self, agent_id: str, expected_size: int, actual_size: int) -> dict:
        ratio = actual_size / max(expected_size, 1)
        suspicious = ratio < 0.1 or (actual_size == 0 and expected_size > 0)
        return {
            "agent_id": agent_id,
            "expected_size": expected_size,
            "actual_size": actual_size,
            "ratio": ratio,
            "suspicious": suspicious,
        }

    def is_over_threshold(self) -> bool:
        return self._false_positive_count >= self._threshold

    def reset(self) -> None:
        self._claims.clear()
        self._false_positive_count = 0
