# [A_test] module_id: SRC-TST-0676 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] tests.test_ct_path_blacklist
# [INVARIANTS] Handler import+instantiation+run return type; name attribute match
# [MODIFY-GUARD] source handler changes require test updates
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError on invariant violation
# [TESTS] pytest tests/test_ct_path_blacklist.py
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


class TestPathBlacklistHandlerImport:
    def test_import_module(self):
        import importlib

        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_path_blacklist")
        assert hasattr(mod, "PathBlacklistHandler")

    def test_class_is_check_type_handler(self):
        import importlib

        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_path_blacklist")
        assert issubclass(mod.PathBlacklistHandler, CheckTypeHandler)


class TestPathBlacklistHandlerInstantiation:
    def test_instantiate(self):
        import importlib

        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_path_blacklist")
        handler = mod.PathBlacklistHandler()
        assert handler is not None

    def test_name_attribute(self):
        import importlib

        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_path_blacklist")
        handler = mod.PathBlacklistHandler()
        assert handler.name == "path_blacklist"

    def test_registered_in_registry(self):
        cls = get_check_type("path_blacklist")
        assert cls is not None


class TestPathBlacklistHandlerRun:
    def test_run_returns_list(self):
        cls = get_check_type("path_blacklist")
        handler = cls()
        task = _make_task()
        result = handler.run(task, {}, _MockCheck(), Path("."))
        assert isinstance(result, list)

    def test_run_with_empty_deliverables(self):
        cls = get_check_type("path_blacklist")
        handler = cls()
        task = _make_task(deliverables=[])
        result = handler.run(task, {}, _MockCheck(), Path("."))
        assert isinstance(result, list)

    def test_run_violations_have_message(self):
        cls = get_check_type("path_blacklist")
        handler = cls()
        task = _make_task()
        result = handler.run(task, {}, _MockCheck(), Path("."))
        for v in result:
            assert "message" in v


class TestPathBlacklistHandlerPathBlacklist:
    def test_blacklisted_path_fails(self):
        cls = get_check_type("path_blacklist")
        handler = cls()
        task = _make_task(deliverables=["secrets/key.pem"])
        result = handler.run(task, {"blacklist": ["secrets/"]}, _MockCheck(), Path("."))
        assert len(result) >= 1

    def test_non_blacklisted_path_passes(self):
        cls = get_check_type("path_blacklist")
        handler = cls()
        task = _make_task(deliverables=["src/main.py"])
        result = handler.run(task, {"blacklist": ["secrets/"]}, _MockCheck(), Path("."))
        assert len(result) == 0

    def test_empty_blacklist(self):
        cls = get_check_type("path_blacklist")
        handler = cls()
        task = _make_task(deliverables=["src/main.py"])
        result = handler.run(task, {"blacklist": []}, _MockCheck(), Path("."))
        assert len(result) == 0
