# [A_test] module_id: SRC-TST-0300 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_ai_construction_detectors
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_ai_construction_detectors.py -q
# [TTL] task_bound

from __future__ import annotations

import os
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from zephyr.gov_drift.ai_construction_detectors import AIConstructionDetectors
from zephyr.gov_drift.drift_models import DriftEvent, DriftState


@pytest.fixture
def detector():
    return AIConstructionDetectors()


@pytest.fixture
def tmp_module_dir(tmp_path):
    return str(tmp_path)


def _make_drift_event(
    detector_id: str = "d1",
    drift_dimension: str = "dim1",
    resolved_by: str | None = None,
) -> DriftEvent:
    return DriftEvent(
        event_id=uuid4(),
        module_id="MOD-INF-023",
        detector_id=detector_id,
        drift_dimension=drift_dimension,
        baseline_version="0.1.0",
        state=DriftState.DETECTED,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        resolved_by=resolved_by,
    )


class TestAIConstructionDetectorsInstantiation:
    def test_creates_instance_without_args(self):
        d = AIConstructionDetectors()
        assert d is not None
        assert isinstance(d, AIConstructionDetectors)

    def test_has_all_seven_detect_methods(self, detector):
        methods = [
            "detect_ai_hallucination_import",
            "detect_ai_dead_code",
            "detect_ai_broken_logic",
            "detect_ai_duplicate_functionality",
            "detect_ai_session_style_drift",
            "detect_ai_knowledge_pollution",
            "detect_cross_session_repair_conflict",
        ]
        for m in methods:
            assert callable(getattr(detector, m, None)), f"Missing method: {m}"

    def test_separate_instances_are_independent(self):
        d1 = AIConstructionDetectors()
        d2 = AIConstructionDetectors()
        assert d1 is not d2


