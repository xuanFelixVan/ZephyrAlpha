# [A_test] module_id: MOD-GOV_test_t_rules_config | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.pf_core.test_t_rules_config
# [TESTS] src/zephyr/pf_core/strategy_engine/tick_strategy_base.py（90 号 Phase2 四规则段）
# [TTL] task_bound
"""90 号 Phase2 项（#21 做T）：四规则配置化已知答案 toy 断言。

裁定真源：90_methodology_open_questions.md §21（v2.0.0 受约束 overlay）——
  sizing：单次做T仓位≤底仓 20-30%（取保守端 0.25）；
  regime 过滤：仅在量比>1 且预期振幅>2×单边成本（≈0.3%）时开仓；
  失败处置：反T 14:30 后强制接回；正T 单笔止损 -1.5%~-2%。
"""

from __future__ import annotations

from datetime import time

import pytest

from zephyr.pf_core.strategy_engine.tick_strategy_base import TRulesConfig


class TestDefaults:
    def test_defaults_match_ruling(self):
        cfg = TRulesConfig()
        assert cfg.max_t_position_ratio == 0.25  # 底仓 20-30% 保守端
        assert cfg.min_volume_ratio == 1.0  # 量比>1
        assert cfg.single_side_cost_rate == 0.0015  # 单边成本≈0.15%
        assert cfg.force_cover_time == time(14, 30)  # 14:30 强制接回
        assert cfg.stop_loss_pct == -0.015  # 单笔止损 -1.5%


class TestRuleChecks:
    def test_position_cap(self):
        """底仓 10 万 → 单次做T上限 2.5 万。"""
        assert TRulesConfig().t_position_cap(100_000.0) == pytest.approx(25_000.0)

    def test_volume_filter(self):
        cfg = TRulesConfig()
        assert cfg.volume_filter_ok(0.8) is False
        assert cfg.volume_filter_ok(1.0) is False  # 须严格 >1
        assert cfg.volume_filter_ok(1.2) is True

    def test_amplitude_filter(self):
        """预期振幅 > 2×单边成本（2×0.15%=0.3%）才开仓。"""
        cfg = TRulesConfig()
        assert cfg.amplitude_filter_ok(0.002) is False
        assert cfg.amplitude_filter_ok(0.003) is False  # 须严格大于
        assert cfg.amplitude_filter_ok(0.004) is True

    def test_force_cover(self):
        cfg = TRulesConfig()
        assert cfg.must_force_cover(time(14, 29)) is False
        assert cfg.must_force_cover(time(14, 30)) is True
        assert cfg.must_force_cover(time(14, 55)) is True

    def test_stop_loss(self):
        cfg = TRulesConfig()
        assert cfg.stop_loss_triggered(-0.010) is False
        assert cfg.stop_loss_triggered(-0.015) is True
        assert cfg.stop_loss_triggered(-0.020) is True


class TestValidation:
    def test_ratio_above_conservative_cap_raises(self):
        """裁定收紧为 20-30%：超 0.30 上限拒绝。"""
        with pytest.raises(ValueError):
            TRulesConfig(max_t_position_ratio=0.5)

    def test_zero_ratio_raises(self):
        with pytest.raises(ValueError):
            TRulesConfig(max_t_position_ratio=0.0)

    def test_negative_volume_ratio_raises(self):
        with pytest.raises(ValueError):
            TRulesConfig(min_volume_ratio=-1.0)

    def test_positive_stop_loss_raises(self):
        with pytest.raises(ValueError):
            TRulesConfig(stop_loss_pct=0.01)

    def test_force_cover_at_close_raises(self):
        """强制接回必须早于收盘 15:00。"""
        with pytest.raises(ValueError):
            TRulesConfig(force_cover_time=time(15, 0))

    def test_negative_cost_raises(self):
        with pytest.raises(ValueError):
            TRulesConfig(single_side_cost_rate=-0.001)
