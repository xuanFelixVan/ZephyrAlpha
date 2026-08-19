# [TTL] permanent
"""25号memo §3.7#3 DecayActionLifecycle 6态 + CUSUM预警层 + 注册表映射 测试。

覆盖：
- 6态全转移路径（NEW→ACTIVE/OBSERVE; ACTIVE→OBSERVE; OBSERVE→DORMANT/ACTIVE;
  DORMANT→RECOVERY/RETIRED; RECOVERY→ACTIVE/DORMANT）
- CusumMonitor: 下行偏移预警/正常不预警
- DECAY_TO_REGISTRY_STATUS 映射完整性
"""
from __future__ import annotations

import pytest

mod = pytest.importorskip("zephyr.factor.analysis.multifactor_decay_lifecycle")

CusumMonitor = mod.CusumMonitor
DecayActionLifecycle = mod.DecayActionLifecycle
DecayState = mod.DecayState
DECAY_TO_REGISTRY_STATUS = mod.DECAY_TO_REGISTRY_STATUS
registry_status_for = mod.registry_status_for


def _walk(life, fid, days, half_life=30.0, abs_ic=0.05, cusum=False):
    st = None
    for _ in range(days):
        st = life.transition_with_boundaries(fid, half_life, abs_ic, cusum)
    return st


class TestNewState:
    def test_init_new_factor(self):
        life = DecayActionLifecycle()
        st = life.init_new_factor("f1")
        assert st.state is DecayState.NEW
        assert st.weight_multiplier == 0.3

    def test_new_to_active_after_warmup(self):
        life = DecayActionLifecycle()
        life.init_new_factor("f1")
        st = _walk(life, "f1", 20, half_life=30.0, abs_ic=0.05)
        assert st.state is DecayState.ACTIVE
        assert st.weight_multiplier == 1.0

    def test_new_to_observe_when_ic_weak(self):
        life = DecayActionLifecycle()
        life.init_new_factor("f1")
        st = _walk(life, "f1", 20, half_life=30.0, abs_ic=0.01)
        assert st.state is DecayState.OBSERVE
        assert st.weight_multiplier == 0.5

    def test_new_stays_before_warmup(self):
        life = DecayActionLifecycle()
        life.init_new_factor("f1")
        st = _walk(life, "f1", 19, half_life=30.0, abs_ic=0.05)
        assert st.state is DecayState.NEW

    def test_unknown_factor_auto_inits(self):
        life = DecayActionLifecycle()
        st = life.transition_with_boundaries("ghost", 30.0, 0.05)
        assert st.state is DecayState.NEW


class TestActiveObserve:
    def test_active_to_observe_on_short_halflife(self):
        life = DecayActionLifecycle()
        life.init_new_factor("f1")
        _walk(life, "f1", 20, half_life=30.0, abs_ic=0.05)
        st = life.transition_with_boundaries("f1", half_life=15.0, abs_ic=0.05)
        assert st.state is DecayState.OBSERVE
        assert st.weight_multiplier == 0.5

    def test_observe_recovers_to_active(self):
        life = DecayActionLifecycle()
        life.init_new_factor("f1")
        _walk(life, "f1", 20, half_life=30.0, abs_ic=0.05)
        life.transition_with_boundaries("f1", 15.0, 0.05)
        st = life.transition_with_boundaries("f1", half_life=25.0, abs_ic=0.05)
        assert st.state is DecayState.ACTIVE
        assert st.weight_multiplier == 1.0

    def test_observe_to_dormant_after_40d_low_ic(self):
        life = DecayActionLifecycle()
        life.init_new_factor("f1")
        _walk(life, "f1", 20, half_life=30.0, abs_ic=0.05)
        life.transition_with_boundaries("f1", 15.0, 0.01)  # →OBSERVE
        st = _walk(life, "f1", 40, half_life=15.0, abs_ic=0.01)
        assert st.state is DecayState.DORMANT
        assert st.weight_multiplier == 0.0
        assert not st.participates_in_synthesis

    def test_observe_blocked_by_cusum(self):
        life = DecayActionLifecycle()
        life.init_new_factor("f1")
        _walk(life, "f1", 20, half_life=30.0, abs_ic=0.05)
        life.transition_with_boundaries("f1", 15.0, 0.05, cusum_alert=True)
        # 半衰期恢复但 CUSUM 预警中 → 不回 ACTIVE
        st = life.transition_with_boundaries("f1", half_life=25.0, abs_ic=0.05, cusum_alert=True)
        assert st.state is DecayState.OBSERVE

    def test_cusum_40d_no_recovery_to_dormant(self):
        life = DecayActionLifecycle()
        life.init_new_factor("f1")
        _walk(life, "f1", 20, half_life=30.0, abs_ic=0.05)
        life.transition_with_boundaries("f1", 15.0, 0.05, cusum_alert=True)
        # CUSUM 预警持续 40 日无恢复 → DORMANT（即使 |IC| 未破 0.02）
        st = _walk(life, "f1", 40, half_life=15.0, abs_ic=0.05, cusum=True)
        assert st.state is DecayState.DORMANT


