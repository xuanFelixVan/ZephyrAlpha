# [A_test] module_id: SRC-TST-1883 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-503 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.gates.test_gate_check_types
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

from __future__ import annotations
from _shared.constants import REPO_ROOT

"""Test suite: gate check type system"""


from pathlib import Path
from typing import Any

import pytest

from zephyr.governance.rule_enforcement.check_types.check_type_registry import (
    CheckTypeHandler,
    get_check_type,
    list_check_types,
    register_check_type,
)
from zephyr.governance.rule_enforcement.gate_engine.gate_engine import CheckConfig, GateEngine, GateResult
from zephyr.governance.rule_enforcement.gate_types import GateEngineError, GateViolation
from zephyr.governance.rule_enforcement.task_types import Task, TaskNamespace, TaskStatus
from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel

GATES_DIR = REPO_ROOT / "src" / "zephyr" / "governance" / "rule_enforcement"


def _make_task(
    task_id: str = "ADR-001",
    deliverables: list[str] | None = None,
    priority: str = "P2",
) -> Task:
    namespace = task_id.split("-")[0]
    seq = int(task_id.split("-")[-1])
    return Task(
        task_id=task_id,
        namespace=TaskNamespace(namespace),
        seq=seq,
        phase=2,
        title="Test task",
        status=TaskStatus.PENDING,
        execution_model="claude",
        safety_level=SafetyLevel.L,
        priority=Priority(priority),
        deliverables=deliverables or [],
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )


def _make_check_config(
    check_id: str = "CHK-001",
    check_type: str = "field_presence",
    severity: str = "P0",
    params: dict[str, Any] | None = None,
) -> CheckConfig:
    return CheckConfig(
        check_id=check_id,
        name=f"Test {check_type}",
        check_type=check_type,
        description="Test check",
        severity=severity,
        params=params or {},
    )


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_check_types.db"


@pytest.fixture
def engine(db_path: Path) -> GateEngine:
    ge = GateEngine(gate_dir=GATES_DIR, db_path=db_path, project_root=Path("."))
    yield ge
    ge.close()


class TestGateEngineInstantiation:
    def test_engine_creates_with_defaults(self, db_path: Path) -> None:
        ge = GateEngine(gate_dir=GATES_DIR, db_path=db_path)
        assert ge is not None
        ge.close()

    def test_engine_context_manager(self, db_path: Path) -> None:
        with GateEngine(gate_dir=GATES_DIR, db_path=db_path) as ge:
            assert ge is not None

    def test_engine_has_gate_dir(self, db_path: Path) -> None:
        ge = GateEngine(gate_dir=GATES_DIR, db_path=db_path)
        assert ge._gate_dir == GATES_DIR
        ge.close()


class TestGateResultCreation:
    def test_pass_result(self) -> None:
        result = GateResult(
            gate_id="G1",
            task_id="ADR-001",
            passed=True,
        )
        assert result.passed is True
        assert result.gate_id == "G1"
        assert result.task_id == "ADR-001"
        assert result.violations == []
        assert result.has_p0 is False

    def test_fail_result_with_p0(self) -> None:
        violation = GateViolation(
            check_id="CHK-001",
            check_name="Test check",
            severity="P0",
            message="Critical violation",
        )
        result = GateResult(
            gate_id="G0",
            task_id="ADR-002",
            passed=False,
            violations=[violation],
        )
        assert result.passed is False
        assert result.has_p0 is True
        assert len(result.p0_violations) == 1

    def test_fail_result_with_p1_only(self) -> None:
        violation = GateViolation(
            check_id="CHK-002",
            check_name="Warning check",
            severity="P1",
            message="Warning violation",
        )
        result = GateResult(
            gate_id="G1",
            task_id="ADR-003",
            passed=True,
            violations=[violation],
        )
        assert result.passed is True
        assert result.has_p0 is False
        assert len(result.violations) == 1

    def test_summary_pass(self) -> None:
        result = GateResult(gate_id="G1", task_id="ADR-004", passed=True)
        assert "[PASS]" in result.summary()

    def test_summary_fail(self) -> None:
        violation = GateViolation(
            check_id="CHK-003",
            check_name="Fail check",
            severity="P0",
            message="Fail",
        )
        result = GateResult(
            gate_id="G0",
            task_id="ADR-005",
            passed=False,
            violations=[violation],
        )
        assert "[FAIL]" in result.summary()

    def test_details_dict(self) -> None:
        result = GateResult(
            gate_id="G1",
            task_id="ADR-006",
            passed=True,
            details={"checks_run": 3, "total_violations": 0},
        )
        assert result.details["checks_run"] == 3

    def test_evaluated_at_populated(self) -> None:
        result = GateResult(gate_id="G1", task_id="ADR-007", passed=True)
        assert result.evaluated_at != ""


