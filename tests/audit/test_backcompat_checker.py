# [A_test] module_id: SRC-TST-0404 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_backcompat_checker
# [INVARIANTS] 向后兼容检查不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] CI;drift_engine
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_backcompat_checker.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_drift.backcompat_checker import (
    CompatBreakEvent,
    FunctionSignature,
    compare_signatures,
    detect_intentional_breaks,
    extract_signatures,
    find_renamed_functions,
    run_backcompat_check,
    scan_impact,
)


class TestCompatBreakEvent:
    def test_creates_with_defaults(self):
        evt = CompatBreakEvent(event_id="test-1")
        assert evt.event_id == "test-1"
        assert evt.severity == "CRITICAL"
        assert evt.intentional_break is False
        assert isinstance(evt.detected_at, object)

    def test_custom_fields(self):
        evt = CompatBreakEvent(event_id="t2", severity="MAJOR", description="desc")
        assert evt.severity == "MAJOR"
        assert evt.description == "desc"


class TestFunctionSignature:
    def test_creates_with_fields(self):
        sig = FunctionSignature(name="foo", params=["a", "b"], return_type="int", file_path="f.py", line_no=1)
        assert sig.name == "foo"
        assert len(sig.params) == 2
        assert sig.return_type == "int"

    def test_return_type_none(self):
        sig = FunctionSignature(name="bar", params=[], return_type=None, file_path="f.py", line_no=1)
        assert sig.return_type is None


class TestExtractSignatures:
    def test_extracts_from_valid_file(self, tmp_path):
        py_file = tmp_path / "mod.py"
        py_file.write_text("def public_func(a: int, b: str) -> bool:\n    return True\n", encoding="utf-8")
        sigs = extract_signatures(str(py_file))
        assert len(sigs) == 1
        assert sigs[0].name == "public_func"
        assert sigs[0].return_type == "bool"

    def test_skips_private_functions(self, tmp_path):
        py_file = tmp_path / "priv.py"
        py_file.write_text("def _private():\n    pass\n", encoding="utf-8")
        sigs = extract_signatures(str(py_file))
        assert len(sigs) == 0

    def test_handles_nonexistent_file(self):
        sigs = extract_signatures("/nonexistent/file.py")
        assert sigs == []

    def test_handles_no_return_type(self, tmp_path):
        py_file = tmp_path / "nort.py"
        py_file.write_text("def no_return(x):\n    pass\n", encoding="utf-8")
        sigs = extract_signatures(str(py_file))
        assert len(sigs) == 1
        assert sigs[0].return_type is None


class TestCompareSignatures:
    def test_detects_removed_function(self):
        baseline = [FunctionSignature(name="old_func", params=["a"], return_type=None, file_path="f.py", line_no=1)]
        current = []
        breaks = compare_signatures(baseline, current)
        assert any(b.event_id.startswith("compat-removed-func") for b in breaks)

    def test_detects_removed_parameter(self):
        baseline = [
            FunctionSignature(name="func", params=["a", "b", "c"], return_type=None, file_path="f.py", line_no=1)
        ]
        current = [FunctionSignature(name="func", params=["a", "b"], return_type=None, file_path="f.py", line_no=1)]
        breaks = compare_signatures(baseline, current)
        assert any("removed" in b.description.lower() and "parameter" in b.description.lower() for b in breaks)

    def test_detects_return_type_change(self):
        baseline = [FunctionSignature(name="func", params=["a"], return_type="int", file_path="f.py", line_no=1)]
        current = [FunctionSignature(name="func", params=["a"], return_type="str", file_path="f.py", line_no=1)]
        breaks = compare_signatures(baseline, current)
        assert any("return type" in b.description.lower() for b in breaks)

    def test_no_breaks_for_identical(self):
        sig = FunctionSignature(name="func", params=["a"], return_type="int", file_path="f.py", line_no=1)
        breaks = compare_signatures([sig], [sig])
        assert len(breaks) == 0

    def test_no_breaks_for_added_param(self):
        baseline = [FunctionSignature(name="func", params=["a"], return_type=None, file_path="f.py", line_no=1)]
        current = [FunctionSignature(name="func", params=["a", "b"], return_type=None, file_path="f.py", line_no=1)]
        breaks = compare_signatures(baseline, current)
        removed_param_breaks = [
            b for b in breaks if "removed" in b.description.lower() and "parameter" in b.description.lower()
        ]
        assert len(removed_param_breaks) == 0


class TestFindRenamedFunctions:
    def test_detects_renamed_with_high_jaccard(self):
        baseline = [FunctionSignature(name="process_data", params=[], return_type=None, file_path="f.py", line_no=1)]
        current = [FunctionSignature(name="process_datb", params=[], return_type=None, file_path="f.py", line_no=1)]
        breaks = find_renamed_functions(baseline, current, threshold=0.5)
        assert len(breaks) >= 1

    def test_no_rename_for_very_different_names(self):
        baseline = [FunctionSignature(name="abc", params=[], return_type=None, file_path="f.py", line_no=1)]
        current = [FunctionSignature(name="xyz", params=[], return_type=None, file_path="f.py", line_no=1)]
        breaks = find_renamed_functions(baseline, current, threshold=0.6)
        assert len(breaks) == 0

    def test_empty_inputs(self):
        assert find_renamed_functions([], []) == []


class TestScanImpact:
    def test_finds_callers(self, tmp_path):
        caller_file = tmp_path / "caller.py"
        caller_file.write_text("old_func()\n", encoding="utf-8")
        breaks = [CompatBreakEvent(event_id="compat-removed-func-old_func", source_file="", description="")]
        impact = scan_impact(breaks, str(tmp_path))
        assert "compat-removed-func-old_func" in impact

    def test_empty_breaks(self, tmp_path):
        impact = scan_impact([], str(tmp_path))
        assert impact == {}


class TestDetectIntentionalBreaks:
    def test_finds_intentional_marks(self, tmp_path):
        py_file = tmp_path / "marked.py"
        py_file.write_text("# INTENTIONAL_BREAK: removing deprecated API\n", encoding="utf-8")
        marks = detect_intentional_breaks(str(py_file))
        assert len(marks) >= 1

    def test_no_marks_in_clean_file(self, tmp_path):
        py_file = tmp_path / "clean.py"
        py_file.write_text("x = 1\n", encoding="utf-8")
        marks = detect_intentional_breaks(str(py_file))
        assert marks == []

    def test_handles_nonexistent_file(self):
        marks = detect_intentional_breaks("/nonexistent/file.py")
        assert marks == []


class TestRunBackcompatCheck:
    def test_returns_dict_structure(self, tmp_path):
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        py_file = src_dir / "mod.py"
        py_file.write_text("def func():\n    pass\n", encoding="utf-8")
        baseline_dir = tmp_path / "baselines"
        baseline_dir.mkdir()
        result = run_backcompat_check(str(tmp_path), str(baseline_dir))
        assert "breaks" in result
        assert "renamed" in result
        assert "impact" in result
