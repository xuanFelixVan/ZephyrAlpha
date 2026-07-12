# [A_test] module_id: SRC-TST-0413 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §baseline_manager
# [MODULE] tests.test_baseline_manager
# [INVARIANTS] BaselineManager.capture必须写入版本化JSON; full_diff必须返回DiffReport
# [MODIFY-GUARD] 仅当baseline_manager公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_baseline_manager.py -q
# [TTL] task_bound

import os

from zephyr.gov_drift.baseline_manager import BaselineManager, DiffReport


class TestDiffReport:
    def test_default_construction(self):
        report = DiffReport(baseline_version="v1", module_id="MOD-001", diff_type="full_diff")
        assert report.baseline_version == "v1"
        assert report.module_id == "MOD-001"
        assert report.diff_type == "full_diff"
        assert report.added == []
        assert report.removed == []
        assert report.modified == []
        assert report.contract_changes == []
        assert report.cumulative_creep_score == 0.0
        assert report.detail == {}


class TestBaselineManager:
    def test_instantiation(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        assert mgr is not None
        assert os.path.isdir(mgr._baselines_root)

    def test_module_baseline_dir(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        d = mgr.module_baseline_dir("MOD-INF-001")
        assert "MOD-INF-001" in d

    def test_snapshot_tree_hash_empty_dir(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        empty = tmp_path / "empty_mod"
        empty.mkdir()
        result = mgr.snapshot_tree_hash(str(empty))
        assert result == {}

    def test_snapshot_tree_hash_with_files(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        mod = tmp_path / "mod_dir"
        mod.mkdir()
        (mod / "test.py").write_text("x = 1", encoding="utf-8")
        result = mgr.snapshot_tree_hash(str(mod))
        assert "test.py" in result
        assert len(result["test.py"]) == 64

    def test_snapshot_tree_hash_nonexistent_dir(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        result = mgr.snapshot_tree_hash("/nonexistent/dir")
        assert result == {}

    def test_snapshot_interface(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        mod = tmp_path / "iface_mod"
        mod.mkdir()
        (mod / "sample.py").write_text(
            "class MyClass:\n    def method(self, x):\n        pass\n\ndef standalone(y):\n    pass\n",
            encoding="utf-8",
        )
        result = mgr.snapshot_interface(str(mod))
        assert "sample.py" in result
        sigs = result["sample.py"]
        assert any("class MyClass" in s for s in sigs)
        assert any("def method" in s for s in sigs)
        assert any("def standalone" in s for s in sigs)

    def test_snapshot_interface_syntax_error(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        mod = tmp_path / "bad_mod"
        mod.mkdir()
        (mod / "bad.py").write_text("def broken(", encoding="utf-8")
        result = mgr.snapshot_interface(str(mod))
        assert isinstance(result, dict)

    def test_snapshot_import_graph(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        mod = tmp_path / "import_mod"
        mod.mkdir()
        (mod / "imports.py").write_text(
            "import os\nimport json\nfrom pathlib import Path\n",
            encoding="utf-8",
        )
        result = mgr.snapshot_import_graph(str(mod))
        assert "imports.py" in result
        assert "os" in result["imports.py"]
        assert "pathlib" in result["imports.py"]

    def test_snapshot_config_yaml(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        mod = tmp_path / "cfg_mod"
        mod.mkdir()
        (mod / "config.yaml").write_text("key: value\n", encoding="utf-8")
        result = mgr.snapshot_config(str(mod))
        assert "config.yaml" in result
        assert result["config.yaml"]["key"] == "value"

    def test_snapshot_config_json(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        mod = tmp_path / "json_mod"
        mod.mkdir()
        (mod / "data.json").write_text('{"x": 1}', encoding="utf-8")
        result = mgr.snapshot_config(str(mod))
        assert "data.json" in result
        assert result["data.json"]["x"] == 1

    def test_capture(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        mod = tmp_path / "cap_mod"
        mod.mkdir()
        (mod / "mod.py").write_text("x = 1\n", encoding="utf-8")
        snapshot = mgr.capture("MOD-CAP", str(mod))
        assert snapshot["module_id"] == "MOD-CAP"
        assert snapshot["version"] == 1
        assert "tree_hash" in snapshot
        assert "interface_snapshot" in snapshot
        assert "captured_at" in snapshot

    def test_capture_increments_version(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        mod = tmp_path / "ver_mod"
        mod.mkdir()
        (mod / "mod.py").write_text("x = 1\n", encoding="utf-8")
        s1 = mgr.capture("MOD-VER", str(mod))
        s2 = mgr.capture("MOD-VER", str(mod))
        assert s1["version"] == 1
        assert s2["version"] == 2

    def test_load_baseline(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        mod = tmp_path / "load_mod"
        mod.mkdir()
        (mod / "mod.py").write_text("x = 1\n", encoding="utf-8")
        mgr.capture("MOD-LOAD", str(mod))
        loaded = mgr.load_baseline("MOD-LOAD", "v001")
        assert loaded is not None
        assert loaded["module_id"] == "MOD-LOAD"

    def test_load_baseline_nonexistent(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        result = mgr.load_baseline("NONEXISTENT", "v001")
        assert result is None

    def test_list_versions(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        mod = tmp_path / "list_mod"
        mod.mkdir()
        (mod / "mod.py").write_text("x = 1\n", encoding="utf-8")
        mgr.capture("MOD-LIST", str(mod))
        mgr.capture("MOD-LIST", str(mod))
        versions = mgr.list_versions("MOD-LIST")
        assert len(versions) == 2
        assert "v001" in versions
        assert "v002" in versions

    def test_full_diff(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        mod = tmp_path / "diff_mod"
        mod.mkdir()
        (mod / "mod.py").write_text("x = 1\n", encoding="utf-8")
        mgr.capture("MOD-DIFF", str(mod))
        (mod / "new.py").write_text("y = 2\n", encoding="utf-8")
        report = mgr.full_diff("MOD-DIFF", str(mod))
        assert isinstance(report, DiffReport)
        assert report.module_id == "MOD-DIFF"
        assert len(report.added) > 0

    def test_full_diff_no_baseline(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        mod = tmp_path / "nobase_mod"
        mod.mkdir()
        (mod / "mod.py").write_text("x = 1\n", encoding="utf-8")
        report = mgr.full_diff("MOD-NOBASE", str(mod))
        assert isinstance(report, DiffReport)

    def test_contract_diff(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        mod = tmp_path / "cdiff_mod"
        mod.mkdir()
        (mod / "mod.py").write_text("def foo(): pass\n", encoding="utf-8")
        mgr.capture("MOD-CDIFF", str(mod))
        (mod / "mod.py").write_text("def foo(x): pass\ndef bar(): pass\n", encoding="utf-8")
        report = mgr.contract_diff("MOD-CDIFF", str(mod))
        assert isinstance(report, DiffReport)
        assert report.diff_type == "contract_only"
        assert len(report.contract_changes) > 0

    def test_slow_creep_check(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        mod = tmp_path / "creep_mod"
        mod.mkdir()
        (mod / "mod.py").write_text("x = 1\n", encoding="utf-8")
        mgr.capture("MOD-CREEP", str(mod))
        mgr.capture("MOD-CREEP", str(mod))
        report = mgr.slow_creep_check("MOD-CREEP", str(mod))
        assert isinstance(report, DiffReport)
        assert report.diff_type == "slow_creep"

    def test_on_phase_complete(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        mod = tmp_path / "phase_mod"
        mod.mkdir()
        (mod / "mod.py").write_text("x = 1\n", encoding="utf-8")
        result = mgr.on_phase_complete("MOD-PHASE", str(mod), "Phase3")
        assert result["module_id"] == "MOD-PHASE"

    def test_manual_capture(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        mod = tmp_path / "manual_mod"
        mod.mkdir()
        (mod / "mod.py").write_text("x = 1\n", encoding="utf-8")
        result = mgr.manual_capture("MOD-MANUAL", str(mod))
        assert result["module_id"] == "MOD-MANUAL"

    def test_cleanup_old_versions(self, tmp_path):
        mgr = BaselineManager(project_root=str(tmp_path))
        mgr.MAX_VERSIONS = 3
        mod = tmp_path / "cleanup_mod"
        mod.mkdir()
        (mod / "mod.py").write_text("x = 1\n", encoding="utf-8")
        for i in range(5):
            mgr.capture("MOD-CLEANUP", str(mod))
        versions = mgr.list_versions("MOD-CLEANUP")
        assert len(versions) <= 3
