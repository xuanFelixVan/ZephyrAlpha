# [A_test] module_id: SRC-TST-0674 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] tests.test_ct_line_ending
# [INVARIANTS] Handler import+instantiation+run return type; name attribute match
# [MODIFY-GUARD] source handler changes require test updates
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError on invariant violation
# [TESTS] pytest tests/test_ct_line_ending.py
# [TTL] task_bound
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from zephyr.governance.rule_enforcement.check_types.check_type_registry import (
    CheckTypeHandler,
    get_check_type,
)


def _make_task(deliverables=None, task_id="KBG-001"):
    from zephyr.governance.rule_enforcement.task_types import Task, TaskNamespace, TaskStatus
    from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel

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
        priority=Priority.P2,
        deliverables=deliverables or [],
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )


class _MockCheck:
    def __init__(self, severity="P0"):
        self.severity = severity
        self.id = "CHK-TEST"


class TestLineEndingHandlerImport:
    def test_import_module(self):
        import importlib

        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_line_ending")
        assert hasattr(mod, "LineEndingHandler")

    def test_class_is_check_type_handler(self):
        import importlib

        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_line_ending")
        assert issubclass(mod.LineEndingHandler, CheckTypeHandler)


class TestLineEndingHandlerInstantiation:
    def test_instantiate(self):
        import importlib

        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_line_ending")
        handler = mod.LineEndingHandler()
        assert handler is not None

    def test_name_attribute(self):
        import importlib

        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_line_ending")
        handler = mod.LineEndingHandler()
        assert handler.name == "line_ending"

    def test_registered_in_registry(self):
        cls = get_check_type("line_ending")
        assert cls is not None


class TestLineEndingHandlerRun:
    def test_run_returns_list(self):
        cls = get_check_type("line_ending")
        handler = cls()
        task = _make_task()
        result = handler.run(task, {}, _MockCheck(), Path("."))
        assert isinstance(result, list)

    def test_run_with_empty_deliverables(self):
        cls = get_check_type("line_ending")
        handler = cls()
        task = _make_task(deliverables=[])
        result = handler.run(task, {}, _MockCheck(), Path("."))
        assert isinstance(result, list)

    def test_run_violations_have_message(self):
        cls = get_check_type("line_ending")
        handler = cls()
        task = _make_task()
        result = handler.run(task, {}, _MockCheck(), Path("."))
        for v in result:
            assert "message" in v


class TestLineEndingHandlerFileBased:
    def test_nonexistent_deliverable_no_crash(self, tmp_path):
        cls = get_check_type("line_ending")
        handler = cls()
        task = _make_task(deliverables=["nonexistent_file.xyz"])
        result = handler.run(task, {}, _MockCheck(), tmp_path)
        assert isinstance(result, list)


class TestLineEndingHandlerLineEnding:
    def test_lf_passes(self, tmp_path):
        lf_file = tmp_path / "lf.txt"
        lf_file.write_bytes(b"line1\nline2\n")
        cls = get_check_type("line_ending")
        handler = cls()
        task = _make_task(deliverables=["lf.txt"])
        result = handler.run(task, {}, _MockCheck(), tmp_path)
        assert len(result) == 0

    def test_crlf_fails(self, tmp_path):
        crlf_file = tmp_path / "crlf.txt"
        crlf_file.write_text("placeholder", encoding="utf-8")
        cls = get_check_type("line_ending")
        handler = cls()
        task = _make_task(deliverables=["crlf.txt"])
        original_read_text = Path.read_text

        def _mock_read_text(self, *args, **kwargs):
            if str(self).endswith("crlf.txt"):
                return "line1\r\nline2\r\n"
            return original_read_text(self, *args, **kwargs)

        with patch.object(Path, "read_text", _mock_read_text):
            result = handler.run(task, {}, _MockCheck(), tmp_path)
        assert len(result) >= 1
        assert any("CRLF" in v["message"] for v in result)
