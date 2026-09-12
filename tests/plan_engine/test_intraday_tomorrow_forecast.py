# [BLUEPRINT] MOD-PLAN-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-PLAN-025 intraday_tomorrow_forecast 单元测试（C13，night-gw-2300）。

红蓝对抗手法覆盖（长城指令 §4）：
- 红-边界：空/缺态/负值/不归一/NaN 先验与三档、Brier 非法值
- 红-前视：fuse 纯函数确定性（同输入必同输出，无墙钟/无隐藏状态）
- 红-竞态：frozen dataclass 不可变（无共享可变状态）
- 红-契约：NextDayState 枚举绑定、SimilarDayScenario 鸭型转换
- 红-故障：校准缺数据→权重中性、相似日停用/退化→安全排除
"""

from __future__ import annotations

import json
import time

import pytest

from zephyr.plan_engine.intraday_tomorrow_forecast import (
    BASE_W_PRIOR,
    BASE_W_SIMILAR,
    DOWNGRADE_TIER_THRESHOLD,
    INTRADAY_POINTS,
    PESSIMISM_ORDER,
    RELIABILITY_FLOOR,
    SimilarDayScenario,
    SourceCalibration,
    TILT_MAX_TIERS,
    TomorrowForecastInputError,
    expected_pessimism_tier,
    fuse,
    reliability_from_brier,
    scenario_tilt,
    tilt_prior_along_pessimism,
)
from zephyr.signal_ashare.ml_forecast.next_day_8state_forecast import NextDayState

# ── 构造辅助 ────────────────────────────────────────────────────────────────


def _prior_by_tier(tier_weights: dict[int, float]) -> dict[NextDayState, float]:
    """档位权重 → 8 态分布（档位↔状态一一对应）。"""
    out = {}
    for tier, state in enumerate(PESSIMISM_ORDER):
        out[state] = float(tier_weights.get(tier, 0.0))
    total = sum(out.values())
    return {s: p / total for s, p in out.items()}


def _scenario(strong: float, flat: float, weak: float, **kw) -> SimilarDayScenario:
    return SimilarDayScenario(
        enabled=kw.get("enabled", True),
        fallback_used=kw.get("fallback_used", False),
        prob_strong=strong,
        prob_flat=flat,
        prob_weak=weak,
    )


# ── 红-契约：枚举绑定 ───────────────────────────────────────────────────────


class TestContractBinding:
    def test_pessimism_order_covers_all_8_states_exactly(self) -> None:
        assert len(PESSIMISM_ORDER) == 8
        assert set(PESSIMISM_ORDER) == set(NextDayState)

    def test_order_endpoints(self) -> None:
        assert PESSIMISM_ORDER[0] == NextDayState.GAP_UP_UP
        assert PESSIMISM_ORDER[-1] == NextDayState.GAP_DOWN_DOWN

    def test_intraday_points_match_node_spec(self) -> None:
        assert INTRADAY_POINTS == ("10:00", "11:00", "13:30", "14:30")

    def test_scenario_from_inference_duck_typing(self) -> None:
        class _Stub:
            enabled = True
            fallback_used = False
            prob_strong = 0.2
            prob_flat = 0.3
            prob_weak = 0.5

        s = SimilarDayScenario.from_inference(_Stub())
        assert (s.prob_strong, s.prob_flat, s.prob_weak) == (0.2, 0.3, 0.5)


# ── 红-边界：输入契约 fail-closed ───────────────────────────────────────────


class TestInputContract:
    def test_missing_state_rejected(self) -> None:
        prior = _prior_by_tier({i: 1.0 for i in range(8)})
        prior.pop(NextDayState.VIOLENT)
        with pytest.raises(TomorrowForecastInputError, match="缺态"):
            fuse(prior, None)

    def test_empty_prior_rejected(self) -> None:
        with pytest.raises(TomorrowForecastInputError, match="缺态"):
            fuse({}, None)

    def test_negative_prob_rejected(self) -> None:
        prior = _prior_by_tier({0: 1.2, 1: -0.2, **{i: 0.0 for i in range(2, 8)}})
        with pytest.raises(TomorrowForecastInputError, match="为负"):
            fuse(prior, None)

    def test_non_normalized_prior_rejected(self) -> None:
        prior = _prior_by_tier({i: 1.0 for i in range(8)})
        prior = {s: p * 1.1 for s, p in prior.items()}
        with pytest.raises(TomorrowForecastInputError, match="不归一"):
            fuse(prior, None)

    def test_nan_prob_rejected(self) -> None:
        prior = _prior_by_tier({i: 1.0 for i in range(8)})
        prior[NextDayState.FLAT_CLOSE] = float("nan")
        with pytest.raises(TomorrowForecastInputError, match="非有限"):
            fuse(prior, None)

    def test_scenario_unnormalized_rejected(self) -> None:
        prior = _prior_by_tier({i: 1.0 for i in range(8)})
        with pytest.raises(TomorrowForecastInputError, match="不归一"):
            fuse(prior, _scenario(0.5, 0.5, 0.5))

    def test_negative_brier_rejected(self) -> None:
        prior = _prior_by_tier({i: 1.0 for i in range(8)})
        with pytest.raises(TomorrowForecastInputError, match="Brier 非法"):
            fuse(prior, None, calibration_prior=SourceCalibration("m", brier=-0.1))

    def test_unnormalized_scenario_skipped_not_error(self) -> None:
        """停用/退化的三档不参与合成，其概率值不校验（不消费即不问责）。"""
        prior = _prior_by_tier({i: 1.0 for i in range(8)})
        out = fuse(prior, _scenario(9.0, 9.0, 9.0, enabled=False))
        assert out.weights["similar"] == 0.0


# ── 可靠度权重 ──────────────────────────────────────────────────────────────


class TestReliability:
    def test_none_is_neutral(self) -> None:
        assert reliability_from_brier(None) == 1.0

    def test_perfect_brier_is_full_weight(self) -> None:
        assert reliability_from_brier(0.0) == 1.0

    def test_half_random_brier_half_weight(self) -> None:
        assert reliability_from_brier(0.25) == pytest.approx(0.5)

    def test_worse_than_random_floored(self) -> None:
        assert reliability_from_brier(0.9) == RELIABILITY_FLOOR

    def test_nan_brier_rejected(self) -> None:
        with pytest.raises(TomorrowForecastInputError):
            reliability_from_brier(float("nan"))


# ── 相似日倾斜 ──────────────────────────────────────────────────────────────


class TestScenarioTilt:
    def test_none_scenario_no_tilt(self) -> None:
        assert scenario_tilt(None) is None

    def test_disabled_excluded(self) -> None:
        assert scenario_tilt(_scenario(0.0, 0.0, 1.0, enabled=False)) is None

    def test_fallback_excluded(self) -> None:
        assert scenario_tilt(_scenario(0.0, 0.0, 1.0, fallback_used=True)) is None

    def test_all_weak_max_pessimistic_tilt(self) -> None:
        assert scenario_tilt(_scenario(0.0, 0.0, 1.0)) == pytest.approx(TILT_MAX_TIERS)

    def test_all_strong_max_optimistic_tilt(self) -> None:
        assert scenario_tilt(_scenario(1.0, 0.0, 0.0)) == pytest.approx(-TILT_MAX_TIERS)

    def test_balanced_scenario_zero_tilt(self) -> None:
        assert scenario_tilt(_scenario(0.5, 0.0, 0.5)) == pytest.approx(0.0)


class TestTiltPrior:
    def test_zero_tilt_is_identity(self) -> None:
        prior = _prior_by_tier({i: 1.0 for i in range(8)})
        assert tilt_prior_along_pessimism(prior, 0.0) == pytest.approx(prior)

    def test_positive_tilt_raises_expected_tier(self) -> None:
        # 点质量才能精确验证位移量：均匀分布经线性插值平移仍均匀，期望档不变
        prior = _prior_by_tier({3: 1.0})
        tilted = tilt_prior_along_pessimism(prior, 1.5)
        assert expected_pessimism_tier(tilted) == pytest.approx(3.0 + 1.5)

    def test_negative_tilt_lowers_expected_tier(self) -> None:
        prior = _prior_by_tier({3: 1.0})
        tilted = tilt_prior_along_pessimism(prior, -0.5)
        assert expected_pessimism_tier(tilted) == pytest.approx(3.0 - 0.5)

    def test_boundary_mass_accumulates_at_pessimistic_end(self) -> None:
        """clamp 语义：越出端点档的质量堆积在边界（档6/7 平移越界→全部落最悲观档）。

        均匀先验 0.125/档，tilt+1.5：档7 收自身(0.125)+档6 越界(0.125)+档5 半格(0.0625)=0.3125。
        """
        prior = _prior_by_tier({i: 1.0 for i in range(8)})
        tilted = tilt_prior_along_pessimism(prior, 1.5)
        assert tilted[NextDayState.GAP_DOWN_DOWN] == pytest.approx(0.3125)
        assert sum(tilted.values()) == pytest.approx(1.0)

    def test_mass_conserved_and_normalized(self) -> None:
        prior = _prior_by_tier({3: 1.0})
        tilted = tilt_prior_along_pessimism(prior, 2.4)
        assert sum(tilted.values()) == pytest.approx(1.0)
        assert all(p >= 0.0 for p in tilted.values())

    def test_extreme_tilt_clamps_at_pessimistic_end(self) -> None:
        prior = _prior_by_tier({7: 1.0})
        tilted = tilt_prior_along_pessimism(prior, 3.0)
        assert tilted[NextDayState.GAP_DOWN_DOWN] == pytest.approx(1.0)

    def test_extreme_tilt_clamps_at_optimistic_end(self) -> None:
        prior = _prior_by_tier({0: 1.0})
        tilted = tilt_prior_along_pessimism(prior, -3.0)
        assert tilted[NextDayState.GAP_UP_UP] == pytest.approx(1.0)


# ── 融合与预警 ──────────────────────────────────────────────────────────────


class TestFuse:
    def test_no_scenario_fused_equals_prior(self) -> None:
        prior = _prior_by_tier({i: 1.0 for i in range(8)})
        out = fuse(prior, None)
        assert out.distribution == pytest.approx({s.value: p for s, p in prior.items()})
        assert out.weights == {"prior": 1.0, "similar": 0.0}
        assert not out.downgrade_warning

    def test_fallback_scenario_excluded_with_note(self) -> None:
        prior = _prior_by_tier({i: 1.0 for i in range(8)})
        out = fuse(prior, _scenario(0.0, 0.0, 1.0, fallback_used=True))
        assert out.weights["similar"] == 0.0
        assert any("双计" in n for n in out.notes)

    def test_disabled_scenario_excluded_with_note(self) -> None:
        prior = _prior_by_tier({i: 1.0 for i in range(8)})
        out = fuse(prior, _scenario(0.0, 0.0, 1.0, enabled=False))
        assert out.weights["similar"] == 0.0
        assert any("停用" in n for n in out.notes)

    def test_brier_downweight_shrinks_similar_weight(self) -> None:
        prior = _prior_by_tier({i: 1.0 for i in range(8)})
        neutral = fuse(prior, _scenario(0.1, 0.1, 0.8))
        penalized = fuse(
            prior,
            _scenario(0.1, 0.1, 0.8),
            calibration_similar=SourceCalibration("similar_day_inference", brier=0.45),
        )
        assert neutral.weights["similar"] > penalized.weights["similar"]
        assert penalized.weights["similar"] < BASE_W_SIMILAR
        # 先验侧校准缺数据=中性（基础权重 0.7 全额参与）
        assert neutral.weights["prior"] == pytest.approx(
            BASE_W_PRIOR / (BASE_W_PRIOR + BASE_W_SIMILAR)
        )

    def test_dominant_tier_gap_diagnostic_present(self) -> None:
        prior = _prior_by_tier({2: 0.30, 4: 0.25, 1: 0.09, 3: 0.09, 5: 0.09, 6: 0.09, 7: 0.09})
        out = fuse(prior, _scenario(0.0, 0.0, 1.0), intraday_point="14:30")
        assert out.dominant_tier_prior == 2
        assert out.dominant_tier_fused > out.dominant_tier_prior
        assert out.intraday_point == "14:30"


class TestDowngradeWarning:
    def test_warning_fires_when_dominant_drops_two_tiers(self) -> None:
        """双峰先验（平开高走主峰档2+剧烈震荡次峰档4）：全弱情景整体下移 2 档后
        次峰质量反超主峰残留 → 最可能态档位差 ≥1 → 预警。"""
        prior = _prior_by_tier({2: 0.30, 4: 0.25, 1: 0.09, 3: 0.09, 5: 0.09, 6: 0.09, 7: 0.09})
        out = fuse(prior, _scenario(0.0, 0.0, 1.0))
        assert out.dominant_tier_fused - out.dominant_tier_prior >= DOWNGRADE_TIER_THRESHOLD
        assert out.downgrade_warning is True
        assert any("降档预警" in n for n in out.notes)

    def test_no_warning_when_prior_dominant_has_safe_lead(self) -> None:
        """先验最可能态大幅领先时，小幅倾斜不翻转 argmax→不误报。"""
        prior = _prior_by_tier({1: 0.9, **{i: 0.0166 for i in (0, 2, 3, 4, 5, 6, 7)}})
        out = fuse(prior, _scenario(0.0, 0.0, 1.0))
        assert out.dominant_tier_prior == 1
        assert out.dominant_tier_fused == 1
        assert out.downgrade_warning is False

    def test_no_warning_on_balanced_scenario(self) -> None:
        prior = _prior_by_tier({2: 0.5, 3: 0.5, **{i: 0.0 for i in (0, 1, 4, 5, 6, 7)}})
        out = fuse(prior, _scenario(0.5, 0.0, 0.5))
        assert out.downgrade_warning is False

    def test_warning_threshold_is_strictly_reached_not_incremental(self) -> None:
        """阈值=整数档 ≥1：档位差恰为 1 触发，0 不触发。"""
        assert DOWNGRADE_TIER_THRESHOLD == 1


# ── 红-前视 / 红-竞态 ───────────────────────────────────────────────────────


class TestPurity:
    def test_deterministic_same_input_same_output(self) -> None:
        prior = _prior_by_tier({i: 1.0 for i in range(8)})
        a = fuse(prior, _scenario(0.2, 0.3, 0.5), intraday_point="11:00")
        b = fuse(prior, _scenario(0.2, 0.3, 0.5), intraday_point="11:00")
        assert a == b

    def test_frozen_output_immutable(self) -> None:
        prior = _prior_by_tier({i: 1.0 for i in range(8)})
        out = fuse(prior, None)
        with pytest.raises(Exception):
            out.downgrade_warning = True  # type: ignore[misc]

    def test_no_wall_clock_in_output(self) -> None:
        """输出键集合封闭（无时间戳/墙钟字段=无前视通道）。"""
        prior = _prior_by_tier({i: 1.0 for i in range(8)})
        d = fuse(prior, None).to_dict()
        assert set(d) == {
            "distribution",
            "expected_tier_prior",
            "expected_tier_fused",
            "dominant_state",
            "dominant_tier_prior",
            "dominant_tier_fused",
            "downgrade_warning",
            "weights",
            "notes",
            "intraday_point",
        }


# ── 序列化与性能（R39 实测） ────────────────────────────────────────────────


class TestSerializationAndLatency:
    def test_to_dict_json_round_trip(self) -> None:
        prior = _prior_by_tier({i: 1.0 for i in range(8)})
        payload = fuse(prior, _scenario(0.2, 0.3, 0.5), intraday_point="13:30").to_dict()
        restored = json.loads(json.dumps(payload, ensure_ascii=False))
        assert restored["dominant_state"] == payload["dominant_state"]
        assert restored["downgrade_warning"] == payload["downgrade_warning"]
        assert len(restored["distribution"]) == 8

    def test_fuse_latency_budget(self) -> None:
        """R39 实测：合成核单次耗时应远低于盘中滚动预算（纯函数，无 IO）。"""
        prior = _prior_by_tier({i: 1.0 for i in range(8)})
        sc = _scenario(0.2, 0.3, 0.5)
        n = 2000
        t0 = time.perf_counter()
        for _ in range(n):
            fuse(prior, sc)
        elapsed = time.perf_counter() - t0
        per_call_ms = elapsed / n * 1000
        assert per_call_ms < 1.0, f"单次合成 {per_call_ms:.3f}ms 超 1ms 预算"