class TestDetectAIHallucinationImport:
    def test_returns_empty_for_nonexistent_dir(self, detector):
        result = detector.detect_ai_hallucination_import("/nonexistent/path/xyz")
        assert result == []

    def test_returns_empty_for_empty_dir(self, detector, tmp_module_dir):
        result = detector.detect_ai_hallucination_import(tmp_module_dir)
        assert result == []

    def test_detects_hallucinated_from_import(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "sample.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("from totally_fake_module_xyz import Nothing\n")
        result = detector.detect_ai_hallucination_import(tmp_module_dir)
        assert len(result) >= 1
        assert result[0].detector_id == "ai_hallucination_import"
        assert result[0].state == DriftState.DETECTED
        assert "totally_fake_module_xyz" in (result[0].resolution_detail or "")

    def test_detects_hallucinated_bare_import(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "bare_import.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("import nonexistent_pkg_abc\n")
        result = detector.detect_ai_hallucination_import(tmp_module_dir)
        assert len(result) >= 1
        assert result[0].detector_id == "ai_hallucination_import"

    def test_skips_stdlib_imports(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "stdlib_user.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("import os\nimport sys\nimport json\n")
        result = detector.detect_ai_hallucination_import(tmp_module_dir)
        assert len(result) == 0

    def test_skips_relative_imports(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "rel_import.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("from .sibling import something\nfrom ..parent import other\n")
        result = detector.detect_ai_hallucination_import(tmp_module_dir)
        assert len(result) == 0

    def test_skips_future_and_builtins(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "safe_prefix.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("from __future__ import annotations\nimport builtins\n")
        result = detector.detect_ai_hallucination_import(tmp_module_dir)
        assert len(result) == 0

    def test_skips_init_file_even_with_fake_import(self, detector, tmp_module_dir):
        init_file = os.path.join(tmp_module_dir, "__init__.py")
        with open(init_file, "w", encoding="utf-8") as f:
            f.write("from totally_fake_module_xyz import Nothing\n")
        result = detector.detect_ai_hallucination_import(tmp_module_dir)
        assert len(result) == 0

    def test_skips_syntax_error_files(self, detector, tmp_module_dir):
        bad_file = os.path.join(tmp_module_dir, "bad_syntax.py")
        with open(bad_file, "w", encoding="utf-8") as f:
            f.write("def broken(:\n")
        result = detector.detect_ai_hallucination_import(tmp_module_dir)
        assert len(result) == 0

    def test_boundary_multiple_hallucinated_in_one_file(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "multi_fake.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("import fake_alpha\nimport fake_beta\nfrom fake_gamma import X\n")
        result = detector.detect_ai_hallucination_import(tmp_module_dir)
        assert len(result) == 3

    def test_boundary_non_py_files_ignored(self, detector, tmp_module_dir):
        txt_file = os.path.join(tmp_module_dir, "notes.txt")
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write("import fake_module\n")
        result = detector.detect_ai_hallucination_import(tmp_module_dir)
        assert len(result) == 0


class TestDetectAIDeadCode:
    def test_returns_empty_for_nonexistent_dir(self, detector):
        result = detector.detect_ai_dead_code("/nonexistent/path/xyz")
        assert result == []

    def test_detects_pass_only_function(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "dead.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("def placeholder():\n    pass\n")
        result = detector.detect_ai_dead_code(tmp_module_dir)
        matches = [
            e for e in result if e.detector_id == "ai_dead_code" and "placeholder" in (e.resolution_detail or "")
        ]
        assert len(matches) >= 1

    def test_detects_ellipsis_only_function(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "ellipsis.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("def placeholder():\n    ...\n")
        result = detector.detect_ai_dead_code(tmp_module_dir)
        matches = [
            e for e in result if e.detector_id == "ai_dead_code" and "placeholder" in (e.resolution_detail or "")
        ]
        assert len(matches) >= 1

    def test_detects_pass_only_class(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "dead_class.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("class EmptyClass:\n    pass\n")
        result = detector.detect_ai_dead_code(tmp_module_dir)
        matches = [e for e in result if e.detector_id == "ai_dead_code" and "EmptyClass" in (e.resolution_detail or "")]
        assert len(matches) >= 1

    def test_detects_ellipsis_only_class(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "ellipsis_class.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("class EllipsisClass:\n    ...\n")
        result = detector.detect_ai_dead_code(tmp_module_dir)
        matches = [
            e for e in result if e.detector_id == "ai_dead_code" and "EllipsisClass" in (e.resolution_detail or "")
        ]
        assert len(matches) >= 1

    def test_no_event_for_real_implementation(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "real_impl.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("def real_func():\n    return 42\n")
        result = detector.detect_ai_dead_code(tmp_module_dir)
        dead_for_real = [e for e in result if "real_func" in (e.resolution_detail or "")]
        assert len(dead_for_real) == 0

    def test_no_event_for_class_with_methods(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "live_class.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("class LiveClass:\n    def method(self):\n        return 1\n")
        result = detector.detect_ai_dead_code(tmp_module_dir)
        dead_for_live = [e for e in result if "LiveClass" in (e.resolution_detail or "")]
        assert len(dead_for_live) == 0

    def test_boundary_skips_init_file(self, detector, tmp_module_dir):
        init_file = os.path.join(tmp_module_dir, "__init__.py")
        with open(init_file, "w", encoding="utf-8") as f:
            f.write("def empty():\n    pass\n")
        result = detector.detect_ai_dead_code(tmp_module_dir)
        assert len(result) == 0

    def test_boundary_syntax_error_file_skipped(self, detector, tmp_module_dir):
        bad_file = os.path.join(tmp_module_dir, "broken.py")
        with open(bad_file, "w", encoding="utf-8") as f:
            f.write("class : pass\n")
        result = detector.detect_ai_dead_code(tmp_module_dir)
        assert len(result) == 0


class TestDetectAIBrokenLogic:
    def test_returns_empty_for_nonexistent_dir(self, detector):
        result = detector.detect_ai_broken_logic("/nonexistent/path/xyz")
        assert result == []

    def test_detects_high_todo_ratio(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "todo_heavy.py")
        lines = ["# TODO: fix this\n"] * 6 + ["x = 1\n"] * 90
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("".join(lines))
        result = detector.detect_ai_broken_logic(tmp_module_dir)
        todo_events = [
            e for e in result if e.detector_id == "ai_broken_logic" and "TODO" in (e.resolution_detail or "")
        ]
        assert len(todo_events) >= 1

    def test_detects_context_truncation(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "truncated.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("def bloated(a, b, c, d, e, f):\n    return a\n")
        result = detector.detect_ai_broken_logic(tmp_module_dir)
        trunc_events = [
            e
            for e in result
            if e.detector_id == "ai_broken_logic" and "truncation" in (e.resolution_detail or "").lower()
        ]
        assert len(trunc_events) >= 1

    def test_no_event_for_clean_code(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "clean.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("def clean_func(a, b):\n    return a + b\n")
        result = detector.detect_ai_broken_logic(tmp_module_dir)
        assert len(result) == 0

    def test_no_event_for_low_todo_ratio(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "low_todo.py")
        lines = ["# TODO: minor\n"] + ["x = 1\n"] * 99
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("".join(lines))
        result = detector.detect_ai_broken_logic(tmp_module_dir)
        todo_events = [e for e in result if "TODO" in (e.resolution_detail or "")]
        assert len(todo_events) == 0

    def test_boundary_exactly_five_args_not_truncated(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "five_args.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("def five_args(a, b, c, d, e):\n    return a\n")
        result = detector.detect_ai_broken_logic(tmp_module_dir)
        trunc_events = [e for e in result if "truncation" in (e.resolution_detail or "").lower()]
        assert len(trunc_events) == 0

    def test_boundary_six_args_short_body_is_truncated(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "six_args.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("def six_args(a, b, c, d, e, f):\n    return a\n")
        result = detector.detect_ai_broken_logic(tmp_module_dir)
        trunc_events = [e for e in result if "truncation" in (e.resolution_detail or "").lower()]
        assert len(trunc_events) >= 1

    def test_boundary_empty_dir_no_crash(self, detector, tmp_module_dir):
        result = detector.detect_ai_broken_logic(tmp_module_dir)
        assert result == []


class TestDetectAIDuplicateFunctionality:
    def test_returns_empty_for_nonexistent_dir(self, detector):
        result = detector.detect_ai_duplicate_functionality("/nonexistent/path/xyz")
        assert result == []

    def test_detects_duplicate_functions_across_files(self, detector, tmp_module_dir):
        code = "def same_func():\n    return 42\n"
        f1 = os.path.join(tmp_module_dir, "a_file.py")
        f2 = os.path.join(tmp_module_dir, "b_file.py")
        with open(f1, "w", encoding="utf-8") as fh:
            fh.write(code)
        with open(f2, "w", encoding="utf-8") as fh:
            fh.write(code)
        result = detector.detect_ai_duplicate_functionality(tmp_module_dir)
        assert any(e.detector_id == "ai_duplicate_functionality" for e in result)

    def test_no_event_for_unique_functions(self, detector, tmp_module_dir):
        f1 = os.path.join(tmp_module_dir, "unique_a.py")
        f2 = os.path.join(tmp_module_dir, "unique_b.py")
        with open(f1, "w", encoding="utf-8") as fh:
            fh.write("def func_alpha():\n    return 1\n")
        with open(f2, "w", encoding="utf-8") as fh:
            fh.write("def func_beta():\n    return 2\n")
        result = detector.detect_ai_duplicate_functionality(tmp_module_dir)
        assert len(result) == 0

    def test_no_event_for_dunder_methods(self, detector, tmp_module_dir):
        code = "def __init__(self):\n    return 42\n"
        f1 = os.path.join(tmp_module_dir, "dunder_a.py")
        f2 = os.path.join(tmp_module_dir, "dunder_b.py")
        with open(f1, "w", encoding="utf-8") as fh:
            fh.write(code)
        with open(f2, "w", encoding="utf-8") as fh:
            fh.write(code)
        result = detector.detect_ai_duplicate_functionality(tmp_module_dir)
        assert len(result) == 0

    def test_boundary_single_file_no_duplicates(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "solo.py")
        with open(py_file, "w", encoding="utf-8") as fh:
            fh.write("def solo_func():\n    return 1\n")
        result = detector.detect_ai_duplicate_functionality(tmp_module_dir)
        assert len(result) == 0

    def test_boundary_same_name_different_body_not_duplicate(self, detector, tmp_module_dir):
        f1 = os.path.join(tmp_module_dir, "diff_a.py")
        f2 = os.path.join(tmp_module_dir, "diff_b.py")
        with open(f1, "w", encoding="utf-8") as fh:
            fh.write("def compute():\n    return 1\n")
        with open(f2, "w", encoding="utf-8") as fh:
            fh.write("def compute():\n    return 2\n")
        result = detector.detect_ai_duplicate_functionality(tmp_module_dir)
        assert len(result) == 0


class TestDetectAISessionStyleDrift:
    def test_returns_empty_for_nonexistent_dir(self, detector):
        result = detector.detect_ai_session_style_drift("/nonexistent/path/xyz")
        assert result == []

    def test_detects_dataclass_with_init(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "style_conflict.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write(
                "from dataclasses import dataclass\n"
                "@dataclass\nclass Foo:\n    x: int = 0\n"
                "class Bar:\n    def __init__(self, y):\n        self.y = y\n"
            )
        result = detector.detect_ai_session_style_drift(tmp_module_dir)
        assert any("dataclass" in (e.resolution_detail or "") for e in result)

    def test_detects_async_sync_mix(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "async_sync.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("async def a_func():\n    return 1\ndef b_func():\n    return 2\n")
        result = detector.detect_ai_session_style_drift(tmp_module_dir)
        assert any("async" in (e.resolution_detail or "") for e in result)

    def test_no_event_for_consistent_sync_style(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "consistent.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("def func_a():\n    return 1\ndef func_b():\n    return 2\n")
        result = detector.detect_ai_session_style_drift(tmp_module_dir)
        assert len(result) == 0

    def test_no_event_for_consistent_async_style(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "all_async.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("async def a():\n    return 1\nasync def b():\n    return 2\n")
        result = detector.detect_ai_session_style_drift(tmp_module_dir)
        sync_events = [e for e in result if "async" in (e.resolution_detail or "")]
        assert len(sync_events) == 0

    def test_boundary_dataclass_without_init_no_drift(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "pure_dataclass.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("from dataclasses import dataclass\n@dataclass\nclass Pure:\n    x: int = 0\n")
        result = detector.detect_ai_session_style_drift(tmp_module_dir)
        dataclass_events = [e for e in result if "dataclass" in (e.resolution_detail or "")]
        assert len(dataclass_events) == 0

    def test_boundary_init_without_dataclass_no_drift(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "pure_init.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("class PureInit:\n    def __init__(self):\n        self.x = 0\n")
        result = detector.detect_ai_session_style_drift(tmp_module_dir)
        dataclass_events = [e for e in result if "dataclass" in (e.resolution_detail or "")]
        assert len(dataclass_events) == 0


class TestDetectAIKnowledgePollution:
    def test_returns_empty_for_nonexistent_dir(self, detector):
        result = detector.detect_ai_knowledge_pollution("/nonexistent/path/xyz")
        assert result == []

    def test_detects_name_collision(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "collision.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("class Foo:\n    pass\ndef Foo():\n    pass\n")
        result = detector.detect_ai_knowledge_pollution(tmp_module_dir)
        assert any("collision" in (e.resolution_detail or "").lower() for e in result)

    def test_detects_naming_convention_conflict(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "naming.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("def snake_case_func():\n    return 1\ndef CamelCaseFunc():\n    return 2\n")
        result = detector.detect_ai_knowledge_pollution(tmp_module_dir)
        assert any("convention" in (e.resolution_detail or "").lower() for e in result)

    def test_no_event_for_consistent_snake_case(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "consistent_naming.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("def func_one():\n    return 1\ndef func_two():\n    return 2\n")
        result = detector.detect_ai_knowledge_pollution(tmp_module_dir)
        assert len(result) == 0

    def test_no_event_for_class_and_distinct_function_names(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "distinct_names.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("class MyClass:\n    pass\ndef my_function():\n    return 1\n")
        result = detector.detect_ai_knowledge_pollution(tmp_module_dir)
        collision_events = [e for e in result if "collision" in (e.resolution_detail or "").lower()]
        assert len(collision_events) == 0

    def test_boundary_empty_file_no_events(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "empty.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("")
        result = detector.detect_ai_knowledge_pollution(tmp_module_dir)
        assert len(result) == 0

    def test_boundary_multiple_collisions_in_one_file(self, detector, tmp_module_dir):
        py_file = os.path.join(tmp_module_dir, "multi_collision.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("class Alpha:\n    pass\ndef Alpha():\n    pass\nclass Beta:\n    pass\ndef Beta():\n    pass\n")
        result = detector.detect_ai_knowledge_pollution(tmp_module_dir)
        collision_events = [e for e in result if "collision" in (e.resolution_detail or "").lower()]
        assert len(collision_events) >= 1


class TestDetectCrossSessionRepairConflict:
    def test_returns_empty_for_empty_list(self, detector):
        result = detector.detect_cross_session_repair_conflict([])
        assert result == []

    def test_detects_conflict_when_same_key_repeated(self, detector):
        events = [
            _make_drift_event(detector_id="d1", drift_dimension="dim1", resolved_by="session-A"),
            _make_drift_event(detector_id="d1", drift_dimension="dim1", resolved_by="session-A"),
        ]
        result = detector.detect_cross_session_repair_conflict(events)
        assert len(result) >= 1
        assert result[0].detector_id == "cross_session_repair_conflict"
        assert result[0].state == DriftState.DETECTED

    def test_no_conflict_for_distinct_keys(self, detector):
        events = [
            _make_drift_event(detector_id="d1", drift_dimension="dim1", resolved_by="session-A"),
            _make_drift_event(detector_id="d2", drift_dimension="dim2", resolved_by="session-B"),
        ]
        result = detector.detect_cross_session_repair_conflict(events)
        assert len(result) == 0

    def test_no_conflict_for_single_event(self, detector):
        events = [_make_drift_event(detector_id="d1", drift_dimension="dim1", resolved_by="session-A")]
        result = detector.detect_cross_session_repair_conflict(events)
        assert len(result) == 0

    def test_conflict_with_none_resolved_by(self, detector):
        events = [
            _make_drift_event(detector_id="d1", drift_dimension="dim1", resolved_by=None),
            _make_drift_event(detector_id="d1", drift_dimension="dim1", resolved_by=None),
        ]
        result = detector.detect_cross_session_repair_conflict(events)
        assert len(result) >= 1

    def test_boundary_three_events_same_key(self, detector):
        events = [
            _make_drift_event(detector_id="d1", drift_dimension="dim1", resolved_by="session-X"),
            _make_drift_event(detector_id="d1", drift_dimension="dim1", resolved_by="session-X"),
            _make_drift_event(detector_id="d1", drift_dimension="dim1", resolved_by="session-X"),
        ]
        result = detector.detect_cross_session_repair_conflict(events)
        assert len(result) >= 1
        assert "3" in (result[0].resolution_detail or "")

    def test_boundary_mixed_conflict_and_distinct(self, detector):
        events = [
            _make_drift_event(detector_id="d1", drift_dimension="dim1", resolved_by="session-A"),
            _make_drift_event(detector_id="d1", drift_dimension="dim1", resolved_by="session-A"),
            _make_drift_event(detector_id="d2", drift_dimension="dim2", resolved_by="session-B"),
        ]
        result = detector.detect_cross_session_repair_conflict(events)
        assert len(result) == 1
