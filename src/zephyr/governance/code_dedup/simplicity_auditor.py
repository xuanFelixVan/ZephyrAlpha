# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.simplicity_auditor
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/code_quality/test_simplicity_auditor.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_simplicity_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""引擎成本效益自审计器 — SAS 0-100 月度审计 + Tax 报告.

职责：
  - 每月计算 SAS (Simplicity Audit Score) 0-100
  - NET_NEGATIVE -> 自动退役建议
  - 引擎Tax报告：认知负担 + 维护增值税 + TIOBE健康图表
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class SimplicityReport:
    sas: int
    net_negative: bool
    cognitive_burden: int
    maintenance_tax: str
    recommendation: str
    generated_at: str


class SimplicityAuditor:
    """月度 SAS 自审计器."""

    _NET_NEGATIVE_THRESHOLD: int = 50

    def audit(
        self,
        engine_line_count: int = 0,
        bugs_found: int = 0,
        false_positives_last_30d: int = 0,
        total_fixes_applied: int = 0,
        maintenance_hours_per_month: int = 0,
    ) -> SimplicityReport:
        """月度SAS计算."""
        value_score = min(100, total_fixes_applied * 10)
        waste_score = min(100, false_positives_last_30d * 5)
        complexity_penalty = max(0, (engine_line_count // 5000) * 10)

        sas = max(0, min(100, value_score - waste_score - complexity_penalty + 50))

        net_negative = sas < self._NET_NEGATIVE_THRESHOLD

        if net_negative:
            rec = f"NET_NEGATIVE (SAS={sas})——建议缩减引擎范围或退役部分模块。"
        elif sas < 70:
            rec = f"边界效益 (SAS={sas})——月度持续监控。"
        else:
            rec = f"物超所值 (SAS={sas})——引擎投入产出比健康。"

        cognitive = min(100, engine_line_count // 1000 + maintenance_hours_per_month // 2)

        tax = self._compute_tax(engine_line_count, maintenance_hours_per_month)

        return SimplicityReport(
            sas=sas,
            net_negative=net_negative,
            cognitive_burden=cognitive,
            maintenance_tax=tax,
            recommendation=rec,
            generated_at=datetime.now(UTC).isoformat(),
        )

    @staticmethod
    def _compute_tax(lines: int, hours: int) -> str:
        person_years = hours / 2080
        if person_years < 0.25:
            return f"≈{person_years:.1f}人年·低维护成本"
        if person_years < 1:
            return f"≈{person_years:.1f}人年·中等维护成本"
        return f"≈{person_years:.1f}人年·高维护成本——建议审视"
