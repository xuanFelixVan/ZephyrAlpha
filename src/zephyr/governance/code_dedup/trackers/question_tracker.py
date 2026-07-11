# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.trackers.question_tracker
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/governance_misc/test_question_tracker.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_question_tracker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""问题追踪——扫描中发现需要人工处理的问题."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
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
            raised_at=datetime.now(UTC).isoformat(),
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
