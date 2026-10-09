# [MODULE] tests.intelligence.test_event_score
# [DOMAIN] D_INTELLIGENCE
# [TTL] permanent
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/intelligence/test_event_score.py -q
"""test_event_score.py — event_score 单元测试（26 号 §2.5 事件驱动评分/进出场）。

覆盖：
  1. event_score_single_factor —— 权重表/方向/情绪/衰减/极端修正/边界 ±1.5
  2. event_score_dual_factor —— SUE+EAR 组合/极端 EAR 反转/std 缺失降级
  3. expectation_gap_with_revision_momentum —— 季报动量/年报静态降权/零值守卫
  4. overnight_return_jump —— 正常/非法收盘价
  5. event_score_triple_factor —— 温和 ORJ 加权/极端 ORJ 反转/契约守卫
  6. compute_event_score —— 调度与降级链（triple→dual→single）
  7. should_enter / should_enter_with_confirmation —— 四分支+确认型第三分支
  8. should_exit —— 三道线+T+1 holding_days 语义+优先级
  9. trading_days_ago —— 周末跨越/n=0/负值异常
  10. has_contradictory_event / has_volume_confirmation —— 辅助函数
  11. check_selling_pressure_absorbed —— CVD/量能/企稳三共振+退化
  12. 量能薄封装 —— fake provider 委托/非法 symbol 守卫
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from zephyr.intelligence.event_score import (
    DECAY_EXIT_WINDOW,
    ClickHouseKlineVolumeProvider,
    EarningsFactorData,
    EventRecord,
    EventScoreError,
    ListEventStore,
    StoredEvent,
    check_selling_pressure_absorbed,
    compute_event_score,
    event_score_dual_factor,
    event_score_single_factor,
    event_score_triple_factor,
    expectation_gap_with_revision_momentum,
    has_contradictory_event,
    has_volume_confirmation,
    overnight_return_jump,
    should_enter,
    should_enter_with_confirmation,
    should_exit,
    trading_days_ago,
    volume_ma,
    volume_series,
)


def _ev(**kw) -> EventRecord:
    base = dict(symbol="600000.SH", class_="ma", surprise_direction=1.0, sentiment_score=0.8)
    base.update(kw)
    return EventRecord(**base)


# ============ 1. single_factor ============


class TestSingleFactor:
    def test_basic_positive(self):
        # ma 权重 1.2 × 1 × 0.8 × 1.0 × 1.0
        assert event_score_single_factor(_ev()) == pytest.approx(1.2 * 0.8)

    def test_unknown_class_weight_default_1(self):
        e = _ev(class_="unknown_class", sentiment_score=0.5)
        assert event_score_single_factor(e) == pytest.approx(0.5)

    def test_negative_direction(self):
        e = _ev(surprise_direction=-1.0)
        assert event_score_single_factor(e) < 0

    def test_extreme_reaction_modifier_shrinks(self):
        normal = event_score_single_factor(_ev())
        extreme = event_score_single_factor(_ev(extreme_reaction_modifier=0.3))
        assert extreme == pytest.approx(normal * 0.3)

    def test_decay_stage_factor(self):
        rising = event_score_single_factor(_ev(decay_stage_factor=1.0))
        post = event_score_single_factor(_ev(decay_stage_factor=0.2))
        assert post == pytest.approx(rising * 0.2)

    def test_bound_max_1_5(self):
        e = _ev(class_="surprise", surprise_direction=1.0, sentiment_score=1.0)
        assert event_score_single_factor(e) == pytest.approx(1.5)
        e2 = _ev(class_="surprise", surprise_direction=-1.0, sentiment_score=1.0)
        assert event_score_single_factor(e2) == pytest.approx(-1.5)


# ============ 2. dual_factor ============


def _dual_data(**kw) -> EarningsFactorData:
    base = dict(consensus_eps=1.0, surprise_std=0.1, ear=0.01)
    base.update(kw)
    return EarningsFactorData(**base)


class TestDualFactor:
    def test_normal_combination(self):
        e = _ev(class_="earnings", actual_eps=1.2)
        # sue=(1.2-1.0)/0.1=2 → z=2；ear=0.01 → w=1/3
        # combined = 2*(1-1/3*0.5) - 0.01*(1/3)*10
        expected = 2 * (1 - (1 / 3) * 0.5) - 0.01 * (1 / 3) * 10
        assert event_score_dual_factor(e, _dual_data()) == pytest.approx(expected)

    def test_extreme_ear_full_reversal_weight(self):
        e = _ev(class_="earnings", actual_eps=1.2)
        # ear=0.06 → w=1.0 → combined = z*0.5 - 0.6
        score = event_score_dual_factor(e, _dual_data(ear=0.06))
        assert score == pytest.approx(2 * 0.5 - 0.6)

    def test_zero_surprise_std_degrades_sue_to_zero(self):
        e = _ev(class_="earnings", actual_eps=5.0)
        score = event_score_dual_factor(e, _dual_data(surprise_std=0.0, ear=0.0))
        assert score == 0.0

    def test_sue_winsorized_at_3(self):
        e = _ev(class_="earnings", actual_eps=100.0)
        # sue=990 → z 裁剪 3；ear=0 → combined = 3
        assert event_score_dual_factor(e, _dual_data(ear=0.0)) == pytest.approx(3.0)


# ============ 3. expectation_gap ============


class TestExpectationGap:
    def test_quarterly_uses_revision_momentum(self):
        gap = expectation_gap_with_revision_momentum(
            1.2,
            "Q1",
            consensus=1.0,
            consensus_before=1.0,
            consensus_after=1.1,
        )
        assert gap == pytest.approx(0.1)

    def test_annual_uses_static_gap_discounted(self):
        gap = expectation_gap_with_revision_momentum(
            1.4,
            "annual",
            consensus=1.0,
            consensus_before=1.0,
            consensus_after=2.0,
        )
        # 静态 (1.4-1.0)/1.0=0.4 × annual 权重 0.4（忽略巨大的上修动量）
        assert gap == pytest.approx(0.4 * 0.4)

    def test_zero_consensus_static_gap_zero(self):
        gap = expectation_gap_with_revision_momentum(
            1.0,
            "annual",
            consensus=0.0,
            consensus_before=1.0,
            consensus_after=1.1,
        )
        assert gap == 0.0

    def test_zero_consensus_before_revision_zero(self):
        gap = expectation_gap_with_revision_momentum(
            1.0,
            "Q1",
            consensus=1.0,
            consensus_before=0.0,
            consensus_after=1.1,
        )
        assert gap == 0.0

    def test_unknown_report_type_still_revision(self):
        gap = expectation_gap_with_revision_momentum(
            1.0,
            "weird",
            consensus=1.0,
            consensus_before=1.0,
            consensus_after=1.2,
        )
        assert gap == pytest.approx(0.2)


# ============ 4. ORJ ============


class TestOvernightReturnJump:
    def test_normal(self):
        assert overnight_return_jump(10.5, 10.0) == pytest.approx(0.05)

    def test_nonpositive_close_degrades_zero(self):
        assert overnight_return_jump(10.0, 0.0) == 0.0
        assert overnight_return_jump(10.0, -1.0) == 0.0


# ============ 5. triple_factor ============


def _triple_data(**kw) -> EarningsFactorData:
    base = dict(
        consensus_eps=1.0,
        surprise_std=0.1,
        ear=0.01,
        consensus_before=1.0,
        consensus_after=1.1,
        open_next=10.1,
        close_event=10.0,
    )
    base.update(kw)
    return EarningsFactorData(**base)


class TestTripleFactor:
    def test_mild_orj_weighted(self):
        e = _ev(class_="earnings", actual_eps=1.2, report_type="Q1")
        # sue=revision 0.1 → z=0.1；orj=0.01（温和）→ signal 0.01；extremity=max(0.01,0.01)/0.03=1/3
        expected = 0.1 * (1 - (1 / 3) * 0.3) + 0.01 * 2.0 - 0.01 * (1 / 3) * 10
        assert event_score_triple_factor(e, _triple_data()) == pytest.approx(expected)

    def test_extreme_orj_reversal_correction(self):
        e = _ev(class_="earnings", actual_eps=1.2, report_type="Q1")
        # orj=0.05 > 3% → signal=-0.025；extremity=max(0.01,0.05)/0.03>1 → w=1
        expected = 0.1 * (1 - 0.3) + (-0.025) * 2.0 - 0.01 * 10
        score = event_score_triple_factor(e, _triple_data(open_next=10.5))
        assert score == pytest.approx(expected)

    def test_missing_triple_fields_raises(self):
        e = _ev(class_="earnings", actual_eps=1.2)
        with pytest.raises(EventScoreError):
            event_score_triple_factor(e, _dual_data())


# ============ 6. compute_event_score 调度 ============


class TestComputeEventScore:
    def test_non_earnings_ignores_data_single(self):
        e = _ev(class_="ma")
        assert compute_event_score(e, _triple_data()) == pytest.approx(event_score_single_factor(e))

    def test_earnings_with_triple_data_uses_triple(self):
        e = _ev(class_="earnings", actual_eps=1.2, report_type="Q1")
        d = _triple_data()
        assert compute_event_score(e, d) == pytest.approx(event_score_triple_factor(e, d))

    def test_earnings_with_dual_only_data_uses_dual(self):
        e = _ev(class_="earnings", actual_eps=1.2)
        d = _dual_data()
        assert compute_event_score(e, d) == pytest.approx(event_score_dual_factor(e, d))

    def test_earnings_without_data_degrades_single(self):
        e = _ev(class_="earnings", sentiment_score=0.5)
        assert compute_event_score(e) == pytest.approx(event_score_single_factor(e))


# ============ 7. should_enter ============


class TestShouldEnter:
    def test_emergency_blocks(self):
        assert should_enter(_ev(), 0, emergency=True) is False

    def test_noise_no_action(self):
        e = _ev(sentiment_score=0.1)  # score=1.2*0.1=0.12 < 0.2
        assert should_enter(e, 0) is False

    def test_positive_flat_enters(self):
        assert should_enter(_ev(), 0) is True

    def test_positive_holding_no_add(self):
        assert should_enter(_ev(), 100) is False

    def test_negative_holding_exit(self):
        e = _ev(surprise_direction=-1.0)
        assert should_enter(e, 100) == "EXIT"

    def test_negative_flat_no_action(self):
        e = _ev(surprise_direction=-1.0)
        assert should_enter(e, 0) is False


class TestShouldEnterWithConfirmation:
    def test_extreme_reaction_wait_confirm(self):
        e = _ev(day0_reaction=0.05)
        assert should_enter_with_confirmation(e, 0) == ("WAIT_CONFIRM", 2)

    def test_extreme_reaction_override_param(self):
        e = _ev(day0_reaction=0.01)
        assert should_enter_with_confirmation(e, 0, day0_reaction=-0.04) == ("WAIT_CONFIRM", 2)

    def test_clear_signal_enters(self):
        assert should_enter_with_confirmation(_ev(day0_reaction=0.01), 0) is True

    def test_fuzzy_with_volume_confirmation_enters(self):
        e = _ev(sentiment_score=0.1, day0_reaction=0.02)  # score<0.2 模糊 + 温和正反应
        assert should_enter_with_confirmation(e, 0, volume_confirmed=True) is True

    def test_fuzzy_without_volume_waits(self):
        e = _ev(sentiment_score=0.1, day0_reaction=0.02)
        assert should_enter_with_confirmation(e, 0, volume_confirmed=False) is False

    def test_fuzzy_negative_reaction_no_enter(self):
        e = _ev(sentiment_score=0.1, day0_reaction=-0.02)
        assert should_enter_with_confirmation(e, 0, volume_confirmed=True) is False

    def test_emergency_blocks(self):
        assert should_enter_with_confirmation(_ev(), 0, emergency=True) is False


# ============ 8. should_exit ============


class TestShouldExit:
    def test_decay_timeout(self):
        e = _ev(class_="surprise")  # 窗口 5
        assert should_exit(e, 100, holding_days=6) == "DECAY_TIMEOUT"
        assert should_exit(e, 100, holding_days=5) is False

    def test_unknown_class_default_window(self):
        e = _ev(class_="weird")
        assert should_exit(e, 100, holding_days=11) == "DECAY_TIMEOUT"

    def test_extreme_reaction_requires_t1(self):
        e = _ev(day0_reaction=0.05)
        # T+1：买入当日 holding_days=0 不可卖
        assert should_exit(e, 100, holding_days=0) is False
        assert should_exit(e, 100, holding_days=1) == "EXTREME_REACTION"

    def test_contradiction(self):
        assert should_exit(_ev(), 100, holding_days=2, contradictory=True) == "CONTRADICTION"

    def test_decay_precedence_over_extreme(self):
        e = _ev(class_="surprise", day0_reaction=0.05)
        assert should_exit(e, 100, holding_days=99) == "DECAY_TIMEOUT"

    def test_no_exit(self):
        assert should_exit(_ev(), 100, holding_days=2) is False

    def test_decay_window_table_complete(self):
        assert DECAY_EXIT_WINDOW == {
            "earnings": 10,
            "ma": 15,
            "policy": 20,
            "surprise": 5,
            "ipo": 15,
            "geopolitical": 25,
        }


# ============ 9. trading_days_ago ============


class TestTradingDaysAgo:
    def test_n_zero_returns_same_date(self):
        assert trading_days_ago(0, from_date=date(2026, 8, 17)) == date(2026, 8, 17)

    def test_skips_weekend(self):
        # 2026-08-17 周一 → 1 个交易日前 = 08-14 周五
        assert trading_days_ago(1, from_date=date(2026, 8, 17)) == date(2026, 8, 14)

    def test_three_days_back(self):
        # 08-14(1) → 08-13(2) → 08-12(3)
        assert trading_days_ago(3, from_date=date(2026, 8, 17)) == date(2026, 8, 12)

    def test_negative_raises(self):
        with pytest.raises(EventScoreError):
            trading_days_ago(-1)


# ============ 10. 辅助函数 ============


class TestHasContradictoryEvent:
    def _store(self) -> ListEventStore:
        store = ListEventStore()
        store.add(StoredEvent("600000.SH", date(2026, 8, 14), surprise_direction=-1.0))
        store.add(StoredEvent("600000.SH", date(2026, 8, 10), surprise_direction=1.0))
        store.add(StoredEvent("000001.SZ", date(2026, 8, 14), surprise_direction=-1.0))
        return store

    def test_detects_opposite_direction(self):
        store = self._store()
        assert has_contradictory_event("600000.SH", 1.0, event_store=store, today=date(2026, 8, 17)) is True

    def test_same_direction_not_contradictory(self):
        store = ListEventStore()
        store.add(StoredEvent("600000.SH", date(2026, 8, 14), surprise_direction=1.0))
        assert has_contradictory_event("600000.SH", 1.0, event_store=store, today=date(2026, 8, 17)) is False

    def test_neutral_event_ignored(self):
        store = ListEventStore()
        store.add(StoredEvent("600000.SH", date(2026, 8, 14), surprise_direction=0.0))
        assert has_contradictory_event("600000.SH", 1.0, event_store=store, today=date(2026, 8, 17)) is False

    def test_other_symbol_isolated(self):
        store = self._store()
        # 000001.SZ 有反向事件但查询标的不同
        assert has_contradictory_event("300750.SZ", 1.0, event_store=store, today=date(2026, 8, 17)) is False

    def test_lookback_window_excludes_old_events(self):
        store = ListEventStore()
        store.add(StoredEvent("600000.SH", date(2026, 8, 3), surprise_direction=-1.0))
        # 2026-08-03 距 08-17 超过 5 个交易日 → 不在窗口内
        assert has_contradictory_event("600000.SH", 1.0, event_store=store, today=date(2026, 8, 17)) is False


class TestHasVolumeConfirmation:
    def test_baseline_nonpositive_conservative_false(self):
        assert has_volume_confirmation([200.0], 0.0) is False
        assert has_volume_confirmation([200.0], -1.0) is False

    def test_empty_recent_false(self):
        assert has_volume_confirmation([], 100.0) is False

    def test_volume_surge_confirmed(self):
        assert has_volume_confirmation([160.0, 200.0], 100.0) is True  # 均 180 ≥ 150

    def test_volume_below_threshold(self):
        assert has_volume_confirmation([140.0], 100.0) is False

    def test_custom_min_ratio(self):
        assert has_volume_confirmation([120.0], 100.0, min_ratio=1.1) is True


# ============ 11. check_selling_pressure_absorbed ============


def _minute_df(closes: list[float], volumes: list[float]) -> pd.DataFrame:
    closes_arr = np.array(closes)
    return pd.DataFrame(
        {
            "high": closes_arr + 0.05,
            "low": closes_arr - 0.05,
            "close": closes_arr,
            "volume": volumes,
        }
    )


class TestCheckSellingPressureAbsorbed:
    def test_seller_active_bars_cvd_negative_not_absorbed(self):
        # mid = close+0.04 > close → 卖方主动 → CVD 全负 → 不吸收
        n = 30
        closes = [10.0] * (n - 1) + [10.1]
        df = _minute_df(closes, [100.0] * 10 + [300.0] * 20)
        df["high"] = df["close"] + 0.10
        df["low"] = df["close"] - 0.02
        out = check_selling_pressure_absorbed(df)
        assert out["cvd_final"] < 0
        assert out["absorbed"] is False

    def test_absorbed_true_terminal_volume_spike(self):
        # memo 字面公式 volume.mean()/rolling(5).mean().mean()：末端突发放量时 >1.5
        # （双水平持续放量该比值退化≈1——G23 校准遗留，登记回执）
        n = 30
        closes = [10.0] * n
        volumes = [100.0] * (n - 1) + [10000.0]  # 末端巨量
        df = _minute_df(closes, volumes)
        df["high"] = df["close"] + 0.02
        df["low"] = df["close"] - 0.10  # mid=close-0.04 < close → 买方主动 → CVD 正
        out = check_selling_pressure_absorbed(df)
        assert out["cvd_final"] > 0
        assert out["volume_ratio"] > 1.5
        assert out["price_stabilized"] is True
        assert out["absorbed"] is True

    def test_price_not_stabilized(self):
        n = 30
        closes = [10.0] + [9.0] * (n - 1)  # 首日 10 → 其后 9（跌 10%）
        df = _minute_df(closes, [300.0] * n)
        df["high"] = df["close"] + 0.02
        df["low"] = df["close"] - 0.10
        out = check_selling_pressure_absorbed(df)
        assert out["price_stabilized"] is False
        assert out["absorbed"] is False

    def test_short_series_volume_ratio_nan_not_absorbed(self):
        df = _minute_df([10.0, 10.0, 10.0], [300.0, 300.0, 300.0])
        df["high"] = df["close"] + 0.02
        df["low"] = df["close"] - 0.10
        out = check_selling_pressure_absorbed(df)
        assert out["absorbed"] is False
        assert np.isnan(out["volume_ratio"])

    def test_empty_df_not_absorbed(self):
        out = check_selling_pressure_absorbed(pd.DataFrame())
        assert out["absorbed"] is False

    def test_missing_column_raises(self):
        df = pd.DataFrame({"close": [1.0], "volume": [1.0]})
        with pytest.raises(EventScoreError):
            check_selling_pressure_absorbed(df)


# ============ 12. 量能薄封装 ============


class _FakeVolumeProvider:
    def volume_series(self, symbol: str, days: int) -> list[float]:
        return [float(days)] * days

    def volume_ma(self, symbol: str, window: int) -> float:
        return float(window)


class TestVolumeThinWrappers:
    def test_volume_series_delegates(self):
        assert volume_series("600000.SH", 3, provider=_FakeVolumeProvider()) == [3.0, 3.0, 3.0]

    def test_volume_ma_delegates(self):
        assert volume_ma("600000.SH", 20, provider=_FakeVolumeProvider()) == 20.0

    def test_invalid_symbol_rejected_before_ch(self):
        provider = ClickHouseKlineVolumeProvider.__new__(ClickHouseKlineVolumeProvider)
        with pytest.raises(EventScoreError):
            provider._fetch("600000.SH'; DROP TABLE--", 5)

    def test_ch_provider_days_nonpositive(self):
        provider = ClickHouseKlineVolumeProvider.__new__(ClickHouseKlineVolumeProvider)
        assert provider.volume_series("600000.SH", 0) == []
        assert provider.volume_ma("600000.SH", 0) == 0.0
