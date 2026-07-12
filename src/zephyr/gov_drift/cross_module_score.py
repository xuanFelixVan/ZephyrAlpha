# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.cross_module_score
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_analysis.py; tests/cross/test_cross_module_score.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 跨模块评分不可人为调整
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_cross_module_score | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Cross Module Score — cross_module_score.py





module_id: MOD-INF-023


跨模块全局健康度评分（加权平均 + 允许阈值 + rustiness系数）。


对标 blueprint.md §2.19 / D-023-33。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class ModuleScore:
    module_id: str

    health_index: float

    active_drifts: int = 0

    last_resolved_at: datetime | None = None

    rustiness_factor: float = 0.0

    category_score: dict[str, float] = field(default_factory=dict)


@dataclass
class CrossModuleReport:
    overall_score: float

    module_scores: dict[str, ModuleScore] = field(default_factory=dict)

    worst_modules: list[str] = field(default_factory=list)

    rustiness_warnings: list[str] = field(default_factory=list)


class CrossModuleScorer:
    WEIGHT_MAP: dict[str, float] = {"P0": 0.5, "P1": 0.3, "P2": 0.2}

    RUSTINESS_THRESHOLD_DAYS: int = 14

    DISASTER_THRESHOLD: float = 0.0

    ALLOWED_THRESHOLD: float = 0.35

    WARNING_THRESHOLD: float = 0.60

    GATE_PASS_THRESHOLD: float = 0.90

    def __init__(self) -> None:
        self._history: list[CrossModuleReport] = []

    def compute(self, module_scores: dict[str, ModuleScore]) -> CrossModuleReport:
        if not module_scores:
            return CrossModuleReport(overall_score=1.0)

        weighted_sum = 0.0

        weight_total = 0.0

        now = datetime.now(UTC)

        for mid, ms in module_scores.items():
            rustiness = self._compute_rustiness(ms.last_resolved_at, now)

            ms.rustiness_factor = rustiness

            rust_adjusted = max(0.0, ms.health_index - rustiness * 0.1)

            w = self.WEIGHT_MAP.get("P0", 0.5)

            weighted_sum += rust_adjusted * w

            weight_total += w

        overall = weighted_sum / weight_total if weight_total > 0 else 0.0

        worst = sorted(
            module_scores.keys(),
            key=lambda k: module_scores[k].health_index - module_scores[k].rustiness_factor * 0.1,
            reverse=False,
        )[:3]

        rustiness_warnings = [mid for mid, ms in module_scores.items() if ms.rustiness_factor > 0.0]

        report = CrossModuleReport(
            overall_score=round(overall, 4),
            module_scores=module_scores,
            worst_modules=worst,
            rustiness_warnings=rustiness_warnings,
        )

        self._history.append(report)

        return report

    def check_thresholds(self, report: CrossModuleReport) -> dict[str, str]:
        if report.overall_score <= self.DISASTER_THRESHOLD:
            return {"status": "DISASTER", "action": "Meltdown protocol: auto-rollback triggered"}

        elif report.overall_score <= self.ALLOWED_THRESHOLD:
            return {"status": "BAD", "action": "Gate FAIL — forbid promotion"}

        elif report.overall_score <= self.WARNING_THRESHOLD:
            return {"status": "WARNING", "action": "Action Required — run deep scan"}

        elif report.overall_score < self.GATE_PASS_THRESHOLD:
            return {"status": "PASS", "action": "Gate OK"}

        else:
            return {"status": "GOLDEN", "action": "Golden — all clear"}

    def _compute_rustiness(self, last_resolved_at: datetime | None, now: datetime) -> float:
        if last_resolved_at is None:
            return 1.0

        delta = now.replace(tzinfo=None) - last_resolved_at.replace(tzinfo=None)

        if delta.days <= self.RUSTINESS_THRESHOLD_DAYS:
            return 0.0

        days_over = delta.days - self.RUSTINESS_THRESHOLD_DAYS

        return min(1.0, days_over / 60.0)
