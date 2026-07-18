# [A_test] module_id: SRC-TST-1786 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §

# [MODULE] tests.test_verify_paths

# [INVARIANTS] verify_all returns dict with keys source_files/test_files/stats; stats keys are fixed

# [MODIFY-GUARD] none

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] verify_all never raises; returns dict

# [TESTS] this file
# [TTL] task_bound

import json
from pathlib import Path
from unittest.mock import patch

from zephyr.shared.utils.verify_paths import (
    CE_DIR,
    SOURCE_FILES,
    TEST_FILES,
    TESTS_DIR,
    verify_all,
)


class TestVerifyAllReturnStructure:
    def test_returns_dict_with_three_top_level_keys(self):
        result = verify_all()
        assert isinstance(result, dict)
        assert set(result.keys()) == {"source_files", "test_files", "stats"}

    def test_source_files_entries_have_required_keys(self):
        result = verify_all()
        for filename, info in result["source_files"].items():
            assert "expected" in info, f"missing 'expected' in {filename}"
            assert "exists" in info, f"missing 'exists' in {filename}"
            assert "size" in info, f"missing 'size' in {filename}"
            assert "category" in info, f"missing 'category' in {filename}"

    def test_test_files_entries_have_required_keys(self):
        result = verify_all()
        for test_path, info in result["test_files"].items():
            assert "type" in info, f"missing 'type' in {test_path}"
            assert "exists" in info, f"missing 'exists' in {test_path}"
            assert "ghost" in info, f"missing 'ghost' in {test_path}"

    def test_stats_has_required_keys(self):
        result = verify_all()
        stats = result["stats"]
        required = {
            "source_expected_exist",
            "source_expected_missing",
            "source_actually_exist",
            "tests_total",
            "tests_exist",
            "ghost_tests",
        }
        assert required.issubset(set(stats.keys())), f"missing keys: {required - set(stats.keys())}"


class TestVerifyAllCorrectness:
    def test_source_files_count_matches_constant(self):
        result = verify_all()
        assert len(result["source_files"]) == len(SOURCE_FILES)

    def test_test_files_count_matches_constant(self):
        result = verify_all()
        assert len(result["test_files"]) == len(TEST_FILES)

    def test_task_validator_is_expected_missing(self):
        result = verify_all()
        tv = result["source_files"].get("task_validator.py")
        assert tv is not None
        assert tv["expected"] == "❌"

    def test_non_task_validator_sources_expected_present(self):
        result = verify_all()
        for filename, info in result["source_files"].items():
            if filename != "task_validator.py":
                assert info["expected"] == "✅", f"{filename} expected ✅ but got {info['expected']}"

    def test_stats_source_expected_exist_excludes_task_validator(self):
        result = verify_all()
        expected = len(SOURCE_FILES) - 1
        assert result["stats"]["source_expected_exist"] == expected

    def test_stats_source_expected_missing_is_one(self):
        result = verify_all()
        assert result["stats"]["source_expected_missing"] == 1

    def test_stats_tests_total_matches_constant(self):
        result = verify_all()
        assert result["stats"]["tests_total"] == len(TEST_FILES)

    def test_ghost_tests_count(self):
        result = verify_all()
        expected_ghosts = sum(1 for t in TEST_FILES.values() if t == "ghost")
        assert result["stats"]["ghost_tests"] == expected_ghosts

    def test_existing_source_files_have_positive_size(self):
        result = verify_all()
        for filename, info in result["source_files"].items():
            if info["exists"]:
                assert info["size"] > 0, f"{filename} exists but size is 0"

    def test_missing_source_files_have_zero_size(self):
        result = verify_all()
        for filename, info in result["source_files"].items():
            if not info["exists"]:
                assert info["size"] == 0, f"{filename} missing but size is {info['size']}"

    def test_ghost_flag_matches_type(self):
        result = verify_all()
        for test_path, info in result["test_files"].items():
            assert info["ghost"] == (info["type"] == "ghost"), f"ghost mismatch for {test_path}"

    def test_source_actually_exist_is_non_negative(self):
        result = verify_all()
        assert result["stats"]["source_actually_exist"] >= 0

    def test_tests_exist_is_non_negative(self):
        result = verify_all()
        assert result["stats"]["tests_exist"] >= 0

    def test_tests_exist_leq_tests_total(self):
        result = verify_all()
        assert result["stats"]["tests_exist"] <= result["stats"]["tests_total"]


