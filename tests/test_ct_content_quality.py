# [A_test] module_id: SRC-TST-0663 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] tests.test_ct_content_quality
# [INVARIANTS] Handler import+instantiation+run return type; name attribute match
# [MODIFY-GUARD] source handler changes require test updates
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError on invariant violation
# [TESTS] pytest tests/test_ct_content_quality.py
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


class TestContentQualityHandlerImport:
    def test_import_module(self):
        import importlib

        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_content_quality")
        assert hasattr(mod, "ContentQualityHandler")

    def test_class_is_check_type_handler(self):
        import importlib

        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_content_quality")
        assert issubclass(mod.ContentQualityHandler, CheckTypeHandler)


class TestContentQualityHandlerInstantiation:
    def test_instantiate(self):
        import importlib

        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_content_quality")
        handler = mod.ContentQualityHandler()
        assert handler is not None

    def test_name_attribute(self):
        import importlib

        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_content_quality")
        handler = mod.ContentQualityHandler()
        assert handler.name == "content_quality"

    def test_registered_in_registry(self):
        cls = get_check_type("content_quality")
        assert cls is not None


class TestContentQualityHandlerRun:
    def test_run_returns_list(self):
        cls = get_check_type("content_quality")
        handler = cls()
        task = _make_task()
        result = handler.run(task, {}, _MockCheck(), Path("."))
        assert isinstance(result, list)

    def test_run_with_empty_deliverables(self):
        cls = get_check_type("content_quality")
        handler = cls()
        task = _make_task(deliverables=[])
        result = handler.run(task, {}, _MockCheck(), Path("."))
        assert isinstance(result, list)

    def test_run_violations_have_message(self):
        cls = get_check_type("content_quality")
        handler = cls()
        task = _make_task()
        result = handler.run(task, {}, _MockCheck(), Path("."))
        for v in result:
            assert "message" in v


class TestContentQualityHandlerFileBased:
    def test_nonexistent_deliverable_no_crash(self, tmp_path):
        cls = get_check_type("content_quality")
        handler = cls()
        task = _make_task(deliverables=["nonexistent_file.xyz"])
        result = handler.run(task, {}, _MockCheck(), tmp_path)
        assert isinstance(result, list)


class TestContentQualityHandlerContentQuality:
    def test_empty_shell_violation(self, tmp_path):
        shell_file = tmp_path / "shell.py"
        shell_file.write_text("# comment\n", encoding="utf-8")
        cls = get_check_type("content_quality")
        handler = cls()
        task = _make_task(deliverables=["shell.py"])
        result = handler.run(task, {"min_lines": 5}, _MockCheck(), tmp_path)
        assert len(result) >= 1

    def test_substantial_content_passes(self, tmp_path):
        good_file = tmp_path / "good.py"
        lines = "\n".join(["x_" + str(i) + " = " + str(i) for i in range(10)])
        good_file.write_text(lines, encoding="utf-8")
        cls = get_check_type("content_quality")
        handler = cls()
        task = _make_task(deliverables=["good.py"])
        result = handler.run(task, {"min_lines": 5}, _MockCheck(), tmp_path)
        assert len(result) == 0
