# [A_test] module_id: SRC-TST-0513 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_chaos_injector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_chaos_injector.py -q
# [TTL] task_bound

from __future__ import annotations

import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from zephyr.gov_drift.chaos_injector import (
    INJECTORS,
    ChaosInjection,
    ChaosInjectionType,
    ChaosMetrics,
    ChaosPhase,
    ChaosResult,
    import_hallucination,
    inject_fake_todo_bomb,
    inject_path_rename,
    inject_yaml_field_flip,
)


class TestChaosInjectionType:
    def test_enum_values(self):
        assert ChaosInjectionType.PATH_RENAME.value == "path_rename"
        assert ChaosInjectionType.YAML_FIELD_FLIP.value == "yaml_field_flip"
        assert ChaosInjectionType.FAKE_TODO_BOMB.value == "fake_todo_bomb"
        assert ChaosInjectionType.IMPORT_HALLUCINATION.value == "import_hallucination"

    def test_enum_count(self):
        assert len(ChaosInjectionType) == 4


class TestChaosPhase:
    def test_enum_values(self):
        assert ChaosPhase.BASELINE.value == "baseline"
        assert ChaosPhase.INJECT.value == "inject"
        assert ChaosPhase.DETECT.value == "detect"
        assert ChaosPhase.ROLLBACK.value == "rollback"
        assert ChaosPhase.COMPLETE.value == "complete"

    def test_enum_count(self):
        assert len(ChaosPhase) == 5


class TestChaosResult:
    def test_enum_values(self):
        assert ChaosResult.DETECTED.value == "DETECTED"
        assert ChaosResult.MISSED.value == "MISSED"
        assert ChaosResult.DEGRADED.value == "DEGRADED"
        assert ChaosResult.ERROR.value == "ERROR"

    def test_enum_count(self):
        assert len(ChaosResult) == 4


class TestChaosInjection:
    def test_instantiation_defaults(self):
        ci = ChaosInjection()
        assert ci.injection_id.startswith("chaos-")
        assert ci.injection_type == ChaosInjectionType.PATH_RENAME
        assert ci.target_file == ""
        assert ci.original_content == ""
        assert ci.mutated_content == ""
        assert ci.baseline_snapshot is None
        assert ci.detection_time_sec == 0.0
        assert ci.detected_by == []
        assert ci.result == ChaosResult.MISSED
        assert ci.phase == ChaosPhase.BASELINE
        assert ci.rolled_back_at is None

    def test_instantiation_custom(self):
        now = datetime.now(UTC)
        ci = ChaosInjection(
            injection_id="chaos-custom",
            injection_type=ChaosInjectionType.YAML_FIELD_FLIP,
            target_file="/tmp/test.py",
            original_content="x = 1",
            mutated_content="x = 2",
            baseline_snapshot=now.isoformat(),
            detection_time_sec=3.5,
            detected_by=["DET-001"],
            result=ChaosResult.DETECTED,
            phase=ChaosPhase.COMPLETE,
            created_at=now,
            rolled_back_at=now,
        )
        assert ci.injection_id == "chaos-custom"
        assert ci.injection_type == ChaosInjectionType.YAML_FIELD_FLIP
        assert ci.detection_time_sec == 3.5
        assert ci.result == ChaosResult.DETECTED
        assert ci.rolled_back_at is not None


class TestChaosMetrics:
    def test_instantiation_defaults(self):
        m = ChaosMetrics()
        assert m.total_injections == 0
        assert m.detected == 0
        assert m.missed == 0
        assert m.degraded == 0
        assert m.avg_time_to_detect_sec == 0.0
        assert m.false_negative_rate == 0.0

    def test_summary(self):
        m = ChaosMetrics(
            total_injections=10, detected=7, missed=2, degraded=1, avg_time_to_detect_sec=4.2, false_negative_rate=0.2
        )
        s = m.summary()
        assert s["detection_rate"] == "7/10"
        assert s["miss_count"] == 2
        assert s["avg_ttd_sec"] == 4.2
        assert s["fn_rate"] == 0.2

    def test_summary_zero_injections(self):
        m = ChaosMetrics()
        s = m.summary()
        assert s["detection_rate"] == "0/0"
        assert s["fn_rate"] == 0.0


class TestInjectPathRename:
    def test_renames_import(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("import os\nimport sys\n\nx = os.path.join('a', 'b')\n")
            f.flush()
            original, mutated = inject_path_rename(Path(f.name))
        os.unlink(f.name)
        assert original != mutated
        assert "_chaos_temp_" in mutated

    def test_no_imports_returns_original(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("x = 1\ny = 2\n")
            f.flush()
            original, mutated = inject_path_rename(Path(f.name))
        os.unlink(f.name)
        assert original == mutated


class TestInjectYamlFieldFlip:
    def test_flips_enabled_true_to_false(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            f.write("name: test\nenabled: true\ncount: 5\n")
            f.flush()
            original, mutated = inject_yaml_field_flip(Path(f.name))
        os.unlink(f.name)
        assert "enabled: false" in mutated
        assert "enabled: true" not in mutated

    def test_no_bool_fields_returns_original(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            f.write("name: test\ncount: 5\n")
            f.flush()
            original, mutated = inject_yaml_field_flip(Path(f.name))
        os.unlink(f.name)
        assert original == mutated


class TestInjectFakeTodoBomb:
    def test_inserts_todo_after_future_import(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("from __future__ import annotations\n\nx = 1\n")
            f.flush()
            original, mutated = inject_fake_todo_bomb(Path(f.name))
        os.unlink(f.name)
        assert "chaos bomb" in mutated
        assert "TODO" in mutated

    def test_inserts_at_top_without_future_import(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("x = 1\ny = 2\n")
            f.flush()
            original, mutated = inject_fake_todo_bomb(Path(f.name))
        os.unlink(f.name)
        assert "chaos bomb" in mutated
        assert mutated.startswith("\n\n# TODO")


class TestImportHallucination:
    def test_adds_fake_import(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("import os\n\nx = 1\n")
            f.flush()
            original, mutated = import_hallucination(Path(f.name))
        os.unlink(f.name)
        assert "chaos_hallucination_xyzzy" in mutated
        assert "this_never_exists_roflmao" in mutated
        assert mutated.startswith("from chaos_hallucination_xyzzy")

    def test_original_unchanged_in_return(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("import os\n")
            f.flush()
            original, mutated = import_hallucination(Path(f.name))
        os.unlink(f.name)
        assert "chaos_hallucination_xyzzy" not in original
        assert "chaos_hallucination_xyzzy" in mutated


class TestInjectorsRegistry:
    def test_all_types_registered(self):
        for itype in ChaosInjectionType:
            assert itype in INJECTORS

    def test_all_injectors_callable(self):
        for itype, injector in INJECTORS.items():
            assert callable(injector)
