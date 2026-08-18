# [BLUEPRINT] MOD-L00-005 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TESTS] zephyr.data.cross_source_validator
# [DOMAIN] D_DATA
# [TTL] task_bound
"""cross_source_validator 单元测试（P1-4 多源交叉校验）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from decimal import Decimal
from unittest.mock import MagicMock, patch

from zephyr.data.cross_source_validator import (
    CrossSourceValidator,
    ValidationReport,
)


class TestValidationReport:
    def test_healthy_when_no_failures(self):
        report = ValidationReport(check_time=None, failures=0)
        assert report.is_healthy is True

    def test_unhealthy_when_failures(self):
        report = ValidationReport(check_time=None, failures=1)
        assert report.is_healthy is False

    def test_summary_string(self):
        report = ValidationReport(
            check_time=None, total_symbols=10, passed=8,
            warnings=1, failures=1, missing_in_backup=2,
        )
        s = report.summary()
        assert "symbols=10" in s
        assert "pass=8" in s
        assert "fail=1" in s


class TestCrossSourceValidator:
    def _mock_ch_response(self, lines: list[str]) -> str:
        """构造 ch_reader.query 返回的 TSV 字符串。"""
        return "\n".join(lines)

    @patch("zephyr.data.cross_source_validator.ch_reader")
    def test_validate_no_data(self, mock_reader):
        """无数据时返回空报告"""
        mock_reader.query.return_value = ""
        validator = CrossSourceValidator()
        report = validator.validate(time_window_minutes=5)
        assert report.total_symbols == 0
        assert report.passed == 0
        assert report.is_healthy is True

    @patch("zephyr.data.cross_source_validator.ch_reader")
    def test_validate_price_pass(self, mock_reader):
        """价格偏差在阈值内 → pass"""
        mock_reader.query.return_value = self._mock_ch_response([
            "000001\tminiqmt\t10.50\t100000",
            "000001\ttdx_backup\t10.51\t100000",
        ])
        validator = CrossSourceValidator(price_threshold=Decimal("0.005"))
        report = validator.validate()
        # price pass + volume pass = 2 passed
        assert report.passed >= 1
        assert report.failures == 0

    @patch("zephyr.data.cross_source_validator.ch_reader")
    def test_validate_price_fail(self, mock_reader):
        """价格偏差超阈值 → fail"""
        mock_reader.query.return_value = self._mock_ch_response([
            "000001\tminiqmt\t11.00\t100000",
            "000001\ttdx_backup\t10.50\t100000",
        ])
        validator = CrossSourceValidator(price_threshold=Decimal("0.001"))
        report = validator.validate()
        assert report.failures >= 1
        assert not report.is_healthy

    @patch("zephyr.data.cross_source_validator.ch_reader")
    def test_validate_missing_in_backup(self, mock_reader):
        """主源有但备源无 → warn + missing_in_backup"""
        mock_reader.query.return_value = self._mock_ch_response([
            "000001\tminiqmt\t10.50\t100000",
        ])
        validator = CrossSourceValidator()
        report = validator.validate()
        assert report.missing_in_backup == 1
        assert report.warnings >= 1

    @patch("zephyr.data.cross_source_validator.ch_reader")
    def test_validate_missing_in_primary(self, mock_reader):
        """备源有但主源无 → fail + missing_in_primary"""
        mock_reader.query.return_value = self._mock_ch_response([
            "000001\ttdx_backup\t10.50\t100000",
        ])
        validator = CrossSourceValidator()
        report = validator.validate()
        assert report.missing_in_primary == 1
        assert report.failures >= 1

    @patch("zephyr.data.cross_source_validator.ch_reader")
    def test_validate_volume_warn(self, mock_reader):
        """成交量偏差超阈值 → warn"""
        mock_reader.query.return_value = self._mock_ch_response([
            "000001\tminiqmt\t10.50\t120000",
            "000001\ttdx_backup\t10.50\t100000",
        ])
        validator = CrossSourceValidator(volume_threshold=Decimal("0.01"))
        report = validator.validate()
        # volume 20% > 1% threshold → warn
        assert report.warnings >= 1

    @patch("zephyr.data.ch_writer")
    @patch("zephyr.data.cross_source_validator.ch_reader")
    def test_validate_writes_log(self, mock_reader, mock_writer):
        """校验结果写入 cross_validation_log"""
        mock_reader.query.return_value = self._mock_ch_response([
            "000001\tminiqmt\t11.00\t100000",
            "000001\ttdx_backup\t10.50\t100000",
        ])
        validator = CrossSourceValidator(price_threshold=Decimal("0.001"))
        validator.validate()
        # ch_writer.query 被调用写入日志
        assert mock_writer.query.called

    @patch("zephyr.data.cross_source_validator.ch_reader")
    def test_validate_malformed_line_skipped(self, mock_reader):
        """格式错误的行被跳过"""
        mock_reader.query.return_value = self._mock_ch_response([
            "000001\tminiqmt\t10.50",  # 缺少 volume 列
            "000002\ttdx_backup\t10.50\t100000",
        ])
        validator = CrossSourceValidator()
        report = validator.validate()
        # 只有 000002 被处理（备源 only → missing_in_primary）
        assert report.missing_in_primary == 1
