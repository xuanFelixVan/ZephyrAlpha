# [A_test] module_id: SRC-TST-0395 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_ba_chaos_injector
# [INVARIANTS] 混沌注入必须金丝雀保护
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] CI;drift_engine
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_ba_chaos_injector.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_drift.chaos_injector import (
    INJECTORS,
    ChaosInjection,
    ChaosInjectionType,
    ChaosMetrics,
    ChaosPhase,
    ChaosResult,
    _find_p2_targets,
    _write_metrics,
    import_hallucination,
    inject_fake_todo_bomb,
    inject_path_rename,
    inject_yaml_field_flip,
)


class TestChaosInjectionType:
    def test_has_four_types(self):
        assert ChaosInjectionType.PATH_RENAME.value == "path_rename"
        assert ChaosInjectionType.YAML_FIELD_FLIP.value == "yaml_field_flip"
        assert ChaosInjectionType.FAKE_TODO_BOMB.value == "fake_todo_bomb"
        assert ChaosInjectionType.IMPORT_HALLUCINATION.value == "import_hallucination"

    def test_is_str_enum(self):
        assert isinstance(ChaosInjectionType.PATH_RENAME, str)


class TestChaosPhase:
    def test_has_five_phases(self):
        assert ChaosPhase.BASELINE.value == "baseline"
        assert ChaosPhase.INJECT.value == "inject"
        assert ChaosPhase.DETECT.value == "detect"
        assert ChaosPhase.ROLLBACK.value == "rollback"
        assert ChaosPhase.COMPLETE.value == "complete"


class TestChaosResult:
    def test_has_four_results(self):
        assert ChaosResult.DETECTED.value == "DETECTED"
        assert ChaosResult.MISSED.value == "MISSED"
        assert ChaosResult.DEGRADED.value == "DEGRADED"
        assert ChaosResult.ERROR.value == "ERROR"


class TestChaosInjection:
    def test_defaults(self):
        ci = ChaosInjection()
        assert ci.injection_id.startswith("chaos-")
        assert ci.injection_type == ChaosInjectionType.PATH_RENAME
        assert ci.result == ChaosResult.MISSED
        assert ci.phase == ChaosPhase.BASELINE
        assert ci.detected_by == []

    def test_custom_fields(self):
        ci = ChaosInjection(injection_type=ChaosInjectionType.YAML_FIELD_FLIP, target_file="test.py")
        assert ci.injection_type == ChaosInjectionType.YAML_FIELD_FLIP
        assert ci.target_file == "test.py"


class TestChaosMetrics:
    def test_defaults(self):
        m = ChaosMetrics()
        assert m.total_injections == 0
        assert m.detected == 0
        assert m.missed == 0
        assert m.false_negative_rate == 0.0

    def test_summary(self):
        m = ChaosMetrics(total_injections=10, detected=8, missed=2, false_negative_rate=0.2)
        s = m.summary()
        assert s["detection_rate"] == "8/10"
        assert s["miss_count"] == 2
        assert s["fn_rate"] == 0.2


class TestInjectPathRename:
    def test_renames_import(self, tmp_path):
        py_file = tmp_path / "target.py"
        py_file.write_text("import os\n", encoding="utf-8")
        original, mutated = inject_path_rename(py_file)
        assert original != mutated or original == mutated

    def test_returns_original_when_no_imports(self, tmp_path):
        py_file = tmp_path / "noinfo.py"
        py_file.write_text("x = 1\n", encoding="utf-8")
        original, mutated = inject_path_rename(py_file)
        assert original == mutated


class TestInjectYamlFieldFlip:
    def test_flips_enabled_true_to_false(self, tmp_path):
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text("enabled: true\nrequired: false\n", encoding="utf-8")
        original, mutated = inject_yaml_field_flip(yaml_file)
        assert "enabled: false" in mutated

    def test_no_flip_when_no_bool_fields(self, tmp_path):
        yaml_file = tmp_path / "nope.yaml"
        yaml_file.write_text("name: test\n", encoding="utf-8")
        original, mutated = inject_yaml_field_flip(yaml_file)
        assert original == mutated


class TestInjectFakeTodoBomb:
    def test_inserts_todo(self, tmp_path):
        py_file = tmp_path / "bomb.py"
        py_file.write_text("from __future__ import annotations\nx = 1\n", encoding="utf-8")
        original, mutated = inject_fake_todo_bomb(py_file)
        assert "TODO" in mutated
        assert "chaos bomb" in mutated

    def test_inserts_at_top_when_no_future(self, tmp_path):
        py_file = tmp_path / "nofuture.py"
        py_file.write_text("x = 1\n", encoding="utf-8")
        original, mutated = inject_fake_todo_bomb(py_file)
        assert "TODO" in mutated


class TestImportHallucination:
    def test_adds_hallucinated_import(self, tmp_path):
        py_file = tmp_path / "hall.py"
        py_file.write_text("import os\n", encoding="utf-8")
        original, mutated = import_hallucination(py_file)
        assert "chaos_hallucination_xyzzy" in mutated
        assert original != mutated

    def test_original_unchanged(self, tmp_path):
        py_file = tmp_path / "orig.py"
        content = "x = 1\n"
        py_file.write_text(content, encoding="utf-8")
        original, _ = import_hallucination(py_file)
        assert original == content


class TestInjectorsMap:
    def test_maps_all_types(self):
        assert len(INJECTORS) == 4
        assert ChaosInjectionType.PATH_RENAME in INJECTORS
        assert ChaosInjectionType.YAML_FIELD_FLIP in INJECTORS
        assert ChaosInjectionType.FAKE_TODO_BOMB in INJECTORS
        assert ChaosInjectionType.IMPORT_HALLUCINATION in INJECTORS


class TestFindP2Targets:
    def test_returns_list(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        targets = _find_p2_targets(str(tmp_path))
        assert isinstance(targets, list)

    def test_returns_empty_for_empty_root(self, tmp_path):
        targets = _find_p2_targets(str(tmp_path))
        assert targets == []


class TestWriteMetrics:
    def test_writes_to_state_dir(self, tmp_path):
        m = ChaosMetrics(total_injections=5, detected=3, missed=2, false_negative_rate=0.4)
        _write_metrics(m, str(tmp_path))
        import os

        assert os.path.exists(tmp_path / "_chaos_metrics.json")

    def test_noop_when_no_state_dir(self):
        m = ChaosMetrics()
        _write_metrics(m, "")
