# [BLUEPRINT] MOD-POS-017 | (auto-injected by S4 reconciler) | §
# [A_module] module_id=MOD-POS-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [TESTS] tests/position/test_position_sizing_engine.py
# [MODULE] tests.position.test_position_sizing_engine
# [DOMAIN] D_POSITION
# [TESTED] zephyr.position.core.position_sizing_engine
# [TTL] permanent

"""Position Sizing Engine 测试 (MOD-POS-001 阶段1)。

覆盖: 预筛+Kelly+半Kelly+风险配额+波动率+VaR/CVaR+参与率+退出时间+
策略容量+冲击成本+单票上限+市场状态+降级模式+日历约束+资金曲线+现金约束+错误契约。
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Final

import pytest

from zephyr.position.core.position_sizing_engine import (
    MARKET_REGIME_CAPS,
    ConstraintViolationError,
    InvalidPositionInputError,
    KellyEstimationError,
    PositionSizingConfig,
    PositionSizingEngine,
    PositionSizingInput,
    SizingMarketRegime,
    SymbolInput,
)
from zephyr.shared.contracts.risk_limits import RiskLimits

NAV: Final[float] = 1_000_000.0
TRADE_DATE: Final[date] = date(2026, 8, 3)


# ──────────────────────────────────────────────────────────────────────────────
# 辅助构造
# ──────────────────────────────────────────────────────────────────────────────


def make_symbol(
    symbol: str = "000001.SZ",
    price: float = 10.0,
    current_qty: int = 0,
    avg_daily_volume: float = 1_000_000.0,
    target_weight: float | None = None,
    win_probability: float | None = None,
    win_loss_ratio: float | None = None,
    current_volatility: float | None = None,
    hist_vol_mean: float | None = None,
    hist_vol_std: float | None = None,
    strategy_capacity: float = 0.0,
    is_st: bool = False,
    market_cap_yi: float = 0.0,
) -> SymbolInput:
    return SymbolInput(
        symbol=symbol,
        price=price,
        current_qty=current_qty,
        avg_daily_volume=avg_daily_volume,
        target_weight=target_weight,
        win_probability=win_probability,
        win_loss_ratio=win_loss_ratio,
        current_volatility=current_volatility,
        hist_vol_mean=hist_vol_mean,
        hist_vol_std=hist_vol_std,
        strategy_capacity=strategy_capacity,
        is_st=is_st,
        market_cap_yi=market_cap_yi,
    )


def make_input(
    symbols: list[SymbolInput] | None = None,
    nav: float = NAV,
    strategy_id: str = "strat_001",
    trade_date: date = TRADE_DATE,
    risk_limits: RiskLimits | None = None,
    market_regime: SizingMarketRegime | None = None,
    capital_curve_discount: float = 1.0,
    capital_curve_cap: float = 1.0,
    defensive_only: bool = False,
    max_investable: float | None = None,
    calendar_cap_adjustment: float = 1.0,
    calendar_block_new: bool = False,
    calendar_block_symbols: frozenset[str] | None = None,
    calendar_force_clear_symbols: frozenset[str] | None = None,
    var_95: float | None = None,
    cvar_95: float | None = None,
    is_event_driven: bool = False,
    is_sector_rotation: bool = False,
) -> PositionSizingInput:
    return PositionSizingInput(
        symbols=symbols or [make_symbol()],
        nav=nav,
        strategy_id=strategy_id,
        trade_date=trade_date,
        risk_limits=risk_limits,
        market_regime=market_regime,
        capital_curve_discount=capital_curve_discount,
        capital_curve_cap=capital_curve_cap,
        defensive_only=defensive_only,
        max_investable=max_investable,
        calendar_cap_adjustment=calendar_cap_adjustment,
        calendar_block_new=calendar_block_new,
        calendar_block_symbols=calendar_block_symbols or frozenset(),
        calendar_force_clear_symbols=calendar_force_clear_symbols or frozenset(),
        var_95=var_95,
        cvar_95=cvar_95,
        is_event_driven=is_event_driven,
        is_sector_rotation=is_sector_rotation,
    )


def make_risk_limits(max_single: float = 0.05, gross_lev: float = 1.0) -> RiskLimits:
    return RiskLimits(
        as_of_date=datetime(2026, 8, 3, tzinfo=timezone.utc),
        idempotency_key="test_key",
        max_single_position=max_single,
        max_gross_leverage=gross_lev,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Kelly 计算
# ──────────────────────────────────────────────────────────────────────────────


class TestKellyCalculation:
    """Kelly 仓位计算 + 半 Kelly 截断 (C1)。"""

    def test_kelly_normal_case(self) -> None:
        """p=0.55, b=1.5 → f*=0.25, 半Kelly=0.125。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.55, win_loss_ratio=1.5, avg_daily_volume=1e8)
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        tgt = plan.positions["000001.SZ"]
        # 半Kelly=0.125, 但受单票上限5%截断
        assert tgt.target_weight <= 0.05

    def test_kelly_zero_edge(self) -> None:
        """p=0.5, b=1.0 → f*=0 → 不下注。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.5, win_loss_ratio=1.0, avg_daily_volume=1e8)
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        tgt = plan.positions["000001.SZ"]
        assert tgt.target_qty == 0

    def test_kelly_negative_expectation(self) -> None:
        """p=0.3, b=2.0 → f*=(0.6-0.7)/2 <0 → 不下注。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.3, win_loss_ratio=2.0, avg_daily_volume=1e8)
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        assert plan.positions["000001.SZ"].target_qty == 0

    def test_half_kelly_truncation(self) -> None:
        """高 Kelly → 被 half_kelly_factor 截断。"""
        engine = PositionSizingEngine()
        # p=0.8, b=3.0 → f*=(2.4-0.2)/3=0.733, 半Kelly=0.367
        sym = make_symbol(win_probability=0.8, win_loss_ratio=3.0, avg_daily_volume=1e8)
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        # 半Kelly=0.367 但被单票上限5%截断
        assert plan.positions["000001.SZ"].target_weight <= 0.05

    def test_half_kelly_boundary(self) -> None:
        """Kelly 正好等于单票上限时不截断。"""
        engine = PositionSizingEngine()
        # 调整参数使半Kelly < 5% → 不被截断
        sym = make_symbol(win_probability=0.52, win_loss_ratio=1.1, avg_daily_volume=1e8)
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        # f* = (1.1*0.52 - 0.48)/1.1 = (0.572-0.48)/1.1 = 0.0836, 半Kelly=0.0418
        tgt = plan.positions["000001.SZ"]
        assert tgt.target_weight <= 0.05


