# [A_test] module_id: SRC-TST-1112 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_import_surface_tracker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.trackers.import_surface_tracker import ImportSurfaceTracker


class TestImportSurfaceTracker:
    def test_instantiation(self):
        tracker = ImportSurfaceTracker()
        assert tracker is not None

    def test_compute_sbs(self):
        tracker = ImportSurfaceTracker()
        result = tracker.compute_sbs(imports_count=5, max_healthy=100)
        assert isinstance(result, (int, float, dict))

    def test_analyze_file(self, tmp_path):
        tracker = ImportSurfaceTracker()
        f = tmp_path / "test_mod.py"
        f.write_text("import os\nimport sys\n", encoding="utf-8")
        result = tracker.analyze_file(str(f))
        assert isinstance(result, dict)

    def test_compute_sbs_zero(self):
        tracker = ImportSurfaceTracker()
        result = tracker.compute_sbs(imports_count=0, max_healthy=100)
        assert isinstance(result, (int, float, dict))
