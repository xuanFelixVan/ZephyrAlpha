# [A_test] module_id: MOD-GOV_rule_execution_pairing_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_RULE_EXECUTION_PAIRING_GATE | docs/03_modules/_domain_governance/blueprint.md | §rule-execution-pairing-gate
# [MODULE] tests.governance.commit_gates.test_rule_execution_pairing_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [A_module] module_id=MOD-GOV_RULE_EXECUTION_PAIRING_GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""Tests for RULE-EXECUTION-PAIRING gate (Phase 3.5)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zephyr.gov_enforcement.commit_gates.rule_execution_pairing_gate import (
    _check_paired_gate_id,
    make_rule_execution_pairing_gate,
)


class TestCheckPairedGateId:
    def test_null_allowed(self):
        ok, _ = _check_paired_gate_id(None, {"GATE-1"})
        assert ok

    def test_valid_string(self):
        ok, _ = _check_paired_gate_id("GATE-1", {"GATE-1"})
        assert ok

    def test_invalid_string(self):
        ok, detail = _check_paired_gate_id("NOT-A-GATE", {"GATE-1"})
        assert not ok
        assert "NOT-A-GATE" in detail

    def test_valid_list(self):
        ok, _ = _check_paired_gate_id(["GATE-1", "GATE-2"], {"GATE-1", "GATE-2"})
        assert ok

    def test_invalid_list_element(self):
        ok, detail = _check_paired_gate_id(["GATE-1", "BAD"], {"GATE-1"})
        assert not ok
        assert "BAD" in detail

    def test_empty_list_allowed(self):
        ok, _ = _check_paired_gate_id([], {"GATE-1"})
        assert ok

    def test_none_known_ids_failopen(self):
        ok, _ = _check_paired_gate_id("ANYTHING", None)
        assert ok

    def test_invalid_type(self):
        ok, detail = _check_paired_gate_id(123, {"GATE-1"})
        assert not ok
        assert "int" in detail


class TestGateSpec:
    def test_gate_id(self):
        spec = make_rule_execution_pairing_gate()
        assert spec.gate_id == "RULE-EXECUTION-PAIRING"

    def test_priority(self):
        spec = make_rule_execution_pairing_gate()
        assert spec.priority == 61  # priority=61 在 CREATE-GUARD(60) 之后，避免冲突

    def test_check_callable(self):
        spec = make_rule_execution_pairing_gate()
        assert callable(spec.check)


class TestCheckBehavior:
    def _make_gateway(self, tmp_path: Path):
        gw = MagicMock()
        gw.project_root = tmp_path
        return gw

    def test_no_trae_files_passes(self, tmp_path):
        gw = self._make_gateway(tmp_path)
        spec = make_rule_execution_pairing_gate()
        ok, _ = spec.check(gw, ["src/some_file.py"], commit_message="")
        assert ok

    def test_escape_hatch(self, tmp_path):
        gw = self._make_gateway(tmp_path)
        spec = make_rule_execution_pairing_gate()
        ok, _ = spec.check(
            gw,
            [],
            commit_message="test [no-pairing:emergency-fix]",
        )
        assert ok

    def test_rule_mod_tag_without_files_passes(self, tmp_path):
        gw = self._make_gateway(tmp_path)
        spec = make_rule_execution_pairing_gate()
        ok, _ = spec.check(gw, [], commit_message="test [rule-mod]")
        assert ok
