# [A_test] module_id: SRC-TST-1989 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-606 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_code_dedup_engine
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""code-dedup-engine 核心模块单元测试 — Scanner, MonocultureGuard, AutoFixer."""


import tempfile
from pathlib import Path

import pytest

from zephyr.gov_code_quality.code_dedup.auto_fixer import (
    AutoFixer,
    FixLevel,
    FixParams,
    SafetyTier,
)
from zephyr.gov_code_quality.code_dedup.monoculture_guard import (
    BlastRadiusScore,
    MonocultureGuard,
)
from zephyr.infrastructure.asset_inventory.models import DuplicateGroup
from zephyr.infrastructure.asset_inventory.scanner import Scanner, ScanResult

_SAMPLE_PYTHON = """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

class Calculator:
    def multiply(self, x, y):
        return x * y
"""

_SAMPLE_DUPLICATE = """
def add(x, y):
    return x + y

def subtract(x, y):
    return x - y
"""

_SAMPLE_DIFFERENT = """
import json
import hashlib
from pathlib import Path

def load_config(path: Path) -> dict:
    return json.loads(path.read_text())
"""


class TestScanner:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.scanner = Scanner()

    def test_scan_file_empty(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write("")
            tmp = f.name
        try:
            result = self.scanner.scan_file(tmp)
            assert isinstance(result, ScanResult)
            assert result.token_count >= 0
        finally:
            Path(tmp).unlink(missing_ok=True)

    def test_scan_file_python(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write(_SAMPLE_PYTHON)
            tmp = f.name
        try:
            result = self.scanner.scan_file(tmp)
            assert isinstance(result, ScanResult)
            assert result.file == tmp
            assert result.token_count > 0
            assert len(result.minhash) == 8
        finally:
            Path(tmp).unlink(missing_ok=True)

    def test_scan_file_not_found(self):
        result = self.scanner.scan_file("/nonexistent/file.py")
        assert isinstance(result, ScanResult)
        assert result.token_count == 0

    def test_scan_files_batch(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write(_SAMPLE_PYTHON)
            f1 = f.name
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write(_SAMPLE_DIFFERENT)
            f2 = f.name
        try:
            results = self.scanner.scan_files([f1, f2])
            assert len(results) == 2
            assert all(isinstance(r, ScanResult) for r in results)
        finally:
            Path(f1).unlink(missing_ok=True)
            Path(f2).unlink(missing_ok=True)

    def test_find_duplicates_similar_files(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write(_SAMPLE_PYTHON)
            f1 = f.name
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write(_SAMPLE_DUPLICATE)
            f2 = f.name
        try:
            self.scanner.scan_file(f1)
            self.scanner.scan_file(f2)
            groups = self.scanner.find_duplicates()
            assert isinstance(groups, list)
        finally:
            Path(f1).unlink(missing_ok=True)
            Path(f2).unlink(missing_ok=True)

    def test_find_duplicates_dissimilar_files(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write(_SAMPLE_PYTHON)
            f1 = f.name
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write(_SAMPLE_DIFFERENT)
            f2 = f.name
        try:
            self.scanner.scan_file(f1)
            self.scanner.scan_file(f2)
            groups = self.scanner.find_duplicates()
            assert isinstance(groups, list)
        finally:
            Path(f1).unlink(missing_ok=True)
            Path(f2).unlink(missing_ok=True)

    def test_duplicate_group_structure(self):
        group = DuplicateGroup(
            group_id="DUP-001",
            members=[("a.py", ""), ("b.py", "")],
            similarity=0.95,
            detection_method="minhash_lsh",
            confidence=90.0,
        )
        assert group.group_id == "DUP-001"
        assert len(group.members) == 2
        assert group.similarity == 0.95
        assert group.detection_method == "minhash_lsh"

    def test_scan_blocks_sufficient_lines(self):
        blocks = self.scanner.scan_blocks(_SAMPLE_PYTHON)
        assert isinstance(blocks, list)

    def test_scan_blocks_insufficient_lines(self):
        blocks = self.scanner.scan_blocks("x = 1")
        assert blocks == []

    def test_token_normalize_preserves_keywords(self):
        tokens = self.scanner._tokenize_and_normalize("def add(a, b): return a + b")
        assert "def" in tokens
        assert "return" in tokens
        assert "_NAME_" in tokens

    def test_token_normalize_strips_comments(self):
        tokens = self.scanner._tokenize_and_normalize("# comment\nx = 1")
        assert "#" not in tokens

    def test_token_normalize_handles_strings(self):
        tokens = self.scanner._tokenize_and_normalize('s = "hello"')
        assert "_STR_" in tokens

    def test_compute_minhash_empty(self):
        minhash = self.scanner._compute_minhash([])
        assert minhash == [0] * 8

    def test_compute_minhash_nonempty(self):
        tokens = ["def", "_NAME_", "(", ")", ":", "return", "_NAME_"]
        minhash = self.scanner._compute_minhash(tokens)
        assert len(minhash) == 8
        assert any(x != 0 for x in minhash)

    def test_jaccard_identical(self):
        a = [1, 2, 3, 4, 5, 6, 7, 8]
        b = [1, 2, 3, 4, 5, 6, 7, 8]
        sim = self.scanner._jaccard_estimate(a, b)
        assert sim == 1.0

    def test_jaccard_different(self):
        a = [1, 2, 3, 4, 5, 6, 7, 8]
        b = [9, 10, 11, 12, 13, 14, 15, 16]
        sim = self.scanner._jaccard_estimate(a, b)
        assert sim == 0.0

    def test_jaccard_empty_input(self):
        assert self.scanner._jaccard_estimate([], [1, 2]) == 0.0
        assert self.scanner._jaccard_estimate([1, 2], []) == 0.0

    def test_path_threshold_shared(self):
        th = self.scanner._get_threshold("src/zephyr/shared/utils.py")
        assert th == 0.3

    def test_path_threshold_core(self):
        th = self.scanner._get_threshold("src/zephyr/core/models.py")
        assert th == 0.6

    def test_path_threshold_tests(self):
        th = self.scanner._get_threshold("tests/governance/test_thing.py")
        assert th == 0.9

    def test_path_threshold_scripts(self):
        th = self.scanner._get_threshold("scripts/governance/audit.py")
        assert th == 0.7

    def test_path_threshold_default(self):
        th = self.scanner._get_threshold("random/file.py")
        assert th == 0.7

    def test_scan_result_defaults(self):
        result = ScanResult(file="test.py")
        assert result.file == "test.py"
        assert result.matches == []
        assert result.minhash == []


class TestMonocultureGuard:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.guard = MonocultureGuard()

    def test_compute_brs_safe(self):
        brs = self.guard.compute_brs(
            caller_count=0, cross_layer_count=0, on_critical_path=False, has_independent_unit_test=True
        )
        assert brs.level == "SAFE"
        assert brs.blast_radius_score <= 25
        assert not self.guard.should_block_dedup(brs)

    def test_compute_brs_caution(self):
        brs = self.guard.compute_brs(
            caller_count=8, cross_layer_count=2, on_critical_path=False, has_independent_unit_test=False
        )
        assert brs.level == "CAUTION"
        assert 26 <= brs.blast_radius_score <= 50

    def test_compute_brs_risky(self):
        brs = self.guard.compute_brs(
            caller_count=14, cross_layer_count=4, on_critical_path=False, has_independent_unit_test=False
        )
        assert brs.level == "RISKY"
        assert 51 <= brs.blast_radius_score <= 75

    def test_compute_brs_dangerous(self):
        brs = self.guard.compute_brs(
            caller_count=25, cross_layer_count=10, on_critical_path=True, has_independent_unit_test=False
        )
        assert brs.level == "DANGEROUS"
        assert brs.blast_radius_score >= 76
        assert self.guard.should_block_dedup(brs)

    def test_brs_max_capped_at_100(self):
        brs = self.guard.compute_brs(
            caller_count=100, cross_layer_count=100, on_critical_path=True, has_independent_unit_test=False
        )
        assert brs.blast_radius_score <= 100

    def test_generate_report_dangerous(self):
        brs = self.guard.compute_brs(
            caller_count=25, cross_layer_count=10, on_critical_path=True, has_independent_unit_test=False
        )
        report = self.guard.generate_report("shared_func", brs)
        assert "Monoculture" in report
        assert "shared_func" in report
        assert "DANGEROUS" in report

    def test_generate_report_non_dangerous(self):
        brs = self.guard.compute_brs(caller_count=0, cross_layer_count=0)
        report = self.guard.generate_report("safe_func", brs)
        assert report == ""

    def test_save_risk_report(self):
        brs = self.guard.compute_brs(caller_count=25, cross_layer_count=10, on_critical_path=True)
        entries = [("func_a", brs)]
        out = Path(tempfile.gettempdir()) / "_test_monoculture_risk.yaml"
        try:
            self.guard.save_risk_report(entries, out)
            assert out.exists()
        finally:
            out.unlink(missing_ok=True)

    def test_blast_radius_score_fields(self):
        brs = BlastRadiusScore(
            caller_count=3, cross_layer_count=1, on_critical_path=True, has_independent_unit_test=False
        )
        assert brs.caller_count == 3
        assert brs.on_critical_path is True
        assert brs.has_independent_unit_test is False


class TestAutoFixer:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.fixer = AutoFixer()

    def test_can_fix_safe_case(self):
        assert self.fixer.can_fix(similarity=0.95, caller_count=3, blast_radius=30, is_grandfathered=False) is True

    def test_can_fix_too_many_callers(self):
        assert self.fixer.can_fix(similarity=0.95, caller_count=10, blast_radius=30, is_grandfathered=False) is False

    def test_can_fix_too_high_blast_radius(self):
        assert self.fixer.can_fix(similarity=0.95, caller_count=3, blast_radius=60, is_grandfathered=False) is False

    def test_can_fix_grandfathered(self):
        fixer = AutoFixer(params=FixParams(grandfather=True))
        assert fixer.can_fix(similarity=0.95, caller_count=3, blast_radius=30, is_grandfathered=True) is False

    def test_can_fix_grandfathered_disabled_in_params(self):
        assert self.fixer.can_fix(similarity=0.95, caller_count=3, blast_radius=30, is_grandfathered=True) is True

    def test_fix_success(self):
        result = self.fixer.fix(
            "src_a", "src_b", similarity=0.95, caller_count=3, blast_radius=30, is_grandfathered=False
        )
        assert result["fixed"] is True
        assert result["source"] == "src_a"
        assert self.fixer.fix_count == 1

    def test_fix_blocked(self):
        result = self.fixer.fix(
            "src_a", "src_b", similarity=0.95, caller_count=10, blast_radius=30, is_grandfathered=False
        )
        assert result["fixed"] is False
        assert result["reason"] == "safety_constraint_blocked"

    def test_safety_tier_enum(self):
        assert SafetyTier.ALWAYS == "always"
        assert SafetyTier.REVIEW == "review"
        assert SafetyTier.NEVER == "never"

    def test_fix_level_enum(self):
        assert FixLevel.TRIVIAL == "trivial"
        assert FixLevel.COMPLEX == "complex"

    def test_fix_params_defaults(self):
        params = FixParams()
        assert params.safety_tier == SafetyTier.ALWAYS
        assert params.caller_count == 7
        assert params.blast_radius == 50
        assert params.grandfather is False

    def test_autofixer_counter_increments(self):
        self.fixer.fix("a", "b", 0.95, 1, 10, False)
        self.fixer.fix("c", "d", 0.96, 2, 20, False)
        assert self.fixer.fix_count == 2
