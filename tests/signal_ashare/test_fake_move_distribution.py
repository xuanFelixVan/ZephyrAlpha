# [BLUEPRINT] MOD-SIG-124 | docs/03_modules/_domain_signal/fake_move_distribution/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-124 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_fake_move_distribution
# [TESTS] src/zephyr/signal_ashare/fake_move_distribution.py
"""MOD-SIG-124 单元测试：fake_move_distribution 主力假动作与筹码派发识别。

蓝图验收（B10-01425/CAND-TESTB-044，A1 模块27，canonical承接TESTB-056归并）：
假动作6模式规则库（词表闭合，表面行为+底层矛盾信号）+ 7维信号打分
（主动买入占比/大单净流入/量能持续/板块跟涨率/拉升时段/底部筹码/龙虎榜，
全注入数据）+ >85%暂停追涨输出FakeMoveWarning。
时钟/告警全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime
import math
from dataclasses import replace

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.fake_move_distribution",
    reason="fake_move_distribution not importable",
)

from zephyr.signal_ashare.fake_move_distribution import (  # noqa: E402
    FAKE_MOVE_RULES,
    FakeMoveConfig,
    FakeMoveDetector,
    FakeMoveError,
    FakeMovePattern,
    FakeMoveWarning,
    PumpWindow,
    SignalDim,
    SignalMetrics,
)

_T0 = datetime.datetime(2026, 8, 26, 15, 30, 0)  # 盘后时刻

#: 真拉升（7 维均健康）
_CLEAN = SignalMetrics(
    active_buy_ratio=0.9,
    big_order_net_inflow=1e8,
    volume_persistence=0.95,
    sector_follow_rate=0.9,
    pump_window=PumpWindow.MORNING,
    bottom_chip_ratio=0.95,
    lhb_net_buy=5e7,
)

#: 假动作（7 维全矛盾）
_FAKE = SignalMetrics(
    active_buy_ratio=0.0,
    big_order_net_inflow=-1e8,
    volume_persistence=0.0,
    sector_follow_rate=0.0,
    pump_window=PumpWindow.TAIL,
    bottom_chip_ratio=0.0,
    lhb_net_buy=-5e7,
)


def _detector(
    warnings: list | None = None,
    config: FakeMoveConfig | None = None,
) -> FakeMoveDetector:
    return FakeMoveDetector(
        clock=lambda: _T0,
        warning_sink=(lambda w: warnings.append(w)) if warnings is not None else None,
        config=config,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 6 模式规则库（词表闭合）
# ──────────────────────────────────────────────────────────────────────────────


class TestRuleLibrary:
    def test_six_patterns_closed_vocab(self) -> None:
        assert len(FAKE_MOVE_RULES) == 6
        assert set(FAKE_MOVE_RULES) == set(FakeMovePattern)

    def test_rule_surface_and_contradiction_complete(self) -> None:
        for rule in FAKE_MOVE_RULES.values():
            assert rule.surface_behavior  # 表面行为非空
            assert rule.contradiction_signals  # 底层矛盾信号非空
            assert rule.contradiction_dims
            assert set(rule.contradiction_dims) <= set(SignalDim)  # 维度词表闭合

    def test_rule_dim_sets_distinct(self) -> None:
        dim_sets = [frozenset(r.contradiction_dims) for r in FAKE_MOVE_RULES.values()]
        assert len(set(dim_sets)) == 6  # 六模式矛盾维度组合两两不同


# ──────────────────────────────────────────────────────────────────────────────
# 7 维信号打分（注入数据）
# ──────────────────────────────────────────────────────────────────────────────


class TestDimScores:
    def _score(self, metrics: SignalMetrics, dim: SignalDim) -> float:
        return _detector().assess("600000", metrics).dim_scores[dim]

    def test_active_buy_score(self) -> None:
        assert self._score(replace(_CLEAN, active_buy_ratio=0.5), SignalDim.ACTIVE_BUY) == 0.0
        assert self._score(replace(_CLEAN, active_buy_ratio=0.0), SignalDim.ACTIVE_BUY) == 1.0
        assert self._score(
            replace(_CLEAN, active_buy_ratio=0.25), SignalDim.ACTIVE_BUY
        ) == pytest.approx(0.5)

    def test_big_order_inflow_score(self) -> None:
        assert self._score(_CLEAN, SignalDim.BIG_ORDER_INFLOW) == 0.0
        assert self._score(
            replace(_CLEAN, big_order_net_inflow=-5e7), SignalDim.BIG_ORDER_INFLOW
        ) == pytest.approx(0.5)
        assert (
            self._score(replace(_CLEAN, big_order_net_inflow=-3e8), SignalDim.BIG_ORDER_INFLOW)
            == 1.0  # 超额截断
        )

    def test_volume_persistence_inverted(self) -> None:
        assert self._score(
            replace(_CLEAN, volume_persistence=0.8), SignalDim.VOLUME_PERSISTENCE
        ) == pytest.approx(0.2)

    def test_sector_follow_inverted(self) -> None:
        assert self._score(
            replace(_CLEAN, sector_follow_rate=0.3), SignalDim.SECTOR_FOLLOW
        ) == pytest.approx(0.7)

    def test_pump_window_static_table(self) -> None:
        tail = self._score(replace(_CLEAN, pump_window=PumpWindow.TAIL), SignalDim.PUMP_WINDOW)
        mid = self._score(replace(_CLEAN, pump_window=PumpWindow.MIDDAY), SignalDim.PUMP_WINDOW)
        morning = self._score(_CLEAN, SignalDim.PUMP_WINDOW)
        assert tail == 1.0 and mid == 0.4 and morning == 0.2
        assert tail > mid > morning  # 尾盘偷袭最可疑

    def test_bottom_chip_inverted(self) -> None:
        assert self._score(
            replace(_CLEAN, bottom_chip_ratio=0.9), SignalDim.BOTTOM_CHIP
        ) == pytest.approx(0.1)

    def test_lhb_score(self) -> None:
        assert self._score(_CLEAN, SignalDim.LHB) == 0.0
        assert self._score(
            replace(_CLEAN, lhb_net_buy=-2.5e7), SignalDim.LHB
        ) == pytest.approx(0.5)


# ──────────────────────────────────────────────────────────────────────────────
# 概率合成 + 模式命中
# ──────────────────────────────────────────────────────────────────────────────


class TestAssessment:
    def test_clean_metrics_low_probability_no_warning(self) -> None:
        a = _detector().assess("600000", _CLEAN)
        assert a.fake_probability < 0.5
        assert a.warning is None
        assert a.matched_patterns == ()
        assert a.assessed_at == _T0  # 注入时钟

    def test_fake_metrics_all_patterns_matched_in_order(self) -> None:
        a = _detector().assess("600000", _FAKE)
        assert a.matched_patterns == tuple(FakeMovePattern)  # 定义序确定

    def test_exact_one_pattern_matched(self) -> None:
        metrics = SignalMetrics(
            active_buy_ratio=0.0,  # 矛盾
            big_order_net_inflow=-1e8,  # 矛盾
            volume_persistence=0.0,  # 矛盾
            sector_follow_rate=1.0,
            pump_window=PumpWindow.MORNING,
            bottom_chip_ratio=1.0,
            lhb_net_buy=1e7,
        )
        a = _detector().assess("600000", metrics)
        assert a.matched_patterns == (FakeMovePattern.FAKE_PUMP_REAL_DUMP,)

    def test_determinism_same_input_same_output(self) -> None:
        d = _detector()
        assert d.assess("600000", _FAKE) == d.assess("600000", _FAKE)


# ──────────────────────────────────────────────────────────────────────────────
# >85% 暂停追涨告警
# ──────────────────────────────────────────────────────────────────────────────


class TestWarning:
    def test_over_85pct_warning_emitted(self) -> None:
        warnings: list[FakeMoveWarning] = []
        a = _detector(warnings).assess("600000", _FAKE)
        assert a.fake_probability > 0.85
        assert a.warning is not None
        assert a.warning.action == "suspend_chase"  # 暂停追涨
        assert a.warning.fake_percent > 85.0
        assert a.warning.raised_at == _T0
        assert warnings == [a.warning]  # 注入 sink 收到

    def test_boundary_exact_threshold_no_warning(self) -> None:
        # 单维等权配置：prob == 主动买入嫌疑分；warn_threshold=0.5 精确边界
        cfg = FakeMoveConfig(weights=(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), warn_threshold=0.5)
        a = _detector(config=cfg).assess("600000", replace(_CLEAN, active_buy_ratio=0.25))
        assert a.fake_probability == pytest.approx(0.5)
        assert a.warning is None  # >阈值严格大于，等于不告警

    def test_just_above_threshold_warns(self) -> None:
        cfg = FakeMoveConfig(weights=(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), warn_threshold=0.5)
        a = _detector(config=cfg).assess("600000", replace(_CLEAN, active_buy_ratio=0.24))
        assert a.fake_probability == pytest.approx(0.52)
        assert a.warning is not None

    def test_sink_failure_not_blocking(self) -> None:
        def _boom(w: FakeMoveWarning) -> None:
            raise RuntimeError("alert route down")

        detector = FakeMoveDetector(clock=lambda: _T0, warning_sink=_boom)
        a = detector.assess("600000", _FAKE)  # 告警异常不阻断
        assert a.warning is not None


# ──────────────────────────────────────────────────────────────────────────────
# Fail-Closed（输入/配置非法）
# ──────────────────────────────────────────────────────────────────────────────


class TestFailClosed:
    def test_invalid_ratio_raises(self) -> None:
        for bad in (1.5, -0.1, math.nan, "high"):
            with pytest.raises(FakeMoveError):
                _detector().assess("600000", replace(_CLEAN, active_buy_ratio=bad))

    def test_invalid_money_raises(self) -> None:
        with pytest.raises(FakeMoveError):
            _detector().assess("600000", replace(_CLEAN, big_order_net_inflow=math.nan))
        with pytest.raises(FakeMoveError):
            _detector().assess("600000", replace(_CLEAN, lhb_net_buy=math.inf))

    def test_unknown_pump_window_raises(self) -> None:
        with pytest.raises(FakeMoveError):
            _detector().assess("600000", replace(_CLEAN, pump_window="midnight"))

    def test_empty_symbol_raises(self) -> None:
        with pytest.raises(FakeMoveError):
            _detector().assess("", _CLEAN)
        with pytest.raises(FakeMoveError):
            _detector().assess("   ", _CLEAN)

    def test_invalid_weights_raises(self) -> None:
        with pytest.raises(FakeMoveError):
            FakeMoveConfig(weights=(0.5, 0.5))  # 非7项
        with pytest.raises(FakeMoveError):
            FakeMoveConfig(weights=(0.2,) * 7)  # Σ≠1
        with pytest.raises(FakeMoveError):
            FakeMoveConfig(weights=(-0.1, 0.2, 0.2, 0.2, 0.2, 0.2, 0.1))  # 负权重

    def test_invalid_threshold_raises(self) -> None:
        with pytest.raises(FakeMoveError):
            FakeMoveConfig(warn_threshold=1.5)
        with pytest.raises(FakeMoveError):
            FakeMoveConfig(warn_threshold=0.0)
        with pytest.raises(FakeMoveError):
            FakeMoveConfig(active_buy_mid=1.5)
        with pytest.raises(FakeMoveError):
            FakeMoveConfig(big_order_scale=0.0)
        with pytest.raises(FakeMoveError):
            FakeMoveConfig(pattern_match_threshold=0.0)
