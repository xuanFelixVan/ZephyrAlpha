# [BLUEPRINT] MOD-RK-21 | docs/03_modules/_domain_risk/liquidity_crisis_manager/blueprint.md | §test
# [MODULE] tests.risk.core.test_liquidity_crisis_manager
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.liquidity_crisis_manager; zephyr.risk.core.ashare_systemic_risk_detector; pytest
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_liquidity_crisis_manager.py
# [A_test] module_id: MOD-RK-21 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-RK-21 Liquidity Crisis Manager 单元测试.

覆盖: sell_pressure OBI反转 / Quoted Spread / 涨跌停五状态检测 / 有效价差解析 /
危机恢复 hysteresis+min_hold 门控 / IPO 抽离预警四级 / 盘中单遍编排
(触发 LEVEL_1/跌停触发/涨停跳过/恢复迁移/恢复被 min_hold 阻断/LEVEL_3 逃生指令).
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest

pytest.importorskip(
    "zephyr.risk.core.liquidity_crisis_manager",
    reason="liquidity_crisis_manager not importable",
)

from zephyr.risk.core.ashare_systemic_risk_detector import (  # noqa: E402
    AshareSystemicRiskDetector,
    SystemicRiskAlertLevel,
)
from zephyr.risk.core.liquidity_crisis_manager import (  # noqa: E402
    InvalidLiquidityCrisisInputError,
    IPODrainLevel,
    IPOEvent,
    LimitStatus,
    LiquidityCrisisConfig,
    LiquidityRecoveryState,
    MarketLiquiditySnapshot,
    RecoveryCheckInput,
    check_recovery,
    compute_bid_ask_spread,
    compute_ipo_liquidity_drain,
    compute_sell_pressure,
    detect_limit_status,
    resolve_effective_spread,
    run_intraday_liquidity_check,
)

NOW = datetime(2026, 8, 13, 14, 0, 0, tzinfo=UTC)
TODAY = NOW.date()


# ── Mock 数据工厂 ─────────────────────────────────────────────────────


def _snapshot(
    *,
    last_price: float = 10.0,
    bid_price: float | None = 9.99,
    ask_price: float | None = 10.01,
    bid_volumes: tuple[float, ...] = (5000.0, 4000.0, 3000.0, 2000.0, 1000.0),
    ask_volumes: tuple[float, ...] = (5000.0, 4000.0, 3000.0, 2000.0, 1000.0),
    limit_up_price: float = 11.0,
    limit_down_price: float = 9.0,
) -> MarketLiquiditySnapshot:
    return MarketLiquiditySnapshot(
        symbol="600000.SH",
        last_price=last_price,
        bid_price=bid_price,
        ask_price=ask_price,
        bid_volumes=bid_volumes,
        ask_volumes=ask_volumes,
        limit_up_price=limit_up_price,
        limit_down_price=limit_down_price,
        timestamp=NOW,
    )


# ── compute_sell_pressure（37号 §3.1.1）──


class TestComputeSellPressure:
    def test_balanced_book_returns_half(self):
        assert compute_sell_pressure([100, 100], [100, 100]) == pytest.approx(0.5)

    def test_pure_ask_returns_one(self):
        assert compute_sell_pressure([0, 0], [100, 50]) == pytest.approx(1.0)

    def test_pure_bid_returns_zero(self):
        assert compute_sell_pressure([100, 50], [0, 0]) == pytest.approx(0.0)

    def test_empty_book_returns_neutral(self):
        assert compute_sell_pressure([], []) == pytest.approx(0.5)

    def test_zero_total_returns_neutral(self):
        assert compute_sell_pressure([0.0], [0.0]) == pytest.approx(0.5)

    def test_crisis_threshold_scenario(self):
        # 卖压 0.70 ≥ 0.65 触发线：买盘仅占 30%
        pressure = compute_sell_pressure([300.0], [700.0])
        assert pressure == pytest.approx(0.70)
        assert pressure >= 0.65

    def test_negative_volume_raises(self):
        with pytest.raises(InvalidLiquidityCrisisInputError):
            compute_sell_pressure([-1.0], [100.0])


# ── compute_bid_ask_spread（37号 §3.1.2）──


