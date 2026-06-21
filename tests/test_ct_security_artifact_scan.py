# [A_test] module_id: SRC-TST-0686 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7
# [MODULE] tests.test_ct_security_artifact_scan
# [INVARIANTS] Handler import+instantiation+run return type; name attribute match
# [MODIFY-GUARD] source handler changes require test updates
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError on invariant violation
# [TESTS] pytest tests/test_ct_security_artifact_scan.py
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

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

class TestSecurityArtifactScanHandlerImport:
    def test_import_module(self):
        import importlib
        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_security_artifact_scan")
        assert hasattr(mod, "SecurityArtifactScanHandler")

    def test_class_is_check_type_handler(self):
        import importlib
        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_security_artifact_scan")
        assert issubclass(mod.SecurityArtifactScanHandler, CheckTypeHandler)

class TestSecurityArtifactScanHandlerInstantiation:
    def test_instantiate(self):
        import importlib
        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_security_artifact_scan")
        handler = mod.SecurityArtifactScanHandler()
        assert handler is not None

    def test_name_attribute(self):
        import importlib
        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_security_artifact_scan")
        handler = mod.SecurityArtifactScanHandler()
        assert handler.name == "security_artifact_scan"

    def test_registered_in_registry(self):
        cls = get_check_type("security_artifact_scan")
        assert cls is not None

class TestSecurityArtifactScanHandlerRun:
    def test_run_returns_list(self):
        cls = get_check_type("security_artifact_scan")
        handler = cls()
        task = _make_task()
        result = handler.run(task, {}, _MockCheck(), Path("."))
        assert isinstance(result, list)

    def test_run_with_empty_deliverables(self):
        cls = get_check_type("security_artifact_scan")
        handler = cls()
        task = _make_task(deliverables=[])
        result = handler.run(task, {}, _MockCheck(), Path("."))
        assert isinstance(result, list)

    def test_run_violations_have_message(self):
        cls = get_check_type("security_artifact_scan")
        handler = cls()
        task = _make_task()
        result = handler.run(task, {}, _MockCheck(), Path("."))
        for v in result:
            assert "message" in v
class TestSecurityArtifactScanHandlerExternalDep:
    def test_run_does_not_crash_on_missing_dep(self):
        cls = get_check_type("security_artifact_scan")
        handler = cls()
        task = _make_task()
        result = handler.run(task, {}, _MockCheck(), Path("."))
        assert isinstance(result, list)

    def test_violations_have_severity(self):
        cls = get_check_type("security_artifact_scan")
        handler = cls()
        task = _make_task()
        result = handler.run(task, {}, _MockCheck(), Path("."))
        for v in result:
            assert "severity" in v
