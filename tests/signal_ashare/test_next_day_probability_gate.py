# [A_test] module_id: MOD-SIG-104 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-104 | docs/03_modules/_domain_signal/next_day_probability_gate/blueprint.md
# [MODULE] tests.signal_ashare.test_next_day_probability_gate
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""次日上涨概率统一门槛模块（MOD-SIG-104，B10-01415）施工验证测试。

覆盖：
- 动作分档封闭集：new_position≥0.65/add_position≥0.60/bottom_fishing≥0.70/
  t_plus≥0.55/t_minus=P(跌)≥0.55（方向概率口径）；
- 动态偏移：牛−5%/熊+5%/放量−5%/缩量+10%/利好落地前+10%/黑天鹅+15%/
  变盘日+5%/情绪高位+5%，叠加求和；调整后门槛钳制 [0.50,0.95]；
- 拦截原因输出（基准+偏移+缺口归因）；拦截统计回写（block 计数/拦截率/
  平均缺口，sink 鸭子类型）；
- fail-closed：未知动作/p_up 越界或非有限/冲突上下文（牛熊同真）/非法配置
  → ValueError；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.signal_ashare.next_day_probability_gate import (
    GATE_ACTIONS,
    GateContext,
    NextDayProbabilityGate,
    ProbabilityGateConfig,
)


def _gate(**kwargs) -> NextDayProbabilityGate:
    return NextDayProbabilityGate(ProbabilityGateConfig(**kwargs))


class TestConfigValidation:
    def test_threshold_out_of_range(self):
        with pytest.raises(ValueError):
            ProbabilityGateConfig(new_position_threshold=0.0)
        with pytest.raises(ValueError):
            ProbabilityGateConfig(bottom_fishing_threshold=1.0)

    def test_floor_cap_inverted(self):
        with pytest.raises(ValueError):
            ProbabilityGateConfig(threshold_floor=0.9, threshold_cap=0.5)

    def test_offset_out_of_range(self):
        with pytest.raises(ValueError):
            ProbabilityGateConfig(black_swan_offset=1.5)


class TestContextValidation:
    def test_bull_and_bear_conflict(self):
        with pytest.raises(ValueError):
            GateContext(bull=True, bear=True)

    def test_surge_and_shrink_conflict(self):
        with pytest.raises(ValueError):
            GateContext(volume_surge=True, volume_shrink=True)


class TestEvaluateFailClosed:
    def test_unknown_action(self):
        with pytest.raises(ValueError):
            _gate().evaluate("mystery_action", 0.7)

    def test_p_up_out_of_range(self):
        with pytest.raises(ValueError):
            _gate().evaluate("new_position", 1.01)
        with pytest.raises(ValueError):
            _gate().evaluate("new_position", -0.01)

    def test_p_up_non_finite(self):
        with pytest.raises(ValueError):
            _gate().evaluate("new_position", float("nan"))


class TestActionThresholds:
    def test_action_set_closed(self):
        assert set(GATE_ACTIONS) == {
            "new_position",
            "add_position",
            "bottom_fishing",
            "t_plus",
            "t_minus",
        }

    def test_new_position_threshold(self):
        g = _gate()
        assert g.evaluate("new_position", 0.65).passed is True
        assert g.evaluate("new_position", 0.649).passed is False

    def test_add_position_threshold(self):
        g = _gate()
        assert g.evaluate("add_position", 0.60).passed is True
        assert g.evaluate("add_position", 0.59).passed is False

    def test_bottom_fishing_threshold(self):
        g = _gate()
        assert g.evaluate("bottom_fishing", 0.70).passed is True
        assert g.evaluate("bottom_fishing", 0.69).passed is False

    def test_t_plus_threshold(self):
        g = _gate()
        assert g.evaluate("t_plus", 0.55).passed is True
        assert g.evaluate("t_plus", 0.54).passed is False

    def test_t_minus_direction_probability(self):
        """反T 看 P(跌)=1−p_up：p_up=0.40 → P(跌)=0.60≥0.55 放行；0.50 拦截。"""
        g = _gate()
        d1 = g.evaluate("t_minus", 0.40)
        assert d1.passed is True
        assert d1.direction_probability == pytest.approx(0.60)
        d2 = g.evaluate("t_minus", 0.50)
        assert d2.passed is False