class TestComputeBidAskSpread:
    def test_normal_spread(self):
        # (10.01-9.99)/10.00 = 0.002
        assert compute_bid_ask_spread(9.99, 10.01) == pytest.approx(0.002)

    def test_none_bid_returns_none(self):
        assert compute_bid_ask_spread(None, 10.01) is None

    def test_none_ask_returns_none(self):
        assert compute_bid_ask_spread(9.99, None) is None

    def test_zero_price_returns_none(self):
        assert compute_bid_ask_spread(0.0, 10.01) is None

    def test_crossed_book_raises(self):
        with pytest.raises(InvalidLiquidityCrisisInputError):
            compute_bid_ask_spread(10.01, 9.99)

    def test_crisis_threshold_scenario(self):
        # spread 0.006 ≥ 0.005 触发线
        spread = compute_bid_ask_spread(9.97, 10.03)
        assert spread == pytest.approx(0.006, abs=1e-6)
        assert spread >= 0.005


# ── detect_limit_status（37号 §3.5.1）──


class TestDetectLimitStatus:
    def test_limit_up_sealed(self):
        status = detect_limit_status(11.0, 11.0, 9.0, bid_price=11.0, ask_price=None)
        assert status is LimitStatus.LIMIT_UP

    def test_limit_down_sealed(self):
        status = detect_limit_status(9.0, 11.0, 9.0, bid_price=None, ask_price=9.0)
        assert status is LimitStatus.LIMIT_DOWN

    def test_at_limit_up_but_ask_present_is_near(self):
        # 价达涨停但卖一仍在（未封死）→ NEAR_UP 而非 LIMIT_UP
        status = detect_limit_status(11.0, 11.0, 9.0, bid_price=11.0, ask_price=11.0)
        assert status is LimitStatus.NEAR_UP

    def test_near_up(self):
        # 10.98 >= 11.0 * 0.995 = 10.945
        status = detect_limit_status(10.98, 11.0, 9.0, bid_price=10.97, ask_price=10.99)
        assert status is LimitStatus.NEAR_UP

    def test_near_down(self):
        # 9.04 <= 9.0 * 1.005 = 9.045
        status = detect_limit_status(9.04, 11.0, 9.0, bid_price=9.03, ask_price=9.05)
        assert status is LimitStatus.NEAR_DOWN

    def test_normal(self):
        status = detect_limit_status(10.0, 11.0, 9.0, bid_price=9.99, ask_price=10.01)
        assert status is LimitStatus.NORMAL

    def test_inverted_limits_raise(self):
        with pytest.raises(InvalidLiquidityCrisisInputError):
            detect_limit_status(10.0, 9.0, 11.0, bid_price=9.99, ask_price=10.01)

    def test_nonpositive_price_raises(self):
        with pytest.raises(InvalidLiquidityCrisisInputError):
            detect_limit_status(0.0, 11.0, 9.0, bid_price=9.99, ask_price=10.01)


# ── resolve_effective_spread（37号 §3.5 算法断裂修复）──


class TestResolveEffectiveSpread:
    def test_limit_down_forces_one(self):
        # 跌停 spread 置 1.0 使 AND 条件可满足（不得为 None 被跳过）
        assert resolve_effective_spread(LimitStatus.LIMIT_DOWN, None) == 1.0

    def test_limit_up_returns_none(self):
        # 涨停买压主导非危机，置 None 跳过检查
        assert resolve_effective_spread(LimitStatus.LIMIT_UP, 0.002) is None

    def test_normal_passthrough(self):
        assert resolve_effective_spread(LimitStatus.NORMAL, 0.002) == pytest.approx(0.002)

    def test_normal_none_passthrough(self):
        assert resolve_effective_spread(LimitStatus.NORMAL, None) is None


# ── check_recovery（37号 §3.6）──


