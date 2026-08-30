# [BLUEPRINT] MOD-RK-08 | docs/03_modules/_domain_risk/liquidity_monitor/blueprint.md | §test
# [MODULE] tests.risk.core.test_liquidity_monitor
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.liquidity_monitor; pandas; numpy
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_liquidity_monitor.py
# [A_test] module_id: MOD-RK-08 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-RK-08 Liquidity Monitor 单元测试.

覆盖: Amihud计算正确性(手工验证)/成交量萎缩/综合判定/
批量评估/数据不足/零成交额/RiskCheckResult转换/不可变性.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("zephyr.risk.core.liquidity_monitor", reason="liquidity_monitor not importable")

from zephyr.risk.core.liquidity_monitor import (  # noqa: E402
    DEFAULT_AMIHUD_THRESHOLD,
    DEFAULT_VOLUME_SHRINKAGE_THRESHOLD,
    InvalidLiquidityInputError,
    LiquidityMetrics,
    LiquidityMonitor,
    LiquiditySpiralConfig,
    LiquiditySpiralGrade,
    LiquiditySpiralInput,
    detect_liquidity_spiral,
)
from zephyr.risk.risk_manager_base import RiskCheckResult  # noqa: E402

# ── Mock 数据工厂 ─────────────────────────────────────────────────────


def _make_ohlcv(
    closes: list[float],
    volumes: list[float] | None = None,
) -> pd.DataFrame:
    """构造 OHLCV DataFrame。"""
    n = len(closes)
    if volumes is None:
        volumes = [1e8] * n  # 默认 1亿成交额
    dates = pd.date_range("2026-07-01", periods=n, freq="B")
    return pd.DataFrame({"close": closes, "volume": volumes}, index=dates)


#: Scenario 1: 正常流动性（低 Amihud + 正常成交量）
MOCK_LIQUID = _make_ohlcv(
    closes=[10.0, 10.1, 10.05, 10.2, 10.15, 10.3, 10.25, 10.4, 10.35, 10.5],
    volumes=[1e8] * 10,
)

#: Scenario 2: 非流动性（高 Amihud：小成交额 + 大价格变动）
MOCK_ILLIQUID = _make_ohlcv(
    closes=[10.0, 11.0, 9.5, 10.5, 9.0, 11.5, 9.8, 10.8, 9.2, 11.0],
    volumes=[1e4] * 10,  # 极小成交额 → 高 Amihud
)

#: Scenario 3: 成交量萎缩（最后一日成交额骤降）
MOCK_SHRINKAGE = _make_ohlcv(
    closes=[10.0, 10.1, 10.05, 10.2, 10.15, 10.3, 10.25, 10.4, 10.35, 10.5],
    volumes=[1e8, 1e8, 1e8, 1e8, 1e8, 1e8, 1e8, 1e8, 1e8, 1e7],  # 最后一日骤降至 1/10
)

#: Scenario 4: 数据不足（仅 1 个数据点）
MOCK_INSUFFICIENT = _make_ohlcv(closes=[10.0])

#: Scenario 5: 含零成交额（测试除零保护）
MOCK_ZERO_VOLUME = _make_ohlcv(
    closes=[10.0, 10.1, 10.05, 10.2, 10.15],
    volumes=[1e8, 0, 1e8, 0, 1e8],
)

#: Scenario 6: 使用 amount 列（优先于 volume）
MOCK_WITH_AMOUNT = pd.DataFrame(
    {
        "close": [10.0, 10.1, 10.05, 10.2, 10.15],
        "volume": [999, 999, 999, 999, 999],  # 应被忽略
        "amount": [1e8, 1e8, 1e8, 1e8, 1e8],
    }
)


# ── LiquidityMetrics 数据模型测试 ──────────────────────────────────────


class TestLiquidityMetrics:
    def test_creation(self):
        m = LiquidityMetrics(
            symbol="600000.SH",
            amihud_illiq=1e-9,
            volume_shrinkage_ratio=0.8,
            bid_ask_spread=0.001,
            is_illiquid=False,
            window=20,
            timestamp=datetime.now(UTC),
            idempotency_key="key-1",
        )
        assert m.symbol == "600000.SH"
        assert m.is_illiquid is False

    def test_frozen_immutability(self):
        m = LiquidityMetrics(
            symbol="s",
            amihud_illiq=0,
            volume_shrinkage_ratio=1,
            bid_ask_spread=None,
            is_illiquid=False,
            window=20,
            timestamp=datetime.now(UTC),
            idempotency_key="k",
        )
        with pytest.raises(AttributeError):
            m.symbol = "other"


