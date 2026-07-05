# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §4.1
# [MODULE] zephyr.governance.semantic_audit.issue_aggregator
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.semantic_audit.models
# [CONSUMERS] cli
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 多源聚合去重；按 severity 排序；输出 UnifiedAuditReport
# [MODIFY-GUARD] 修改排序/去重逻辑必须同步蓝图 §4.2 SemanticAuditReport
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空输入返回空 SemanticAuditReport
# [TESTS] tests/semantic-auditor/test_issue_aggregator.py
# [A_module] module_id=MOD-GOV_issue_aggregator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-028 — 问题聚合器 Stage 5

收集各阶段审计结果，去重合并排序输出。
"""

from __future__ import annotations

import logging
from datetime import datetime

from zephyr.governance.semantic_audit.models import (
    AlignmentReport,
    HealResult,
    LLMFixResult,
    SemanticAuditReport,
    Severity,
    TriggerResult,
)

logger = logging.getLogger(__name__)


class IssueAggregator:
    _SEVERITY_ORDER: dict[Severity, int] = {
        Severity.RED: 0,
        Severity.YELLOW: 1,
        Severity.INFO: 2,
    }

    def aggregate(
        self,
        audit_id: str,
        rule_document: str,
        triggers: list[TriggerResult],
        alignments: list[AlignmentReport] | None = None,
        fixes: list[LLMFixResult] | None = None,
        heals: list[HealResult] | None = None,
        duration_ms: int = 0,
        token_used: int = 0,
    ) -> SemanticAuditReport:
        deduped = self._deduplicate(triggers)

        reds: list[dict] = []
        yellows: list[dict] = []
        safety_filtered = 0

        for t in deduped:
            entry = t.model_dump()
            if t.severity is Severity.RED:
                reds.append(entry)
            elif t.severity is Severity.YELLOW:
                yellows.append(entry)
            else:
                safety_filtered += 1

        reds.sort(key=lambda x: self._severity_sort_key(x.get("certainty", 0)))
        yellows.sort(key=lambda x: self._severity_sort_key(x.get("certainty", 0)))

        return SemanticAuditReport(
            audit_id=audit_id,
            rule_document=rule_document,
            total_triggers=len(triggers),
            safety_filtered_out=safety_filtered,
            red_issues=reds,
            yellow_issues=yellows,
            alignment_reports=alignments or [],
            llm_fixes=fixes or [],
            heal_results=heals or [],
            duration_ms=duration_ms,
            token_used=token_used,
            fresh_until=datetime.now(),
        )

    def _deduplicate(self, triggers: list[TriggerResult]) -> list[TriggerResult]:
        seen: dict[str, TriggerResult] = {}
        for t in triggers:
            key = f"{t.trigger_type}:{t.target_location}"
            if key not in seen or (t.severity is Severity.RED and seen[key].severity is not Severity.RED):
                seen[key] = t
        return list(seen.values())

    def _severity_sort_key(self, certainty: float) -> float:
        return -certainty