class TestCheckRecovery:
    KW = dict(
        trigger_threshold_spread=0.005,
        recovery_threshold_spread=0.0025,
        trigger_threshold_pressure=0.65,
        recovery_threshold_pressure=0.50,
    )

    def test_min_hold_blocks_recovery(self):
        # elapsed 8 < min_hold 10 → None
        result = check_recovery(
            RecoveryCheckInput(
                current_spread=0.001,
                current_sell_pressure=0.40,
                min_hold_minutes=10,
                elapsed=8.0,
                current_level=1,
                active_signals=0,
                **self.KW,
            )
        )
        assert result is None

    def test_level1_full_recovery(self):
        # 双半阈值满足 + 0 信号 + 持续足够 → 0（正常态）
        result = check_recovery(
            RecoveryCheckInput(
                current_spread=0.002,
                current_sell_pressure=0.45,
                min_hold_minutes=10,
                elapsed=12.0,
                current_level=1,
                active_signals=0,
                **self.KW,
            )
        )
        assert result == 0
        assert result is not None  # 0 是有效恢复，须 is not None 判定

    def test_level1_hysteresis_blocks(self):
        # spread 0.003 介于恢复阈值 0.0025 与触发阈值 0.005 之间 → 不恢复
        result = check_recovery(
            RecoveryCheckInput(
                current_spread=0.003,
                current_sell_pressure=0.45,
                min_hold_minutes=10,
                elapsed=12.0,
                current_level=1,
                active_signals=0,
                **self.KW,
            )
        )
        assert result is None

    def test_level1_active_signal_blocks(self):
        # 信号未归零（spread 仍超触发阈值）→ 不恢复
        result = check_recovery(
            RecoveryCheckInput(
                current_spread=0.002,
                current_sell_pressure=0.45,
                min_hold_minutes=10,
                elapsed=12.0,
                current_level=1,
                active_signals=1,
                **self.KW,
            )
        )
        assert result is None

    def test_level2_downgrades_to_1(self):
        # 信号降至 1 + spread < 0.0025*1.2=0.003 → 降到 LEVEL_1
        result = check_recovery(
            RecoveryCheckInput(
                current_spread=0.0028,
                current_sell_pressure=0.60,
                min_hold_minutes=15,
                elapsed=20.0,
                current_level=2,
                active_signals=1,
                **self.KW,
            )
        )
        assert result == 1

    def test_level3_downgrades_to_2(self):
        # 冷却期满（min_hold=30 覆盖 Kill Switch 冷却）+ 信号≤2 + spread 放宽
        result = check_recovery(
            RecoveryCheckInput(
                current_spread=0.0028,
                current_sell_pressure=0.70,
                min_hold_minutes=30,
                elapsed=35.0,
                current_level=3,
                active_signals=2,
                **self.KW,
            )
        )
        assert result == 2

    def test_invalid_level_raises(self):
        with pytest.raises(InvalidLiquidityCrisisInputError):
            check_recovery(
                RecoveryCheckInput(
                    current_spread=0.001,
                    current_sell_pressure=0.40,
                    min_hold_minutes=10,
                    elapsed=12.0,
                    current_level=0,
                    active_signals=0,
                    **self.KW,
                )
            )

    def test_recovery_above_trigger_rejected(self):
        # 恢复阈值 ≥ 触发阈值 = 无 hysteresis 缓冲带，构造即拒绝
        with pytest.raises(InvalidLiquidityCrisisInputError):
            check_recovery(
                RecoveryCheckInput(
                    current_spread=0.001,
                    current_sell_pressure=0.40,
                    trigger_threshold_spread=0.005,
                    recovery_threshold_spread=0.006,
                    trigger_threshold_pressure=0.65,
                    recovery_threshold_pressure=0.50,
                    min_hold_minutes=10,
                    elapsed=12.0,
                    current_level=1,
                    active_signals=0,
                )
            )


# ── compute_ipo_liquidity_drain（37号 §3.2a）──


