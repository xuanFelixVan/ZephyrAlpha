# [A_test] module_id: SRC-TST-0107 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-265 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.contracts.test_ct_rbk_gate_001
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""CT-RBK-GATE-001 集成测试——Rollback System Exit Code → Gate 判定 → Pipeline 行为。"""

from __future__ import annotations

from zephyr.infrastructure.rollback.contract import (
    EXIT_CODE_TO_GATE_ACTION,
    PIPELINE_ACTIONS,
    RollbackExitCode,
    get_gate_action,
    get_pipeline_action,
    resolve_exit_code,
)
from zephyr.orchestrator.contracts.contract_registry import ContractRegistry
from zephyr.orchestrator.contracts.contract_router import ContractRouter


def test_ct_rbk_gate_registered():
    contract = ContractRegistry().get("CT-RBK-GATE-001")
    assert contract is not None
    assert contract.producer == "Rollback System"
    assert contract.consumer == "Gate Engine"


def test_ct_rbk_gate_caution_stub():
    result = ContractRegistry().check_ai_read_only("CT-RBK-GATE-001")
    assert result.allowed is True


def test_ct_rbk_gate_route():
    router = ContractRouter(ContractRegistry())
    result = router.route("CT-RBK-GATE-001")
    assert result.target_system == "rollback"


def test_rollback_exit_code_enum_has_46_entries():
    codes = [e for e in RollbackExitCode]
    assert len(codes) >= 40
    assert RollbackExitCode.SUCCESS == 0
    assert RollbackExitCode.DRILL_MELTDOWN == 33


def test_exit_code_to_gate_action_covers_all_enum_values():
    for code in RollbackExitCode:
        assert code.value in EXIT_CODE_TO_GATE_ACTION, (
            f"Exit code {code.name}={code.value} missing from EXIT_CODE_TO_GATE_ACTION"
        )


def test_get_gate_action_known_code():
    gate, desc = get_gate_action(0)
    assert gate == "PASS"
    assert "No action" in desc


def test_get_gate_action_unknown_code():
    gate, desc = get_gate_action(9999)
    assert gate == "UNKNOWN"


def test_get_pipeline_action_known():
    action = get_pipeline_action("PASS")
    assert "Continue pipeline" in action


def test_get_pipeline_action_unknown():
    action = get_pipeline_action("NONEXISTENT")
    assert "Unknown" in action


def test_resolve_exit_code_success():
    result = resolve_exit_code(0)
    assert result["exit_code"] == "0"
    assert result["gate_action"] == "PASS"
    assert "Continue" in result["pipeline_action"]


def test_resolve_exit_code_drill_meltdown():
    result = resolve_exit_code(33)
    assert result["exit_code"] == "33"
    assert result["gate_action"] == "BLOCK_AUTO"


def test_resolve_exit_code_secrets_leak_l3():
    result = resolve_exit_code(22)
    assert result["gate_action"] == "L3_KILL"


def test_pipeline_actions_covers_all_gate_actions():
    all_gates = {action for action, _ in EXIT_CODE_TO_GATE_ACTION.values()}
    for gate in all_gates:
        if gate != "UNKNOWN":
            assert gate in PIPELINE_ACTIONS, f"Gate action '{gate}' missing from PIPELINE_ACTIONS"