# ── Amihud 计算测试 ───────────────────────────────────────────────────


class TestComputeAmihud:
    def test_amihud_manual_verification(self):
        """手工验证 Amihud 计算。

        2日数据: close=[10, 11], volume=[1e8, 1e8]
        r_1 = (11-10)/10 = 0.1
        ILLIQ_1 = 0.1 / 1e8 = 1e-9
        ILLIQ_N = 1e-9 (仅1个数据点)
        """
        df = _make_ohlcv(closes=[10.0, 11.0], volumes=[1e8, 1e8])
        mon = LiquidityMonitor()
        illiq = mon.compute_amihud(df["close"], df["volume"])
        expected = 0.1 / 1e8  # 1e-9
        assert illiq == pytest.approx(expected, rel=1e-6)

    def test_amihud_multi_day_average(self):
        """3日数据手工验证: (|r1|/V1 + |r2|/V2) / 2"""
        closes = pd.Series([10.0, 11.0, 9.9])
        volumes = pd.Series([1e8, 2e8, 1e8])
        mon = LiquidityMonitor()
        illiq = mon.compute_amihud(closes, volumes)

        r1 = abs(11.0 - 10.0) / 10.0  # 0.1
        r2 = abs(9.9 - 11.0) / 11.0  # 0.1
        expected = (r1 / 1e8 + r2 / 2e8) / 2
        assert illiq == pytest.approx(expected, rel=1e-6)

    def test_amihud_liquid_stock_low_value(self):
        """流动性好的股票 → 低 Amihud"""
        mon = LiquidityMonitor()
        illiq = mon.compute_amihud(MOCK_LIQUID["close"], MOCK_LIQUID["volume"])
        assert illiq < DEFAULT_AMIHUD_THRESHOLD

    def test_amihud_illiquid_stock_high_value(self):
        """非流动性股票 → 高 Amihud"""
        mon = LiquidityMonitor()
        illiq = mon.compute_amihud(MOCK_ILLIQUID["close"], MOCK_ILLIQUID["volume"])
        assert illiq > DEFAULT_AMIHUD_THRESHOLD

    def test_amihud_zero_volume_no_crash(self):
        """零成交额不崩溃（NaN 过滤后跳过）"""
        mon = LiquidityMonitor()
        illiq = mon.compute_amihud(MOCK_ZERO_VOLUME["close"], MOCK_ZERO_VOLUME["volume"])
        assert illiq >= 0  # 不崩溃，返回有效值

    def test_amihud_insufficient_data_raises(self):
        """少于2个数据点 → InvalidLiquidityInputError"""
        mon = LiquidityMonitor()
        with pytest.raises(InvalidLiquidityInputError):
            mon.compute_amihud(pd.Series([10.0]), pd.Series([1e8]))

    def test_amihud_length_mismatch_raises(self):
        """close 和 volume 长度不匹配 → InvalidLiquidityInputError"""
        mon = LiquidityMonitor()
        with pytest.raises(InvalidLiquidityInputError):
            mon.compute_amihud(pd.Series([10, 11, 12]), pd.Series([1e8, 2e8]))

    def test_amihud_window_truncation(self):
        """窗口截断：取最近 N 日"""
        # 10 日数据，窗口=3 → 只取最后 3 日
        closes = pd.Series([10.0 + i * 0.1 for i in range(10)])
        volumes = pd.Series([1e8] * 10)
        mon = LiquidityMonitor(window=3)
        illiq_n3 = mon.compute_amihud(closes, volumes, window=3)

        mon_full = LiquidityMonitor(window=10)
        illiq_n10 = mon_full.compute_amihud(closes, volumes, window=10)

        # 不同窗口结果应该不同（除非恰好均匀）
        assert illiq_n3 != illiq_n10


# ── 成交量萎缩测试 ────────────────────────────────────────────────────


