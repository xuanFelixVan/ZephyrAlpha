# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain-data/datasource-core/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.default_quality_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_enforcement.quality_gate; zephyr.shared.contracts.errors.data_quality_error
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
# [A_module] module_id=MOD-DAT_default_quality_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: data
# category: quality_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_DATA — Default Data Quality Gate

数据质量门禁具体实现。对齐 DataQualityGate (OCP 扩展点) + CTR-ERR-001 (DataQualityError)。

核心职责：
  - 行情质量评分（缺失/异常/延迟/停牌检测）
  - 不合格数据自动拒绝
  - 质量问题分级告警

CTR 契约：
  生产者 — CTR-ERR-001 (DataQualityError) -> D_FACTOR

SSoT: cross_layer_contracts.yaml -> CTR-ERR-001
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from zephyr.governance.rule_enforcement.quality_gate import (
    DataQualityGate,
    QualityFailureReason,
    QualityReport,
    RecoveryHint,
)

_logger = logging.getLogger(__name__)

__gate_id__ = "default-quality-gate"


class DefaultQualityGate(DataQualityGate):
    """默认数据质量门禁——5 项质检规则"""

    __gate_id__ = __gate_id__

    def __init__(
        self,
        max_stale_seconds: int = 300,
        max_price_change_pct: float = 0.20,
        min_volume_threshold: int = 0,
    ):
        self._max_stale_seconds = max_stale_seconds
        self._max_price_change_pct = max_price_change_pct
        self._min_volume_threshold = min_volume_threshold

    def check(
        self,
        symbol: str,
        open_price: Decimal,
        high: Decimal,
        low: Decimal,
        close: Decimal,
        volume: Decimal,
        timestamp: datetime,
        prev_close: Decimal | None = None,
    ) -> QualityReport:
        score = 1.0
        failure_reason = None
        failed_field = None
        recovery_hint = RecoveryHint.RETRY

        if close is None or close <= 0:
            return QualityReport(
                symbol=symbol,
                quality_score=0.0,
                passed=False,
                failure_reason=QualityFailureReason.MISSING_TICK,
                failed_field="close",
                failed_value="None",
                recovery_hint=RecoveryHint.SKIP_SYMBOL,
            )

        now = datetime.now(UTC)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)
        lateness = (now - timestamp).total_seconds()
        if lateness > self._max_stale_seconds:
            score -= 0.3
            if failure_reason is None:
                failure_reason = QualityFailureReason.STALE_DATA
                failed_field = "timestamp"
                recovery_hint = RecoveryHint.SWITCH_SOURCE

        if timestamp > now + timedelta(seconds=60):
            score -= 0.5
            failure_reason = QualityFailureReason.TIMESTAMP_FUTURE
            failed_field = "timestamp"

        if high <= 0 or low <= 0:
            score -= 0.3
            if failure_reason is None:
                failure_reason = QualityFailureReason.MISSING_TICK
                failed_field = "high" if high <= 0 else "low"

        if high < low:
            score -= 0.5
            failure_reason = QualityFailureReason.OUTLIER_PRICE
            failed_field = "high_low"

        if prev_close and prev_close > 0:
            change_pct = abs(close - prev_close) / prev_close
            if change_pct > self._max_price_change_pct:
                score -= 0.2
                if failure_reason is None:
                    failure_reason = QualityFailureReason.SUSPENSION_DETECTED

        if volume == 0:
            score -= 0.4
            failure_reason = QualityFailureReason.VOLUME_ZERO
            failed_field = "volume"
            recovery_hint = RecoveryHint.SKIP_SYMBOL

        score = max(0.0, min(1.0, score))
        passed = score >= self.QUALITY_THRESHOLD

        if not passed:
            _logger.warning(
                "Quality gate failed: symbol=%s score=%.2f reason=%s field=%s",
                symbol,
                score,
                failure_reason,
                failed_field,
            )

        return QualityReport(
            symbol=symbol,
            quality_score=score,
            passed=passed,
            failure_reason=failure_reason if not passed else None,
            failed_field=failed_field if not passed else None,
            recovery_hint=recovery_hint if not passed else RecoveryHint.RETRY,
            checked_at=datetime.now(UTC),
        )

    def check_batch(self, data: list[dict]) -> list[QualityReport]:
        """批量质检"""
        reports = []
        for row in data:
            report = self.check(
                symbol=row.get("symbol", ""),
                open_price=Decimal(str(row.get("open", 0))),
                high=Decimal(str(row.get("high", 0))),
                low=Decimal(str(row.get("low", 0))),
                close=Decimal(str(row.get("close", 0))),
                volume=Decimal(str(row.get("volume", 0))),
                timestamp=row.get("timestamp", datetime.now(UTC)),
                prev_close=Decimal(str(row["prev_close"])) if row.get("prev_close") is not None else None,
            )
            reports.append(report)

        passed = sum(1 for r in reports if r.passed)
        _logger.info("Batch quality check: %d/%d passed", passed, len(reports))
        return reports


__all__ = ["DefaultQualityGate"]
