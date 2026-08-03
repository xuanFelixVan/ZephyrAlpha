# [A_test] module_id: MOD-GOV_adaptive_threshold | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_adaptive_threshold
# [DOMAIN] D_GOV_CODE_QUALITY
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from collections import deque

from zephyr.gov_enforcement.rule_enforcement.adaptive_threshold import (
    AdaptiveThreshold,
    ThresholdMode,
    ThresholdState,
)


class TestThresholdState:
    def test_default_history_is_deque_maxlen_100(self) -> None:
        state = ThresholdState(gate_id="G1", current_threshold=0.8)
        assert isinstance(state.history, deque)
        assert state.history.maxlen == 100

    def test_fields_assigned(self) -> None:
        state = ThresholdState(gate_id="G2", current_threshold=0.5)
        assert state.gate_id == "G2"
        assert state.current_threshold == 0.5
        assert len(state.history) == 0

    def test_explicit_history_preserved(self) -> None:
        h: deque[float] = deque([1.0, 2.0], maxlen=50)
        state = ThresholdState(gate_id="G3", current_threshold=0.9, history=h)
        assert state.history is h
        assert len(state.history) == 2


class TestAdaptiveThresholdInit:
    def test_default_params(self) -> None:
        at = AdaptiveThreshold()
        assert at.window == 50
        assert at.smoothing == 0.2
        assert at.states == {}

    def test_custom_params(self) -> None:
        at = AdaptiveThreshold(window=20, smoothing=0.5)
        assert at.window == 20
        assert at.smoothing == 0.5


class TestGetState:
    def test_creates_new_state_with_default_initial(self) -> None:
        at = AdaptiveThreshold()
        state = at.get_state("G1")
        assert state.gate_id == "G1"
        assert state.current_threshold == 0.8
        assert len(state.history) == 0

    def test_creates_new_state_with_custom_initial(self) -> None:
        at = AdaptiveThreshold()
        state = at.get_state("G1", initial=0.3)
        assert state.current_threshold == 0.3

    def test_returns_same_state_for_same_gate_id(self) -> None:
        at = AdaptiveThreshold()
        s1 = at.get_state("G1")
        s2 = at.get_state("G1")
        assert s1 is s2

    def test_different_gate_ids_independent(self) -> None:
        at = AdaptiveThreshold()
        s1 = at.get_state("G1", initial=0.5)
        s2 = at.get_state("G2", initial=0.9)
        assert s1 is not s2
        assert s1.current_threshold == 0.5
        assert s2.current_threshold == 0.9


class TestObserve:
    def test_fail_increases_threshold(self) -> None:
        at = AdaptiveThreshold(smoothing=0.2)
        initial = 0.5
        at.get_state("G1", initial=initial)
        new_t = at.observe("G1", 0.6, "FAIL")
        assert new_t > initial

    def test_pass_decreases_threshold(self) -> None:
        at = AdaptiveThreshold(smoothing=0.2)
        initial = 0.5
        at.get_state("G1", initial=initial)
        new_t = at.observe("G1", 0.6, "PASS")
        assert new_t < initial

    def test_invalid_outcome_no_change(self) -> None:
        at = AdaptiveThreshold(smoothing=0.2)
        initial = 0.5
        at.get_state("G1", initial=initial)
        new_t = at.observe("G1", 0.6, "MAYBE")
        assert new_t == initial

    def test_value_appended_to_history(self) -> None:
        at = AdaptiveThreshold()
        at.observe("G1", 0.7, "PASS")
        state = at.get_state("G1")
        assert 0.7 in state.history

    def test_threshold_clamped_upper(self) -> None:
        at = AdaptiveThreshold(smoothing=0.5)
        at.get_state("G1", initial=0.99)
        new_t = at.observe("G1", 1.0, "FAIL")
        assert new_t <= 0.99

    def test_threshold_clamped_lower(self) -> None:
        at = AdaptiveThreshold(smoothing=0.5)
        at.get_state("G1", initial=0.1)
        new_t = at.observe("G1", 0.0, "PASS")
        assert new_t >= 0.1

    def test_observe_creates_state_if_missing(self) -> None:
        at = AdaptiveThreshold()
        new_t = at.observe("NEW_GATE", 0.5, "PASS")
        assert "NEW_GATE" in at.states
        assert isinstance(new_t, float)

    def test_multiple_observations_accumulate(self) -> None:
        at = AdaptiveThreshold(smoothing=0.2)
        at.get_state("G1", initial=0.5)
        t1 = at.observe("G1", 0.6, "FAIL")
        t2 = at.observe("G1", 0.6, "FAIL")
        assert t2 > t1


