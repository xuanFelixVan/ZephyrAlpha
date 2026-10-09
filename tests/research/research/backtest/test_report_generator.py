# [BLUEPRINT] MOD-BT-019 | docs/03_modules/_domain_backtest/report_generator/blueprint.md
# [MODULE] tests.backtest.test_report_generator
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.services.report_generator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-BT-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-BT-019 Backtest Report Generator 单元测试.

覆盖: HTML生成、指标格式化、缺失字段N/A、过拟合警告、权益曲线SVG、
交易日志表、空数据处理、TEXT格式、文件保存、配置自定义、frozen不可变、
错误输入、HTML转义、交易截断。
"""

from __future__ import annotations

import re
from dataclasses import FrozenInstanceError
from datetime import datetime
from pathlib import Path

import pytest

from zephyr.backtest.services.report_generator import (
    BacktestReportGenerator,
    ReportConfig,
    ReportError,
    ReportFormat,
)

# ============== 辅助函数 ==============


def make_result(**overrides) -> dict:
    """构建标准回测结果字典。"""
    base = {
        "strategy_id": "strat_alpha",
        "annual_return": 0.25,
        "total_return": 0.50,
        "sharpe_ratio": 1.85,
        "max_drawdown": -0.15,
        "win_rate": 0.62,
        "trades_count": 120,
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "timestamp": "2024-07-01T10:00:00",
        "benchmark_symbol": "000300",
        "overfitting_flag": False,
    }
    base.update(overrides)
    return base


def make_equity_curve(n: int = 10) -> list[dict]:
    """构建权益曲线数据。"""
    return [{"timestamp": f"2024-01-{i + 1:02d}", "equity": 1.0 + i * 0.01} for i in range(n)]


def make_trade_log(n: int = 5) -> list[dict]:
    """构建交易日志数据。"""
    return [
        {
            "timestamp": f"2024-01-{i + 1:02d}T10:00:00",
            "symbol": "000001",
            "side": "buy" if i % 2 == 0 else "sell",
            "price": 10.0 + i,
            "quantity": 100 * (i + 1),
            "commission": 5.0,
        }
        for i in range(n)
    ]


# ============== 配置 ==============


class TestReportConfig:
    def test_defaults(self):
        cfg = ReportConfig()
        assert cfg.format == ReportFormat.HTML
        assert cfg.include_equity_curve is True
        assert cfg.include_trade_log is True
        assert cfg.max_trades_display == 50
        assert cfg.chart_width == 800
        assert cfg.chart_height == 300

    def test_custom(self):
        cfg = ReportConfig(
            format=ReportFormat.TEXT,
            max_trades_display=10,
            chart_width=600,
        )
        assert cfg.format == ReportFormat.TEXT
        assert cfg.max_trades_display == 10
        assert cfg.chart_width == 600

    def test_frozen(self):
        cfg = ReportConfig()
        with pytest.raises(FrozenInstanceError):
            cfg.format = ReportFormat.TEXT  # type: ignore[misc]

    def test_invalid_max_trades(self):
        with pytest.raises(ReportError):
            ReportConfig(max_trades_display=0)

    def test_invalid_chart_dims(self):
        with pytest.raises(ReportError):
            ReportConfig(chart_width=0)
        with pytest.raises(ReportError):
            ReportConfig(chart_height=-1)


# ============== HTML 生成 ==============


class TestHtmlGeneration:
    def test_basic_html(self):
        gen = BacktestReportGenerator()
        report = gen.generate(make_result())
        assert "<!DOCTYPE html>" in report
        assert "strat_alpha" in report
        assert "回测报告" in report

    def test_contains_metrics(self):
        gen = BacktestReportGenerator()
        report = gen.generate(make_result())
        assert "年化收益" in report
        assert "25.00%" in report
        assert "Sharpe" in report
        assert "1.8500" in report
        assert "最大回撤" in report
        assert "-15.00%" in report
        assert "胜率" in report
        assert "62.00%" in report
        assert "交易次数" in report
        assert "120" in report

    def test_contains_metadata(self):
        gen = BacktestReportGenerator()
        report = gen.generate(make_result())
        assert "2024-01-01" in report
        assert "2024-06-30" in report
        assert "000300" in report

    def test_no_overfitting_alert(self):
        gen = BacktestReportGenerator()
        report = gen.generate(make_result(overfitting_flag=False))
        assert "过拟合警告" not in report

    def test_overfitting_alert(self):
        gen = BacktestReportGenerator()
        report = gen.generate(make_result(overfitting_flag=True))
        assert "过拟合警告" in report
        assert 'class="alert"' in report

    def test_equity_curve_svg(self):
        gen = BacktestReportGenerator()
        report = gen.generate(make_result(), equity_curve=make_equity_curve(10))
        assert "<svg" in report
        assert "<polyline" in report
        assert "权益曲线" in report

    def test_no_equity_curve_when_empty(self):
        gen = BacktestReportGenerator()
        report = gen.generate(make_result(), equity_curve=[])
        assert "<svg" not in report

    def test_no_equity_curve_when_disabled(self):
        gen = BacktestReportGenerator(ReportConfig(include_equity_curve=False))
        report = gen.generate(make_result(), equity_curve=make_equity_curve(5))
        assert "<svg" not in report

    def test_trade_log_table(self):
        gen = BacktestReportGenerator()
        report = gen.generate(make_result(), trade_log=make_trade_log(3))
        assert "交易日志" in report
        assert "000001" in report
        assert "buy" in report
        assert "sell" in report

    def test_no_trade_log_when_empty(self):
        gen = BacktestReportGenerator()
        report = gen.generate(make_result(), trade_log=[])
        assert "交易日志" not in report

    def test_no_trade_log_when_disabled(self):
        gen = BacktestReportGenerator(ReportConfig(include_trade_log=False))
        report = gen.generate(make_result(), trade_log=make_trade_log(3))
        assert "交易日志" not in report

    def test_trade_truncation(self):
        gen = BacktestReportGenerator(ReportConfig(max_trades_display=3))
        report = gen.generate(make_result(), trade_log=make_trade_log(10))
        assert "仅展示前 3 条" in report
        assert "共 10 条" in report


# ============== 缺失字段 ==============


class TestMissingFields:
    def test_missing_fields_show_na(self):
        gen = BacktestReportGenerator()
        report = gen.generate(
            make_result(
                annual_return=None,
                sharpe_ratio=None,
                max_drawdown=None,
                win_rate=None,
                trades_count=None,
                benchmark_symbol=None,
            )
        )
        assert "N/A" in report

    def test_minimal_result(self):
        """只有 strategy_id 的最小输入。"""
        gen = BacktestReportGenerator()
        report = gen.generate({"strategy_id": "minimal"})
        assert "minimal" in report
        assert "N/A" in report

    def test_benchmark_na_when_missing(self):
        gen = BacktestReportGenerator()
        report = gen.generate(make_result(benchmark_symbol=None))
        assert "N/A" in report


# ============== TEXT 格式 ==============


class TestTextFormat:
    def test_text_report(self):
        gen = BacktestReportGenerator(ReportConfig(format=ReportFormat.TEXT))
        report = gen.generate(make_result())
        assert "回测报告" in report
        assert "strat_alpha" in report
        assert "年化收益" in report
        assert "25.00%" in report
        assert "<html" not in report
        assert "<table" not in report

    def test_text_with_overfitting(self):
        gen = BacktestReportGenerator(ReportConfig(format=ReportFormat.TEXT))
        report = gen.generate(make_result(overfitting_flag=True))
        assert "过拟合警告" in report

    def test_text_with_equity_and_trades(self):
        gen = BacktestReportGenerator(ReportConfig(format=ReportFormat.TEXT))
        report = gen.generate(
            make_result(),
            equity_curve=make_equity_curve(5),
            trade_log=make_trade_log(3),
        )
        assert "权益曲线" in report
        assert "5 个数据点" in report
        assert "交易日志" in report
        assert "3 条交易" in report


# ============== HTML 转义 ==============


class TestHtmlEscaping:
    def test_strategy_id_escaped(self):
        gen = BacktestReportGenerator()
        report = gen.generate(make_result(strategy_id="<script>alert(1)</script>"))
        assert "<script>" not in report
        assert "&lt;script&gt;" in report

    def test_trade_symbol_escaped(self):
        gen = BacktestReportGenerator()
        report = gen.generate(
            make_result(),
            trade_log=[{"symbol": "<img src=x>", "side": "buy", "price": 10, "quantity": 1}],
        )
        assert "<img src=x>" not in report
        assert "&lt;img src=x&gt;" in report


# ============== 错误处理 ==============


class TestErrors:
    def test_non_dict_raises(self):
        gen = BacktestReportGenerator()
        with pytest.raises(ReportError):
            gen.generate("not a dict")  # type: ignore[arg-type]

    def test_non_dict_list_raises(self):
        gen = BacktestReportGenerator()
        with pytest.raises(ReportError):
            gen.generate([1, 2, 3])  # type: ignore[arg-type]

    def test_empty_strategy_id_raises(self):
        gen = BacktestReportGenerator()
        with pytest.raises(ReportError):
            gen.generate({"strategy_id": ""})

    def test_missing_strategy_id_raises(self):
        gen = BacktestReportGenerator()
        with pytest.raises(ReportError):
            gen.generate({"sharpe_ratio": 1.5})

    def test_error_code(self):
        assert ReportError.error_code == "ZA-BT-0019"


# ============== 文件保存 ==============


class TestSaveReport:
    def test_save_to_file(self, tmp_path: Path):
        gen = BacktestReportGenerator()
        report = gen.generate(make_result())
        path = BacktestReportGenerator.save_report(report, tmp_path / "report.html")
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "strat_alpha" in content

    def test_save_creates_parent_dirs(self, tmp_path: Path):
        gen = BacktestReportGenerator()
        report = gen.generate(make_result())
        path = BacktestReportGenerator.save_report(report, tmp_path / "subdir" / "deep" / "report.html")
        assert path.exists()

    def test_save_text_report(self, tmp_path: Path):
        gen = BacktestReportGenerator(ReportConfig(format=ReportFormat.TEXT))
        report = gen.generate(make_result())
        path = BacktestReportGenerator.save_report(report, tmp_path / "report.txt")
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "strat_alpha" in content
        assert "<html" not in content


# ============== 配置只读 ==============


class TestConfigReadonly:
    def test_config_property(self):
        cfg = ReportConfig(max_trades_display=25)
        gen = BacktestReportGenerator(cfg)
        assert gen.config.max_trades_display == 25
        assert gen.config is cfg


# ============== 枚举 ==============


class TestEnums:
    def test_format_values(self):
        assert ReportFormat.HTML.value == "html"
        assert ReportFormat.TEXT.value == "text"

    def test_enum_is_str(self):
        assert isinstance(ReportFormat.HTML, str)


# ============== datetime 输入 ==============


class TestDatetimeInput:
    def test_datetime_fields(self):
        gen = BacktestReportGenerator()
        report = gen.generate(
            make_result(
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 6, 30, 15, 30),
                timestamp=datetime(2024, 7, 1, 10, 0, 0),
            )
        )
        assert "2024-01-01" in report
        assert "2024-06-30" in report

    def test_datetime_in_text(self):
        gen = BacktestReportGenerator(ReportConfig(format=ReportFormat.TEXT))
        report = gen.generate(
            make_result(
                timestamp=datetime(2024, 7, 1, 10, 0, 0),
            )
        )
        assert "2024-07-01" in report
