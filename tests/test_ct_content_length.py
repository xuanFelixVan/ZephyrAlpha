# [A_test] module_id: SRC-TST-0662 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] tests.test_ct_content_length
# [INVARIANTS] Handler import+instantiation+run return type; name attribute match
# [MODIFY-GUARD] source handler changes require test updates
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError on invariant violation
# [TESTS] pytest tests/test_ct_content_length.py
# [TTL] task_bound
from __future__ import annotations

from pathlib import Path

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


class TestContentLengthHandlerImport:
    def test_import_module(self):
        import importlib

        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_content_length")
        assert hasattr(mod, "ContentLengthHandler")

    def test_class_is_check_type_handler(self):
        import importlib

        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_content_length")
        assert issubclass(mod.ContentLengthHandler, CheckTypeHandler)


class TestContentLengthHandlerInstantiation:
    def test_instantiate(self):
        import importlib

        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_content_length")
        handler = mod.ContentLengthHandler()
        assert handler is not None

    def test_name_attribute(self):
        import importlib

        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_content_length")
        handler = mod.ContentLengthHandler()
        assert handler.name == "content_length"

    def test_registered_in_registry(self):
        cls = get_check_type("content_length")
        assert cls is not None


class TestContentLengthHandlerRun:
    def test_run_returns_list(self):
        cls = get_check_type("content_length")
        handler = cls()
        task = _make_task()
        result = handler.run(task, {}, _MockCheck(), Path("."))
        assert isinstance(result, list)

    def test_run_with_empty_deliverables(self):
        cls = get_check_type("content_length")
        handler = cls()
        task = _make_task(deliverables=[])
        result = handler.run(task, {}, _MockCheck(), Path("."))
        assert isinstance(result, list)

    def test_run_violations_have_message(self):
        cls = get_check_type("content_length")
        handler = cls()
        task = _make_task()
        result = handler.run(task, {}, _MockCheck(), Path("."))
        for v in result:
            assert "message" in v


class TestContentLengthHandlerFileBased:
    def test_nonexistent_deliverable_no_crash(self, tmp_path):
        cls = get_check_type("content_length")
        handler = cls()
        task = _make_task(deliverables=["nonexistent_file.xyz"])
        result = handler.run(task, {}, _MockCheck(), tmp_path)
        assert isinstance(result, list)


class TestContentLengthHandlerContentLength:
    def test_short_content_violation(self, tmp_path):
        short_file = tmp_path / "short.txt"
        short_file.write_text("hi", encoding="utf-8")
        cls = get_check_type("content_length")
        handler = cls()
        task = _make_task(deliverables=["short.txt"])
        result = handler.run(task, {"min_chars": 100}, _MockCheck(), tmp_path)
        assert len(result) >= 1

    def test_long_content_passes(self, tmp_path):
        long_file = tmp_path / "long.txt"
        long_file.write_text("x" * 200, encoding="utf-8")
        cls = get_check_type("content_length")
        handler = cls()
        task = _make_task(deliverables=["long.txt"])
        result = handler.run(task, {"min_chars": 100}, _MockCheck(), tmp_path)
        assert len(result) == 0