class TestVolumeShrinkage:
    def test_normal_volume_ratio_near_one(self):
        """正常成交量 → ratio ≈ 1"""
        mon = LiquidityMonitor()
        ratio = mon.compute_volume_shrinkage(MOCK_LIQUID["volume"])
        assert 0.8 < ratio < 1.2

    def test_shrinkage_detected(self):
        """成交量萎缩 → ratio < 0.5"""
        mon = LiquidityMonitor()
        ratio = mon.compute_volume_shrinkage(MOCK_SHRINKAGE["volume"])
        assert ratio < DEFAULT_VOLUME_SHRINKAGE_THRESHOLD

    def test_shrinkage_manual_verification(self):
        """手工验证: 前N日均值 vs 当日"""
        volumes = pd.Series([1e8, 1e8, 1e8, 1e8, 1e7])
        mon = LiquidityMonitor(window=4)
        ratio = mon.compute_volume_shrinkage(volumes)
        # MA(前4日) = 1e8, V_today = 1e7
        expected = 1e7 / 1e8  # 0.1
        assert ratio == pytest.approx(expected, rel=1e-6)

    def test_volume_surge_ratio_above_one(self):
        """成交量放量 → ratio > 1"""
        volumes = pd.Series([1e8, 1e8, 1e8, 1e8, 5e8])
        mon = LiquidityMonitor()
        ratio = mon.compute_volume_shrinkage(volumes)
        assert ratio > 1.0

    def test_empty_volume_raises(self):
        """空序列 → InvalidLiquidityInputError"""
        mon = LiquidityMonitor()
        with pytest.raises(InvalidLiquidityInputError):
            mon.compute_volume_shrinkage(pd.Series([], dtype=float))

    def test_single_data_point_returns_one(self):
        """仅1个数据点 → 返回1.0（不判定萎缩）"""
        mon = LiquidityMonitor()
        ratio = mon.compute_volume_shrinkage(pd.Series([1e8]))
        assert ratio == 1.0


# ── 综合评估测试 ──────────────────────────────────────────────────────


class TestAssess:
    def test_liquid_stock_not_illiquid(self):
        mon = LiquidityMonitor()
        m = mon.assess("600000.SH", MOCK_LIQUID)
        assert m.is_illiquid is False
        assert m.amihud_illiq < DEFAULT_AMIHUD_THRESHOLD
        assert m.volume_shrinkage_ratio > DEFAULT_VOLUME_SHRINKAGE_THRESHOLD

    def test_illiquid_stock_detected(self):
        mon = LiquidityMonitor()
        m = mon.assess("600001.SZ", MOCK_ILLIQUID)
        assert m.is_illiquid is True
        assert m.amihud_illiq > DEFAULT_AMIHUD_THRESHOLD

    def test_shrinkage_detected(self):
        mon = LiquidityMonitor()
        m = mon.assess("600002.SH", MOCK_SHRINKAGE)
        assert m.is_illiquid is True
        assert m.volume_shrinkage_ratio < DEFAULT_VOLUME_SHRINKAGE_THRESHOLD

    def test_insufficient_data_not_illiquid(self):
        """数据不足 → 默认不判定为非流动性"""
        mon = LiquidityMonitor()
        m = mon.assess("600003.SH", MOCK_INSUFFICIENT)
        assert m.is_illiquid is False
        assert m.amihud_illiq == 0.0
        assert m.volume_shrinkage_ratio == 1.0

    def test_amount_column_preferred(self):
        """amount 列优先于 volume 列"""
        mon = LiquidityMonitor()
        m = mon.assess("600004.SH", MOCK_WITH_AMOUNT)
        # amount=1e8 → 正常流动性
        assert m.amihud_illiq < DEFAULT_AMIHUD_THRESHOLD

    def test_bid_ask_spread_stored(self):
        """买卖价差透传存储"""
        mon = LiquidityMonitor()
        m = mon.assess("600005.SH", MOCK_LIQUID, bid_ask_spread=0.002)
        assert m.bid_ask_spread == 0.002

    def test_idempotency_key_unique(self):
        """每次评估生成唯一幂等键"""
        mon = LiquidityMonitor()
        m1 = mon.assess("600000.SH", MOCK_LIQUID)
        m2 = mon.assess("600000.SH", MOCK_LIQUID)
        assert m1.idempotency_key != m2.idempotency_key

    def test_missing_close_raises(self):
        """缺少 close 列 → InvalidLiquidityInputError"""
        mon = LiquidityMonitor()
        df = pd.DataFrame({"volume": [1e8, 2e8]})
        with pytest.raises(InvalidLiquidityInputError):
            mon.assess("X", df)

    def test_missing_volume_and_amount_raises(self):
        """缺少 volume 和 amount → InvalidLiquidityInputError"""
        mon = LiquidityMonitor()
        df = pd.DataFrame({"close": [10.0, 11.0]})
        with pytest.raises(InvalidLiquidityInputError):
            mon.assess("X", df)


# ── 批量评估测试 ──────────────────────────────────────────────────────