class TestEwma:
    def test_empty_history_returns_current_threshold(self) -> None:
        at = AdaptiveThreshold()
        at.get_state("G1", initial=0.75)
        assert at.ewma("G1") == 0.75

    def test_single_value_returns_that_value(self) -> None:
        at = AdaptiveThreshold()
        at.observe("G1", 0.6, "PASS")
        result = at.ewma("G1")
        assert result == 0.6

    def test_multiple_values_computes_ewma(self) -> None:
        at = AdaptiveThreshold(window=3)
        at.observe("G1", 1.0, "PASS")
        at.observe("G1", 0.0, "FAIL")
        state = at.get_state("G1")
        history = list(state.history)
        alpha = 2.0 / (min(len(history), 3) + 1)
        expected = history[0]
        for v in history[1:]:
            expected = alpha * v + (1 - alpha) * expected
        result = at.ewma("G1")
        assert abs(result - expected) < 1e-10

    def test_ewma_creates_state_if_missing(self) -> None:
        at = AdaptiveThreshold()
        result = at.ewma("UNKNOWN")
        assert result == 0.8


class TestBoundaryConditions:
    def test_smoothing_zero_no_adjustment(self) -> None:
        at = AdaptiveThreshold(smoothing=0.0)
        at.get_state("G1", initial=0.5)
        new_t = at.observe("G1", 0.6, "FAIL")
        assert new_t == 0.5

    def test_smoothing_zero_pass_no_adjustment(self) -> None:
        at = AdaptiveThreshold(smoothing=0.0)
        at.get_state("G1", initial=0.5)
        new_t = at.observe("G1", 0.6, "PASS")
        assert new_t == 0.5

    def test_history_respects_maxlen(self) -> None:
        at = AdaptiveThreshold()
        at.get_state("G1", initial=0.5)
        for i in range(150):
            at.observe("G1", float(i) / 150.0, "PASS")
        state = at.get_state("G1")
        assert len(state.history) == 100

    def test_empty_string_gate_id(self) -> None:
        at = AdaptiveThreshold()
        state = at.get_state("", initial=0.4)
        assert state.gate_id == ""
        assert state.current_threshold == 0.4

    def test_negative_value_observed(self) -> None:
        at = AdaptiveThreshold()
        new_t = at.observe("G1", -1.0, "PASS")
        assert isinstance(new_t, float)

    def test_large_value_observed(self) -> None:
        at = AdaptiveThreshold()
        new_t = at.observe("G1", 999.0, "FAIL")
        assert isinstance(new_t, float)

    def test_window_one(self) -> None:
        at = AdaptiveThreshold(window=1)
        at.observe("G1", 0.5, "PASS")
        at.observe("G1", 0.8, "FAIL")
        result = at.ewma("G1")
        assert isinstance(result, float)


# ============== P3-0 新增：count_threshold 模式测试（#ARCH-PREVENTABILITY-LAYER-001 Phase 3）==============


class TestThresholdMode:
    def test_enum_values(self) -> None:
        assert ThresholdMode.PROBABILITY.value == "probability"
        assert ThresholdMode.COUNT.value == "count"

    def test_default_mode_is_probability(self) -> None:
        state = ThresholdState(gate_id="G", current_threshold=0.5)
        assert state.mode == ThresholdMode.PROBABILITY

    def test_default_static_floor_zero(self) -> None:
        state = ThresholdState(gate_id="G", current_threshold=0.5)
        assert state.static_floor == 0.0

    def test_default_factor_1_5(self) -> None:
        state = ThresholdState(gate_id="G", current_threshold=0.5)
        assert state.factor == 1.5


class TestSetCountConfig:
    def test_creates_count_state_for_new_gate(self) -> None:
        at = AdaptiveThreshold()
        at.set_count_config("warn_only_24h", static_floor=20.0, factor=1.5)
        state = at.get_state("warn_only_24h")
        assert state.mode == ThresholdMode.COUNT
        assert state.static_floor == 20.0
        assert state.factor == 1.5

    def test_initial_threshold_equals_static_floor(self) -> None:
        at = AdaptiveThreshold()
        at.set_count_config("warn_only_24h", static_floor=20.0, factor=1.5)
        assert at.get_threshold("warn_only_24h") == 20.0

    def test_update_config_on_existing_count_state(self) -> None:
        at = AdaptiveThreshold()
        at.set_count_config("G1", static_floor=10.0, factor=1.5)
        at.observe_count("G1", 20)
        at.set_count_config("G1", static_floor=15.0, factor=2.0)
        state = at.get_state("G1")
        assert state.static_floor == 15.0
        assert state.factor == 2.0
        # 阈值应重算为 max(ewma * 2.0, 15.0)
        assert state.current_threshold >= 15.0

    def test_set_count_config_ignored_for_probability_state(self) -> None:
        at = AdaptiveThreshold()
        at.observe("G1", 0.5, "PASS")  # 创建 PROBABILITY 状态
        at.set_count_config("G1", static_floor=20.0, factor=1.5)  # 应被忽略
        state = at.get_state("G1")
        assert state.mode == ThresholdMode.PROBABILITY  # 模式未变更
        assert state.static_floor == 0.0  # 配置未应用


