# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §3.1 Stage 8
# [MODULE] zephyr.governance.semantic_audit.fix_prioritizer
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.semantic_audit.models
# [CONSUMERS] self_healer; cli
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] RED > YELLOW > INFO; 高确定性 > 低确定性; 大 blast_radius > 小 blast_radius
# [MODIFY-GUARD] 修改排序权重必须同步蓝图 §3.2 数据流
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空列表返回空排序结果
# [TESTS] tests/semantic-auditor/test_fix_prioritizer.py
# [A_module] module_id=MOD-GOV_fix_prioritizer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-028 — 修复优先级排序 Stage 8

按 severity -> certainty -> blast_radius 三级排序,分组输出批次。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from zephyr.governance.semantic_audit.models import Severity, TriggerResult

logger = logging.getLogger(__name__)

__all__ = [
    "FixPrioritizer",
    "PrioritizedFix",
]

_SEVERITY_PRIORITY: dict[Severity, int] = {
    Severity.RED: 0,
    Severity.YELLOW: 1,
    Severity.INFO: 2,
}


@dataclass(order=True)
class PrioritizedFix:
    sort_key: float = field(init=False, default=0.0)
    trigger: TriggerResult = field(compare=False)
    blast_radius_score: float = field(compare=False, default=0.0)
    rank: int = field(compare=False, default=0)

    def __post_init__(self) -> None:
        sev = _SEVERITY_PRIORITY.get(self.trigger.severity, 2)
        self.sort_key = sev * 1000 - self.trigger.certainty * 100 - self.blast_radius_score


class FixPrioritizer:
    def prioritize(
        self,
        triggers: list[TriggerResult],
        blast_scores: dict[str, float] | None = None,
    ) -> list[PrioritizedFix]:
        if blast_scores is None:
            blast_scores = {}
        fixes: list[PrioritizedFix] = []
        for t in triggers:
            score = blast_scores.get(t.target_location, 0.0)
            fixes.append(PrioritizedFix(trigger=t, blast_radius_score=score))
        fixes.sort()
        for i, f in enumerate(fixes):
            f.rank = i + 1
        return fixes

    def batch(
        self,
        fixes: list[PrioritizedFix],
        batch_size: int = 5,
    ) -> list[list[PrioritizedFix]]:
        batches: list[list[PrioritizedFix]] = []
        for i in range(0, len(fixes), batch_size):
            batches.append(fixes[i : i + batch_size])
        return batches

    def summary(self, fixes: list[PrioritizedFix]) -> dict[str, Any]:
        reds = [f for f in fixes if f.trigger.severity is Severity.RED]
        yellows = [f for f in fixes if f.trigger.severity is Severity.YELLOW]
        infos = [f for f in fixes if f.trigger.severity is Severity.INFO]
        return {
            "total": len(fixes),
            "red_count": len(reds),
            "yellow_count": len(yellows),
            "info_count": len(infos),
            "top_5": [
                {
                    "rank": f.rank,
                    "target": f.trigger.target_location,
                    "severity": f.trigger.severity.value,
                    "certainty": f.trigger.certainty,
                    "blast_radius": f.blast_radius_score,
                }
                for f in fixes[:5]
            ],
        }