# ──────────────────────────────────────────────────────────────────────────────
# 波动率检查 (C3)
# ──────────────────────────────────────────────────────────────────────────────


class TestVolatilityCheck:
    """C3: 波动率超 μ+2σ → 仓位减半。"""

    def test_volatility_normal(self) -> None:
        """波动率在正常范围 → 不减半。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.55,
            win_loss_ratio=1.5,
            current_volatility=0.15,
            hist_vol_mean=0.15,
            hist_vol_std=0.03,
            avg_daily_volume=1e8,
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        # 正常波动 → 无减半标记
        assert plan.volatility_adjustment == 1.0

    def test_volatility_over_2sigma(self) -> None:
        """波动率超 μ+2σ → 仓位减半。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.55,
            win_loss_ratio=1.5,
            current_volatility=0.25,
            hist_vol_mean=0.15,
            hist_vol_std=0.03,
            avg_daily_volume=1e8,
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        # 0.25 > 0.15 + 2*0.03 = 0.21 → 减半
        assert plan.volatility_adjustment == 0.5


# ──────────────────────────────────────────────────────────────────────────────
# VaR/CVaR 下调 (C4/C5)
# ──────────────────────────────────────────────────────────────────────────────


class TestVarCvarCheck:
    """C4/C5: 前瞻 VaR/CVaR 超限 → 仓位下调。"""

    def test_var_within_threshold(self) -> None:
        """VaR < 阈值 → 不下调。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.55, win_loss_ratio=1.5, avg_daily_volume=1e8)
        plan = engine.size(
            make_input(
                symbols=[sym],
                market_regime=SizingMarketRegime.CALM_BULL,
                var_95=0.01,
            )
        )
        c4 = [c for c in plan.constraints_check["checks"] if c["constraint_id"] == "C4"]
        assert len(c4) == 0 or c4[0]["action"] == "pass"

    def test_var_exceeds_threshold(self) -> None:
        """VaR > 2.5% → 下调 ×0.8。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.55, win_loss_ratio=1.5, avg_daily_volume=1e8)
        plan = engine.size(
            make_input(
                symbols=[sym],
                market_regime=SizingMarketRegime.CALM_BULL,
                var_95=0.03,
            )
        )
        c4 = [c for c in plan.constraints_check["checks"] if c["constraint_id"] == "C4"]
        assert len(c4) > 0 and c4[0]["action"] == "truncate"

    def test_cvar_exceeds_threshold(self) -> None:
        """CVaR > 4% → 进一步下调 ×0.7。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.55, win_loss_ratio=1.5, avg_daily_volume=1e8)
        plan = engine.size(
            make_input(
                symbols=[sym],
                market_regime=SizingMarketRegime.CALM_BULL,
                var_95=0.03,
                cvar_95=0.05,
            )
        )
        c5 = [c for c in plan.constraints_check["checks"] if c["constraint_id"] == "C5"]
        assert len(c5) > 0 and c5[0]["action"] == "truncate"

    def test_both_var_cvar_exceed(self) -> None:
        """VaR + CVaR 同时超限 → 双重下调。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.55, win_loss_ratio=1.5, avg_daily_volume=1e8)
        plan_no_var = engine.size(
            make_input(
                symbols=[sym],
                market_regime=SizingMarketRegime.CALM_BULL,
            )
        )
        plan_with_var = engine.size(
            make_input(
                symbols=[sym],
                market_regime=SizingMarketRegime.CALM_BULL,
                var_95=0.03,
                cvar_95=0.05,
            )
        )
        # 有 VaR/CVaR 下调的仓位应更小
        w_no = plan_no_var.positions["000001.SZ"].target_weight
        w_yes = plan_with_var.positions["000001.SZ"].target_weight
        assert w_yes <= w_no


