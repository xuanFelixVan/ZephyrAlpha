# [A_test] module_id: SRC-TST-1118 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_incremental_scanner
# [INVARIANTS] 增量扫描不可遗漏变更
# [MODIFY-GUARD] src/zephyr/behavioral-auditor/incremental_scanner.py
# [CONSUMERS] CI pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip
# [TESTS] python -m pytest tests/test_incremental_scanner.py -q
# [TTL] task_bound

from __future__ import annotations

import hashlib

from zephyr.gov_drift.incremental_scanner import (
    ChangeSet,
    DetectorFileMapping,
    FileChange,
    IncrementalScanner,
)


class TestFileChange:
    def test_creation(self):
        fc = FileChange(path="src/zephyr/mod_a/file.py", status="M")
        assert fc.path == "src/zephyr/mod_a/file.py"
        assert fc.status == "M"
        assert fc.sha256 == ""

    def test_with_hash(self):
        fc = FileChange(path="a.py", status="A", sha256="abc123")
        assert fc.sha256 == "abc123"


class TestChangeSet:
    def test_defaults(self):
        cs = ChangeSet()
        assert cs.changed_files == []
        assert cs.affected_detectors == []
        assert cs.affected_modules == []
        assert cs.is_storm is False
        assert cs.total_changes == 0

    def test_with_data(self):
        fc = FileChange(path="a.py", status="M")
        cs = ChangeSet(changed_files=[fc], total_changes=1, is_storm=False)
        assert len(cs.changed_files) == 1
        assert cs.total_changes == 1


class TestDetectorFileMapping:
    def test_register_and_find(self):
        m = DetectorFileMapping()
        m.register("det_a", "*.py")
        result = m.find_detectors(["src/zephyr/mod.py"])
        assert "det_a" in result

    def test_find_no_match(self):
        m = DetectorFileMapping()
        m.register("det_a", "*.yaml")
        result = m.find_detectors(["src/zephyr/mod.py"])
        assert result == []

    def test_multiple_detectors_same_pattern(self):
        m = DetectorFileMapping()
        m.register("det_a", "*.py")
        m.register("det_b", "*.py")
        result = m.find_detectors(["test.py"])
        assert "det_a" in result
        assert "det_b" in result

    def test_empty_input(self):
        m = DetectorFileMapping()
        result = m.find_detectors([])
        assert result == []

    def test_pattern_substring_match(self):
        m = DetectorFileMapping()
        m.register("det_x", "config.yaml")
        result = m.find_detectors(["src/config.yaml"])
        assert "det_x" in result


class TestIncrementalScanner:
    def test_init_default_root(self):
        scanner = IncrementalScanner()
        assert scanner._project_root is not None

    def test_init_custom_root(self, tmp_path):
        scanner = IncrementalScanner(project_root=str(tmp_path))
        assert scanner._project_root == str(tmp_path)

    def test_extract_module_src(self):
        scanner = IncrementalScanner()
        result = scanner._extract_module("src/zephyr/governance/check.py")
        assert result == "governance"

    def test_extract_module_docs(self):
        scanner = IncrementalScanner()
        result = scanner._extract_module("docs/03_modules/_domain-infra_ops/file.md")
        assert result == "l01-infrastructure"

    def test_extract_module_unknown(self):
        scanner = IncrementalScanner()
        result = scanner._extract_module("scripts/run.py")
        assert result == "unknown"

    def test_extract_module_short_path(self):
        scanner = IncrementalScanner()
        result = scanner._extract_module("src/zephyr/")
        assert result == ""

    def test_register_mapping(self):
        scanner = IncrementalScanner()
        scanner.register_mapping("det_a", ["*.py", "*.yaml"])
        result = scanner._mapping.find_detectors(["test.py"])
        assert "det_a" in result

    def test_file_hash_existing(self, tmp_path):
        test_file = tmp_path / "sample.txt"
        test_file.write_text("hello world", encoding="utf-8")
        scanner = IncrementalScanner(project_root=str(tmp_path))
        result = scanner.file_hash("sample.txt")
        expected = hashlib.sha256(b"hello world").hexdigest()
        assert result == expected

    def test_file_hash_nonexistent(self, tmp_path):
        scanner = IncrementalScanner(project_root=str(tmp_path))
        result = scanner.file_hash("nonexistent.txt")
        assert result == ""

    def test_get_changed_files_no_git(self, tmp_path):
        scanner = IncrementalScanner(project_root=str(tmp_path))
        result = scanner.get_changed_files()
        assert isinstance(result, list)

    def test_compute_impact_no_git(self, tmp_path):
        scanner = IncrementalScanner(project_root=str(tmp_path))
        cs = scanner.compute_impact()
        assert isinstance(cs, ChangeSet)
