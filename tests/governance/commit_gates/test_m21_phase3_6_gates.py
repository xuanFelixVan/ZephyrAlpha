"""Smoke tests for Phase 3.6 第1期 AST 门禁 (3 new gates).

验证 3 个新 gate 的检测逻辑能正确识别违规模式：
- SNAPSHOT-DRIFT (rc1): 快照文件结构/新鲜度/SHA 校验
- VOCAB-CHAIN (rc2): SSoT 路径硬编码检测
- MANUAL-ONLY-PERMANENT (rc4): permanent 脚本 manual 触发无事件订阅检测

#ARCH-GOV-CONVERGENCE-META Phase 3.6
"""
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

import ast

from zephyr.gov_enforcement.commit_gates.manual_only_permanent_gate import (
    _detect_event_or_auto_trigger,
    _detect_manual_trigger,
    _has_permanent_ttl,
    make_manual_only_permanent_gate,
)
from zephyr.gov_enforcement.commit_gates.snapshot_drift_gate import (
    _validate_commit_sha,
    _validate_generated_at_freshness,
    _validate_snapshot_structure,
    make_snapshot_drift_gate,
)
from zephyr.gov_enforcement.commit_gates.vocab_chain_gate import (
    _detect_ssot_hardcoding,
    _matches_ssot_pattern,
    make_vocab_chain_gate,
)

# ── SNAPSHOT-DRIFT gate tests ──────────────────────────────────────────────

class TestSnapshotDriftGate:
    def test_validate_structure_valid(self):
        data = {"generated_at": "2026-07-19T10:00:00Z", "commit_sha": "abc123", "violations": []}
        assert _validate_snapshot_structure(data) == []

    def test_validate_structure_missing_field(self):
        data = {"generated_at": "2026-07-19T10:00:00Z", "commit_sha": "abc123"}
        errors = _validate_snapshot_structure(data)
        assert any("violations" in e for e in errors)

    def test_validate_structure_not_dict(self):
        errors = _validate_snapshot_structure([1, 2, 3])
        assert any("not a JSON object" in e for e in errors)

    def test_generated_at_freshness_valid(self):
        recent = datetime.now(timezone.utc).isoformat()
        assert _validate_generated_at_freshness(recent) == ""

    def test_generated_at_freshness_stale(self):
        old = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
        err = _validate_generated_at_freshness(old)
        assert "stale" in err

    def test_generated_at_freshness_invalid_format(self):
        err = _validate_generated_at_freshness("not-a-timestamp")
        assert "invalid ISO timestamp" in err

    def test_commit_sha_match(self):
        assert _validate_commit_sha("abc123def456", "abc123def456789") == ""

    def test_commit_sha_mismatch(self):
        err = _validate_commit_sha("abc123", "def789")
        assert "drift" in err

    def test_commit_sha_none_head(self):
        # head_sha=None → fail-open (skip check)
        assert _validate_commit_sha("anything", None) == ""

    def test_gate_returns_pass_when_snapshot_not_staged(self):
        """快照未 staged 时 gate 通过。"""
        gw = MagicMock()
        diff_result = MagicMock()
        diff_result.returncode = 0
        diff_result.stdout = "src/some_file.py\n"
        gw.run_git.return_value = diff_result
        gw.project_root = REPO_ROOT

        gate = make_snapshot_drift_gate()
        passed, msg = gate.check(gw, [])
        assert passed is True


# ── VOCAB-CHAIN gate tests ─────────────────────────────────────────────────

class TestVocabChainGate:
    def test_matches_ssot_pattern_yaml(self):
        assert _matches_ssot_pattern("docs/01_policies_and_standards/rules/trae_001.yaml")
        assert _matches_ssot_pattern("docs/02_enterprise_architecture/governance_convergence_map.yaml")

    def test_matches_ssot_pattern_json(self):
        assert _matches_ssot_pattern("data/runtime_violation_snapshot/latest.json")
        assert _matches_ssot_pattern("data/telemetry/blueprint_reads.jsonl")

    def test_does_not_match_non_ssot(self):
        assert not _matches_ssot_pattern("src/zephyr/foo.py")
        assert not _matches_ssot_pattern("not a path")
        assert not _matches_ssot_pattern("docs/random.txt")

    def test_detect_ssot_hardcoding_finds_violation(self):
        code = '''
PATH = "docs/01_policies_and_standards/rules/trae_001.yaml"
OTHER = "regular string"
'''
        violations = _detect_ssot_hardcoding("<test>", code)
        assert any("trae_001.yaml" in v for v in violations)

    def test_detect_ssot_hardcoding_clean(self):
        code = 'PATH = "src/zephyr/foo.py"\n'
        assert _detect_ssot_hardcoding("<test>", code) == []

    def test_gate_passes_when_no_staged_files(self):
        gw = MagicMock()
        diff_result = MagicMock()
        diff_result.returncode = 0
        diff_result.stdout = ""
        gw.run_git.return_value = diff_result
        gw.project_root = REPO_ROOT

        gate = make_vocab_chain_gate()
        passed, msg = gate.check(gw, [])
        assert passed is True


# ── MANUAL-ONLY-PERMANENT gate tests ───────────────────────────────────────

class TestManualOnlyPermanentGate:
    def test_has_permanent_ttl(self):
        content = "# [TTL] permanent\n# rest of file\n"
        assert _has_permanent_ttl(content) is True

    def test_no_permanent_ttl(self):
        content = "# [TTL] provisional\n# rest of file\n"
        assert _has_permanent_ttl(content) is False

    def test_detect_argparse_trigger(self):
        tree = ast.parse("import argparse\nparser = argparse.ArgumentParser()")
        assert _detect_manual_trigger(tree) is True

    def test_detect_input_trigger(self):
        tree = ast.parse("x = input('Enter: ')")
        assert _detect_manual_trigger(tree) is True

    def test_detect_main_guard_with_argv(self):
        code = '''
import sys
if __name__ == "__main__":
    cmd = sys.argv[1]
'''
        tree = ast.parse(code)
        assert _detect_manual_trigger(tree) is True

    def test_no_manual_trigger(self):
        tree = ast.parse("x = 1 + 2\n")
        assert _detect_manual_trigger(tree) is False

    def test_detect_event_subscription(self):
        code = "event_bus.subscribe('topic', handler)"
        tree = ast.parse(code)
        assert _detect_event_or_auto_trigger(tree) is True

    def test_detect_auto_trigger_registration(self):
        code = "registry.register_reconciler('my_reconciler')"
        tree = ast.parse(code)
        assert _detect_event_or_auto_trigger(tree) is True

    def test_no_event_subscription(self):
        tree = ast.parse("x = 1 + 2\n")
        assert _detect_event_or_auto_trigger(tree) is False

    def test_gate_passes_when_no_staged_files(self):
        gw = MagicMock()
        diff_result = MagicMock()
        diff_result.returncode = 0
        diff_result.stdout = ""
        gw.run_git.return_value = diff_result
        gw.project_root = REPO_ROOT

        gate = make_manual_only_permanent_gate()
        passed, msg = gate.check(gw, [])
        assert passed is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
