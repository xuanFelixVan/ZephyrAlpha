# [BLUEPRINT] MOD-RK-19 | docs/03_modules/_domain_risk/operational_risk_monitor/blueprint.md | §
# [MODULE] zephyr.risk.core.operational_risk_monitor
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.risk_manager_base; zephyr.ex_core.audit_journal.auditor
# [CONSUMERS] MOD-L04-001(DefaultRiskManagerOrchestrator,操作风险评估)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 阈值解释层不重算统计;overall_severity=max(failure,latent);纯机制零参数
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidOperationalRiskInputError
# [TESTS] tests/risk/core/test_operational_risk_monitor.py
# [A_module] module_id=MOD-RK-19 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""D_RISK — Operational Risk Monitor (MOD-RK-19)

操作风险审计阈值解释层——在 MOD-EX-003 `compute_operational_risk_stats()`
产出的纯统计数据之上构建薄解释层，将统计转换为风险评估 + 告警。

组装缺口（非从零实现）：MOD-EX-003 (auditor.py) 已提供 OperationalRiskStats
（failure_rate / fill_rate / latency p50/p95/max/mean），但**无阈值告警**。
本模块不重算任何统计，仅做阈值解释 + RiskCheckResult 转换。

核心规则 (blueprint §3):
  failure_rate_breached: failure_rate > failure_rate_threshold (默认 0.05)
  latency_breached: latency_p95_ms > latency_p95_threshold_ms (默认 500.0)
  严重度倍数: 实际值 >= 2×阈值 → severe
  overall_severity:
    - HALT: failure_rate severe OR (failure_rate breached AND latency breached)
    - warning: failure_rate breached OR latency breached (非 HALT)
    - info: 均未突破

日志埋点:
  - INFO: 评估完成（failure_rate + latency_p95 + severity + findings 数）
  - WARNING: 无提交数据（submission_count=0）
  - DEBUG: 逐阈值对比

边界:
  - 不重算统计（MOD-EX-003 真源）
  - 纯延迟（时间差）不依赖 TCA（MOD-EX-012）

SSoT: depgraph MOD-RK-19 | blueprint.md §3 核心规则
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from zephyr.ex_core.audit_journal.auditor import OperationalRiskStats
from zephyr.risk.risk_manager_base import RiskCheckResult

_logger = logging.getLogger(__name__)

__all__ = [
    "OperationalRiskAssessment",
    "OperationalRiskMonitor",
    "InvalidOperationalRiskInputError",
]

#: 失败率告警阈值（5%，行业标准）
DEFAULT_FAILURE_RATE_THRESHOLD: float = 0.05

#: p95 延迟告警阈值（500ms，行业标准）
DEFAULT_LATENCY_P95_THRESHOLD_MS: float = 500.0

#: 严重度倍数（实际值 >= 2×阈值 → severe）
_SEVERE_MULTIPLIER: float = 2.0


class InvalidOperationalRiskInputError(ValueError):
    """操作风险监控输入数据无效。"""


# ── 数据模型 ──────────────────────────────────────────────────────────


@dataclass(frozen=True)
class OperationalRiskAssessment:
    """操作风险评估结果（不可变）。

    包装 MOD-EX-003 的统计数据 + 阈值解释结论。

    Attributes:
        stats: 原始操作风险统计（来自 MOD-EX-003，不修改）
        failure_rate_breached: 失败率是否突破阈值
        latency_breached: p95 延迟是否突破阈值
        failure_rate_severe: 失败率是否严重突破（>=2×阈值）
        latency_severe: p95 延迟是否严重突破（>=2×阈值）
        overall_severity: 综合严重度 info/warning/HALT
        findings: 人类可读的发现清单
        timestamp: 评估时间（UTC）
        idempotency_key: 幂等键
    """

    stats: OperationalRiskStats
    failure_rate_breached: bool
    latency_breached: bool
    failure_rate_severe: bool
    latency_severe: bool
    overall_severity: str
    findings: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    idempotency_key: str = ""


# ── 操作风险监控器 ──────────────────────────────────────────────────