class TestDynamicOffsets:
    def test_bull_offset_eases(self):
        """牛市 −5%：新开仓 0.65→0.60，p=0.62 放行。"""
        g = _gate()
        d = g.evaluate("new_position", 0.62, GateContext(bull=True))
        assert d.passed is True
        assert d.adjusted_threshold == pytest.approx(0.60)
        assert d.offset_total == pytest.approx(-0.05)

    def test_bear_offset_tightens(self):
        """熊市 +5%：0.65→0.70，p=0.66 拦截。"""
        g = _gate()
        d = g.evaluate("new_position", 0.66, GateContext(bear=True))
        assert d.passed is False
        assert d.adjusted_threshold == pytest.approx(0.70)

    def test_offsets_stacking(self):
        """熊+5% 缩量+10% → 0.65→0.80。"""
        g = _gate()
        d = g.evaluate("new_position", 0.78, GateContext(bear=True, volume_shrink=True))
        assert d.passed is False
        assert d.adjusted_threshold == pytest.approx(0.80)
        assert set(d.applied_offsets) == {"bear", "volume_shrink"}

    def test_cap_clamp(self):
        """全利空叠加超过 cap=0.95 钳制。"""
        g = _gate()
        ctx = GateContext(
            bear=True,
            volume_shrink=True,
            pre_news=True,
            black_swan=True,
            turn_day=True,
            sentiment_high=True,
        )
        d = g.evaluate("new_position", 0.99, ctx)
        assert d.adjusted_threshold == pytest.approx(0.95)
        assert d.passed is True

    def test_floor_clamp(self):
        """正T 0.55 + 牛−5% + 放量−5% = 0.45 → 钳制 floor=0.50。"""
        g = _gate()
        d = g.evaluate("t_plus", 0.48, GateContext(bull=True, volume_surge=True))
        assert d.adjusted_threshold == pytest.approx(0.50)
        assert d.passed is False


class TestInterceptionReasonAndStats:
    def test_blocked_reason_attribution(self):
        g = _gate()
        d = g.evaluate("new_position", 0.60, GateContext(bear=True))
        assert d.passed is False
        assert "拦截" in d.reason
        assert "0.65" in d.reason  # 基准门槛
        assert "bear" in d.reason

    def test_passed_reason(self):
        g = _gate()
        d = g.evaluate("new_position", 0.80)
        assert "通过" in d.reason

    def test_stats_accumulation(self):
        g = _gate()
        g.evaluate("new_position", 0.80)  # pass
        g.evaluate("new_position", 0.60)  # block（缺口 0.05）
        g.evaluate("new_position", 0.50)  # block（缺口 0.15）
        snap = g.stats_snapshot()
        row = snap.actions["new_position"]
        assert row.total == 3
        assert row.blocked == 2
        assert row.block_rate == pytest.approx(2.0 / 3.0)
        assert row.avg_shortfall == pytest.approx(0.10)

    def test_block_sink_called_only_on_block(self):
        calls: list[str] = []
        g = _gate()
        g.set_block_sink(lambda d: calls.append(d.action))
        g.evaluate("add_position", 0.90)  # pass → 不回写
        g.evaluate("add_position", 0.50)  # block → 回写
        assert calls == ["add_position"]


class TestContract:
    def test_frozen_and_json_serializable(self):
        g = _gate()
        d = g.evaluate("new_position", 0.80)
        assert dataclasses.is_dataclass(d)
        with pytest.raises(dataclasses.FrozenInstanceError):
            d.passed = False  # type: ignore[misc]
        json.dumps(d.to_dict(), ensure_ascii=False)
        json.dumps(g.stats_snapshot().to_dict(), ensure_ascii=False)