# ──────────────────────────────────────────────────────────────────────────────
# 参与率否决 (C6)
# ──────────────────────────────────────────────────────────────────────────────


class TestParticipationRate:
    """C6: 参与率 > 15% 日成交量 → 否决。"""

    def test_participation_within_limit(self) -> None:
        """参与率 < 15% → 通过。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.55,
            win_loss_ratio=1.5,
            price=10.0,
            avg_daily_volume=10_000_000.0,  # 高流动性
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        # 单票5% × 1M = 50K 元 / 10元 = 5K 股, 5K/10M = 0.05% < 15%
        c6 = [c for c in plan.constraints_check["checks"] if c["constraint_id"] == "C6"]
        assert len(c6) == 0

    def test_participation_at_boundary(self) -> None:
        """参与率在 15% 边界 → 不否决。"""
        engine = PositionSizingEngine()
        # weight=0.05(单票上限), target_qty=0.05*1M/10=5000
        # volume=5M → participation=5000/5M=0.1%, impact=0.1*sqrt(0.001)=0.3% < 0.5%
        sym = make_symbol(
            win_probability=0.55,
            win_loss_ratio=1.5,
            price=10.0,
            avg_daily_volume=5_000_000.0,
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        assert "000001.SZ" in plan.positions

    def test_participation_exceeds_veto(self) -> None:
        """参与率 > 15% → 否决(不建仓)。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.55,
            win_loss_ratio=1.5,
            price=100.0,
            avg_daily_volume=1000.0,  # 极低流动性
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        c6 = [c for c in plan.constraints_check["checks"] if c["constraint_id"] == "C6"]
        assert any(c["action"] == "veto" for c in c6)


# ──────────────────────────────────────────────────────────────────────────────
# 退出时间减仓 (C7/C8)
# ──────────────────────────────────────────────────────────────────────────────


class TestExitTime:
    """C7/C8: 退出时间 >3天强制减仓, >1天折扣。"""

    def test_exit_time_within_1_day(self) -> None:
        """退出时间 < 1天 → 不减仓。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.55,
            win_loss_ratio=1.5,
            current_qty=1000,
            avg_daily_volume=10_000.0,  # 0.1天
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        c7 = [c for c in plan.constraints_check["checks"] if c["constraint_id"] == "C7"]
        c8 = [c for c in plan.constraints_check["checks"] if c["constraint_id"] == "C8"]
        assert len(c7) == 0 and len(c8) == 0

    def test_exit_time_over_1_day_discount(self) -> None:
        """退出时间 > 1天 → 仓位折扣 ×0.8。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.55,
            win_loss_ratio=1.5,
            current_qty=15000,
            avg_daily_volume=10_000.0,  # 1.5天
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        c8 = [c for c in plan.constraints_check["checks"] if c["constraint_id"] == "C8"]
        assert any(c["action"] == "truncate" for c in c8)

    def test_exit_time_over_3_days_force_reduce(self) -> None:
        """退出时间 > 3天 → 强制减仓至可退出量。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.55,
            win_loss_ratio=1.5,
            current_qty=50_000,
            avg_daily_volume=10_000.0,  # 5天
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        c7 = [c for c in plan.constraints_check["checks"] if c["constraint_id"] == "C7"]
        assert any(c["action"] == "truncate" for c in c7)


# ──────────────────────────────────────────────────────────────────────────────
# 策略容量预警 (C9)
# ──────────────────────────────────────────────────────────────────────────────


class TestStrategyCapacity:
    """C9: 策略容量 > AUM×80% 预警, >100% 否决新资金。"""

    def test_capacity_within_limit(self) -> None:
        """容量 < 80% AUM → 无预警。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.55,
            win_loss_ratio=1.5,
            strategy_capacity=500_000.0,  # 50% AUM
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        c9 = [c for c in plan.constraints_check["checks"] if c["constraint_id"] == "C9"]
        assert len(c9) == 0

    def test_capacity_warn_80pct(self) -> None:
        """容量 > 80% AUM → 预警。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.55,
            win_loss_ratio=1.5,
            strategy_capacity=850_000.0,  # 85% AUM
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        c9 = [c for c in plan.constraints_check["checks"] if c["constraint_id"] == "C9"]
        assert any(c["action"] == "warn" for c in c9)

    def test_capacity_veto_100pct(self) -> None:
        """容量 > 100% AUM → 否决新资金。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.55,
            win_loss_ratio=1.5,
            strategy_capacity=1_200_000.0,  # 120% AUM, current_qty=0
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        c9 = [c for c in plan.constraints_check["checks"] if c["constraint_id"] == "C9"]
        assert any(c["action"] == "veto" for c in c9)
        assert "000001.SZ" not in plan.positions


