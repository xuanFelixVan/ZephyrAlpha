# [BLUEPRINT] MOD-BT-023 | docs/03_modules/_domain_backtest/anomaly_diagnoser/blueprint.md
# [MODULE] tests.backtest.test_anomaly_diagnoser
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.services.anomaly_diagnoser
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-BT-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-BT-023 Anomaly Diagnoser 单元测试.

覆盖: 各异常规则触发/不触发、严重度分级、修复建议、缺失字段跳过、
空结果、passed判定、配置自定义、frozen不可变、报告统计属性。
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from zephyr.backtest.services.anomaly_diagnoser import (
    Anomaly,
    AnomalyConfig,
    AnomalyDiagnoser,
    DiagnosisError,
    DiagnosisReport,
)
from zephyr.backtest.services.data_quality_checker import Severity

# ============== 辅助函数 ==============


def make_result(**overrides) -> dict:
    """构建正常的回测结果 (无异常)。"""
    base = {
        "strategy_id": "strat_normal",
        "sharpe_ratio": 1.5,
        "win_rate": 0.55,
        "max_drawdown": -0.15,
        "trades_count": 100,
        "annual_return": 0.20,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "benchmark_symbol": "000300",
    }
    base.update(overrides)
    return base


# ============== 配置 ==============


class TestAnomalyConfig:
    def test_defaults(self):
        cfg = AnomalyConfig()
        assert cfg.high_sharpe_threshold == 3.0
        assert cfg.high_win_rate_threshold == 0.80
        assert cfg.deep_drawdown_threshold == -0.50
        assert cfg.min_trades == 30
        assert cfg.min_backtest_days == 252

    def test_custom(self):
        cfg = AnomalyConfig(high_sharpe_threshold=2.0, min_trades=50)
        assert cfg.high_sharpe_threshold == 2.0
        assert cfg.min_trades == 50

    def test_frozen(self):
        cfg = AnomalyConfig()
        with pytest.raises(FrozenInstanceError):
            cfg.high_sharpe_threshold = 5.0  # type: ignore[misc]

    def test_invalid_sharpe_threshold(self):
        with pytest.raises(DiagnosisError):
            AnomalyConfig(high_sharpe_threshold=0)

    def test_invalid_win_rate_threshold(self):
        with pytest.raises(DiagnosisError):
            AnomalyConfig(high_win_rate_threshold=1.5)

    def test_invalid_min_trades(self):
        with pytest.raises(DiagnosisError):
            AnomalyConfig(min_trades=0)


# ============== Frozen Dataclass ==============


class TestFrozenDataclasses:
    def test_anomaly_frozen(self):
        a = Anomaly(rule="test", severity=Severity.WARN, message="msg")
        with pytest.raises(FrozenInstanceError):
            a.rule = "other"  # type: ignore[misc]


# ============== 正常结果 (无异常) ==============