class TestCheckTypeRegistry:
    def test_list_check_types_returns_list(self) -> None:
        types = list_check_types()
        assert isinstance(types, list)
        assert len(types) > 0

    def test_known_types_registered(self) -> None:
        types = list_check_types()
        expected = {"field_presence", "classification", "encoding", "line_ending"}
        assert expected.issubset(set(types)), f"Missing: {expected - set(types)}"

    def test_get_check_type_returns_handler(self) -> None:
        handler_cls = get_check_type("field_presence")
        assert handler_cls is not None
        assert issubclass(handler_cls, CheckTypeHandler)

    def test_get_check_type_unknown_returns_none(self) -> None:
        handler_cls = get_check_type("nonexistent_type_xyz")
        assert handler_cls is None

    def test_list_check_types_sorted(self) -> None:
        types = list_check_types()
        assert types == sorted(types)


class TestFieldPresenceHandler:
    def test_missing_required_field(self) -> None:
        handler_cls = get_check_type("field_presence")
        assert handler_cls is not None
        handler = handler_cls()
        check = _make_check_config(
            check_type="field_presence",
            params={"required_fields": ["directive"]},
        )
        task = _make_task()
        task.directive = ""
        violations = handler.run(task, {"required_fields": ["directive"]}, check, Path("."))
        assert len(violations) > 0
        assert any("directive" in v["message"] for v in violations)

    def test_present_required_field_passes(self) -> None:
        handler_cls = get_check_type("field_presence")
        assert handler_cls is not None
        handler = handler_cls()
        check = _make_check_config(
            check_type="field_presence",
            params={"required_fields": ["task_id"]},
        )
        task = _make_task()
        violations = handler.run(task, {"required_fields": ["task_id"]}, check, Path("."))
        assert len(violations) == 0

    def test_multiple_missing_fields(self) -> None:
        handler_cls = get_check_type("field_presence")
        assert handler_cls is not None
        handler = handler_cls()
        check = _make_check_config(
            check_type="field_presence",
            params={"required_fields": ["directive", "source_blueprint"]},
        )
        task = _make_task()
        task.directive = ""
        task.source_blueprint = ""
        violations = handler.run(
            task,
            {"required_fields": ["directive", "source_blueprint"]},
            check,
            Path("."),
        )
        assert len(violations) == 2