class TestComputeIpoLiquidityDrain:
    def test_negligible(self):
        ipos = [IPOEvent("600001.SH", TODAY + timedelta(days=2), 100.0)]
        result = compute_ipo_liquidity_drain(ipos, 27000.0, today=TODAY)
        assert result.drain_level is IPODrainLevel.NEGLIGIBLE
        assert result.position_cap_adjustment == 1.0
        assert result.counted_ipos == 1

    def test_moderate(self):
        # 405/27000 = 1.5% → MODERATE
        ipos = [IPOEvent("600001.SH", TODAY + timedelta(days=3), 405.0)]
        result = compute_ipo_liquidity_drain(ipos, 27000.0, today=TODAY)
        assert result.drain_level is IPODrainLevel.MODERATE
        assert result.position_cap_adjustment == pytest.approx(0.90)

    def test_severe_changxin_scenario(self):
        # 长鑫科技 666/27000 ≈ 2.47% → SEVERE（memo §3.2a 实证场景）
        ipos = [IPOEvent("688825.SH", TODAY + timedelta(days=1), 666.0)]
        result = compute_ipo_liquidity_drain(ipos, 27000.0, today=TODAY)
        assert result.drain_level is IPODrainLevel.SEVERE
        assert result.position_cap_adjustment == pytest.approx(0.75)

    def test_extreme(self):
        ipos = [IPOEvent("600001.SH", TODAY + timedelta(days=1), 900.0)]
        result = compute_ipo_liquidity_drain(ipos, 27000.0, today=TODAY)
        assert result.drain_level is IPODrainLevel.EXTREME
        assert result.position_cap_adjustment == pytest.approx(0.60)

    def test_horizon_filter_excludes_far_future(self):
        # 上市日 6 天后 > 5 日前瞻窗口 → 不计入
        ipos = [IPOEvent("600001.SH", TODAY + timedelta(days=6), 900.0)]
        result = compute_ipo_liquidity_drain(ipos, 27000.0, today=TODAY)
        assert result.counted_ipos == 0
        assert result.drain_level is IPODrainLevel.NEGLIGIBLE

    def test_past_ipo_excluded(self):
        ipos = [IPOEvent("600001.SH", TODAY - timedelta(days=1), 900.0)]
        result = compute_ipo_liquidity_drain(ipos, 27000.0, today=TODAY)
        assert result.counted_ipos == 0

    def test_multiple_ipos_accumulate(self):
        ipos = [
            IPOEvent("600001.SH", TODAY + timedelta(days=1), 200.0),
            IPOEvent("600002.SH", TODAY + timedelta(days=4), 200.0),
        ]
        result = compute_ipo_liquidity_drain(ipos, 27000.0, today=TODAY)
        assert result.counted_ipos == 2
        assert result.drain_ratio == pytest.approx(400.0 / 27000.0)

    def test_invalid_market_volume_raises(self):
        with pytest.raises(InvalidLiquidityCrisisInputError):
            compute_ipo_liquidity_drain([], 0.0, today=TODAY)

    def test_negative_raise_raises(self):
        ipos = [IPOEvent("600001.SH", TODAY + timedelta(days=1), -5.0)]
        with pytest.raises(InvalidLiquidityCrisisInputError):
            compute_ipo_liquidity_drain(ipos, 27000.0, today=TODAY)


# ── LiquidityRecoveryState ──


class TestLiquidityRecoveryState:
    def test_enter_and_elapsed(self):
        state = LiquidityRecoveryState()
        assert not state.in_crisis
        state.enter_crisis(1, NOW)
        assert state.in_crisis and state.level == 1
        later = NOW + timedelta(minutes=12)
        assert state.elapsed_minutes(later) == pytest.approx(12.0)

    def test_exit_to_normal_clears(self):
        state = LiquidityRecoveryState()
        state.enter_crisis(1, NOW)
        state.exit_crisis(0, NOW + timedelta(minutes=12))
        assert not state.in_crisis and state.level == 0 and state.entered_at is None

    def test_exit_downgrade_keeps_anchor(self):
        state = LiquidityRecoveryState()
        state.enter_crisis(3, NOW)
        ts = NOW + timedelta(minutes=31)
        state.exit_crisis(2, ts)
        assert state.in_crisis and state.level == 2 and state.entered_at == ts

    def test_exit_upward_raises(self):
        state = LiquidityRecoveryState()
        state.enter_crisis(1, NOW)
        with pytest.raises(InvalidLiquidityCrisisInputError):
            state.exit_crisis(2, NOW)  # 恢复只能降级不能升级


# ── run_intraday_liquidity_check（37号 §3.8 编排）──


