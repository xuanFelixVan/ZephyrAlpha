"""跨切面 D 异常检测 + 蓝图保真 + 原生API守卫 + 内存守卫 测试."""
from __future__ import annotations

import pytest
from zephyr.agent_rbac.anomaly_detector import AnomalyDetector
from zephyr.agent_rbac.blueprint_fidelity import BlueprintFidelity
from zephyr.agent_rbac.native_api_guard import NativeApiGuard
from zephyr.agent_rbac.memory_guard import MemoryGuard


class TestCrossCutD:
    def test_anomaly_detector_normal(self):
        detector = AnomalyDetector()
        for i in range(20):
            result = detector.feed("request_rate", 100.0 + i * 0.5)
        assert not result.anomalous

    def test_anomaly_detector_spike(self):
        detector = AnomalyDetector()
        for i in range(20):
            detector.feed("request_rate", 100.0)
        result = detector.feed("request_rate", 500.0)
        assert result.anomalous
        assert result.z_score > 3.0

    def test_blueprint_fidelity_field_check(self):
        fidelity = BlueprintFidelity()
        fc = fidelity.check_field_count("identity", 6, 6)
        assert fc.match is True

    def test_blueprint_fidelity_mismatch(self):
        fidelity = BlueprintFidelity()
        fc = fidelity.check_field_count("identity", 6, 3)
        assert fc.match is False

    def test_native_api_guard_blocked(self):
        guard = NativeApiGuard()
        result = guard.scan("import ctypes; ctypes.CDLL('libc.so')", "test.py")
        assert result["allowed"] is False
        assert len(result["matched"]) > 0

    def test_native_api_guard_allowed(self):
        guard = NativeApiGuard()
        result = guard.scan("def calculate(x): return x * 2", "calc.py")
        assert result["allowed"] is True

    def test_memory_guard_normal_access(self):
        guard = MemoryGuard()
        result = guard.check_access("agent_test", "read_buffer", 1024)
        assert result["allowed"] is True

    def test_memory_guard_size_exceeded(self):
        guard = MemoryGuard()
        result = guard.check_access("agent_test", "read_buffer", 2000000)
        assert result["allowed"] is False

    def test_memory_guard_privileged_op(self):
        guard = MemoryGuard()
        result = guard.check_access("agent_test", "mprotect", 1024)
        assert result["allowed"] is False
