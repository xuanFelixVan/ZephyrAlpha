# [BLUEPRINT] MOD-SIG-113 | docs/03_modules/_domain_signal/banker_pattern_simulator/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-113 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_banker_pattern_simulator
# [TESTS] src/zephyr/signal_ashare/banker_pattern_simulator.py
"""MOD-SIG-113 单元测试：banker_pattern_simulator 庄家行为模式识别与模拟。

蓝图验收（B1-00168/CAND-TESTB-030，C2 C-035）：
六阶段规则识别 + 阶段转移判定 + 反庄沙盒模拟 + 风险警示 + advisory 硬标注。
内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.banker_pattern_simulator",
    reason="banker_pattern_simulator not importable",
)

from zephyr.signal_ashare.banker_pattern_simulator import (  # noqa: E402
    BankerPatternError,
    BankerPatternSimulator,
    BankerPhase,
    PriceVolumeRule,
)


def _sim(**kwargs) -> BankerPatternSimulator:
    return BankerPatternSimulator(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 构造期 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_invalid_phase_in_rule_raises(self) -> None:
        with pytest.raises(BankerPatternError):
            PriceVolumeRule(
                phase="INVALID",  # type: ignore[arg-type]
                min_price_change_pct=0,
                max_price_change_pct=1,
                min_volume_ratio=0,
                max_volume_ratio=1,
            )

    def test_price_range_inverted_raises(self) -> None:
        with pytest.raises(BankerPatternError):
            PriceVolumeRule(
                phase=BankerPhase.PULL,
                min_price_change_pct=5,
                max_price_change_pct=1,
                min_volume_ratio=0,
                max_volume_ratio=1,
            )

    def test_volume_range_inverted_raises(self) -> None:
        with pytest.raises(BankerPatternError):
            PriceVolumeRule(
                phase=BankerPhase.PULL,
                min_price_change_pct=0,
                max_price_change_pct=1,
                min_volume_ratio=2,
                max_volume_ratio=1,
            )

    def test_weight_out_of_range_raises(self) -> None:
        with pytest.raises(BankerPatternError):
            PriceVolumeRule(
                phase=BankerPhase.PULL,
                min_price_change_pct=0,
                max_price_change_pct=1,
                min_volume_ratio=0,
                max_volume_ratio=1,
                weight=1.5,
            )

    def test_rules_contain_invalid_type_raises(self) -> None:
        with pytest.raises(BankerPatternError):
            _sim(
                rules=[
                    PriceVolumeRule(
                        phase=BankerPhase.PULL,
                        min_price_change_pct=0,
                        max_price_change_pct=1,
                        min_volume_ratio=0,
                        max_volume_ratio=1,
                    ),
                    "not-a-rule",
                ]
            )  # type: ignore[list-item]


# ──────────────────────────────────────────────────────────────────────────────
# 规则匹配
# ──────────────────────────────────────────────────────────────────────────────


class TestMatch:
    def test_empty_sequence_raises(self) -> None:
        sim = _sim()
        with pytest.raises(BankerPatternError):
            sim.match_phase([], [])
        with pytest.raises(BankerPatternError):
            sim.match_phase([1.0], [])

    def test_mismatched_length_raises(self) -> None:
        sim = _sim()
        with pytest.raises(BankerPatternError):
            sim.match_phase([1.0, 2.0], [100])

    def test_single_bar_raises(self) -> None:
        sim = _sim()
        with pytest.raises(BankerPatternError):
            sim.match_phase([1.0], [100])

    def test_accumulation_match(self) -> None:
        sim = _sim()
        # 价格横盘5日，量比1.0
        result = sim.match_phase([10.0, 10.1, 10.0, 10.1, 10.05], [100, 105, 98, 102, 100])
        assert result.phase == BankerPhase.ACCUMULATION
        assert result.advisory is True
        assert result.confidence > 0

    def test_pull_match(self) -> None:
        sim = _sim()
        # 价格拉升3日，量比2.0
        result = sim.match_phase([10.0, 10.5, 11.0, 11.5], [100, 150, 200, 250])
        assert result.phase == BankerPhase.PULL
        assert result.confidence > 0

    def test_no_match_fallback(self) -> None:
        sim = _sim()
        # 价格暴涨100%，超出所有规则
        result = sim.match_phase([10.0, 20.0], [100, 100])
        assert result.confidence == 0.0
        assert result.phase == BankerPhase.ACCUMULATION
        assert result.notes

    def test_custom_rules(self) -> None:
        rule = PriceVolumeRule(
            phase=BankerPhase.WASH,
            min_price_change_pct=-10.0,
            max_price_change_pct=-5.0,
            min_volume_ratio=0.1,
            max_volume_ratio=0.5,
            min_duration=2,
            max_duration=5,
            weight=0.9,
        )
        sim = _sim(rules=[rule])
        # 价变 -7%∈[-10,-5]；均量50，末量20→量比0.4∈[0.1,0.5]；duration=3∈[2,5]
        result = sim.match_phase([10.0, 9.5, 9.3], [100, 30, 20])
        assert result.phase == BankerPhase.WASH
        assert result.confidence > 0


# ──────────────────────────────────────────────────────────────────────────────
# 阶段转移
# ──────────────────────────────────────────────────────────────────────────────


class TestTransition:
    def test_valid_transitions(self) -> None:
        sim = _sim()
        assert sim.transition_allowed(BankerPhase.ACCUMULATION, BankerPhase.WASH) is True
        assert sim.transition_allowed(BankerPhase.PULL, BankerPhase.DISTRIBUTION) is True

    def test_invalid_transitions(self) -> None:
        sim = _sim()
        assert sim.transition_allowed(BankerPhase.ACCUMULATION, BankerPhase.DISTRIBUTION) is False
        assert sim.transition_allowed(BankerPhase.SUPPORT, BankerPhase.MATCH_TRADE) is False

    def test_next_phases_sorted(self) -> None:
        sim = _sim()
        nexts = sim.next_phases(BankerPhase.ACCUMULATION)
        assert nexts == tuple(sorted(nexts, key=lambda p: p.value))
        assert BankerPhase.WASH in nexts


# ──────────────────────────────────────────────────────────────────────────────
# 沙盒模拟
# ──────────────────────────────────────────────────────────────────────────────


class TestSandbox:
    def test_no_runner_skips(self) -> None:
        sim = _sim(backtest_runner=None)
        result = sim.sandbox_simulate(BankerPhase.PULL, [1.0, 2.0], [100, 200])
        assert result.simulated is False
        assert "未注入" in result.notes[0]

    def test_runner_ok(self) -> None:
        sim = _sim(backtest_runner=lambda p, pr, vol: {"pnl_estimate": 0.05})
        result = sim.sandbox_simulate(BankerPhase.PULL, [1.0, 2.0], [100, 200])
        assert result.simulated is True
        assert result.pnl_estimate == pytest.approx(0.05)

    def test_runner_exception_downgrades(self) -> None:
        def _boom(p, pr, vol):
            raise RuntimeError("backtest crash")

        sim = _sim(backtest_runner=_boom)
        result = sim.sandbox_simulate(BankerPhase.PULL, [1.0, 2.0], [100, 200])
        assert result.simulated is False
        assert "异常" in result.notes[0]


# ──────────────────────────────────────────────────────────────────────────────
# 综合识别
# ──────────────────────────────────────────────────────────────────────────────


class TestAnalyze:
    def test_analyze_structure(self) -> None:
        sim = _sim()
        out = sim.analyze([10.0, 10.1, 10.0, 10.1, 10.05], [100, 105, 98, 102, 100])
        assert out["phase"] == "建仓"
        assert out["advisory"] is True
        assert isinstance(out["risk_warnings"], tuple)
        assert "sandbox" in out


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_output(self) -> None:
        sim = _sim()
        p = [10.0, 10.5, 11.0, 11.5]
        v = [100, 150, 200, 250]
        r1 = sim.match_phase(p, v)
        r2 = sim.match_phase(p, v)
        assert r1 == r2
