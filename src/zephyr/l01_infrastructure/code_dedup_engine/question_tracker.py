# [BLUEPRINT] MOD-INF-017 | 03_modules/l01_infrastructure/code-dedup-engine/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.code_dedup_engine.question_tracker

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""问题追踪——扫描中发现需要人工处理的问题."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Question:
    q_id: str
    category: str
    description: str
    raised_at: str
    status: str = "OPEN"


@dataclass
class QuestionTracker:
    questions: dict[str, Question] = field(default_factory=dict)

    def raise_question(self, q_id: str, category: str, description: str) -> Question:
        q = Question(
            q_id=q_id,
            category=category,
            description=description,
            raised_at=datetime.now(timezone.utc).isoformat(),
        )
        self.questions[q_id] = q
        return q

    def resolve(self, q_id: str) -> None:
        if q_id in self.questions:
            self.questions[q_id].status = "RESOLVED"

    def get_open(self) -> list[Question]:
        return [q for q in self.questions.values() if q.status == "OPEN"]

    def summary(self) -> dict[str, Any]:
        total = len(self.questions)
        open_count = sum(1 for q in self.questions.values() if q.status == "OPEN")
        return {"total_questions": total, "open": open_count, "resolved": total - open_count}
