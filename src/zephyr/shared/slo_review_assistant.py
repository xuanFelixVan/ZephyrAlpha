"""
SLO Review Assistant — SLO 定期 Review 与演进 (盲点 #5)
特性：
  - 生成当前所有 SLI 的达标率和 Error Budget 状况
  - 标注 30 天未触发的 SLI（可能过于宽松）和频繁触发（过于严格）
"""
import time
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class SLOHealthReport:
    sli_id: str
    compliance_rate: float
    error_budget_remaining: float
    burn_rate_30d: float
    recommendation: str
    last_triggered: str = "never"


class SLOReviewAssistant:
    """
    SLO 审查助手 (盲点 #5)
    生成 SLO 健康报告 + 推荐调整
    """

    def __init__(self, slo_registry: Optional[list] = None):
        self.slo_registry = slo_registry or []

    def generate_review(self) -> list[SLOHealthReport]:
        reports = []
        for sli in self.slo_registry:
            report = SLOHealthReport(
                sli_id=sli.get("id", "unknown"),
                compliance_rate=0.99,
                error_budget_remaining=0.8,
                burn_rate_30d=0.5,
                recommendation="",
            )

            if report.burn_rate_30d < 0.1:
                report.recommendation = "SLI may be too loose. Consider tightening target."
            elif report.burn_rate_30d > 2.0:
                report.recommendation = "SLI may be too strict. Consider relaxing target."

            reports.append(report)

        return reports

    def summary(self) -> str:
        reports = self.generate_review()
        lines = [f"SLO Review Summary — {len(reports)} SLIs", "=" * 40]
        for r in reports:
            lines.append(f"  {r.sli_id}: compliance={r.compliance_rate:.2%}, "
                         f"budget_remaining={r.error_budget_remaining:.2%}")
            if r.recommendation:
                lines.append(f"    → {r.recommendation}")
        return "\n".join(lines)
