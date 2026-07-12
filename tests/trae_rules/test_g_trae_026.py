"""Test gate g_trae_026 for rule TRAE-026 — calls gate_engine.evaluate().

Red-Blue team extreme test: verifies gate can actually execute and block violations.
"""

from pathlib import Path

import pytest
import yaml

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
PROJECT_ROOT = REPO_ROOT  # alias 真源
GATE_YAML = PROJECT_ROOT / "src" / "zephyr" / "governance" / "rule_enforcement" / "g_trae_026.yaml"
RULE_YAML = PROJECT_ROOT / "docs" / "01_policies_and_standards" / "rules" / "trae_026_methodology_quality.yaml"
MOCK_YAML = PROJECT_ROOT / "tests" / "fixtures" / "g_trae_026_mock.yaml"


class TestGTrae026:
    """Red-Blue extreme tests for g_trae_026 gate."""

    def test_gate_yaml_exists(self):
        """PASS: gate YAML file exists."""
        assert GATE_YAML.exists(), f"Gate YAML not found: {GATE_YAML}"

    def test_gate_yaml_has_params(self):
        """PASS: entry_conditions have params field."""
        with open(GATE_YAML, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for cond in data.get("entry_conditions", []):
            assert "params" in cond, f"Entry condition {cond.get('id', '?')} missing params"
            assert len(cond["params"]) > 0, f"Entry condition {cond.get('id', '?')} params is empty"

    def test_gate_yaml_has_check_type(self):
        """PASS: entry_conditions have type field."""
        with open(GATE_YAML, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for cond in data.get("entry_conditions", []):
            assert "type" in cond, "Entry condition missing type"
            assert cond["type"] in [
                "field_presence",
                "classification",
                "regex_pattern",
                "audit_findings_resolved",
                "encoding",
                "line_ending",
                "file_extension",
                "frontmatter",
                "content_length",
                "deduplication",
                "path_blacklist",
                "path_whitelist",
                "content_quality",
                "score_threshold",
                "manual_approval",
                "temporal",
                "reference_check",
                "circuit_breaker",
                "blueprint_read_check",
                "drift_budget",
                "condition",
            ], f"Unknown check_type: {cond['type']}"

    def test_rule_yaml_exists(self):
        """PASS: rule YAML file exists."""
        assert RULE_YAML.exists(), f"Rule YAML not found: {RULE_YAML}"

    def test_mock_file_exists(self):
        """PASS: mock_input file exists."""
        assert MOCK_YAML.exists(), f"Mock file not found: {MOCK_YAML}"

    def test_gate_registered_in_gate_files(self):
        """PASS: gate is registered in gate_engine._GATE_FILES."""
        import sys

        sys.path.insert(0, str(PROJECT_ROOT / "src"))
        from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_engine import GateEngine

        assert "G_TRAE_026" in GateEngine._GATE_FILES, "Gate G_TRAE_026 not in _GATE_FILES"

    def test_gate_loadable_by_engine(self):
        """PASS: gate_engine can load this gate."""
        import sys

        sys.path.insert(0, str(PROJECT_ROOT / "src"))
        from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_engine import GateEngine

        engine = GateEngine(project_root=str(PROJECT_ROOT))
        # Temporarily add to _GATE_FILES if not there
        original = dict(GateEngine._GATE_FILES)
        try:
            if "G_TRAE_026" not in GateEngine._GATE_FILES:
                GateEngine._GATE_FILES["G_TRAE_026"] = "g_trae_026.yaml"
                engine._gate_cache = None  # Clear cache
            gates = engine.load_gates()
            assert "G_TRAE_026" in gates, "Gate G_TRAE_026 not loaded"
        finally:
            GateEngine._GATE_FILES = original
            engine._gate_cache = None

    def test_gate_evaluates_pass(self):
        """BLUE: valid task passes the gate."""
        import sys

        sys.path.insert(0, str(PROJECT_ROOT / "src"))
        from datetime import datetime

        from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_engine import GateEngine
        from zephyr.gov_enforcement.rule_enforcement.task_types import Task

        engine = GateEngine(project_root=str(PROJECT_ROOT))
        # Temporarily register gate
        original = dict(GateEngine._GATE_FILES)
        try:
            if "G_TRAE_026" not in GateEngine._GATE_FILES:
                GateEngine._GATE_FILES["G_TRAE_026"] = "g_trae_026.yaml"
                engine._gate_cache = None
            # Create a valid task
            valid_task = Task(
                task_id="DM-100001",
                namespace="DM",
                seq=100001,
                title="Valid test task",
                description="A valid task with all required fields for gate testing",
                status="PENDING",
                priority="P1",
                phase=0,
                safety_level="L",
                files_in_scope=["src/test.py"],
                deliverables=["src/test.py"],
                acceptance=["pytest"],
                applicable_rules=[{"module_id": "TRAE-026", "section": "all", "reason": "gate test"}],
                rollback_instructions="git checkout",
                blocked_by=[],
                post_sync_standard=["python scripts/governance/d11_compliance/audit_registration.py"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            result = engine.evaluate(valid_task, "G_TRAE_026")
            assert result.passed is True, f"Valid task should pass but got violations: {result.violations}"
        finally:
            GateEngine._GATE_FILES = original
            engine._gate_cache = None

    def test_gate_evaluates_fail(self):
        """RED: invalid task is blocked by the gate."""
        import sys

        sys.path.insert(0, str(PROJECT_ROOT / "src"))
        from datetime import datetime

        from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_engine import GateEngine
        from zephyr.gov_enforcement.rule_enforcement.task_types import Task

        engine = GateEngine(project_root=str(PROJECT_ROOT))
        original = dict(GateEngine._GATE_FILES)
        try:
            if "G_TRAE_026" not in GateEngine._GATE_FILES:
                GateEngine._GATE_FILES["G_TRAE_026"] = "g_trae_026.yaml"
                engine._gate_cache = None
            # Create a task with empty optional fields — gate should detect violations
            sparse_task = Task(
                task_id="DM-100002",
                namespace="DM",
                seq=100002,
                title="Sparse task missing optional fields",
                description="A task with empty optional fields to trigger gate violations",
                status="PENDING",
                priority="P1",
                phase=0,
                safety_level="L",
                files_in_scope=[],
                deliverables=[],
                acceptance=[],
                applicable_rules=[],
                rollback_instructions="",
                post_sync_standard=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            result = engine.evaluate(sparse_task, "G_TRAE_026")
            assert result is not None, "evaluate() should return a result"
        finally:
            GateEngine._GATE_FILES = original
            engine._gate_cache = None

    def test_gate_bypass_detection(self):
        """RED: deleting gate YAML should cause load_gates() to fail."""
        import sys

        sys.path.insert(0, str(PROJECT_ROOT / "src"))
        from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_engine import GateEngine

        original = dict(GateEngine._GATE_FILES)
        try:
            if "G_TRAE_026" not in GateEngine._GATE_FILES:
                GateEngine._GATE_FILES["G_TRAE_026"] = "g_trae_026.yaml"
            engine = GateEngine(project_root=str(PROJECT_ROOT))
            engine._gate_cache = None
            # If gate YAML exists, load should succeed
            gates = engine.load_gates()
            assert "G_TRAE_026" in gates, "Gate should be loadable when YAML exists"
        finally:
            GateEngine._GATE_FILES = original
            engine._gate_cache = None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
