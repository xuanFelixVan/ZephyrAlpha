# [BLUEPRINT] MOD-SIG-122 | docs/03_modules/_domain_signal/calendar_effects_model/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-122 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_calendar_effects_model
# [TESTS] src/zephyr/signal_ashare/calendar_effects_model.py
"""MOD-SIG-122 单元测试：calendar_effects_model A股日历效应模型。

蓝图验收（B10-01390/CAND-TESTB-042，A1 模块55）：
月度/周内/节假日/交割日四类效应滚动 t 检验注入统计器 + 分年稳健性 +
显著效应节点日历输出（数量由数据决定非人为）。时钟/统计器全注入内存替身，
纯内存不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.calendar_effects_model",
    reason="calendar_effects_model not importable",
)

from zephyr.signal_ashare.calendar_effects_model import (  # noqa: E402
    CalendarEffectsModel,
    CalendarEffectsError,
    CalendarEffectType,
)

_T0 = datetime.datetime(2026, 8, 26, 10, 0, 0)


def _ttest_strong(a, b):
    """强效应统计器：组间差异显著。"""
    return (3.5, 0.001)


def _ttest_weak(a, b):
    """弱效应统计器：不显著。"""
    return (0.3, 0.76)


def _ttest_mixed(a, b):
    """按组大小决定：大组显著小组不显著。"""
    if len(a) > 10:
        return (2.5, 0.01)
    return (0.1, 0.9)


def _model(ttest=None) -> CalendarEffectsModel:
    return CalendarEffectsModel(
        ttest_runner=ttest,
        clock=lambda: _T0,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 通用校验
# ──────────────────────────────────────────────────────────────────────────────


class TestValidation:
    def test_not_injected_raises(self) -> None:
        with pytest.raises(CalendarEffectsError):
            _model().monthly_effect(
                years=[2023, 2024, 2025],
                returns=[0.01, 0.02, 0.01],
                months=[1, 1, 1],
                target_month=1,
            )

    def test_invalid_month_raises(self) -> None:
        with pytest.raises(CalendarEffectsError):
            _model(_ttest_strong).monthly_effect(
                years=[2023], returns=[0.01], months=[1], target_month=0,
            )
        with pytest.raises(CalendarEffectsError):
            _model(_ttest_strong).monthly_effect(
                years=[2023], returns=[0.01], months=[1], target_month=13,
            )

    def test_invalid_weekday_raises(self) -> None:
        with pytest.raises(CalendarEffectsError):
            _model(_ttest_strong).weekly_effect(
                years=[2023], returns=[0.01], weekdays=[0], target_weekday=-1,
            )
        with pytest.raises(CalendarEffectsError):
            _model(_ttest_strong).weekly_effect(
                years=[2023], returns=[0.01], weekdays=[0], target_weekday=7,
            )

    def test_series_mismatch_raises(self) -> None:
        with pytest.raises(CalendarEffectsError):
            _model(_ttest_strong).monthly_effect(
                years=[2023], returns=[0.01, 0.02], months=[1], target_month=1,
            )
        with pytest.raises(CalendarEffectsError):
            _model(_ttest_strong).weekly_effect(
                years=[2023, 2024], returns=[0.01], weekdays=[0, 1], target_weekday=0,
            )
        with pytest.raises(CalendarEffectsError):
            _model(_ttest_strong).holiday_effect(
                years=[2023, 2024], returns=[0.01], holiday_flags=[True],
            )

    def test_non_finite_raises(self) -> None:
        with pytest.raises(CalendarEffectsError):
            _model(_ttest_strong).monthly_effect(
                years=[2023], returns=[float("nan")], months=[1], target_month=1,
            )


# ──────────────────────────────────────────────────────────────────────────────
# 月度效应
# ──────────────────────────────────────────────────────────────────────────────


class TestMonthlyEffect:
    def test_strong_effect_significant(self) -> None:
        """三年数据，1月收益显著高于其他月份（统计器强）。"""
        # 每年 1月 1 个高值，其余 11 个月低值；3 年共 36 条
        years = [2023, 2024, 2025] * 12
        months = [m for m in range(1, 13) for _ in range(3)]
        returns = [0.05 if m == 1 else 0.005 for m in months]
        node = _model(_ttest_strong).monthly_effect(
            years=years, returns=returns, months=months, target_month=1,
        )
        assert node is not None
        assert node.effect_type is CalendarEffectType.MONTHLY
        assert node.label == "1月"
        assert node.mean_effect == pytest.approx(0.05)
        assert node.is_significant is True

    def test_weak_effect_not_significant(self) -> None:
        years = [2023, 2024, 2025] * 12
        months = [m for m in range(1, 13) for _ in range(3)]
        returns = [0.05 if m == 1 else 0.005 for m in months]
        node = _model(_ttest_weak).monthly_effect(
            years=years, returns=returns, months=months, target_month=1,
        )
        assert node is not None
        assert node.is_significant is False

    def test_no_target_month_data_returns_none(self) -> None:
        """数据中无 target_month → None（数据决定不人为）。"""
        years = [2023, 2024, 2025] * 11
        months = [m for m in range(2, 13) for _ in range(3)]
        returns = [0.01] * len(months)
        node = _model(_ttest_strong).monthly_effect(
            years=years, returns=returns, months=months, target_month=1,
        )
        assert node is None

    def test_robustness_split(self) -> None:
        """分年稳健性：强统计器下 3 年全显著 → robust_years=3。"""
        years = [2023, 2024, 2025] * 12
        months = [m for m in range(1, 13) for _ in range(3)]
        returns = [0.05 if m == 1 else 0.005 for m in months]
        node = _model(_ttest_strong).monthly_effect(
            years=years, returns=returns, months=months, target_month=1,
        )
        assert node is not None
        assert node.robust_years == 3
        assert node.total_years == 3


# ──────────────────────────────────────────────────────────────────────────────
# 周内效应
# ──────────────────────────────────────────────────────────────────────────────


class TestWeeklyEffect:
    def test_monday_strong(self) -> None:
        """周一效应（0=周一）。"""
        years = [2023, 2024, 2025] * 5
        weekdays = [d for d in range(5) for _ in range(3)]
        returns = [0.03 if d == 0 else 0.005 for d in weekdays]
        node = _model(_ttest_strong).weekly_effect(
            years=years, returns=returns, weekdays=weekdays, target_weekday=0,
        )
        assert node is not None
        assert node.effect_type is CalendarEffectType.WEEKLY
        assert node.label == "周一"
        assert node.mean_effect == pytest.approx(0.03)
        assert node.is_significant is True

    def test_friday_not_significant(self) -> None:
        years = [2023, 2024, 2025] * 5
        weekdays = [d for d in range(5) for _ in range(3)]
        returns = [0.005] * len(weekdays)
        node = _model(_ttest_weak).weekly_effect(
            years=years, returns=returns, weekdays=weekdays, target_weekday=4,
        )
        assert node is not None
        assert node.is_significant is False


# ──────────────────────────────────────────────────────────────────────────────
# 节假日效应
# ──────────────────────────────────────────────────────────────────────────────


class TestHolidayEffect:
    def test_holiday_strong(self) -> None:
        years = [2023, 2024, 2025] * 10
        flags = [True] * 3 + [False] * 27
        returns = [0.04] * 3 + [0.005] * 27
        node = _model(_ttest_strong).holiday_effect(
            years=years, returns=returns, holiday_flags=flags,
        )
        assert node is not None
        assert node.effect_type is CalendarEffectType.HOLIDAY
        assert node.label == "节假日"
        assert node.mean_effect == pytest.approx(0.04)
        assert node.is_significant is True

    def test_no_holiday_returns_none(self) -> None:
        years = [2023, 2024, 2025] * 10
        flags = [False] * 30
        returns = [0.005] * 30
        node = _model(_ttest_strong).holiday_effect(
            years=years, returns=returns, holiday_flags=flags,
        )
        assert node is None


# ──────────────────────────────────────────────────────────────────────────────
# 交割日效应
# ──────────────────────────────────────────────────────────────────────────────


class TestSettlementEffect:
    def test_settlement_strong(self) -> None:
        years = [2023, 2024, 2025] * 10
        flags = [False] * 27 + [True] * 3
        returns = [0.005] * 27 + [-0.03] * 3  # 交割日下跌效应
        node = _model(_ttest_strong).settlement_effect(
            years=years, returns=returns, settlement_flags=flags,
        )
        assert node is not None
        assert node.effect_type is CalendarEffectType.SETTLEMENT
        assert node.label == "交割日"
        assert node.mean_effect == pytest.approx(-0.03)
        assert node.is_significant is True


# ──────────────────────────────────────────────────────────────────────────────
# 日历输出（数据驱动 + 确定性）
# ──────────────────────────────────────────────────────────────────────────────


class TestCalendarNodes:
    def test_all_types_covered(self) -> None:
        """四类效应同时检测，节点数量由数据决定。"""
        years = [2023, 2024, 2025] * 20
        months = [m for m in range(1, 13) for _ in range(5)][:len(years)]
        weekdays = [d for d in range(5) for _ in range(12)][:len(years)]
        holiday_flags = [False] * len(years)
        settlement_flags = [False] * len(years)
        returns = [0.01] * len(years)
        out = _model(_ttest_weak).calendar_nodes(
            years=years,
            returns=returns,
            months=months,
            weekdays=weekdays,
            holiday_flags=holiday_flags,
            settlement_flags=settlement_flags,
        )
        # 无显著效应 → significant_nodes 为空
        assert out.significant_nodes == ()
        assert len(out.nodes) > 0  # 但节点本身由数据决定非零
        assert out.assessed_at == _T0

    def test_significant_nodes_filtered(self) -> None:
        """显著节点过滤：只保留 is_significant。"""
        years = [2023, 2024, 2025] * 12
        months = [m for m in range(1, 13) for _ in range(3)]
        returns = [0.05 if m == 1 else 0.005 for m in months]
        out = _model(_ttest_strong).calendar_nodes(
            years=years,
            returns=returns,
            months=months,
            min_years=3,
        )
        assert len(out.significant_nodes) > 0
        assert all(n.is_significant for n in out.significant_nodes)
        # 显著节点 ⊆ 全部节点
        assert set(out.significant_nodes) <= set(out.nodes)

    def test_data_driven_node_count(self) -> None:
        """节点数量由数据决定：传 3 类序列 vs 传 4 类序列节点数不同。"""
        years = [2023, 2024, 2025] * 20
        months = [m for m in range(1, 13) for _ in range(5)][:len(years)]
        weekdays = [d for d in range(5) for _ in range(12)][:len(years)]
        returns = [0.01] * len(years)
        out3 = _model(_ttest_weak).calendar_nodes(
            years=years, returns=returns, months=months, weekdays=weekdays,
        )
        holiday_flags = [True] * 5 + [False] * (len(years) - 5)
        out4 = _model(_ttest_weak).calendar_nodes(
            years=years,
            returns=returns,
            months=months,
            weekdays=weekdays,
            holiday_flags=holiday_flags,
        )
        assert len(out4.nodes) > len(out3.nodes)

    def test_min_years_raises(self) -> None:
        with pytest.raises(CalendarEffectsError):
            _model(_ttest_strong).calendar_nodes(
                years=[2023, 2024],
                returns=[0.01, 0.01],
                months=[1, 1],
                min_years=3,
            )

    def test_determinism(self) -> None:
        years = [2023, 2024, 2025] * 12
        months = [m for m in range(1, 13) for _ in range(3)]
        returns = [0.05 if m == 1 else 0.005 for m in months]
        kwargs = dict(years=years, returns=returns, months=months, min_years=3)
        a = _model(_ttest_strong).calendar_nodes(**kwargs)
        b = _model(_ttest_strong).calendar_nodes(**kwargs)
        assert a == b