class TestClassificationHandler:
    def test_valid_classification_passes(self) -> None:
        handler_cls = get_check_type("classification")
        assert handler_cls is not None
        handler = handler_cls()
        check = _make_check_config(
            check_type="classification",
            params={
                "field": "priority",
                "allowed_values": ["Priority.P0", "Priority.P1", "Priority.P2", "Priority.P3", "Priority.P4"],
            },
        )
        task = _make_task(priority="P2")
        violations = handler.run(
            task,
            {
                "field": "priority",
                "allowed_values": ["Priority.P0", "Priority.P1", "Priority.P2", "Priority.P3", "Priority.P4"],
            },
            check,
            Path("."),
        )
        assert len(violations) == 0

    def test_invalid_classification_fails(self) -> None:
        handler_cls = get_check_type("classification")
        assert handler_cls is not None
        handler = handler_cls()
        check = _make_check_config(
            check_type="classification",
            params={"field": "priority", "allowed_values": ["Priority.P0", "Priority.P1"]},
        )
        task = _make_task(priority="P2")
        violations = handler.run(
            task,
            {"field": "priority", "allowed_values": ["Priority.P0", "Priority.P1"]},
            check,
            Path("."),
        )
        assert len(violations) > 0
        assert any("priority" in v["message"] for v in violations)

    def test_no_field_name_no_violation(self) -> None:
        handler_cls = get_check_type("classification")
        assert handler_cls is not None
        handler = handler_cls()
        check = _make_check_config(check_type="classification", params={})
        task = _make_task()
        violations = handler.run(task, {}, check, Path("."))
        assert len(violations) == 0


class TestEncodingHandler:
    def test_utf8_file_passes(self, tmp_path: Path) -> None:
        handler_cls = get_check_type("encoding")
        assert handler_cls is not None
        handler = handler_cls()
        good_file = tmp_path / "good.md"
        good_file.write_bytes(b"Normal UTF-8 content\n")
        check = _make_check_config(check_type="encoding")
        task = _make_task(deliverables=["good.md"])
        violations = handler.run(task, {}, check, tmp_path)
        assert len(violations) == 0

    def test_bom_file_fails(self, tmp_path: Path) -> None:
        handler_cls = get_check_type("encoding")
        assert handler_cls is not None
        handler = handler_cls()
        bom_file = tmp_path / "bom.md"
        bom_file.write_bytes(b"\xef\xbb\xbf# BOM\n")
        check = _make_check_config(check_type="encoding")
        task = _make_task(deliverables=["bom.md"])
        violations = handler.run(task, {}, check, tmp_path)
        assert len(violations) > 0
        assert any("BOM" in v["message"] for v in violations)

    def test_nonexistent_file_no_violation(self, tmp_path: Path) -> None:
        handler_cls = get_check_type("encoding")
        assert handler_cls is not None
        handler = handler_cls()
        check = _make_check_config(check_type="encoding")
        task = _make_task(deliverables=["nonexistent.md"])
        violations = handler.run(task, {}, check, tmp_path)
        assert len(violations) == 0


class TestRegisterCheckTypeDecorator:
    def test_custom_handler_registration(self) -> None:
        @register_check_type
        class _TestCustomHandler(CheckTypeHandler):
            name = "test_custom_handler_xyz"

            def run(self, task, params, check, project_root):
                return []

        retrieved = get_check_type("test_custom_handler_xyz")
        assert retrieved is _TestCustomHandler

    def test_custom_handler_in_list(self) -> None:
        @register_check_type
        class _TestListHandler(CheckTypeHandler):
            name = "test_list_handler_xyz"

            def run(self, task, params, check, project_root):
                return []

        types = list_check_types()
        assert "test_list_handler_xyz" in types


class TestGateEngineEvaluateWithCheckTypes:
    def test_evaluate_g0_with_missing_fields(self, engine: GateEngine) -> None:
        task = _make_task()
        task.directive = ""
        result = engine.evaluate(task, "G0")
        assert isinstance(result, GateResult)
        assert result.gate_id == "G0"

    def test_evaluate_unknown_gate_raises(self, engine: GateEngine) -> None:
        task = _make_task()
        with pytest.raises(GateEngineError, match="未知 gate_id"):
            engine.evaluate(task, "G99")

    def test_evaluate_g1_returns_result(self, engine: GateEngine) -> None:
        task = _make_task()
        result = engine.evaluate(task, "G1")
        assert isinstance(result, GateResult)
        assert result.gate_id == "G1"
        assert result.task_id == "ADR-001"