class TestObserveCount:
    def test_appends_to_history(self) -> None:
        at = AdaptiveThreshold()
        at.set_count_config("G1", static_floor=10.0, factor=1.5)
        at.observe_count("G1", 30)
        state = at.get_state("G1")
        assert 30 in state.history

    def test_single_observation_threshold_is_max_of_ewma_x_factor_or_floor(self) -> None:
        at = AdaptiveThreshold()
        at.set_count_config("G1", static_floor=10.0, factor=1.5)
        # 单值 ewma=30, threshold=max(30*1.5, 10)=45
        at.observe_count("G1", 30)
        assert at.get_threshold("G1") == 45.0

    def test_threshold_uses_static_floor_when_ewma_low(self) -> None:
        at = AdaptiveThreshold()
        at.set_count_config("G1", static_floor=20.0, factor=1.5)
        # ewma=5, threshold=max(5*1.5, 20)=20
        at.observe_count("G1", 5)
        assert at.get_threshold("G1") == 20.0

    def test_multiple_observations_ewma_weights_recent(self) -> None:
        at = AdaptiveThreshold(window=50)
        at.set_count_config("G1", static_floor=0.0, factor=1.0)  # factor=1 让阈值=ewma
        at.observe_count("G1", 10)
        at.observe_count("G1", 20)
        at.observe_count("G1", 30)
        # ewma 应介于 10 和 30 之间，且偏向 30（近期权重高）
        threshold = at.get_threshold("G1")
        assert 20 < threshold < 30

    def test_observe_count_creates_count_state_with_default_config(self) -> None:
        at = AdaptiveThreshold()
        # 未调 set_count_config，直接 observe_count
        at.observe_count("G1", 50)
        state = at.get_state("G1")
        assert state.mode == ThresholdMode.COUNT
        assert state.factor == at.DEFAULT_COUNT_FACTOR
        assert state.static_floor == at.DEFAULT_COUNT_FLOOR

    def test_observe_count_ignored_for_probability_state(self) -> None:
        at = AdaptiveThreshold()
        at.observe("G1", 0.5, "PASS")  # PROBABILITY
        original_threshold = at.get_threshold("G1")
        at.observe_count("G1", 100)  # 应被忽略
        assert at.get_threshold("G1") == original_threshold


class TestModeImmutability:
    def test_observe_ignored_after_observe_count(self) -> None:
        at = AdaptiveThreshold()
        at.observe_count("G1", 30)  # COUNT 模式
        original = at.get_threshold("G1")
        at.observe("G1", 0.5, "FAIL")  # 应被忽略
        assert at.get_threshold("G1") == original

    def test_observe_count_ignored_after_observe(self) -> None:
        at = AdaptiveThreshold()
        at.observe("G1", 0.5, "FAIL")  # PROBABILITY 模式
        original = at.get_threshold("G1")
        at.observe_count("G1", 100)  # 应被忽略
        assert at.get_threshold("G1") == original


class TestGetThreshold:
    def test_returns_current_threshold(self) -> None:
        at = AdaptiveThreshold()
        at.set_count_config("G1", static_floor=10.0, factor=1.5)
        at.observe_count("G1", 40)
        # threshold = max(40*1.5, 10) = 60
        assert at.get_threshold("G1") == 60.0

    def test_creates_default_state_for_unknown_gate(self) -> None:
        at = AdaptiveThreshold()
        # 未配置的 gate，get_threshold 应返回默认 initial=0.8
        assert at.get_threshold("UNKNOWN") == 0.8


