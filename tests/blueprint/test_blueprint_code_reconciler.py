# [A_test] module_id: SRC-TST-0433 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_blueprint_code_reconciler
# [INVARIANTS] Scan must return DriftReport list; autofix must return dict
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

import os
import tempfile

from zephyr.feedback_loop.gates.blueprint_code_reconciler import BlueprintCodeReconciler, DriftReport


class TestDriftReport:
    def test_creation(self):
        dr = DriftReport(file="test.py", blueprint_version="0.14.0", code_version="0.10.0", drifted=True)
        assert dr.file == "test.py"
        assert dr.drifted is True


class TestBlueprintCodeReconcilerInstantiation:
    def test_default_values(self):
        bcr = BlueprintCodeReconciler()
        assert bcr.reports == []
        assert bcr.scan_interval_hours == 24.0


class TestScan:
    def test_scan_nonexistent_dir(self):
        bcr = BlueprintCodeReconciler()
        results = bcr.scan("/nonexistent/path", "/nonexistent/code")
        assert results == []

    def test_scan_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bcr = BlueprintCodeReconciler()
            results = bcr.scan(tmpdir, tmpdir)
            assert results == []

    def test_scan_with_py_files(self):
        with tempfile.TemporaryDirectory() as bp_dir:
            with open(os.path.join(bp_dir, "module.py"), "w", encoding="utf-8") as f:
                f.write("x = 1")
            bcr = BlueprintCodeReconciler()
            results = bcr.scan(bp_dir, bp_dir)
            assert len(results) == 1
            assert results[0].file == "module.py"
            assert results[0].drifted is False

    def test_scan_ignores_non_py_files(self):
        with tempfile.TemporaryDirectory() as bp_dir:
            with open(os.path.join(bp_dir, "readme.md"), "w", encoding="utf-8") as f:
                f.write("doc")
            bcr = BlueprintCodeReconciler()
            results = bcr.scan(bp_dir, bp_dir)
            assert results == []

    def test_scan_appends_to_reports(self):
        with tempfile.TemporaryDirectory() as bp_dir:
            with open(os.path.join(bp_dir, "a.py"), "w", encoding="utf-8") as f:
                f.write("a = 1")
            bcr = BlueprintCodeReconciler()
            bcr.scan(bp_dir, bp_dir)
            assert len(bcr.reports) == 1


class TestAutofixPr:
    def test_autofix_returns_dict(self):
        bcr = BlueprintCodeReconciler()
        result = bcr.autofix_pr(["file1.py", "file2.py"])
        assert isinstance(result, dict)
        assert len(result) == 2

    def test_autofix_empty_list(self):
        bcr = BlueprintCodeReconciler()
        result = bcr.autofix_pr([])
        assert result == {}

    def test_autofix_message_format(self):
        bcr = BlueprintCodeReconciler()
        result = bcr.autofix_pr(["drifted.py"])
        assert "drifted.py" in result
        assert "auto-PR" in result["drifted.py"]
