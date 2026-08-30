# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.maintenance.slo_review_assistant
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.gov_enforcement.rule_enforcement.gate_engine ; zephyr.infrastructure.capacity_assurance.modules.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: slo_review_assistant.py
# 层: 算法
# - id: A1
#   name_zh: ① SloReviewAssistant
#   name_en: SloReviewAssistant
#   intro: class SloReviewAssistant 源码 L65-L84
#   desc: 公共方法（定义序）: register_slo, update_actual, review, non_compliant；源码 L65-L84
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: SloReviewAssistant
#   downstream: zephyr.gov_enforcement.rule_enforcement.gate_engine ; zephyr.infrastructure.cap…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SloReview:
    slo_name: str
    target: float
    actual: float
    compliance: bool
    gap: float


SloStatus = SloReview


class SloReviewAssistant:
    def __init__(self):
        self._slos: dict[str, tuple[float, float]] = {}

    def register_slo(self, name: str, target: float) -> None:
        self._slos[name] = (target, 0.0)

    def update_actual(self, name: str, actual: float) -> None:
        if name in self._slos:
            target, _ = self._slos[name]
            self._slos[name] = (target, actual)

    def review(self) -> list[SloReview]:
        results = []
        for name, (target, actual) in self._slos.items():
            results.append(SloReview(name, target, actual, actual >= target, max(0.0, target - actual)))
        return results

    def non_compliant(self) -> list[SloReview]:
        return [r for r in self.review() if not r.compliance]