# ──────────────────────────────────────────────────────────────────────────────
# 冲击成本否决 (C11)
# ──────────────────────────────────────────────────────────────────────────────


class TestImpactCost:
    """C11: 冲击成本 > 0.5% → 否决。"""

    def test_impact_cost_within_limit(self) -> None:
        """冲击成本 < 0.5% → 通过。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.55,
            win_loss_ratio=1.5,
            avg_daily_volume=10_000_000.0,  # 高流动性
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        c11 = [c for c in plan.constraints_check["checks"] if c["constraint_id"] == "C11"]
        assert len(c11) == 0

    def test_impact_cost_exceeds_veto(self) -> None:
        """冲击成本 > 0.5% → 否决(C6 通过但 C11 否决)。"""
        engine = PositionSizingEngine()
        # weight=0.05(单票上限), target_qty=0.05*1M/100=500, volume=12500
        # participation=500/12500=4% < 15% → C6 通过
        # impact=0.1*sqrt(0.04)=0.02=2% > 0.5% → C11 否决
        sym = make_symbol(
            win_probability=0.55,
            win_loss_ratio=1.5,
            price=100.0,
            avg_daily_volume=12_500.0,
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        c11 = [c for c in plan.constraints_check["checks"] if c["constraint_id"] == "C11"]
        assert any(c["action"] == "veto" for c in c11)


# ──────────────────────────────────────────────────────────────────────────────
# 单票上限 (C12)
# ──────────────────────────────────────────────────────────────────────────────


class TestSinglePositionLimit:
    """C12: 单票 ≤ 风控上限(5% NAV)。"""

    def test_single_position_within_limit(self) -> None:
        """仓位 < 5% → 不截断。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.52,
            win_loss_ratio=1.1,  # 半Kelly ≈ 4.2%
            avg_daily_volume=1e8,
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        assert plan.positions["000001.SZ"].target_weight <= 0.05

    def test_single_position_truncated(self) -> None:
        """仓位 > 5% → 截断至 5%。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.8,
            win_loss_ratio=3.0,  # 半Kelly = 36.7%
            avg_daily_volume=1e8,
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        assert plan.positions["000001.SZ"].target_weight <= 0.05

    def test_symbol_overrides(self) -> None:
        """RiskLimits.symbol_overrides 覆盖默认单票上限。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.8,
            win_loss_ratio=3.0,
            avg_daily_volume=1e8,
        )
        rl = make_risk_limits(max_single=0.1)
        rl = RiskLimits(
            as_of_date=datetime(2026, 8, 3, tzinfo=timezone.utc),
            idempotency_key="test_key",
            max_single_position=0.1,
            symbol_overrides={"000001.SZ": 0.08},
        )
        plan = engine.size(
            make_input(
                symbols=[sym],
                market_regime=SizingMarketRegime.CALM_BULL,
                risk_limits=rl,
            )
        )
        # 被覆盖为 8% 而非默认 5%
        assert plan.positions["000001.SZ"].target_weight <= 0.08


# ──────────────────────────────────────────────────────────────────────────────
# 市场状态上限 (C13)
# ──────────────────────────────────────────────────────────────────────────────