class TestAssessBatch:
    def test_batch_mixed_results(self):
        mon = LiquidityMonitor()
        results = mon.assess_batch(
            {
                "liquid": MOCK_LIQUID,
                "illiquid": MOCK_ILLIQUID,
                "shrinkage": MOCK_SHRINKAGE,
            }
        )
        assert len(results) == 3
        liquid = next(m for m in results if m.symbol == "liquid")
        illiquid = next(m for m in results if m.symbol == "illiquid")
        assert liquid.is_illiquid is False
        assert illiquid.is_illiquid is True

    def test_batch_with_bid_ask_spreads(self):
        mon = LiquidityMonitor()
        results = mon.assess_batch(
            {"a": MOCK_LIQUID, "b": MOCK_LIQUID},
            bid_ask_spreads={"a": 0.001, "b": 0.002},
        )
        spreads = {m.symbol: m.bid_ask_spread for m in results}
        assert spreads["a"] == 0.001
        assert spreads["b"] == 0.002

    def test_batch_skips_invalid(self):
        """无效输入跳过，不崩溃"""
        mon = LiquidityMonitor()
        results = mon.assess_batch(
            {
                "valid": MOCK_LIQUID,
                "invalid": pd.DataFrame({"close": [10.0]}),  # 仅1行
            }
        )
        assert len(results) == 1  # invalid 被跳过


# ── RiskCheckResult 转换测试 ──────────────────────────────────────────


class TestToRiskCheckResult:
    def test_illiquid_to_halt(self):
        mon = LiquidityMonitor()
        m = LiquidityMetrics(
            symbol="600000.SH",
            amihud_illiq=1e-7,
            volume_shrinkage_ratio=0.3,
            bid_ask_spread=None,
            is_illiquid=True,
            window=20,
            timestamp=datetime.now(UTC),
            idempotency_key="k",
        )
        r = mon.to_risk_check_result(m)
        assert r.passed is False
        assert r.severity == "HALT"
        assert r.rule_name == "liquidity_monitor"

    def test_liquid_to_pass(self):
        mon = LiquidityMonitor()
        m = LiquidityMetrics(
            symbol="600000.SH",
            amihud_illiq=1e-10,
            volume_shrinkage_ratio=0.9,
            bid_ask_spread=None,
            is_illiquid=False,
            window=20,
            timestamp=datetime.now(UTC),
            idempotency_key="k",
        )
        r = mon.to_risk_check_result(m)
        assert r.passed is True
        assert r.severity == "info"


# ── 流动性螺旋检测（CAND-RSK-015）──────────────────────────────────────


def _spiral_input(
    *,
    current_spread: float = 0.001,
    baseline_spread: float = 0.001,
    volume_ratio: float = 1.0,
    limit_down_counts: tuple[int, ...] = (5, 8, 10),
) -> LiquiditySpiralInput:
    """默认三因子平静输入（不触发任何子分）。"""
    return LiquiditySpiralInput(
        symbol="600000.SH",
        current_spread=current_spread,
        baseline_spread=baseline_spread,
        volume_ratio=volume_ratio,
        limit_down_counts=limit_down_counts,
        timestamp=datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
    )


class TestLiquiditySpiralConfig:
    def test_defaults_valid(self):
        cfg = LiquiditySpiralConfig()
        assert cfg.spread_expansion_early == 1.5
        assert cfg.chain_severe_days == 3

    def test_spread_thresholds_inverted_raises(self):
        with pytest.raises(InvalidLiquidityInputError):
            LiquiditySpiralConfig(spread_expansion_early=2.5, spread_expansion_severe=1.5)

    def test_shrink_thresholds_inverted_raises(self):
        with pytest.raises(InvalidLiquidityInputError):
            LiquiditySpiralConfig(volume_shrink_early=0.4, volume_shrink_severe=0.7)

    def test_chain_days_inverted_raises(self):
        with pytest.raises(InvalidLiquidityInputError):
            LiquiditySpiralConfig(chain_early_days=3, chain_severe_days=2)


