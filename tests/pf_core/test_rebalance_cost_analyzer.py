# [BLUEPRINT] MOD-PF-014 | docs/03_modules/_domain_portfolio_core/rebalance_cost_analyzer/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-PF-014 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.pf_core.test_rebalance_cost_analyzer
# [TESTS] src/zephyr/pf_core/core/rebalance_cost_analyzer.py
"""MOD-PF-014 单元测试：rebalance_cost_analyzer 再平衡成本分析器。

蓝图验收（B10-02079/CAND-PF004-007，A1 PC-10）：
调仓成本四拆解（显性/隐性/税收/机会成本，税率表注入）+ 占比排序报告
+ 成本异常告警。Decimal-only；税率表/告警/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import dataclasses
import datetime
from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.pf_core.core.rebalance_cost_analyzer",
    reason="rebalance_cost_analyzer not importable",
)

from zephyr.pf_core.core.rebalance_cost_analyzer import (  # noqa: E402
    CostCategory,
    RebalanceCostAnalyzer,
    RebalanceCostError,
    TradeLeg,
    TradeSide,
)

_T0 = datetime.datetime(2026, 8, 26, 15, 0, 0)
_TAX_TABLE = {"dividend_rate": Decimal("0.1"), "capital_gain_rate": Decimal("0.2")}


def _leg(symbol: str = "600000.SH", **kwargs) -> TradeLeg:
    kwargs.setdefault("symbol", symbol)
    kwargs.setdefault("side", TradeSide.BUY)
    kwargs.setdefault("qty", Decimal("100"))
    kwargs.setdefault("price", Decimal("10"))
    kwargs.setdefault("commission", Decimal("5"))
    kwargs.setdefault("stamp_duty", Decimal("1"))
    kwargs.setdefault("impact_cost", Decimal("2"))
    kwargs.setdefault("spread_cost", Decimal("1"))
    return TradeLeg(**kwargs)


def _analyzer(alerts: list | None = None, **kwargs) -> RebalanceCostAnalyzer:
    kwargs.setdefault("tax_table", _TAX_TABLE)
    kwargs.setdefault("clock", lambda: _T0)
    if alerts is not None:
        kwargs["alert_sink"] = lambda r: alerts.append(r)
    return RebalanceCostAnalyzer(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 初始化
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_default_ok(self) -> None:
        assert _analyzer() is not None

    def test_tax_table_missing_key_raises(self) -> None:
        with pytest.raises(RebalanceCostError):
            _analyzer(tax_table={"dividend_rate": Decimal("0.1")})

    def test_tax_table_empty_raises(self) -> None:
        with pytest.raises(RebalanceCostError):
            _analyzer(tax_table={})

    def test_rate_out_of_range_raises(self) -> None:
        with pytest.raises(RebalanceCostError):
            _analyzer(tax_table={"dividend_rate": Decimal("1.2"), "capital_gain_rate": Decimal("0.2")})
        with pytest.raises(RebalanceCostError):
            _analyzer(tax_table={"dividend_rate": Decimal("-0.1"), "capital_gain_rate": Decimal("0.2")})

    def test_non_decimal_config_raises(self) -> None:
        with pytest.raises(RebalanceCostError):
            _analyzer(tax_table={"dividend_rate": 0.1, "capital_gain_rate": Decimal("0.2")})
        with pytest.raises(RebalanceCostError):
            _analyzer(alert_threshold_bps=50.0)
        with pytest.raises(RebalanceCostError):
            _analyzer(alert_threshold_bps=Decimal("-1"))


# ──────────────────────────────────────────────────────────────────────────────
# 四拆解
# ──────────────────────────────────────────────────────────────────────────────


class TestBreakdown:
    def _legs(self) -> list[TradeLeg]:
        return [
            _leg("600000.SH", qty=Decimal("100"), price=Decimal("10"),
                 commission=Decimal("5"), stamp_duty=Decimal("1"),
                 impact_cost=Decimal("2"), spread_cost=Decimal("1")),
            _leg("600519.SH", qty=Decimal("200"), price=Decimal("20"),
                 commission=Decimal("10"), stamp_duty=Decimal("2"),
                 impact_cost=Decimal("4"), spread_cost=Decimal("2")),
        ]

    def _analyze(self, alerts: list | None = None, **kwargs):
        kwargs.setdefault("dividend_income", Decimal("100"))
        kwargs.setdefault("capital_gain", Decimal("200"))
        kwargs.setdefault("portfolio_return", Decimal("0.005"))
        kwargs.setdefault("benchmark_return", Decimal("0.01"))
        return _analyzer(alerts).analyze(legs=self._legs(), **kwargs)

    def test_four_categories_amounts(self) -> None:
        report = self._analyze()
        amounts = {item.category: item.amount for item in report.items}
        assert amounts[CostCategory.EXPLICIT] == Decimal("18")   # (5+1)+(10+2)
        assert amounts[CostCategory.IMPLICIT] == Decimal("9")    # (2+1)+(4+2)
        assert amounts[CostCategory.TAX] == Decimal("50")        # 100×0.1+200×0.2
        assert amounts[CostCategory.OPPORTUNITY] == Decimal("25")  # 5000×(0.01-0.005)

    def test_total_and_notional_and_bps(self) -> None:
        report = self._analyze()
        assert report.total_notional == Decimal("5000")
        assert report.total_cost == Decimal("102")
        assert report.cost_bps == Decimal("204")

    def test_items_sorted_by_ratio_desc(self) -> None:
        report = self._analyze()
        assert [item.category for item in report.items] == [
            CostCategory.TAX,           # 50
            CostCategory.OPPORTUNITY,   # 25
            CostCategory.EXPLICIT,      # 18
            CostCategory.IMPLICIT,      # 9
        ]
        ratios = {item.category: item.ratio for item in report.items}
        assert ratios[CostCategory.TAX] == Decimal("50") / Decimal("102")
        assert ratios[CostCategory.IMPLICIT] == Decimal("9") / Decimal("102")

    def test_tie_broken_by_category_name(self) -> None:
        analyzer = _analyzer(tax_table={"dividend_rate": Decimal("0"), "capital_gain_rate": Decimal("0")})
        # 四类全 0：显隐各0、税0、机会0 → 平手按类名字典序
        report = analyzer.analyze(
            legs=[_leg(commission=Decimal("0"), stamp_duty=Decimal("0"),
                       impact_cost=Decimal("0"), spread_cost=Decimal("0"))],
            portfolio_return=Decimal("0.01"), benchmark_return=Decimal("0.01"),
        )
        assert [item.category for item in report.items] == sorted(CostCategory, key=lambda c: c.value)
        assert all(item.ratio == Decimal("0") for item in report.items)

    def test_tax_negative_gain_clamped(self) -> None:
        report = _analyzer().analyze(
            legs=self._legs(), dividend_income=Decimal("100"), capital_gain=Decimal("-200"),
        )
        amounts = {item.category: item.amount for item in report.items}
        assert amounts[CostCategory.TAX] == Decimal("10")  # 负利得不退税，仅股息 100×0.1

    def test_opportunity_negative_when_outperform(self) -> None:
        report = _analyzer().analyze(
            legs=self._legs(), portfolio_return=Decimal("0.02"), benchmark_return=Decimal("0.01"),
        )
        amounts = {item.category: item.amount for item in report.items}
        assert amounts[CostCategory.OPPORTUNITY] == Decimal("-50")  # 跑赢基准=负成本

    def test_report_frozen(self) -> None:
        report = self._analyze()
        with pytest.raises(dataclasses.FrozenInstanceError):
            report.total_cost = Decimal("0")


# ──────────────────────────────────────────────────────────────────────────────
# 告警
# ──────────────────────────────────────────────────────────────────────────────


class TestAlert:
    def _legs(self) -> list[TradeLeg]:
        return [_leg(qty=Decimal("100"), price=Decimal("10"))]

    def test_alert_above_threshold(self) -> None:
        alerts: list = []
        report = _analyzer(alerts, alert_threshold_bps=Decimal("50")).analyze(
            legs=self._legs(), dividend_income=Decimal("100"), capital_gain=Decimal("200"),
            portfolio_return=Decimal("0.005"), benchmark_return=Decimal("0.01"),
        )
        assert report.alerted is True
        assert len(alerts) == 1
        assert alerts[0] is report

    def test_no_alert_below_threshold(self) -> None:
        alerts: list = []
        report = _analyzer(alerts, alert_threshold_bps=Decimal("500")).analyze(legs=self._legs())
        assert report.alerted is False
        assert alerts == []

    def test_alert_boundary_not_triggered(self) -> None:
        # cost_bps=640，阈值=640 → 严格大于才告警
        report = _analyzer(alert_threshold_bps=Decimal("640")).analyze(
            legs=self._legs(), dividend_income=Decimal("100"), capital_gain=Decimal("200"),
            portfolio_return=Decimal("0.005"), benchmark_return=Decimal("0.01"),
        )
        assert report.alerted is False

    def test_alert_sink_exception_not_blocking(self) -> None:
        def _boom(_r) -> None:
            raise RuntimeError("sink down")

        analyzer = RebalanceCostAnalyzer(
            tax_table=_TAX_TABLE, alert_threshold_bps=Decimal("1"),
            alert_sink=_boom, clock=lambda: _T0,
        )
        report = analyzer.analyze(legs=self._legs(), dividend_income=Decimal("100"))
        assert report.alerted is True  # 告警失败不阻断报告产出


# ──────────────────────────────────────────────────────────────────────────────
# Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestFailClosed:
    def test_empty_legs_raises(self) -> None:
        with pytest.raises(RebalanceCostError):
            _analyzer().analyze(legs=[])

    def test_non_positive_qty_price_raises(self) -> None:
        with pytest.raises(RebalanceCostError):
            _analyzer().analyze(legs=[_leg(qty=Decimal("0"))])
        with pytest.raises(RebalanceCostError):
            _analyzer().analyze(legs=[_leg(price=Decimal("-1"))])

    def test_negative_cost_component_raises(self) -> None:
        with pytest.raises(RebalanceCostError):
            _analyzer().analyze(legs=[_leg(commission=Decimal("-0.1"))])

    def test_non_decimal_leg_field_raises(self) -> None:
        with pytest.raises(RebalanceCostError):
            _analyzer().analyze(legs=[_leg(qty=100)])

    def test_non_leg_raises(self) -> None:
        with pytest.raises(RebalanceCostError):
            _analyzer().analyze(legs=[{"symbol": "600000.SH"}])


# ──────────────────────────────────────────────────────────────────────────────
# 确定性 / 时钟注入
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_output(self) -> None:
        legs = [_leg()]
        r1 = _analyzer().analyze(legs=legs, dividend_income=Decimal("100"))
        r2 = _analyzer().analyze(legs=legs, dividend_income=Decimal("100"))
        assert r1 == r2

    def test_clock_injected(self) -> None:
        report = _analyzer().analyze(legs=[_leg()])
        assert report.analyzed_at == _T0
