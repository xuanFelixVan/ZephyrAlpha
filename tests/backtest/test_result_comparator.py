# [BLUEPRINT] MOD-BT-024 | docs/03_modules/_domain_backtest/result_comparator/blueprint.md | §
# [MODULE] tests.backtest.test_result_comparator
# [DOMAIN] D_BACKTEST
# [A_module] module_id=MOD-BT-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-BT-024 Result Comparator — 回测结果比较器单元测试。

覆盖: 配置校验、指标比较(better/worse/中性)、相对差异、
显著性检验(交易不足/足够/缺std)、报告生成、空输入、输入校验。
"""

from __future__ import annotations

import pytest

from zephyr.backtest.services.result_comparator import (
    ComparativeMetric,
    ComparisonReport,
    ResultComparator,
    ResultComparisonConfig,
    ResultComparisonError,
)


def make_result(
    *,
    annual_return: float | None = None,
    total_return: float | None = None,
    sharpe_ratio: float | None = None,
    max_drawdown: float | None = None,
    win_rate: float | None = None,
    trades_count: float | None = None,
    annual_return_std: float | None = None,
    sharpe_ratio_std: float | None = None,
) -> dict:
    """构建回测结果 dict, 只包含非 None 字段。"""
    d = {
        "annual_return": annual_return,
        "total_return": total_return,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "win_rate": win_rate,
        "trades_count": trades_count,
        "annual_return_std": annual_return_std,
        "sharpe_ratio_std": sharpe_ratio_std,
    }
    return {k: v for k, v in d.items() if v is not None}


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_default_config(self):
        cfg = ResultComparisonConfig()
        assert cfg.significance_level == 0.05
        assert cfg.min_trades_for_significance == 30
        assert cfg.relative_threshold == 0.10

    def test_invalid_significance_level(self):
        with pytest.raises(ResultComparisonError):
            ResultComparisonConfig(significance_level=0.0)
        with pytest.raises(ResultComparisonError):
            ResultComparisonConfig(significance_level=1.0)

    def test_invalid_min_trades(self):
        with pytest.raises(ResultComparisonError):
            ResultComparisonConfig(min_trades_for_significance=0)

    def test_config_is_frozen(self):
        cfg = ResultComparisonConfig()
        with pytest.raises(Exception):
            cfg.significance_level = 0.01  # type: ignore[misc]


# ──────────────────────────────────────────────────────────────────────────────
# 指标比较
# ──────────────────────────────────────────────────────────────────────────────


class TestCompare:
    def test_compare_better_metrics(self):
        comparator = ResultComparator()
        baseline = make_result(annual_return=0.15, sharpe_ratio=1.2, max_drawdown=-0.2, trades_count=10)
        candidate = make_result(annual_return=0.20, sharpe_ratio=1.5, max_drawdown=-0.15, trades_count=10)
        comp = comparator.compare(baseline, candidate)

        # 年化收益/Sharpe 更好(更高), 最大回撤更好(更高, -0.15 > -0.2)
        assert comp.better_count == 3
        assert comp.worse_count == 0

    def test_compare_worse_metrics(self):
        comparator = ResultComparator()
        baseline = make_result(annual_return=0.20, max_drawdown=-0.10, trades_count=5)
        candidate = make_result(annual_return=0.10, max_drawdown=-0.30, trades_count=5)
        comp = comparator.compare(baseline, candidate)
        # 年化更差, 最大回撤更差(-0.30 < -0.10)
        assert comp.worse_count == 2
        assert comp.better_count == 0

    def test_neutral_metric_trades_count(self):
        comparator = ResultComparator()
        baseline = make_result(trades_count=50, annual_return=0.1)
        candidate = make_result(trades_count=80, annual_return=0.1)
        comp = comparator.compare(baseline, candidate)
        trades_metric = next(m for m in comp.metrics if m.name == "交易次数")
        assert trades_metric.is_better is None  # 中性指标

    def test_missing_fields_become_none(self):
        comparator = ResultComparator()
        baseline = make_result(annual_return=0.1)
        candidate = make_result(sharpe_ratio=1.0)
        comp = comparator.compare(baseline, candidate)
        annual = next(m for m in comp.metrics if m.name == "年化收益")
        assert annual.baseline_value == 0.1
        assert annual.candidate_value is None
        assert annual.absolute_diff is None
        assert annual.relative_diff is None
        assert annual.is_better is None

    def test_total_metrics_count(self):
        comparator = ResultComparator()
        comp = comparator.compare({}, {})
        assert comp.total_metrics == 6  # 6 个标准指标

    def test_relative_diff_calculation(self):
        comparator = ResultComparator()
        baseline = make_result(annual_return=0.10, trades_count=5)
        candidate = make_result(annual_return=0.15, trades_count=5)
        comp = comparator.compare(baseline, candidate)
        annual = next(m for m in comp.metrics if m.name == "年化收益")
        assert annual.absolute_diff == pytest.approx(0.05)
        assert annual.relative_diff == pytest.approx(0.5)  # 0.05/0.10

    def test_relative_diff_baseline_zero_is_none(self):
        comparator = ResultComparator()
        baseline = make_result(annual_return=0.0, trades_count=5)
        candidate = make_result(annual_return=0.1, trades_count=5)
        comp = comparator.compare(baseline, candidate)
        annual = next(m for m in comp.metrics if m.name == "年化收益")
        assert annual.absolute_diff == pytest.approx(0.1)
        assert annual.relative_diff is None  # baseline=0 → None

    def test_custom_ids(self):
        comparator = ResultComparator()
        comp = comparator.compare({}, {}, baseline_id="v1", candidate_id="v2")
        assert comp.baseline_id == "v1"
        assert comp.candidate_id == "v2"

    def test_non_numeric_value_treated_as_none(self):
        comparator = ResultComparator()
        baseline = {"annual_return": "not_a_number", "trades_count": 5}
        candidate = {"annual_return": 0.2, "trades_count": 5}
        comp = comparator.compare(baseline, candidate)
        annual = next(m for m in comp.metrics if m.name == "年化收益")
        assert annual.baseline_value is None
        assert annual.candidate_value == 0.2


# ──────────────────────────────────────────────────────────────────────────────
# 输入校验
# ──────────────────────────────────────────────────────────────────────────────


class TestInputValidation:
    def test_baseline_not_dict(self):
        comparator = ResultComparator()
        with pytest.raises(ResultComparisonError):
            comparator.compare([1, 2, 3], {})

    def test_candidate_not_dict(self):
        comparator = ResultComparator()
        with pytest.raises(ResultComparisonError):
            comparator.compare({}, "not a dict")

    def test_error_code(self):
        assert ResultComparisonError.error_code == "ZA-BT-0024"


# ──────────────────────────────────────────────────────────────────────────────
# 显著性检验
# ──────────────────────────────────────────────────────────────────────────────


class TestSignificance:
    def test_insufficient_trades_not_significant(self):
        comparator = ResultComparator(ResultComparisonConfig(min_trades_for_significance=30))
        baseline = make_result(trades_count=20, annual_return=0.10, annual_return_std=0.02)
        candidate = make_result(trades_count=20, annual_return=0.50, annual_return_std=0.02)
        comp = comparator.compare(baseline, candidate)
        # 交易不足 → 不显著
        assert all(not m.is_significant for m in comp.metrics)

    def test_significant_when_diff_exceeds_se(self):
        comparator = ResultComparator(ResultComparisonConfig(min_trades_for_significance=30, significance_level=0.05))
        # n=100, std=0.01, diff=0.10 → se≈0.001414, z*se≈0.00277 << 0.10 → 显著
        baseline = make_result(trades_count=100, annual_return=0.10, annual_return_std=0.01)
        candidate = make_result(trades_count=100, annual_return=0.20, annual_return_std=0.01)
        comp = comparator.compare(baseline, candidate)
        annual = next(m for m in comp.metrics if m.name == "年化收益")
        assert annual.is_significant is True

    def test_not_significant_when_diff_within_se(self):
        comparator = ResultComparator(ResultComparisonConfig(min_trades_for_significance=30, significance_level=0.05))
        # n=100, std=0.5, diff=0.001 → se≈0.0707, z*se≈0.1386 >> 0.001 → 不显著
        baseline = make_result(trades_count=100, annual_return=0.100, annual_return_std=0.5)
        candidate = make_result(trades_count=100, annual_return=0.101, annual_return_std=0.5)
        comp = comparator.compare(baseline, candidate)
        annual = next(m for m in comp.metrics if m.name == "年化收益")
        assert annual.is_significant is False

    def test_missing_std_not_significant(self):
        comparator = ResultComparator(ResultComparisonConfig(min_trades_for_significance=30))
        baseline = make_result(trades_count=100, annual_return=0.10)
        candidate = make_result(trades_count=100, annual_return=0.50)
        comp = comparator.compare(baseline, candidate)
        # 缺 std → 不显著
        assert all(not m.is_significant for m in comp.metrics)

    def test_significant_count(self):
        comparator = ResultComparator(ResultComparisonConfig(min_trades_for_significance=30, significance_level=0.05))
        baseline = make_result(
            trades_count=100,
            annual_return=0.10,
            annual_return_std=0.01,
            sharpe_ratio=1.0,
            sharpe_ratio_std=0.01,
        )
        candidate = make_result(
            trades_count=100,
            annual_return=0.20,
            annual_return_std=0.01,
            sharpe_ratio=2.0,
            sharpe_ratio_std=0.01,
        )
        comp = comparator.compare(baseline, candidate)
        # 年化 + Sharpe 均显著
        assert comp.significant_count >= 2


# ──────────────────────────────────────────────────────────────────────────────
# 报告生成
# ──────────────────────────────────────────────────────────────────────────────


class TestReport:
    def test_generate_diff_report_structure(self):
        comparator = ResultComparator()
        baseline = make_result(annual_return=0.15, sharpe_ratio=1.2, trades_count=5)
        candidate = make_result(annual_return=0.20, sharpe_ratio=1.5, trades_count=5)
        report = comparator.generate_diff_report(baseline, candidate, "v1", "v2")

        assert isinstance(report, ComparisonReport)
        assert "v1" in report.summary and "v2" in report.summary
        assert "<table" in report.detailed_table
        assert "</table>" in report.detailed_table
        assert len(report.significance_notes) >= 1

    def test_report_table_contains_all_metrics(self):
        comparator = ResultComparator()
        report = comparator.generate_diff_report(
            make_result(annual_return=0.1, trades_count=5),
            make_result(annual_return=0.2, trades_count=5),
        )
        for name in ["年化收益", "总收益", "Sharpe比率", "最大回撤", "胜率", "交易次数"]:
            assert name in report.detailed_table

    def test_report_significance_notes_warn_low_trades(self):
        comparator = ResultComparator(ResultComparisonConfig(min_trades_for_significance=30))
        report = comparator.generate_diff_report(
            make_result(trades_count=5, annual_return=0.1),
            make_result(trades_count=5, annual_return=0.2),
        )
        # 应包含交易次数不足的警告
        assert any("不足" in n for n in report.significance_notes)

    def test_report_no_significance_note_when_sufficient(self):
        comparator = ResultComparator(ResultComparisonConfig(min_trades_for_significance=30))
        report = comparator.generate_diff_report(
            make_result(trades_count=100, annual_return=0.1, annual_return_std=0.5),
            make_result(trades_count=100, annual_return=0.101, annual_return_std=0.5),
        )
        # 交易充足 → 不应有"不足"警告
        assert not any("不足" in n for n in report.significance_notes)

    def test_models_are_frozen(self):
        comp = ResultComparator().compare(
            make_result(annual_return=0.1, trades_count=5),
            make_result(annual_return=0.2, trades_count=5),
        )
        metric = comp.metrics[0]
        with pytest.raises(Exception):
            metric.name = "x"  # type: ignore[misc]
        with pytest.raises(Exception):
            comp.better_count = 99  # type: ignore[misc]