class TestDetectLiquiditySpiral:
    def test_all_calm_none(self):
        alert = detect_liquidity_spiral(_spiral_input())
        assert alert.grade is LiquiditySpiralGrade.NONE
        assert alert.composite_score == pytest.approx(0.0)
        assert alert.active_factors == ()
        assert alert.limit_down_chain_days == 0

    def test_single_factor_not_spiral(self):
        """单因子满堂（价差×3）仍不判螺旋——螺旋须多因子共振"""
        alert = detect_liquidity_spiral(_spiral_input(current_spread=0.003))
        assert alert.spread_expansion_ratio == pytest.approx(3.0)
        assert alert.composite_score == pytest.approx(1.0 / 3.0)
        assert alert.grade is LiquiditySpiralGrade.NONE

    def test_spread_severe_plus_shrink_early_is_early(self):
        """价差满分 + 量缩半分 = 0.5 → early"""
        alert = detect_liquidity_spiral(_spiral_input(current_spread=0.003, volume_ratio=0.6))
        assert alert.composite_score == pytest.approx(0.5)
        assert alert.grade is LiquiditySpiralGrade.EARLY
        assert set(alert.active_factors) == {"spread_expansion", "volume_shrink"}

    def test_all_half_is_early(self):
        """三因子均半分 = 0.5 → early"""
        alert = detect_liquidity_spiral(
            _spiral_input(current_spread=0.0015, volume_ratio=0.7, limit_down_counts=(10, 40, 50))
        )
        assert alert.limit_down_chain_days == 2
        assert alert.composite_score == pytest.approx(0.5)
        assert alert.grade is LiquiditySpiralGrade.EARLY

    def test_two_severe_is_accelerating(self):
        """价差满分 + 量缩满分 = 2/3 → accelerating"""
        alert = detect_liquidity_spiral(_spiral_input(current_spread=0.003, volume_ratio=0.3))
        assert alert.composite_score == pytest.approx(2.0 / 3.0)
        assert alert.grade is LiquiditySpiralGrade.ACCELERATING

    def test_two_severe_one_half_is_severe(self):
        """2×1 + 0.5 合成 5/6 ≈ 0.833 → severe"""
        alert = detect_liquidity_spiral(
            _spiral_input(current_spread=0.003, volume_ratio=0.3, limit_down_counts=(10, 40, 50))
        )
        assert alert.composite_score == pytest.approx(2.5 / 3.0)
        assert alert.grade is LiquiditySpiralGrade.SEVERE

    def test_all_severe_is_severe(self):
        """三因子满堂 = 1.0 → severe"""
        alert = detect_liquidity_spiral(
            _spiral_input(current_spread=0.005, volume_ratio=0.2, limit_down_counts=(50, 60, 80))
        )
        assert alert.composite_score == pytest.approx(1.0)
        assert alert.grade is LiquiditySpiralGrade.SEVERE
        assert len(alert.active_factors) == 3
        assert "severe" in alert.message

    def test_chain_counts_trailing_only(self):
        """连环跌停只数尾部连续段：[40, 5, 60, 70] → 2（中间断层重置）"""
        alert = detect_liquidity_spiral(_spiral_input(limit_down_counts=(40, 5, 60, 70)))
        assert alert.limit_down_chain_days == 2

    def test_spread_boundary_at_early(self):
        """价差扩大恰好 = 早警线 1.5 → 计半分"""
        alert = detect_liquidity_spiral(_spiral_input(current_spread=0.0015))
        assert alert.spread_expansion_ratio == pytest.approx(1.5)
        assert "spread_expansion" in alert.active_factors

    def test_shrink_boundary_at_early(self):
        """量比恰好 = 早警线 0.7 → 计半分"""
        alert = detect_liquidity_spiral(_spiral_input(volume_ratio=0.7))
        assert "volume_shrink" in alert.active_factors

    def test_timestamp_passthrough(self):
        ts = datetime(2026, 8, 30, 14, 30, tzinfo=UTC)
        inp = LiquiditySpiralInput(
            symbol="X",
            current_spread=0.001,
            baseline_spread=0.001,
            volume_ratio=1.0,
            limit_down_counts=(),
            timestamp=ts,
        )
        assert detect_liquidity_spiral(inp).timestamp == ts

    def test_empty_counts_chain_zero(self):
        alert = detect_liquidity_spiral(_spiral_input(limit_down_counts=()))
        assert alert.limit_down_chain_days == 0
        assert alert.grade is LiquiditySpiralGrade.NONE

    def test_invalid_inputs_raise(self):
        with pytest.raises(InvalidLiquidityInputError):
            detect_liquidity_spiral(_spiral_input(current_spread=-0.001))
        with pytest.raises(InvalidLiquidityInputError):
            detect_liquidity_spiral(_spiral_input(baseline_spread=0.0))
        with pytest.raises(InvalidLiquidityInputError):
            detect_liquidity_spiral(_spiral_input(volume_ratio=-0.1))
        with pytest.raises(InvalidLiquidityInputError):
            detect_liquidity_spiral(_spiral_input(limit_down_counts=(10, -1)))

    def test_empty_symbol_raises(self):
        inp = LiquiditySpiralInput(
            symbol="  ",
            current_spread=0.001,
            baseline_spread=0.001,
            volume_ratio=1.0,
            limit_down_counts=(),
        )
        with pytest.raises(InvalidLiquidityInputError):
            detect_liquidity_spiral(inp)