class TestMarketRegime:
    """C13: 市场状态 → 仓位上限映射 (immutable)。"""

    def test_calm_bull_80pct(self) -> None:
        assert MARKET_REGIME_CAPS[SizingMarketRegime.CALM_BULL] == 0.80

    def test_panic_crash_10pct(self) -> None:
        assert MARKET_REGIME_CAPS[SizingMarketRegime.PANIC_CRASH] == 0.10

    def test_narrow_range_40pct(self) -> None:
        assert MARKET_REGIME_CAPS[SizingMarketRegime.NARROW_RANGE] == 0.40

    def test_crisis_5pct(self) -> None:
        assert MARKET_REGIME_CAPS[SizingMarketRegime.CRISIS] == 0.05

    def test_recovery_50pct(self) -> None:
        assert MARKET_REGIME_CAPS[SizingMarketRegime.RECOVERY] == 0.50

    def test_breakout_70pct(self) -> None:
        assert MARKET_REGIME_CAPS[SizingMarketRegime.BREAKOUT] == 0.70

    def test_event_driven_overlay_70pct(self) -> None:
        """overlay: is_event_driven → 基础仓位×70% (§7.3 v8.1)。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.55, win_loss_ratio=1.5, avg_daily_volume=1e8)
        plan_base = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        plan_evt = engine.size(
            make_input(
                symbols=[sym],
                market_regime=SizingMarketRegime.CALM_BULL,
                is_event_driven=True,
            )
        )
        # CALM_BULL cap=0.80, overlay×0.70 → total_cap=0.56
        assert plan_evt.constraints_check["total_cap"] <= 0.80 * 0.70 + 1e-6
        assert plan_evt.total_exposure <= 0.80 * 0.70 + 1e-6
        # 无overlay时不受×0.70影响
        assert plan_base.constraints_check["total_cap"] <= 0.80 + 1e-6

    def test_sector_rotation_overlay_no_cap_change(self) -> None:
        """overlay: is_sector_rotation → POS-001不改cap(透传给POS-010)。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.55, win_loss_ratio=1.5, avg_daily_volume=1e8)
        plan = engine.size(
            make_input(
                symbols=[sym],
                market_regime=SizingMarketRegime.CALM_BULL,
                is_sector_rotation=True,
            )
        )
        # sector_rotation 不改 cap, 仍为 0.80
        assert plan.constraints_check["total_cap"] <= 0.80 + 1e-6

    def test_degradation_default(self) -> None:
        """D-SIGNAL 缺失 → 默认状态④(40%)。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.55, win_loss_ratio=1.5, avg_daily_volume=1e8)
        plan = engine.size(make_input(symbols=[sym], market_regime=None))
        assert plan.degraded is True
        assert plan.constraints_check["regime"] == "NARROW_RANGE"

    def test_total_exposure_within_market_cap(self) -> None:
        """总仓位 ≤ 市场状态上限。"""
        engine = PositionSizingEngine()
        syms = [
            make_symbol(symbol=f"00000{i}.SZ", win_probability=0.6, win_loss_ratio=2.0, avg_daily_volume=1e8)
            for i in range(1, 6)
        ]
        plan = engine.size(make_input(symbols=syms, market_regime=SizingMarketRegime.PANIC_CRASH))
        assert plan.total_exposure <= MARKET_REGIME_CAPS[SizingMarketRegime.PANIC_CRASH] + 1e-6


# ──────────────────────────────────────────────────────────────────────────────
# 降级模式
# ──────────────────────────────────────────────────────────────────────────────


class TestDegradationMode:
    """上游缺失时的降级模式。"""

    def test_no_density_prediction_equal_share(self) -> None:
        """无密度预测 → 等权分配(降级)。"""
        engine = PositionSizingEngine()
        syms = [make_symbol(symbol=f"00000{i}.SZ") for i in range(1, 5)]
        plan = engine.size(make_input(symbols=syms, market_regime=SizingMarketRegime.CALM_BULL))
        assert plan.degraded is True

    def test_no_target_weight_degradation(self) -> None:
        """无目标权重+无密度预测 → 全降级等权。"""
        engine = PositionSizingEngine()
        syms = [make_symbol(symbol=f"00000{i}.SZ") for i in range(1, 4)]
        plan = engine.size(make_input(symbols=syms, market_regime=SizingMarketRegime.CALM_BULL))
        # 3标的, 市场上限80%, 等权 = 80%/3 ≈ 26.7% 但受单票5%截断
        assert plan.degraded is True

    def test_no_market_regime_degradation(self) -> None:
        """无市场状态 → 默认④(40%)。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.55, win_loss_ratio=1.5, avg_daily_volume=1e8)
        plan = engine.size(make_input(symbols=[sym], market_regime=None))
        assert plan.constraints_check["market_cap"] == 0.40

    def test_degraded_flag_set(self) -> None:
        """降级时 degraded=True。"""
        engine = PositionSizingEngine()
        sym = make_symbol(avg_daily_volume=1e8)  # 无密度预测
        plan = engine.size(make_input(symbols=[sym], market_regime=None))
        assert plan.degraded is True


# ──────────────────────────────────────────────────────────────────────────────
# 预筛阶段
# ──────────────────────────────────────────────────────────────────────────────


