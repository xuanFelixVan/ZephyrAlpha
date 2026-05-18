# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.intent_binder

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
Intent Binder — 意图绑定与连续验证 (IBAC)

MOD-INF-018 §2.15  D-018-22/D-018-23

Agent 声明施工意图 → 行为预期 → 偏差检测 → 超限阻断.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class IntentState(str, Enum):
    DECLARED = "declared"
    ACTIVE = "active"
    DRIFTED = "drifted"
    EXCEEDED = "exceeded"
    COMPLETED = "completed"


@dataclass
class IntentDeclaration:
    agent_id: str
    file: str
    task: str
    expected_operations: list[str]
    declared_at: float = field(default_factory=time.time)
    state: IntentState = IntentState.DECLARED
    actual_operations: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return self.state not in (IntentState.DRIFTED, IntentState.EXCEEDED)


class IntentBinder:
    def __init__(self) -> None:
        self._intents: dict[str, IntentDeclaration] = {}
        self._drift_threshold: float = 0.3

    def declare(
        self,
        agent_id: str,
        file: str,
        task: str,
        expected_operations: list[str],
    ) -> IntentDeclaration:
        intent = IntentDeclaration(
            agent_id=agent_id,
            file=file,
            task=task,
            expected_operations=list(expected_operations),
            state=IntentState.ACTIVE,
        )
        self._intents[agent_id] = intent
        return intent

    def verify(self, agent_id: str, operation: str) -> bool:
        intent = self._intents.get(agent_id)
        if intent is None:
            return False
        intent.actual_operations.append(operation)
        if operation not in intent.expected_operations:
            intent.violations.append(operation)
            expected_count = len(intent.expected_operations)
            violation_ratio = len(intent.violations) / max(expected_count, 1)
            if violation_ratio > self._drift_threshold:
                intent.state = IntentState.DRIFTED
            return False
        return True

    def check_drift(self, agent_id: str) -> bool:
        intent = self._intents.get(agent_id)
        if intent is None:
            return False
        return intent.state == IntentState.DRIFTED

    def close(self, agent_id: str) -> None:
        intent = self._intents.get(agent_id)
        if intent:
            intent.state = IntentState.COMPLETED

    def get_active_intent(self, agent_id: str) -> Optional[IntentDeclaration]:
        return self._intents.get(agent_id)