class TestDormantRecoveryRetired:
    def _make_dormant(self, life, fid="f1"):
        life.init_new_factor(fid)
        _walk(life, fid, 20, half_life=30.0, abs_ic=0.05)
        life.transition_with_boundaries(fid, 15.0, 0.01)
        _walk(life, fid, 40, half_life=15.0, abs_ic=0.01)
        assert life.states[fid].state is DecayState.DORMANT

    def test_dormant_to_recovery_after_10d_strong_ic(self):
        life = DecayActionLifecycle()
        self._make_dormant(life)
        st = _walk(life, "f1", 10, half_life=15.0, abs_ic=0.04)
        assert st.state is DecayState.RECOVERY
        assert st.weight_multiplier == 0.3

    def test_dormant_streak_resets_on_weak_day(self):
        life = DecayActionLifecycle()
        self._make_dormant(life)
        _walk(life, "f1", 9, half_life=15.0, abs_ic=0.04)
        life.transition_with_boundaries("f1", 15.0, 0.01)  # 中断
        st = _walk(life, "f1", 9, half_life=15.0, abs_ic=0.04)
        assert st.state is DecayState.DORMANT  # 重新计 9 日未满 10

    def test_dormant_to_retired_after_120d(self):
        life = DecayActionLifecycle()
        self._make_dormant(life)
        st = _walk(life, "f1", 120, half_life=15.0, abs_ic=0.01)
        assert st.state is DecayState.RETIRED
        assert not st.participates_in_synthesis
        # 终态不再转移
        st = life.transition_with_boundaries("f1", 30.0, 0.10)
        assert st.state is DecayState.RETIRED

    def test_recovery_to_active(self):
        life = DecayActionLifecycle()
        self._make_dormant(life)
        _walk(life, "f1", 10, half_life=15.0, abs_ic=0.04)
        st = life.transition_with_boundaries("f1", half_life=25.0, abs_ic=0.04)
        assert st.state is DecayState.ACTIVE
        assert st.weight_multiplier == 1.0

    def test_recovery_relapses_to_dormant(self):
        life = DecayActionLifecycle()
        self._make_dormant(life)
        _walk(life, "f1", 10, half_life=15.0, abs_ic=0.04)
        st = life.transition_with_boundaries("f1", half_life=15.0, abs_ic=0.01)
        assert st.state is DecayState.DORMANT


class TestCusumMonitor:
    def test_alert_on_downward_shift(self):
        # μ=0.05, σ=0.02 → k=0.01, h=0.08；持续 IC=0.0 → 每日累积 0.04，3 日越界
        m = CusumMonitor(mu_ic=0.05, sigma_ic=0.02)
        assert not m.update(0.0)
        assert not m.update(0.0)
        assert m.update(0.0)
        assert m.alert

    def test_no_alert_on_normal_ic(self):
        m = CusumMonitor(mu_ic=0.05, sigma_ic=0.02)
        for _ in range(50):
            assert not m.update(0.05)  # IC=μ → 每步 -k，恒 0
        assert not m.alert

    def test_reset(self):
        m = CusumMonitor(mu_ic=0.05, sigma_ic=0.02)
        for _ in range(5):
            m.update(0.0)
        assert m.alert
        m.reset()
        assert not m.alert


class TestRegistryMapping:
    def test_all_states_mapped(self):
        assert set(DECAY_TO_REGISTRY_STATUS) == set(DecayState)

    def test_mapping_values(self):
        assert registry_status_for(DecayState.NEW) == "experimental"
        assert registry_status_for(DecayState.ACTIVE) == "active"
        assert registry_status_for(DecayState.OBSERVE) == "active"
        assert registry_status_for(DecayState.DORMANT) == "deprecated"
        assert registry_status_for(DecayState.RECOVERY) == "experimental"
        assert registry_status_for(DecayState.RETIRED) == "retired"

    def test_mapping_targets_valid_registry_states(self):
        valid = {"candidate", "experimental", "active", "deprecated", "retired"}
        assert set(DECAY_TO_REGISTRY_STATUS.values()) <= valid