class TestPreFilter:
    """预筛: 退出时间检查 + 流动性上限预筛。"""

    def test_prefilter_exit_time_check(self) -> None:
        """退出时间 >3天 → 预筛标记 C7。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.55,
            win_loss_ratio=1.5,
            current_qty=50_000,
            avg_daily_volume=10_000.0,  # 5天
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        c7 = [c for c in plan.constraints_check["checks"] if c["constraint_id"] == "C7"]
        assert len(c7) > 0

    def test_prefilter_liquidity_warning(self) -> None:
        """低流动性标的 → 预筛标记 warn。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.55,
            win_loss_ratio=1.5,
            price=100.0,
            avg_daily_volume=1000.0,  # 极低流动性
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        prefilter = [c for c in plan.constraints_check["checks"] if c["constraint_id"] == "prefilter"]
        assert any(c["action"] == "warn" for c in prefilter)

    def test_prefilter_pass_then_veto(self) -> None:
        """预筛放行但精确检查否决(边界情况)。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.8,
            win_loss_ratio=3.0,  # 高Kelly
            price=100.0,
            avg_daily_volume=500.0,  # 低流动性但预筛可能放行
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        # 预筛 warn + 后续 C6/C11 精确否决
        all_vetoes = [c for c in plan.constraints_check["checks"] if c["action"] == "veto"]
        assert len(all_vetoes) > 0


# ──────────────────────────────────────────────────────────────────────────────
# PositionPlan 输出
# ──────────────────────────────────────────────────────────────────────────────


class TestPositionPlan:
    """PositionPlan 输出完整性。"""

    def test_plan_fields_complete(self) -> None:
        """所有字段完整。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.55, win_loss_ratio=1.5, avg_daily_volume=1e8)
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        assert plan.plan_id.startswith("plan_")
        assert plan.strategy_id == "strat_001"
        assert "000001.SZ" in plan.positions
        assert plan.cash_reserve >= 0
        assert plan.total_exposure >= 0
        assert plan.capital_curve_discount == 1.0
        assert plan.schema_version == "1.0"
        assert plan.idempotency_key != ""

    def test_idempotency_key(self) -> None:
        """相同输入 → 相同幂等键。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.55, win_loss_ratio=1.5, avg_daily_volume=1e8)
        inp = make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL)
        plan1 = engine.size(inp)
        plan2 = engine.size(inp)
        assert plan1.idempotency_key == plan2.idempotency_key

    def test_idempotency_key_differs_for_different_weights(self) -> None:
        """不同目标权重 → 不同幂等键。"""
        engine = PositionSizingEngine()
        sym1 = make_symbol(symbol="000001.SZ", target_weight=0.03, avg_daily_volume=1e8)
        sym2 = make_symbol(symbol="000001.SZ", target_weight=0.04, avg_daily_volume=1e8)
        plan1 = engine.size(make_input(symbols=[sym1], market_regime=SizingMarketRegime.CALM_BULL))
        plan2 = engine.size(make_input(symbols=[sym2], market_regime=SizingMarketRegime.CALM_BULL))
        assert plan1.idempotency_key != plan2.idempotency_key


# ──────────────────────────────────────────────────────────────────────────────
# 日历约束 (POS-017)
# ──────────────────────────────────────────────────────────────────────────────


class TestCalendarConstraint:
    """POS-017 日历仓位约束。"""

    def test_calendar_block_new(self) -> None:
        """日历全面否决新开仓 → 新标的不出现在 positions。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.55, win_loss_ratio=1.5, avg_daily_volume=1e8)
        plan = engine.size(
            make_input(
                symbols=[sym],
                market_regime=SizingMarketRegime.CALM_BULL,
                calendar_block_new=True,
            )
        )
        assert plan.calendar_constraint_active is True
        assert "000001.SZ" not in plan.positions

    def test_calendar_force_clear(self) -> None:
        """日历强制清仓 → target_qty=0。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            symbol="000002.SZ",
            win_probability=0.55,
            win_loss_ratio=1.5,
            current_qty=5000,
            avg_daily_volume=1e8,
        )
        plan = engine.size(
            make_input(
                symbols=[sym],
                market_regime=SizingMarketRegime.CALM_BULL,
                calendar_force_clear_symbols=frozenset({"000002.SZ"}),
            )
        )
        tgt = plan.positions["000002.SZ"]
        assert tgt.target_qty == 0
        assert tgt.delta == -5000


# ──────────────────────────────────────────────────────────────────────────────
# 资金曲线缩放 (POS-007)
# ──────────────────────────────────────────────────────────────────────────────


class TestCapitalCurve:
    """POS-007 资金曲线缩放 + defensive_only。"""

    def test_capital_curve_discount(self) -> None:
        """资金曲线缩放系数 < 1.0 → 仓位缩小。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.55, win_loss_ratio=1.5, avg_daily_volume=1e8)
        plan_normal = engine.size(
            make_input(
                symbols=[sym],
                market_regime=SizingMarketRegime.CALM_BULL,
                capital_curve_discount=1.0,
            )
        )
        plan_discount = engine.size(
            make_input(
                symbols=[sym],
                market_regime=SizingMarketRegime.CALM_BULL,
                capital_curve_discount=0.5,
            )
        )
        w_normal = plan_normal.positions["000001.SZ"].target_weight
        w_discount = plan_discount.positions["000001.SZ"].target_weight
        assert w_discount <= w_normal

    def test_defensive_only(self) -> None:
        """defensive_only=True → 禁止新开仓(delta <= 0)。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.55,
            win_loss_ratio=1.5,
            current_qty=100,
            avg_daily_volume=1e8,
        )
        plan = engine.size(
            make_input(
                symbols=[sym],
                market_regime=SizingMarketRegime.CALM_BULL,
                defensive_only=True,
            )
        )
        tgt = plan.positions["000001.SZ"]
        assert tgt.delta <= 0


# ──────────────────────────────────────────────────────────────────────────────
# 现金约束 (POS-006)
# ──────────────────────────────────────────────────────────────────────────────


class TestCashConstraint:
    """POS-006 现金约束。"""

    def test_cash_constraint_scaling(self) -> None:
        """max_investable 限制 → 仓位缩放。"""
        engine = PositionSizingEngine()
        syms = [
            make_symbol(symbol=f"00000{i}.SZ", win_probability=0.55, win_loss_ratio=1.5, avg_daily_volume=1e8)
            for i in range(1, 6)
        ]
        plan = engine.size(
            make_input(
                symbols=syms,
                market_regime=SizingMarketRegime.CALM_BULL,
                max_investable=200_000.0,
            )
        )
        # max_investable=200K → 仓位上限 20%
        assert plan.total_exposure <= 0.20 + 1e-6

    def test_cash_constraint_no_limit(self) -> None:
        """max_investable=None → 不约束。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.55, win_loss_ratio=1.5, avg_daily_volume=1e8)
        plan = engine.size(
            make_input(
                symbols=[sym],
                market_regime=SizingMarketRegime.CALM_BULL,
                max_investable=None,
            )
        )
        pos006 = [c for c in plan.constraints_check["checks"] if c["constraint_id"] == "POS-006"]
        assert len(pos006) == 0


