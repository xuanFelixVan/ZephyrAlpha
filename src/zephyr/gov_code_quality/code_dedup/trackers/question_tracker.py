# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.trackers.question_tracker
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/governance_misc/test_question_tracker.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
问题追踪——扫描中发现需要人工处理的问题.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: question_tracker.py
# 层: 算法
# - id: A1
#   name_zh: ① QuestionTracker
#   name_en: QuestionTracker
#   intro: class QuestionTracker 源码 L64-L87
#   desc: 公共方法（定义序）: raise_question, resolve, get_open, summary；源码 L64-L87
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: QuestionTracker
#   downstream: tests/governance/governance_misc/test_question_tracker.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