class TestAbuseMonitorScenario:
    """模拟 abuse_monitor 5 维场景，验证 P3-0 设计满足 P3-1 接入需求。"""

    def test_warn_only_24h_scenario(self) -> None:
        """warn_only_24h：static_floor=20, factor=1.5"""
        at = AdaptiveThreshold()
        at.set_count_config("warn_only_24h", static_floor=20.0, factor=1.5)
        # 模拟 7 天每日 warn_only 计数：[15, 25, 30, 20, 35, 40, 28]
        for daily in [15, 25, 30, 20, 35, 40, 28]:
            at.observe_count("warn_only_24h", daily)
        threshold = at.get_threshold("warn_only_24h")
        # ewma 介于 15-40 之间，threshold = max(ewma*1.5, 20) >= 20
        assert threshold >= 20.0
        # ewma * 1.5 应大于 20（基线 30 左右 * 1.5 = 45 左右）
        assert threshold > 30.0

    def test_emergency_24h_scenario_low_count_keeps_floor(self) -> None:
        """emergency_24h：static_floor=5, factor=2.0，低计数场景保持 floor"""
        at = AdaptiveThreshold()
        at.set_count_config("emergency_24h", static_floor=5.0, factor=2.0)
        # 模拟 7 天低计数：[1, 2, 1, 0, 1, 2, 1]
        for daily in [1, 2, 1, 0, 1, 2, 1]:
            at.observe_count("emergency_24h", daily)
        threshold = at.get_threshold("emergency_24h")
        # ewma 约 1.x，ewma*2 约 2-3，小于 floor 5，threshold 应 = 5
        assert threshold == 5.0

    def test_forged_24h_scenario_high_count_triggers_higher_threshold(self) -> None:
        """forged_24h：static_floor=3, factor=2.0，高计数触发更高阈值"""
        at = AdaptiveThreshold()
        at.set_count_config("forged_24h", static_floor=3.0, factor=2.0)
        # 模拟 7 天高计数：[5, 8, 10, 12, 15, 20, 18]
        for daily in [5, 8, 10, 12, 15, 20, 18]:
            at.observe_count("forged_24h", daily)
        threshold = at.get_threshold("forged_24h")
        # ewma 偏向近期（15-20），ewma*2 约 30-40，远大于 floor 3
        assert threshold > 20.0

    def test_five_dimensions_independent(self) -> None:
        """5 维各自独立配置，互不干扰"""
        at = AdaptiveThreshold()
        at.set_count_config("warn_only_24h", static_floor=20.0, factor=1.5)
        at.set_count_config("emergency_24h", static_floor=5.0, factor=2.0)
        at.set_count_config("allow_overlap_7d", static_floor=15.0, factor=1.5)
        at.set_count_config("forged_24h", static_floor=3.0, factor=2.0)
        at.set_count_config("non_gw_24h", static_floor=5.0, factor=2.0)

        at.observe_count("warn_only_24h", 50)
        at.observe_count("emergency_24h", 2)
        at.observe_count("allow_overlap_7d", 30)
        at.observe_count("forged_24h", 8)
        at.observe_count("non_gw_24h", 3)

        # 各维阈值独立
        assert at.get_threshold("warn_only_24h") == 75.0  # 50*1.5
        assert at.get_threshold("emergency_24h") == 5.0  # max(2*2, 5)=5
        assert at.get_threshold("allow_overlap_7d") == 45.0  # 30*1.5
        assert at.get_threshold("forged_24h") == 16.0  # 8*2
        assert at.get_threshold("non_gw_24h") == 6.0  # max(3*2, 5)=6


class TestEwmaCountMode:
    def test_ewma_with_count_history(self) -> None:
        at = AdaptiveThreshold()
        at.set_count_config("G1", static_floor=0.0, factor=1.0)
        for v in [10, 20, 30, 40, 50]:
            at.observe_count("G1", v)
        ewma_val = at.ewma("G1")
        # ewma 应介于 10 和 50 之间，偏向近期（40-50）
        assert 30 < ewma_val < 50

    def test_ewma_single_count_returns_that_count(self) -> None:
        at = AdaptiveThreshold()
        at.set_count_config("G1", static_floor=0.0, factor=1.0)
        at.observe_count("G1", 42)
        assert at.ewma("G1") == 42.0


class TestBackwardCompatibility:
    """P3-0 扩展必须保持向后兼容——原 PROBABILITY 模式所有行为不变。"""

    def test_observe_still_works_without_mode_param(self) -> None:
        at = AdaptiveThreshold()
        at.get_state("G1", initial=0.5)
        new_t = at.observe("G1", 0.6, "FAIL")
        assert new_t > 0.5

    def test_threshold_state_default_mode_probability(self) -> None:
        state = ThresholdState(gate_id="G", current_threshold=0.5)
        assert state.mode == ThresholdMode.PROBABILITY

    def test_probability_state_no_static_floor_interference(self) -> None:
        """PROBABILITY 模式不受 static_floor/factor 影响"""
        at = AdaptiveThreshold()
        at.get_state("G1", initial=0.5, mode=ThresholdMode.PROBABILITY)
        # observe 后阈值在 [0.1, 0.99] 内
        new_t = at.observe("G1", 0.6, "FAIL")
        assert 0.1 <= new_t <= 0.99
