# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.context_evaluator
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
context_evaluator.py — AI 引用率评估 (TASK-014 beta b)
=========================================================
计算 Agent 实际引用了多少注入的 KE，作为上下文效率的可量化指标。
"""

from dataclasses import dataclass, field


@dataclass
class EvaluationReport:
    injected_count: int = 0
    cited_count: int = 0
    citation_rate: float = 0.0  # 0.0~1.0
    unused_ke_ids: list[str] = field(default_factory=list)
    efficiency_score: float = 0.0  # 0-100


class ContextEvaluator:
    """AI 引用率 = 上下文效率评估器。

    citation_rate = cited_ke_count / injected_ke_count

    Using::

        evaluator = ContextEvaluator()
        report = evaluator.evaluate(
            injected_ids=["KE-001", "KE-002", "KE-003"],
            cited_ids=["KE-001", "KE-003"],
        )
        print(f"Citation rate: {report.citation_rate:.1%}")
    """

    def evaluate(
        self,
        injected_ids: list[str],
        cited_ids: list[str],
    ) -> EvaluationReport:
        injected_set = set(injected_ids)
        cited_set = set(cited_ids)
        cited = injected_set & cited_set
        unused = [k for k in injected_ids if k not in cited_set]

        cited_count = len(cited)
        injected_count = len(injected_set)
        citation_rate = cited_count / max(1, injected_count)
        efficiency = round(citation_rate * 100, 1)

        return EvaluationReport(
            injected_count=injected_count,
            cited_count=cited_count,
            citation_rate=round(citation_rate, 4),
            unused_ke_ids=unused,
            efficiency_score=efficiency,
        )

    def batch_evaluate(
        self,
        turns: list[tuple[list[str], list[str]]],
    ) -> list[EvaluationReport]:
        return [self.evaluate(inj, cit) for inj, cit in turns]