class TestRunIntradayLiquidityCheck:
    def test_normal_market_no_crisis(self):
        state = LiquidityRecoveryState()
        result = run_intraday_liquidity_check(_snapshot(), state, now=NOW)
        assert result.alert.alert_level is SystemicRiskAlertLevel.NONE
        assert not result.halt_new_orders
        assert result.recovery_target is None
        assert not state.in_crisis

    def test_crisis_triggers_level1(self):
        # 卖压 0.70 + spread 0.006 双超阈 → LEVEL_1 停开仓
        snap = _snapshot(
            bid_price=9.97,
            ask_price=10.03,
            bid_volumes=(300.0,),
            ask_volumes=(700.0,),
        )
        state = LiquidityRecoveryState()
        result = run_intraday_liquidity_check(snap, state, now=NOW)
        assert result.alert.alert_level is SystemicRiskAlertLevel.LEVEL_1
        assert result.halt_new_orders
        assert result.position_cap == pytest.approx(1.0)  # LEVEL_1 现有仓位不动
        assert result.escape_directive is None
        assert state.in_crisis and state.level == 1

    def test_limit_down_triggers_crisis(self):
        # 跌停：卖压≈1.0 + effective_spread=1.0 → 双条件 AND 满足（算法断裂修复验证）
        snap = _snapshot(
            last_price=9.0,
            bid_price=None,
            ask_price=9.0,
            bid_volumes=(0.0,),
            ask_volumes=(9999.0,),
        )
        state = LiquidityRecoveryState()
        result = run_intraday_liquidity_check(snap, state, now=NOW)
        assert result.limit_status is LimitStatus.LIMIT_DOWN
        assert result.effective_spread == 1.0
        assert result.alert.alert_level is SystemicRiskAlertLevel.LEVEL_1
        assert result.halt_new_orders

    def test_limit_up_never_triggers(self):
        # 涨停：spread 置 None 跳过检查（买压主导非危机）
        snap = _snapshot(
            last_price=11.0,
            bid_price=11.0,
            ask_price=None,
            bid_volumes=(9999.0,),
            ask_volumes=(0.0,),
        )
        state = LiquidityRecoveryState()
        result = run_intraday_liquidity_check(snap, state, now=NOW)
        assert result.limit_status is LimitStatus.LIMIT_UP
        assert result.effective_spread is None
        assert result.alert.alert_level is SystemicRiskAlertLevel.NONE

    def test_recovery_after_crisis(self):
        # 先触发 LEVEL_1，12 分钟后盘口恢复（卖压 0.45<0.50 恢复阈值
        # + spread 0.002<0.0025 半阈值 + 0 活动信号）→ 恢复至正常态
        detector = AshareSystemicRiskDetector()
        state = LiquidityRecoveryState()
        crisis_snap = _snapshot(
            bid_price=9.97,
            ask_price=10.03,
            bid_volumes=(300.0,),
            ask_volumes=(700.0,),
        )
        run_intraday_liquidity_check(crisis_snap, state, detector=detector, now=NOW)
        assert state.in_crisis and state.level == 1

        later = NOW + timedelta(minutes=12)
        ok_snap = _snapshot(
            bid_volumes=(550.0,),
            ask_volumes=(450.0,),  # 卖压 0.45 < 0.50 恢复阈值
        )
        result = run_intraday_liquidity_check(ok_snap, state, detector=detector, now=later)
        assert result.recovery_target == 0
        assert not state.in_crisis
        assert not result.halt_new_orders
        assert result.position_cap == pytest.approx(1.0)

    def test_recovery_blocked_by_min_hold(self):
        # 触发后仅 5 分钟（<10 分钟门控）→ 不恢复
        detector = AshareSystemicRiskDetector()
        state = LiquidityRecoveryState()
        crisis_snap = _snapshot(
            bid_price=9.97,
            ask_price=10.03,
            bid_volumes=(300.0,),
            ask_volumes=(700.0,),
        )
        run_intraday_liquidity_check(crisis_snap, state, detector=detector, now=NOW)

        early = NOW + timedelta(minutes=5)
        result = run_intraday_liquidity_check(_snapshot(), state, detector=detector, now=early)
        assert result.recovery_target is None
        assert state.in_crisis and state.level == 1

    def test_level3_escape_directive(self):
        # 3 信号（流动性危机+量化踩踏+外围冲击）→ LEVEL_3 清仓 + 逃生指令
        detector = AshareSystemicRiskDetector()
        state = LiquidityRecoveryState()
        crisis_snap = _snapshot(
            bid_price=9.97,
            ask_price=10.03,
            bid_volumes=(300.0,),
            ask_volumes=(700.0,),
        )
        # 直接以 detector.check 构造多信号场景等价验证：本模块编排只传流动性两输入，
        # LEVEL_3 由 MOD-RK-10 聚合其他信号产出；此处验证逃生指令通路。
        alert = detector.check(
            sell_pressure=0.70,
            bid_ask_spread=0.006,
            index_change_pct=-0.03,
            volume_surge_ratio=2.5,
            external_market_change=-0.04,
            now=NOW,
        )
        assert alert.alert_level is SystemicRiskAlertLevel.LEVEL_3
        directive = detector.build_escape_directive(alert)
        assert directive["action"] == "liquidate_all"
        assert directive["position_cap"] == 0.0
        assert directive["kill_switch_required"] is True
        # 编排层单流动性信号 → LEVEL_1（分级响应不被本模块放大）
        result = run_intraday_liquidity_check(crisis_snap, state, detector=detector, now=NOW)
        assert result.alert.alert_level is SystemicRiskAlertLevel.LEVEL_1

    def test_no_crisis_no_recovery_check_when_not_in_crisis(self):
        # 非危机且未在危机中 → 不做恢复判定（结果 recovery_target=None）
        state = LiquidityRecoveryState()
        result = run_intraday_liquidity_check(_snapshot(), state, now=NOW)
        assert result.recovery_target is None
