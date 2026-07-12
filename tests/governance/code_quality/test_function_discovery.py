# [A_test] module_id: SRC-TST-1037 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_function_discovery
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_function_discovery.py
# [TTL] task_bound

from __future__ import annotations

import tempfile
from pathlib import Path

from zephyr.gov_code_quality.code_dedup.function_discovery import FunctionDiscovery


class TestFunctionDiscovery:
    def test_instantiation(self):
        fd = FunctionDiscovery()
        assert fd is not None

    def test_scan_codebase_empty_dir(self):
        fd = FunctionDiscovery()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = fd.scan_codebase(tmpdir, known_shared=set())
            assert result == []

    def test_scan_codebase_with_duplicates(self):
        fd = FunctionDiscovery()
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ["a", "b"]:
                path = Path(tmpdir) / f"{name}.py"
                path.write_text("def common_helper():\n    return 42\n", encoding="utf-8")
            result = fd.scan_codebase(tmpdir, known_shared=set())
            assert len(result) > 0
            assert result[0]["name"] == "common_helper"
            assert result[0]["occurrences"] == 2

    def test_scan_codebase_filters_private(self):
        fd = FunctionDiscovery()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "mod.py"
            path.write_text("def _private():\n    pass\n\ndef public():\n    pass\n", encoding="utf-8")
            result = fd.scan_codebase(tmpdir, known_shared=set())
            names = [c["name"] for c in result]
            assert "_private" not in names

    def test_scan_codebase_filters_known_shared(self):
        fd = FunctionDiscovery()
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ["a", "b"]:
                path = Path(tmpdir) / f"{name}.py"
                path.write_text("def known_func():\n    pass\n", encoding="utf-8")
            result = fd.scan_codebase(tmpdir, known_shared={"known_func"})
            names = [c["name"] for c in result]
            assert "known_func" not in names

    def test_scan_codebase_recommendation_suggest_shared(self):
        fd = FunctionDiscovery()
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ["a", "b", "c"]:
                path = Path(tmpdir) / f"{name}.py"
                path.write_text("def popular_func():\n    pass\n", encoding="utf-8")
            result = fd.scan_codebase(tmpdir, known_shared=set())
            popular = [c for c in result if c["name"] == "popular_func"]
            assert len(popular) == 1
            assert popular[0]["recommendation"] == "SUGGEST_SHARED"

    def test_scan_codebase_recommendation_monitor(self):
        fd = FunctionDiscovery()
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ["a", "b"]:
                path = Path(tmpdir) / f"{name}.py"
                path.write_text("def two_time_func():\n    pass\n", encoding="utf-8")
            result = fd.scan_codebase(tmpdir, known_shared=set())
            two_time = [c for c in result if c["name"] == "two_time_func"]
            assert len(two_time) == 1
            assert two_time[0]["recommendation"] == "MONITOR"

    def test_scan_codebase_max_20_results(self):
        fd = FunctionDiscovery()
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(25):
                for name in ["a", "b"]:
                    path = Path(tmpdir) / f"{name}_{i}.py"
                    path.write_text(f"def func_{i}():\n    pass\n", encoding="utf-8")
            result = fd.scan_codebase(tmpdir, known_shared=set())
            assert len(result) <= 20

    def test_scan_codebase_sorted_by_occurrences(self):
        fd = FunctionDiscovery()
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ["a", "b", "c"]:
                path = Path(tmpdir) / f"{name}_rare.py"
                path.write_text("def rare_func():\n    pass\n", encoding="utf-8")
            for name in ["a", "b"]:
                path = Path(tmpdir) / f"{name}_common.py"
                path.write_text("def common_func():\n    pass\n", encoding="utf-8")
            result = fd.scan_codebase(tmpdir, known_shared=set())
            if len(result) >= 2:
                assert result[0]["occurrences"] >= result[1]["occurrences"]

    def test_scan_codebase_syntax_error_file(self):
        fd = FunctionDiscovery()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "broken.py"
            path.write_text("def broken(:\n", encoding="utf-8")
            result = fd.scan_codebase(tmpdir, known_shared=set())
            assert isinstance(result, list)

    def test_scan_codebase_nonexistent_root(self):
        fd = FunctionDiscovery()
        result = fd.scan_codebase("/nonexistent/path", known_shared=set())
        assert result == []

    def test_scan_codebase_files_limited_to_5(self):
        fd = FunctionDiscovery()
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(7):
                path = Path(tmpdir) / f"mod_{i}.py"
                path.write_text("def multi_func():\n    pass\n", encoding="utf-8")
            result = fd.scan_codebase(tmpdir, known_shared=set())
            multi = [c for c in result if c["name"] == "multi_func"]
            if multi:
                assert len(multi[0]["files"]) <= 5