class TestNormalResult:
    def test_no_anomalies(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(make_result())
        # 只有 missing_benchmark 是 INFO, 但 benchmark 已设置 → 无异常
        assert len(report.anomalies) == 0
        assert report.passed is True

    def test_total_checks(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(make_result())
        # 8 checks: sharpe, win_rate, max_dd, annual_return, trades, days, high_return_low_sharpe, benchmark
        assert report.total_checks >= 7


# ============== 性能异常 ==============


class TestPerformanceAnomalies:
    def test_high_sharpe(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(make_result(sharpe_ratio=4.5))
        anomalies = [a for a in report.anomalies if a.rule == "high_sharpe"]
        assert len(anomalies) == 1
        assert anomalies[0].severity is Severity.WARN
        assert "过拟合" in anomalies[0].suggestion

    def test_normal_sharpe_no_alert(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(make_result(sharpe_ratio=1.5))
        assert not any(a.rule == "high_sharpe" for a in report.anomalies)

    def test_high_win_rate(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(make_result(win_rate=0.90))
        anomalies = [a for a in report.anomalies if a.rule == "high_win_rate"]
        assert len(anomalies) == 1
        assert anomalies[0].severity is Severity.WARN
        assert "前瞻偏差" in anomalies[0].suggestion

    def test_normal_win_rate_no_alert(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(make_result(win_rate=0.55))
        assert not any(a.rule == "high_win_rate" for a in report.anomalies)

    def test_deep_drawdown(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(make_result(max_drawdown=-0.60))
        anomalies = [a for a in report.anomalies if a.rule == "deep_drawdown"]
        assert len(anomalies) == 1
        assert anomalies[0].severity is Severity.ERROR
        assert report.passed is False  # ERROR → not passed

    def test_normal_drawdown_no_alert(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(make_result(max_drawdown=-0.15))
        assert not any(a.rule == "deep_drawdown" for a in report.anomalies)

    def test_negative_return(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(make_result(annual_return=-0.10))
        anomalies = [a for a in report.anomalies if a.rule == "negative_return"]
        assert len(anomalies) == 1
        assert anomalies[0].severity is Severity.WARN

    def test_zero_return_no_alert(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(make_result(annual_return=0.0))
        assert not any(a.rule == "negative_return" for a in report.anomalies)


# ============== 统计异常 ==============


class TestStatisticalAnomalies:
    def test_few_trades(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(make_result(trades_count=10))
        anomalies = [a for a in report.anomalies if a.rule == "few_trades"]
        assert len(anomalies) == 1
        assert anomalies[0].severity is Severity.WARN

    def test_sufficient_trades_no_alert(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(make_result(trades_count=100))
        assert not any(a.rule == "few_trades" for a in report.anomalies)

    def test_short_period(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(
            make_result(start_date="2024-06-01", end_date="2024-08-01")
        )
        anomalies = [a for a in report.anomalies if a.rule == "short_period"]
        assert len(anomalies) == 1
        assert anomalies[0].severity is Severity.WARN

    def test_long_period_no_alert(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(
            make_result(start_date="2023-01-01", end_date="2024-12-31")
        )
        assert not any(a.rule == "short_period" for a in report.anomalies)


# ============== 一致性异常 ==============


class TestConsistencyAnomalies:
    def test_high_return_low_sharpe(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(
            make_result(annual_return=0.30, sharpe_ratio=0.3)
        )
        anomalies = [a for a in report.anomalies if a.rule == "high_return_low_sharpe"]
        assert len(anomalies) == 1
        assert anomalies[0].severity is Severity.WARN

    def test_high_return_good_sharpe_no_alert(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(
            make_result(annual_return=0.30, sharpe_ratio=2.0)
        )
        assert not any(a.rule == "high_return_low_sharpe" for a in report.anomalies)

    def test_missing_benchmark(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(make_result(benchmark_symbol=None))
        anomalies = [a for a in report.anomalies if a.rule == "missing_benchmark"]
        assert len(anomalies) == 1
        assert anomalies[0].severity is Severity.INFO

    def test_has_benchmark_no_alert(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(make_result(benchmark_symbol="000300"))
        assert not any(a.rule == "missing_benchmark" for a in report.anomalies)


# ============== 缺失字段 ==============


class TestMissingFields:
    def test_missing_sharpe_skipped(self):
        diag = AnomalyDiagnoser()
        result = make_result()
        del result["sharpe_ratio"]
        report = diag.diagnose(result)
        assert not any(a.rule == "high_sharpe" for a in report.anomalies)

    def test_missing_trades_skipped(self):
        diag = AnomalyDiagnoser()
        result = make_result()
        del result["trades_count"]
        report = diag.diagnose(result)
        assert not any(a.rule == "few_trades" for a in report.anomalies)

    def test_missing_dates_skipped(self):
        diag = AnomalyDiagnoser()
        result = make_result()
        del result["start_date"]
        del result["end_date"]
        report = diag.diagnose(result)
        assert not any(a.rule == "short_period" for a in report.anomalies)

    def test_minimal_result(self):
        """只有 strategy_id。"""
        diag = AnomalyDiagnoser()
        report = diag.diagnose({"strategy_id": "minimal"})
        # missing_benchmark 仍会触发 (INFO)
        assert any(a.rule == "missing_benchmark" for a in report.anomalies)
        assert report.passed is True  # INFO 不影响 passed


# ============== 错误处理 ==============


class TestErrors:
    def test_non_dict_raises(self):
        diag = AnomalyDiagnoser()
        with pytest.raises(DiagnosisError):
            diag.diagnose("not a dict")  # type: ignore[arg-type]

    def test_empty_strategy_id_raises(self):
        diag = AnomalyDiagnoser()
        with pytest.raises(DiagnosisError):
            diag.diagnose({"strategy_id": ""})

    def test_missing_strategy_id_raises(self):
        diag = AnomalyDiagnoser()
        with pytest.raises(DiagnosisError):
            diag.diagnose({"sharpe_ratio": 1.5})

    def test_error_code(self):
        assert DiagnosisError.error_code == "ZA-BT-0023"


# ============== 报告统计 ==============


class TestReportStats:
    def test_error_count(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(make_result(max_drawdown=-0.60))
        assert report.error_count == 1
        assert report.passed is False

    def test_warning_count(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(
            make_result(sharpe_ratio=4.0, win_rate=0.90, trades_count=10)
        )
        assert report.warning_count >= 3
        assert report.error_count == 0
        assert report.passed is True

    def test_info_count(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(make_result(benchmark_symbol=None))
        assert report.info_count == 1

    def test_anomalies_by_severity(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(
            make_result(sharpe_ratio=4.0, benchmark_symbol=None)
        )
        warns = report.anomalies_by_severity(Severity.WARN)
        infos = report.anomalies_by_severity(Severity.INFO)
        assert len(warns) == 1
        assert len(infos) == 1


# ============== 配置自定义 ==============


class TestCustomConfig:
    def test_custom_sharpe_threshold(self):
        cfg = AnomalyConfig(high_sharpe_threshold=2.0)
        diag = AnomalyDiagnoser(cfg)
        # 2.5 > 2.0 (custom) but < 3.0 (default)
        report = diag.diagnose(make_result(sharpe_ratio=2.5))
        assert any(a.rule == "high_sharpe" for a in report.anomalies)

    def test_custom_min_trades(self):
        cfg = AnomalyConfig(min_trades=200)
        diag = AnomalyDiagnoser(cfg)
        report = diag.diagnose(make_result(trades_count=100))
        assert any(a.rule == "few_trades" for a in report.anomalies)

    def test_config_property(self):
        cfg = AnomalyConfig(min_trades=50)
        diag = AnomalyDiagnoser(cfg)
        assert diag.config.min_trades == 50
        assert diag.config is cfg


# ============== datetime 输入 ==============


class TestDatetimeInput:
    def test_datetime_dates(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(
            make_result(
                start_date=datetime(2024, 6, 1),
                end_date=datetime(2024, 8, 1),
            )
        )
        assert any(a.rule == "short_period" for a in report.anomalies)

    def test_datetime_long_period(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(
            make_result(
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2024, 12, 31),
            )
        )
        assert not any(a.rule == "short_period" for a in report.anomalies)


# ============== 多异常组合 ==============


class TestMultipleAnomalies:
    def test_multiple_anomalies(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(
            make_result(
                sharpe_ratio=5.0,
                win_rate=0.95,
                max_drawdown=-0.60,
                trades_count=5,
                annual_return=-0.10,
                benchmark_symbol=None,
            )
        )
        assert report.error_count == 1  # deep_drawdown
        assert report.warning_count >= 4  # high_sharpe, high_win_rate, few_trades, negative_return
        assert report.info_count == 1  # missing_benchmark
        assert report.passed is False

    def test_all_clear(self):
        diag = AnomalyDiagnoser()
        report = diag.diagnose(
            make_result(
                sharpe_ratio=1.5,
                win_rate=0.55,
                max_drawdown=-0.10,
                trades_count=200,
                annual_return=0.15,
                start_date="2023-01-01",
                end_date="2024-12-31",
                benchmark_symbol="000300",
            )
        )
        assert len(report.anomalies) == 0
        assert report.passed is True
