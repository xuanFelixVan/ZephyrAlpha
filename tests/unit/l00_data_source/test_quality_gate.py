# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l00_data_source.test_quality_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""
单元测试：src/zephyr/l00_data_source/quality_gate.py
====================================================

覆盖矩阵：
  DataQualityGate (ABC):
    - 抽象类不可实例化 × 1
  QualityReport:
    - frozen × 1
    - 默认值 × 1
  QualityFailureReason:
    - 枚举完整性 × 1
  RecoveryHint:
    - 枚举完整性 × 1
  is_within_normal_range:
    - 主板 ±10% 通过 × 1
    - 主板 ±10% 触发 × 1
    - 科创板/创业板 ±20% 通过 × 1
    - 科创板/创业板 ±20% 触发 × 1
    - 零前收盘价 × 1
    - 自定义 limit_pct × 1
  QUALITY_THRESHOLD:
    - 值为 0.7 × 1
"""

from datetime import datetime
from decimal import Decimal

import pytest
from zephyr.l00_data_source.quality_gate import (
    DataQualityGate,
    QualityFailureReason,
    QualityReport,
    RecoveryHint,
)


class TestDataQualityGateABC:
    def test_abstract_class_cannot_instantiate(self):
        with pytest.raises(TypeError):
            DataQualityGate()


class TestQualityReport:
    def test_frozen(self):
        r = QualityReport(
            symbol="600519",
            quality_score=0.9,
            passed=True,
        )
        with pytest.raises(Exception):
            r.symbol = "000858"

    def test_defaults(self):
        r = QualityReport(
            symbol="600519",
            quality_score=0.9,
            passed=True,
        )
        assert r.failure_reason is None
        assert r.failed_field is None
        assert r.failed_value is None
        assert r.recovery_hint == RecoveryHint.SKIP_SYMBOL
        assert isinstance(r.checked_at, datetime)


class TestQualityFailureReason:
    def test_all_values(self):
        expected = {"missing_tick", "stale_data", "outlier_price", "timestamp_future", "suspension_detected", "volume_zero"}
        actual = {e.value for e in QualityFailureReason}
        assert actual == expected


class TestRecoveryHint:
    def test_all_values(self):
        expected = {"RETRY", "SKIP_SYMBOL", "SWITCH_SOURCE", "HALT"}
        actual = {e.value for e in RecoveryHint}
        assert actual == expected


class TestIsWithinNormalRange:
    def test_mainboard_within_10pct_pass(self):
        assert DataQualityGate.is_within_normal_range(
            Decimal("11.0"), Decimal("10.0"), limit_pct=Decimal("0.10")
        )

    def test_mainboard_exceed_10pct_fail(self):
        assert not DataQualityGate.is_within_normal_range(
            Decimal("11.1"), Decimal("10.0"), limit_pct=Decimal("0.10")
        )

    def test_chinext_within_20pct_pass(self):
        assert DataQualityGate.is_within_normal_range(
            Decimal("12.0"), Decimal("10.0"), limit_pct=Decimal("0.20")
        )

    def test_chinext_exceed_20pct_fail(self):
        assert not DataQualityGate.is_within_normal_range(
            Decimal("12.1"), Decimal("10.0"), limit_pct=Decimal("0.20")
        )

    def test_zero_prev_close_returns_false(self):
        assert not DataQualityGate.is_within_normal_range(
            Decimal("5.0"), Decimal("0")
        )

    def test_default_limit_pct_is_10pct(self):
        assert DataQualityGate.is_within_normal_range(
            Decimal("10.9"), Decimal("10.0")
        )
        assert not DataQualityGate.is_within_normal_range(
            Decimal("11.1"), Decimal("10.0")
        )

    def test_custom_limit_pct(self):
        assert DataQualityGate.is_within_normal_range(
            Decimal("10.5"), Decimal("10.0"), limit_pct=Decimal("0.05")
        )
        assert not DataQualityGate.is_within_normal_range(
            Decimal("10.6"), Decimal("10.0"), limit_pct=Decimal("0.05")
        )


class TestQualityThreshold:
    def test_threshold_is_0_7(self):
        assert DataQualityGate.QUALITY_THRESHOLD == 0.7