class OperationalRiskMonitor:
    """操作风险审计阈值解释层。

    纯机制零参数：阈值使用行业标准默认值，不重算统计。

    Usage:
        mon = OperationalRiskMonitor()
        stats = audit_logger.compute_operational_risk_stats(start, end)
        assessment = mon.assess(stats)
    """

    def __init__(
        self,
        failure_rate_threshold: float = DEFAULT_FAILURE_RATE_THRESHOLD,
        latency_p95_threshold_ms: float = DEFAULT_LATENCY_P95_THRESHOLD_MS,
    ):
        """初始化操作风险监控器。

        Args:
            failure_rate_threshold: 失败率告警阈值（默认 0.05）
            latency_p95_threshold_ms: p95 延迟告警阈值 ms（默认 500.0）
        """
        self._failure_rate_threshold = failure_rate_threshold
        self._latency_p95_threshold_ms = latency_p95_threshold_ms

    # ── 阈值解释 ──

    def assess(self, stats: OperationalRiskStats) -> OperationalRiskAssessment:
        """将操作风险统计转换为风险评估（阈值解释层）。

        不重算任何统计，仅做阈值对比 + 严重度判定。

        Args:
            stats: MOD-EX-003 产出的操作风险统计

        Returns:
            OperationalRiskAssessment 含突破判定 + 严重度 + findings

        Raises:
            InvalidOperationalRiskInputError: stats 为 None
        """
        if stats is None:
            raise InvalidOperationalRiskInputError("OperationalRiskStats is None")

        failure_rate_severe = (
            stats.failure_rate >= _SEVERE_MULTIPLIER * self._failure_rate_threshold
        )
        latency_severe = (
            stats.latency_p95_ms >= _SEVERE_MULTIPLIER * self._latency_p95_threshold_ms
        )
        failure_rate_breached = stats.failure_rate > self._failure_rate_threshold
        latency_breached = stats.latency_p95_ms > self._latency_p95_threshold_ms

        # 严重度判定
        # - 任一维度 severe（>=2×阈值）→ HALT（系统严重受损）
        # - 双维度都突破（非 severe）→ HALT（复合风险）
        # - 单维度突破（非 severe）→ warning
        # - 均未突破 → info
        if (
            failure_rate_severe
            or latency_severe
            or (failure_rate_breached and latency_breached)
        ):
            overall_severity = "HALT"
        elif failure_rate_breached or latency_breached:
            overall_severity = "warning"
        else:
            overall_severity = "info"

        # 人类可读 findings
        findings: list[str] = []
        if stats.submission_count == 0:
            findings.append(
                "no submissions in period — insufficient data for failure_rate assessment"
            )
            _logger.warning(
                "Operational risk assess: submission_count=0 period=[%s, %s]",
                stats.period_start.isoformat(),
                stats.period_end.isoformat(),
            )
        if failure_rate_severe:
            findings.append(
                f"failure_rate SEVERE: {stats.failure_rate:.4f} "
                f">= {self._failure_rate_threshold * _SEVERE_MULTIPLIER:.4f} "
                f"(2× threshold {self._failure_rate_threshold:.4f})"
            )
        elif failure_rate_breached:
            findings.append(
                f"failure_rate breached: {stats.failure_rate:.4f} "
                f"> threshold {self._failure_rate_threshold:.4f} "
                f"(rejection={stats.rejection_count}/submission={stats.submission_count})"
            )
        if latency_severe:
            findings.append(
                f"latency_p95 SEVERE: {stats.latency_p95_ms:.2f}ms "
                f">= {self._latency_p95_threshold_ms * _SEVERE_MULTIPLIER:.2f}ms "
                f"(2× threshold {self._latency_p95_threshold_ms:.2f}ms)"
            )
        elif latency_breached:
            findings.append(
                f"latency_p95 breached: {stats.latency_p95_ms:.2f}ms "
                f"> threshold {self._latency_p95_threshold_ms:.2f}ms "
                f"(pairs={stats.latency_count})"
            )

        assessment = OperationalRiskAssessment(
            stats=stats,
            failure_rate_breached=failure_rate_breached,
            latency_breached=latency_breached,
            failure_rate_severe=failure_rate_severe,
            latency_severe=latency_severe,
            overall_severity=overall_severity,
            findings=findings,
            timestamp=datetime.now(UTC),
            idempotency_key=f"oprisk-{uuid.uuid4().hex[:8]}",
        )

        _logger.info(
            "Operational risk assessed: failure_rate=%.4f latency_p95=%.2fms "
            "severity=%s findings=%d",
            stats.failure_rate,
            stats.latency_p95_ms,
            overall_severity,
            len(findings),
        )
        _logger.debug(
            "Threshold compare: failure_rate %.4f vs %.4f (severe %.4f); "
            "latency_p95 %.2f vs %.2f (severe %.2f)",
            stats.failure_rate,
            self._failure_rate_threshold,
            self._failure_rate_threshold * _SEVERE_MULTIPLIER,
            stats.latency_p95_ms,
            self._latency_p95_threshold_ms,
            self._latency_p95_threshold_ms * _SEVERE_MULTIPLIER,
        )
        return assessment

    # ── 风控检查结果转换 ──

    def to_risk_check_result(
        self,
        assessment: OperationalRiskAssessment,
    ) -> RiskCheckResult:
        """将 OperationalRiskAssessment 转换为 RiskCheckResult（供编排器聚合）。

        severity 映射:
          - HALT → HALT (passed=False)
          - warning → warning (passed=False)
          - info → info (passed=True)

        Args:
            assessment: 操作风险评估结果

        Returns:
            RiskCheckResult
        """
        severity = assessment.overall_severity
        passed = severity == "info"

        return RiskCheckResult(
            check_id=f"operational-risk-{assessment.idempotency_key}",
            rule_name="operational_risk_monitor",
            passed=passed,
            limit_value=Decimal(str(self._failure_rate_threshold)),
            actual_value=Decimal(str(assessment.stats.failure_rate)),
            message=(
                f"severity={severity} "
                f"failure_rate={assessment.stats.failure_rate:.4f} "
                f"(threshold {self._failure_rate_threshold:.4f}, "
                f"breached={assessment.failure_rate_breached}, "
                f"severe={assessment.failure_rate_severe}) "
                f"latency_p95={assessment.stats.latency_p95_ms:.2f}ms "
                f"(threshold {self._latency_p95_threshold_ms:.2f}ms, "
                f"breached={assessment.latency_breached}, "
                f"severe={assessment.latency_severe}) "
                f"findings={len(assessment.findings)}"
            ),
            severity=severity,
        )