class TestVerifyAllBoundaryConditions:
    def test_empty_source_files(self):
        with patch("zephyr.shared.utils.verify_paths.SOURCE_FILES", {}):
            result = verify_all()
            assert result["source_files"] == {}
            assert result["stats"]["source_expected_exist"] == 0
            assert result["stats"]["source_expected_missing"] == 0
            assert result["stats"]["source_actually_exist"] == 0

    def test_empty_test_files(self):
        with patch("zephyr.shared.utils.verify_paths.TEST_FILES", {}):
            result = verify_all()
            assert result["test_files"] == {}
            assert result["stats"]["tests_total"] == 0
            assert result["stats"]["tests_exist"] == 0
            assert result["stats"]["ghost_tests"] == 0

    def test_both_dicts_empty(self):
        with (
            patch("zephyr.shared.utils.verify_paths.SOURCE_FILES", {}),
            patch("zephyr.shared.utils.verify_paths.TEST_FILES", {}),
        ):
            result = verify_all()
            assert result["source_files"] == {}
            assert result["test_files"] == {}
            assert result["stats"]["source_expected_exist"] == 0
            assert result["stats"]["source_expected_missing"] == 0
            assert result["stats"]["source_actually_exist"] == 0
            assert result["stats"]["tests_total"] == 0
            assert result["stats"]["tests_exist"] == 0
            assert result["stats"]["ghost_tests"] == 0

    def test_nonexistent_source_file_has_zero_size(self):
        fake_files = {"nonexistent_module.py": "source"}
        with patch("zephyr.shared.utils.verify_paths.SOURCE_FILES", fake_files):
            result = verify_all()
            info = result["source_files"]["nonexistent_module.py"]
            assert info["exists"] is False
            assert info["size"] == 0

    def test_nonexistent_test_file_exists_is_false(self):
        fake_tests = {"unit/context-engine/test_fake.py": "test"}
        with patch("zephyr.shared.utils.verify_paths.TEST_FILES", fake_tests):
            result = verify_all()
            info = result["test_files"]["unit/context-engine/test_fake.py"]
            assert info["exists"] is False


class TestModuleConstants:
    def test_ce_dir_is_path(self):
        assert isinstance(CE_DIR, Path)

    def test_tests_dir_is_path(self):
        assert isinstance(TESTS_DIR, Path)

    def test_ce_dir_exists(self):
        assert CE_DIR.exists()

    def test_source_files_is_dict(self):
        assert isinstance(SOURCE_FILES, dict)

    def test_test_files_is_dict(self):
        assert isinstance(TEST_FILES, dict)

    def test_source_files_values_in_valid_set(self):
        valid = {"source", "data"}
        for v in SOURCE_FILES.values():
            assert v in valid, f"invalid source category: {v}"

    def test_test_files_values_in_valid_set(self):
        valid = {"test", "ghost"}
        for v in TEST_FILES.values():
            assert v in valid, f"invalid test type: {v}"


class TestVerifyAllDiscrepancyField:
    def test_task_validator_missing_has_discrepancy(self):
        result = verify_all()
        tv = result["source_files"].get("task_validator.py")
        if tv is not None and not tv["exists"]:
            assert "discrepancy" in tv

    def test_existing_source_files_no_discrepancy_key(self):
        result = verify_all()
        for filename, info in result["source_files"].items():
            if info["exists"] and filename != "task_validator.py":
                assert "discrepancy" not in info, f"unexpected discrepancy for {filename}"


class TestVerifyAllJsonSerializable:
    def test_result_is_json_serializable(self):
        result = verify_all()
        serialized = json.dumps(result, ensure_ascii=False)
        assert isinstance(serialized, str)
        deserialized = json.loads(serialized)
        assert deserialized["stats"]["tests_total"] == result["stats"]["tests_total"]