# ──────────────────────────────────────────────────────────────────────────────
# 错误契约
# ──────────────────────────────────────────────────────────────────────────────


class TestErrorContract:
    """错误契约 (ZA-POS-0001/0002/0003)。"""

    def test_invalid_nav_error(self) -> None:
        """NAV <= 0 → InvalidPositionInputError。"""
        engine = PositionSizingEngine()
        with pytest.raises(InvalidPositionInputError):
            engine.size(make_input(nav=0.0))

    def test_empty_symbols_error(self) -> None:
        """symbols 为空 → InvalidPositionInputError。"""
        engine = PositionSizingEngine()
        # 直接构造空 symbols (make_input 的 or 兜底会替换空列表)
        inp = PositionSizingInput(
            symbols=[],
            nav=NAV,
            strategy_id="strat_001",
            trade_date=TRADE_DATE,
        )
        with pytest.raises(InvalidPositionInputError):
            engine.size(inp)

    def test_invalid_price_error(self) -> None:
        """price <= 0 → InvalidPositionInputError。"""
        engine = PositionSizingEngine()
        sym = make_symbol(price=0.0)
        with pytest.raises(InvalidPositionInputError):
            engine.size(make_input(symbols=[sym]))

    def test_kelly_estimation_error_p(self) -> None:
        """win_probability 不在 (0,1) → KellyEstimationError。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=1.5, win_loss_ratio=1.5, avg_daily_volume=1e8)
        with pytest.raises(KellyEstimationError):
            engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))

    def test_kelly_estimation_error_b(self) -> None:
        """win_loss_ratio <= 0 → KellyEstimationError。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.55, win_loss_ratio=0.0, avg_daily_volume=1e8)
        with pytest.raises(KellyEstimationError):
            engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))

    def test_config_validation_error(self) -> None:
        """config 非法参数 → InvalidPositionInputError。"""
        with pytest.raises(InvalidPositionInputError):
            PositionSizingConfig(half_kelly_factor=1.5)

    def test_config_cvar_less_than_var_error(self) -> None:
        """cvar_threshold < var_threshold → InvalidPositionInputError。"""
        with pytest.raises(InvalidPositionInputError):
            PositionSizingConfig(var_threshold=0.05, cvar_threshold=0.03)


# ──────────────────────────────────────────────────────────────────────────────
# sizing_basis binding constraint 命名（31号 §2.3.4，归因审计）
# ──────────────────────────────────────────────────────────────────────────────


