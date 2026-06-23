# [A_test] module_id: SRC-TST-F15-PM | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_auto_fix_phase_manager
# [INVARIANTS] 测试F15注册到phase_manager;覆盖gate_auto_fix_start检查函数
# [MODIFY-GUARD] blueprint.md §3
# [CONSUMERS] CI
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] self

"""DM-202508 验收测试: F15注册到phase_manager实现自动启停"""
from __future__ import annotations

import pytest

from zephyr.governance.phase_manager import (
    ConstructionPhase,
    PHASE_SEQUENCE,
    get_phase,
)
from zephyr.governance.phase_check_registry import (
    GateResult,
    PhaseCheckRegistry,
    check_auto_fix_start,
    run_check,
)


class TestGateAutoFixStartRegistered:
    """验证 gate_auto_fix_start 已注册到 PHASE_1_FUNCTIONAL"""

    def test_gate_in_phase_1_functional(self):
        p1 = PHASE_SEQUENCE[ConstructionPhase.PHASE_1_FUNCTIONAL]
        assert "gate_auto_fix_start" in p1.gate_checks

    def test_gate_in_check_map(self):
        func = PhaseCheckRegistry.get("gate_auto_fix_start")
        assert func is not None
        assert callable(func)

    def test_gate_not_in_phase_0(self):
        p0 = PHASE_SEQUENCE[ConstructionPhase.PHASE_0_SKELETON]
        assert "gate_auto_fix_start" not in p0.gate_checks

    def test_gate_not_in_phase_2(self):
        p2 = PHASE_SEQUENCE[ConstructionPhase.PHASE_2_E2E]
        assert "gate_auto_fix_start" not in p2.gate_checks


class TestCheckAutoFixStartFunction:
    """验证 check_auto_fix_start 检查函数"""

    def test_returns_gate_result(self):
        result = check_auto_fix_start()
        assert isinstance(result, GateResult)

    def test_returns_green_when_registered(self):
        result = check_auto_fix_start()
        assert result == GateResult.GREEN

    def test_run_check_integration(self):
        result = run_check("gate_auto_fix_start")
        assert result == GateResult.GREEN


class TestFixSchedulerStartStop:
    """验证 FixScheduler 可启动和停止"""

    def test_scheduler_can_start(self):
        from zephyr.infrastructure.auto_fix_engine.fix_scheduler import FixScheduler

        scheduler = FixScheduler()
        assert not scheduler.is_running
        scheduler.start()
        assert scheduler.is_running
        scheduler.stop()
        assert not scheduler.is_running

    def test_scheduler_start_idempotent(self):
        from zephyr.infrastructure.auto_fix_engine.fix_scheduler import FixScheduler

        scheduler = FixScheduler()
        scheduler.start()
        scheduler.start()
        assert scheduler.is_running
        scheduler.stop()

    def test_scheduler_stop_idempotent(self):
        from zephyr.infrastructure.auto_fix_engine.fix_scheduler import FixScheduler

        scheduler = FixScheduler()
        scheduler.stop()
        assert not scheduler.is_running


class TestAutoFixEngineImportable:
    """验证 AutoFixEngine 可导入和实例化"""

    def test_engine_importable(self):
        from zephyr.infrastructure.auto_fix_engine.engine import AutoFixEngine

        assert AutoFixEngine is not None

    def test_engine_instantiable(self):
        from zephyr.infrastructure.auto_fix_engine.engine import AutoFixEngine

        engine = AutoFixEngine()
        assert engine is not None


class TestPhaseGateIntegrity:
    """验证添加 gate_auto_fix_start 后 Phase 1 完整性"""

    def test_phase_1_gate_count_increased(self):
        p1 = PHASE_SEQUENCE[ConstructionPhase.PHASE_1_FUNCTIONAL]
        assert len(p1.gate_checks) >= 25

    def test_phase_1_dependencies_unchanged(self):
        p1 = PHASE_SEQUENCE[ConstructionPhase.PHASE_1_FUNCTIONAL]
        assert ConstructionPhase.PHASE_0_SKELETON in p1.dependencies

    def test_get_phase_returns_gate(self):
        gate = get_phase(ConstructionPhase.PHASE_1_FUNCTIONAL)
        assert gate is not None
        assert "gate_auto_fix_start" in gate.gate_checks
