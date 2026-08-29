# [A_test] module_id: MOD-LLM_SECURITY_phase_gate_hookup | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §17a
# [MODULE] tests.llm_security.test_phase_gate_lsg_hookup
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""check_lsg_security 挂接测试（09 号文 §4.3 P1-4 / 蓝图 §17a 第 7 项）。

验收：phase_manager Phase 1 门禁可消费 LSG 健康状态——
PHASE_SEQUENCE 登记 gate_lsg_security、phase_check_registry 映射到
check_lsg_security、run_check 回调可执行且返回 GateResult。
全部断言基于注册表/映射，不触网、不写盘。
"""

from __future__ import annotations

from typing import Any

from zephyr.governance.ops_governance.phase_check_registry import (
    GateResult,
    PhaseCheckRegistry,
    check_lsg_security,
    run_check,
)


class TestPhaseSequenceRegistration:
    def test_phase1_gate_checks_include_lsg_security(self) -> None:
        from zephyr.governance.ops_governance.phase_manager import (
            PHASE_SEQUENCE,
            ConstructionPhase,
        )

        gate = PHASE_SEQUENCE[ConstructionPhase.PHASE_1_FUNCTIONAL]
        assert "gate_lsg_security" in gate.gate_checks

    def test_registry_maps_gate_name_to_check_function(self) -> None:
        func = PhaseCheckRegistry.get("gate_lsg_security")
        assert func is check_lsg_security

    def test_registered_checks_contains_lsg(self) -> None:
        assert "gate_lsg_security" in PhaseCheckRegistry.registered_checks()


class TestCheckLsgSecurityExecution:
    def test_run_check_returns_gate_result(self) -> None:
        """phase_manager 消费路径：run_check("gate_lsg_security") 不抛异常且返回 GateResult。"""
        result = run_check("gate_lsg_security")
        assert isinstance(result, GateResult)

    def test_healthy_stack_returns_green(self) -> None:
        """真实构造 LSGSecurityGateway（纯本地，无网络）：层数齐全 → GREEN。"""
        result = check_lsg_security()
        assert result is GateResult.GREEN

    def test_import_failure_degrades_gracefully(self, monkeypatch: Any) -> None:
        """LSG 模块不可导入 → 不抛异常，降级为 RED/YELLOW（fail-safe）。"""
        import importlib

        def _raise_import(name: str, *args: Any, **kwargs: Any) -> Any:
            raise ImportError("simulated missing lsg module")

        monkeypatch.setattr(importlib, "import_module", _raise_import)
        result = check_lsg_security()
        assert result in (GateResult.RED, GateResult.YELLOW)
