# [A_test] module_id: SRC-TST-0667 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7
# [MODULE] tests.test_ct_encoding
# [INVARIANTS] Handler import+instantiation+run return type; name attribute match
# [MODIFY-GUARD] source handler changes require test updates
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError on invariant violation
# [TESTS] pytest tests/test_ct_encoding.py
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

class TestEncodingHandlerImport:
    def test_import_module(self):
        import importlib
        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_encoding")
        assert hasattr(mod, "EncodingHandler")

    def test_class_is_check_type_handler(self):
        import importlib
        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_encoding")
        assert issubclass(mod.EncodingHandler, CheckTypeHandler)

class TestEncodingHandlerInstantiation:
    def test_instantiate(self):
        import importlib
        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_encoding")
        handler = mod.EncodingHandler()
        assert handler is not None

    def test_name_attribute(self):
        import importlib
        mod = importlib.import_module("zephyr.governance.rule_enforcement.check_types.ct_encoding")
        handler = mod.EncodingHandler()
        assert handler.name == "encoding"

    def test_registered_in_registry(self):
        cls = get_check_type("encoding")
        assert cls is not None

class TestEncodingHandlerRun:
    def test_run_returns_list(self):
        cls = get_check_type("encoding")
        handler = cls()
        task = _make_task()
        result = handler.run(task, {}, _MockCheck(), Path("."))
        assert isinstance(result, list)

    def test_run_with_empty_deliverables(self):
        cls = get_check_type("encoding")
        handler = cls()
        task = _make_task(deliverables=[])
        result = handler.run(task, {}, _MockCheck(), Path("."))
        assert isinstance(result, list)

    def test_run_violations_have_message(self):
        cls = get_check_type("encoding")
        handler = cls()
        task = _make_task()
        result = handler.run(task, {}, _MockCheck(), Path("."))
        for v in result:
            assert "message" in v
class TestEncodingHandlerFileBased:
    def test_nonexistent_deliverable_no_crash(self, tmp_path):
        cls = get_check_type("encoding")
        handler = cls()
        task = _make_task(deliverables=["nonexistent_file.xyz"])
        result = handler.run(task, {}, _MockCheck(), tmp_path)
        assert isinstance(result, list)
class TestEncodingHandlerEncoding:
    def test_utf8_file_passes(self, tmp_path):
        good_file = tmp_path / "good.txt"
        good_file.write_text("UTF-8 content", encoding="utf-8")
        cls = get_check_type("encoding")
        handler = cls()
        task = _make_task(deliverables=["good.txt"])
        result = handler.run(task, {}, _MockCheck(), tmp_path)
        assert len(result) == 0

    def test_bom_file_fails(self, tmp_path):
        bom_file = tmp_path / "bom.txt"
        bom_file.write_bytes(b"\xef\xbb\xbfBOM content\n")
        cls = get_check_type("encoding")
        handler = cls()
        task = _make_task(deliverables=["bom.txt"])
        result = handler.run(task, {}, _MockCheck(), tmp_path)
        assert len(result) >= 1
        assert any("BOM" in v["message"] for v in result)
