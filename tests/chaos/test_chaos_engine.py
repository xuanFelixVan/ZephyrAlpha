# [A_test] module_id: SRC-TST-0509 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_chaos_engine
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_chaos_engine.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.trading.orchestrator.fault_tolerance.chaos_engine import (
    INJECTION_POINTS,
    ChaosEngine,
    ChaosInjectError,
    InjectionResult,
)


class TestChaosEngineInstantiation:
    def test_default_construction(self):
        engine = ChaosEngine()
        assert engine is not None


class TestChaosEngineGetInjectionPoints:
    def test_returns_list(self):
        engine = ChaosEngine()
        points = engine.get_injection_points()
        assert isinstance(points, list)

    def test_injection_points_count(self):
        engine = ChaosEngine()
        points = engine.get_injection_points()
        assert len(points) == 4

    def test_injection_points_have_required_keys(self):
        engine = ChaosEngine()
        points = engine.get_injection_points()
        for point in points:
            assert "name" in point
            assert "system" in point
            assert "type" in point
            assert "duration_s" in point

    def test_injection_point_names(self):
        engine = ChaosEngine()
        points = engine.get_injection_points()
        names = [p["name"] for p in points]
        assert "vms_latency" in names
        assert "vms_error" in names
        assert "lsg_crash" in names
        assert "script_exit3" in names

    def test_injection_point_types(self):
        engine = ChaosEngine()
        points = engine.get_injection_points()
        types = {p["name"]: p["type"] for p in points}
        assert types["vms_latency"] == "latency"
        assert types["vms_error"] == "error"
        assert types["lsg_crash"] == "crash"
        assert types["script_exit3"] == "exit_code"


class TestChaosEngineInject:
    def test_inject_known_point(self):
        engine = ChaosEngine()
        result = engine.inject("vms_latency")
        assert result is True

    def test_inject_another_known_point(self):
        engine = ChaosEngine()
        result = engine.inject("lsg_crash")
        assert result is True

    def test_inject_unknown_point(self):
        engine = ChaosEngine()
        result = engine.inject("nonexistent")
        assert result is False

    def test_inject_empty_string(self):
        engine = ChaosEngine()
        result = engine.inject("")
        assert result is False

    def test_inject_all_known_points(self):
        engine = ChaosEngine()
        for point in INJECTION_POINTS:
            assert engine.inject(point["name"]) is True


class TestInjectionPointsConstant:
    def test_injection_points_is_list(self):
        assert isinstance(INJECTION_POINTS, list)

    def test_injection_points_count(self):
        assert len(INJECTION_POINTS) == 4

    def test_duration_s_non_negative(self):
        for point in INJECTION_POINTS:
            assert point["duration_s"] >= 0

    def test_systems_are_strings(self):
        for point in INJECTION_POINTS:
            assert isinstance(point["system"], str)
            assert len(point["system"]) > 0


class TestChaosEngineInjectDirect:
    """Phase 7d 补充测试：直接 inject_type 调用 + 错误路径 + 副作用验证"""

    def test_inject_latency_direct(self):
        result = ChaosEngine().inject("latency", delay_ms=1, target="test_target")
        assert isinstance(result, InjectionResult)
        assert result.injected is True
        assert result.injection_type == "latency"
        assert result.target == "test_target"

    def test_inject_error_direct(self):
        result = ChaosEngine().inject("error", target="test_target")
        assert isinstance(result, InjectionResult)
        assert result.injected is True
        assert result.injection_type == "error"

    def test_inject_exit_code_direct(self):
        result = ChaosEngine().inject("exit_code", target="test_target")
        assert isinstance(result, InjectionResult)
        assert result.injected is True
        assert result.injection_type == "exit_code"

    def test_inject_unknown_type_returns_false(self):
        """完全未知的 type（非 InjectType 成员）走 ValueError 路径返回 False"""
        result = ChaosEngine().inject("totally_unknown_type")
        assert result is False

    def test_inject_unhandled_injecttype_raises(self):
        """InjectType 有 7 值但 inject 只处理 4 个，其余 raise"""
        with pytest.raises(ChaosInjectError):
            ChaosEngine().inject("resource_exhaustion")

    def test_inject_crash_without_confirmation_raises(self):
        with pytest.raises(ChaosInjectError):
            ChaosEngine().inject("crash", target="test_target")

    def test_inject_updates_last_result(self):
        engine = ChaosEngine()
        engine.inject("error", target="test_target")
        assert engine._last_result is not None
        assert engine._last_result.injection_type == "error"

    def test_inject_updates_injection_state(self):
        engine = ChaosEngine()
        engine.inject("error", target="test_target")
        assert "test_target" in engine._injection_state
        assert engine._injection_state["test_target"] is True

    def test_inject_returns_duration_ms(self):
        result = ChaosEngine().inject("latency", delay_ms=1, target="test_target")
        assert isinstance(result, InjectionResult)
        assert result.duration_ms >= 0.0

    def test_inject_crash_via_point_silent_success(self):
        """crash 通过 point 调用时，ChaosInjectError 被捕获返回 True"""
        result = ChaosEngine().inject("lsg_crash")
        assert result is True