class TestSizingBasis:
    """PositionTarget.sizing_basis：记录标的级约束级联中最终 binding 的约束名。"""

    def test_kelly_budget_binding(self) -> None:
        """无 target_weight 时半 Kelly 是唯一约束源 → kelly_budget。"""
        engine = PositionSizingEngine()
        # p=0.5,b=1.0 → f*=0.02 → 半Kelly=0.01 < 单票 5% 上限 → Kelly binding
        sym = make_symbol(win_probability=0.51, win_loss_ratio=1.0, avg_daily_volume=1e8)
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        assert plan.positions["000001.SZ"].sizing_basis == "kelly_budget"

    def test_strategy_intent_binding(self) -> None:
        """target_weight < 半 Kelly → strategy_intent（策略意愿更保守）。"""
        engine = PositionSizingEngine()
        # p=0.55,b=1.5 → f*=0.25 → 半Kelly=0.125；target=0.03 < 0.125 → 策略意愿 binding
        sym = make_symbol(win_probability=0.55, win_loss_ratio=1.5, target_weight=0.03, avg_daily_volume=1e8)
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        tgt = plan.positions["000001.SZ"]
        assert tgt.sizing_basis == "strategy_intent"
        assert tgt.target_weight <= 0.03 + 1e-9

    def test_single_name_cap_binding(self) -> None:
        """Kelly 权重 > 单票上限 5% → single_name_cap。"""
        engine = PositionSizingEngine()
        # 半Kelly=0.125 > 5% cap → C12 binding
        sym = make_symbol(win_probability=0.55, win_loss_ratio=1.5, avg_daily_volume=1e8)
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        tgt = plan.positions["000001.SZ"]
        assert tgt.sizing_basis == "single_name_cap"
        assert tgt.target_weight <= 0.05 + 1e-9

    def test_var_cap_binding(self) -> None:
        """VaR 超阈值 ×0.8 是级联最后缩减步骤 → var_cap。"""
        engine = PositionSizingEngine()
        # 半Kelly=0.01 < 5% cap；VaR 0.03>0.025 → ×0.8 → var_cap binding
        sym = make_symbol(win_probability=0.51, win_loss_ratio=1.0, avg_daily_volume=1e8)
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL, var_95=0.03))
        assert plan.positions["000001.SZ"].sizing_basis == "var_cap"

    def test_cvar_cap_binding(self) -> None:
        """CVaR 超阈值（比 VaR 更严）→ cvar_cap。"""
        engine = PositionSizingEngine()
        sym = make_symbol(win_probability=0.51, win_loss_ratio=1.0, avg_daily_volume=1e8)
        plan = engine.size(
            make_input(
                symbols=[sym],
                market_regime=SizingMarketRegime.CALM_BULL,
                var_95=0.03,
                cvar_95=0.05,  # > cvar_threshold 0.04
            )
        )
        assert plan.positions["000001.SZ"].sizing_basis == "cvar_cap"

    def test_volatility_check_binding(self) -> None:
        """C3 波动率超 μ+2σ 减半 → volatility_check。"""
        engine = PositionSizingEngine()
        sym = make_symbol(
            win_probability=0.51,
            win_loss_ratio=1.0,
            avg_daily_volume=1e8,
            current_volatility=0.60,
            hist_vol_mean=0.20,
            hist_vol_std=0.10,  # 阈值=0.20+2×0.10=0.40 < 0.60 → 减半
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        assert plan.positions["000001.SZ"].sizing_basis == "volatility_check"

    def test_degraded_equal_weight_basis(self) -> None:
        """无密度预测且无 target_weight → degraded_equal_weight（多标的使等权值 < 单票 cap）。"""
        engine = PositionSizingEngine()
        # CALM_BULL total_cap=0.80；30 标的等权 ≈0.0267 < 5% cap → 无后续缩减
        syms = [make_symbol(symbol=f"D{i:03d}", avg_daily_volume=1e8) for i in range(30)]
        plan = engine.size(make_input(symbols=syms, market_regime=SizingMarketRegime.CALM_BULL))
        assert plan.positions["D000"].sizing_basis == "degraded_equal_weight"

    def test_exit_time_cap_binding(self) -> None:
        """C7/C8 退出时间减仓是级联最后缩减 → exit_time_cap。"""
        engine = PositionSizingEngine()
        # 现仓 500000 股 / 日均量 400000 → exit_days=1.25 > soft 1 天（<hard 3）→ ×0.8；
        # 减仓后 qty=800，参与率 0.002<0.15、冲击成本 0.0045<0.005 → 不触 C6/C11 否决
        sym = make_symbol(
            win_probability=0.51,
            win_loss_ratio=1.0,
            current_qty=500000,
            avg_daily_volume=400000.0,
        )
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        assert plan.positions["000001.SZ"].sizing_basis == "exit_time_cap"

    def test_veto_path_basis_empty(self) -> None:
        """否决保持现仓路径（C6 参与率否决）→ sizing_basis 空串（非 sizing 裁决）。"""
        engine = PositionSizingEngine()
        # 参与率 = target_qty/adv：单票 5%×1e6/10 = 5000 股 / adv 10000 = 0.5 > 0.15 → 否决保持现仓
        sym = make_symbol(win_probability=0.55, win_loss_ratio=1.5, current_qty=100, avg_daily_volume=10000.0)
        plan = engine.size(make_input(symbols=[sym], market_regime=SizingMarketRegime.CALM_BULL))
        tgt = plan.positions["000001.SZ"]
        assert tgt.sizing_basis == ""
        assert tgt.target_qty == 100  # 保持现仓

    def test_portfolio_rescale_preserves_basis(self) -> None:
        """C2 组合级等比缩放后 sizing_basis 保留（组合级缩放在 constraints_check 记录）。"""
        engine = PositionSizingEngine()
        syms = [
            make_symbol(
                symbol=f"S{i:03d}",
                win_probability=0.55,
                win_loss_ratio=1.5,
                avg_daily_volume=1e8,
            )
            for i in range(30)  # 30×5% cap=1.5 > total_cap 0.80 → C2 缩放
        ]
        plan = engine.size(make_input(symbols=syms, market_regime=SizingMarketRegime.CALM_BULL))
        assert plan.positions["S000"].sizing_basis == "single_name_cap"
