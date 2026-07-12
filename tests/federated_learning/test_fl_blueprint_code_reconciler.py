# [A_test] module_id: SRC-TST-0937 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_blueprint_code_reconciler
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.blueprint_code_reconciler
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_blueprint_code_reconciler.py
# [TTL] task_bound

import os
import tempfile

from zephyr.feedback_loop.gates.blueprint_code_reconciler import BlueprintCodeReconciler, DriftReport


class TestBlueprintCodeReconcilerInstantiation:
    def test_default_construction(self):
        bcr = BlueprintCodeReconciler()
        assert bcr.reports == []
        assert bcr.scan_interval_hours == 24.0


class TestScan:
    def test_scan_empty_dir(self):
        bcr = BlueprintCodeReconciler()
        with tempfile.TemporaryDirectory() as td:
            results = bcr.scan(td, td)
            assert results == []

    def test_scan_nonexistent_dir(self):
        bcr = BlueprintCodeReconciler()
        results = bcr.scan("/nonexistent/path/abc", "/nonexistent/path/def")
        assert results == []

    def test_scan_with_py_files(self):
        bcr = BlueprintCodeReconciler()
        with tempfile.TemporaryDirectory() as td:
            for name in ("module_a.py", "module_b.py"):
                with open(os.path.join(td, name), "w", encoding="utf-8") as f:
                    f.write("pass\n")
            results = bcr.scan(td, td)
            assert len(results) == 2
            assert all(isinstance(r, DriftReport) for r in results)
            assert all(r.drifted is False for r in results)

    def test_scan_accumulates_reports(self):
        bcr = BlueprintCodeReconciler()
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "x.py"), "w", encoding="utf-8") as f:
                f.write("pass\n")
            bcr.scan(td, td)
            bcr.scan(td, td)
            assert len(bcr.reports) == 2


class TestAutofixPr:
    def test_autofix_pr_returns_mapping(self):
        bcr = BlueprintCodeReconciler()
        result = bcr.autofix_pr(["file_a.py", "file_b.py"])
        assert isinstance(result, dict)
        assert len(result) == 2
        assert "file_a.py" in result

    def test_autofix_pr_empty_list(self):
        bcr = BlueprintCodeReconciler()
        result = bcr.autofix_pr([])
        assert result == {}
