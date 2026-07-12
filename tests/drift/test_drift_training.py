# [A_test] module_id: SRC-TST-0781 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_drift_training
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_drift_training.py -q
# [TTL] task_bound

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from zephyr.gov_drift.drift_training import (
    CROSS_LANG_CONFIG,
    LANGUAGE_AGNOSTIC_DIMENSIONS,
    LANGUAGE_SPECIFIC_INTERFACES,
    AITrainingLoopResult,
    CrossLanguageConfig,
    DriftTrainingPattern,
    detect_ai_training_loop,
    detect_cross_language_drift,
    detect_python_dead_code,
    extract_training_patterns,
    inject_patterns_to_prompt,
    parse_python_imports,
    parse_python_public_api,
    track_training_effectiveness,
)


class TestDriftTrainingPatternInstantiation:
    def test_required_fields(self):
        p = DriftTrainingPattern(
            pattern_id="p1",
            detector_id="det-001",
            frequency=5,
            dimension="D5_semantic",
            commit_diff_pattern="git diff abc",
            root_cause_summary="missing validation",
        )
        assert p.pattern_id == "p1"
        assert p.detector_id == "det-001"
        assert p.frequency == 5
        assert p.dimension == "D5_semantic"
        assert p.commit_diff_pattern == "git diff abc"
        assert p.root_cause_summary == "missing validation"

    def test_default_fields(self):
        p = DriftTrainingPattern(
            pattern_id="p2",
            detector_id="det-002",
            frequency=1,
            dimension="D5",
            commit_diff_pattern="",
            root_cause_summary="",
        )
        assert p.injected is False
        assert p.effectiveness is None
        assert isinstance(p.first_seen, datetime)
        assert isinstance(p.last_seen, datetime)

    def test_custom_optional_fields(self):
        now = datetime.now(UTC)
        p = DriftTrainingPattern(
            pattern_id="p3",
            detector_id="det-003",
            frequency=10,
            dimension="D5",
            commit_diff_pattern="",
            root_cause_summary="",
            first_seen=now,
            last_seen=now,
            injected=True,
            effectiveness=0.75,
        )
        assert p.injected is True
        assert p.effectiveness == 0.75
        assert p.first_seen == now


class TestAITrainingLoopResultInstantiation:
    def test_default_fields(self):
        r = AITrainingLoopResult()
        assert r.detector_name == "ai_training_loop"
        assert r.patterns_extracted == 0
        assert r.patterns_injected == 0
        assert r.patterns_suppressed == 0

    def test_custom_fields(self):
        r = AITrainingLoopResult(
            patterns_extracted=5,
            patterns_injected=3,
            patterns_suppressed=2,
        )
        assert r.patterns_extracted == 5
        assert r.patterns_injected == 3
        assert r.patterns_suppressed == 2


class TestCrossLanguageConfigInstantiation:
    def test_default_config(self):
        config = CrossLanguageConfig()
        assert "Python" in config.enabled_languages
        assert config.fallback_on_unsupported is True
        assert len(config.agnostic_dimensions) > 0

    def test_custom_config(self):
        config = CrossLanguageConfig(
            enabled_languages=["Python", "Go"],
            fallback_on_unsupported=False,
        )
        assert "Go" in config.enabled_languages
        assert config.fallback_on_unsupported is False

    def test_global_config_instance(self):
        assert isinstance(CROSS_LANG_CONFIG, CrossLanguageConfig)
        assert "Python" in CROSS_LANG_CONFIG.enabled_languages


class TestExtractTrainingPatterns:
    def test_no_drift_data_dir(self, tmp_path):
        result = extract_training_patterns(str(tmp_path))
        assert result == []

    def test_with_drift_data_above_threshold(self, tmp_path):
        drift_dir = tmp_path / "data" / "drift"
        drift_dir.mkdir(parents=True)
        events = [
            {"detector_id": "det-001", "description": "issue 1"},
            {"detector_id": "det-001", "description": "issue 2"},
            {"detector_id": "det-001", "description": "issue 3"},
        ]
        data_file = drift_dir / "events.json"
        data_file.write_text(json.dumps(events), encoding="utf-8")
        patterns = extract_training_patterns(str(tmp_path), days=30)
        assert len(patterns) == 1
        assert patterns[0].detector_id == "det-001"
        assert patterns[0].frequency == 3

    def test_below_threshold_no_pattern(self, tmp_path):
        drift_dir = tmp_path / "data" / "drift"
        drift_dir.mkdir(parents=True)
        events = [{"detector_id": "det-002", "description": "rare"}]
        data_file = drift_dir / "events.json"
        data_file.write_text(json.dumps(events), encoding="utf-8")
        patterns = extract_training_patterns(str(tmp_path), days=30)
        assert len(patterns) == 0

    def test_old_events_excluded(self, tmp_path):
        drift_dir = tmp_path / "data" / "drift"
        drift_dir.mkdir(parents=True)
        old_ts = (datetime.now(UTC) - timedelta(days=60)).isoformat()
        events = [{"detector_id": "det-old", "description": "old", "timestamp": old_ts}]
        data_file = drift_dir / "old_events.json"
        data_file.write_text(json.dumps(events), encoding="utf-8")
        import os

        old_mtime = (datetime.now(UTC) - timedelta(days=60)).timestamp()
        os.utime(str(data_file), (old_mtime, old_mtime))
        patterns = extract_training_patterns(str(tmp_path), days=30)
        assert len(patterns) == 0

    def test_nested_events_format(self, tmp_path):
        drift_dir = tmp_path / "data" / "drift"
        drift_dir.mkdir(parents=True)
        data = {"events": [{"detector_id": "det-nest"}] * 4}
        data_file = drift_dir / "nested.json"
        data_file.write_text(json.dumps(data), encoding="utf-8")
        patterns = extract_training_patterns(str(tmp_path), days=30)
        assert len(patterns) == 1
        assert patterns[0].frequency == 4

    def test_malformed_json_skipped(self, tmp_path):
        drift_dir = tmp_path / "data" / "drift"
        drift_dir.mkdir(parents=True)
        bad_file = drift_dir / "bad.json"
        bad_file.write_text("not valid json{{{", encoding="utf-8")
        patterns = extract_training_patterns(str(tmp_path), days=30)
        assert patterns == []


class TestInjectPatternsToPrompt:
    def test_generates_markdown(self):
        patterns = [
            DriftTrainingPattern(
                pattern_id="p1",
                detector_id="det-001",
                frequency=5,
                dimension="D5",
                commit_diff_pattern="diff",
                root_cause_summary="root cause here",
            )
        ]
        result = inject_patterns_to_prompt(patterns)
        assert "## AI Error-Prone Patterns" in result
        assert "det-001" in result
        assert "freq=5" in result

    def test_empty_patterns(self):
        result = inject_patterns_to_prompt([])
        assert "## AI Error-Prone Patterns" in result
        assert "0 patterns" in result

    def test_limits_to_five_patterns(self):
        patterns = [
            DriftTrainingPattern(
                pattern_id=f"p{i}",
                detector_id=f"det-{i:03d}",
                frequency=i + 1,
                dimension="D5",
                commit_diff_pattern="",
                root_cause_summary=f"cause {i}",
            )
            for i in range(8)
        ]
        result = inject_patterns_to_prompt(patterns)
        assert "det-000" in result
        assert "det-004" in result

    def test_root_cause_truncated(self):
        long_cause = "x" * 300
        patterns = [
            DriftTrainingPattern(
                pattern_id="p1",
                detector_id="det-001",
                frequency=3,
                dimension="D5",
                commit_diff_pattern="",
                root_cause_summary=long_cause,
            )
        ]
        result = inject_patterns_to_prompt(patterns)
        for line in result.split("\n"):
            if "det-001" in line:
                assert len(line) < len(long_cause) + 100


class TestTrackTrainingEffectiveness:
    def test_full_suppression(self):
        pattern = DriftTrainingPattern(
            pattern_id="p1",
            detector_id="d1",
            frequency=10,
            dimension="D5",
            commit_diff_pattern="",
            root_cause_summary="",
        )
        effectiveness = track_training_effectiveness(pattern, 0)
        assert effectiveness == 1.0

    def test_partial_suppression(self):
        pattern = DriftTrainingPattern(
            pattern_id="p1",
            detector_id="d1",
            frequency=10,
            dimension="D5",
            commit_diff_pattern="",
            root_cause_summary="",
        )
        effectiveness = track_training_effectiveness(pattern, 5)
        assert effectiveness == 0.5

    def test_no_suppression(self):
        pattern = DriftTrainingPattern(
            pattern_id="p1",
            detector_id="d1",
            frequency=10,
            dimension="D5",
            commit_diff_pattern="",
            root_cause_summary="",
        )
        effectiveness = track_training_effectiveness(pattern, 10)
        assert effectiveness == 0.0

    def test_zero_frequency_boundary(self):
        pattern = DriftTrainingPattern(
            pattern_id="p1",
            detector_id="d1",
            frequency=0,
            dimension="D5",
            commit_diff_pattern="",
            root_cause_summary="",
        )
        effectiveness = track_training_effectiveness(pattern, 5)
        assert effectiveness == 0.0

    def test_negative_effectiveness_clamped(self):
        pattern = DriftTrainingPattern(
            pattern_id="p1",
            detector_id="d1",
            frequency=5,
            dimension="D5",
            commit_diff_pattern="",
            root_cause_summary="",
        )
        effectiveness = track_training_effectiveness(pattern, 10)
        assert effectiveness == 0.0

    def test_single_frequency(self):
        pattern = DriftTrainingPattern(
            pattern_id="p1",
            detector_id="d1",
            frequency=1,
            dimension="D5",
            commit_diff_pattern="",
            root_cause_summary="",
        )
        effectiveness = track_training_effectiveness(pattern, 0)
        assert effectiveness == 1.0


class TestParsePythonImports:
    def test_import_statements(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text("import os\nimport sys\nfrom pathlib import Path\n", encoding="utf-8")
        imports = parse_python_imports(str(py_file))
        assert "os" in imports
        assert "sys" in imports
        assert "pathlib" in imports

    def test_from_import(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text("from collections import OrderedDict\n", encoding="utf-8")
        imports = parse_python_imports(str(py_file))
        assert "collections" in imports

    def test_nonexistent_file(self):
        imports = parse_python_imports("/nonexistent/file.py")
        assert imports == []

    def test_empty_file(self, tmp_path):
        py_file = tmp_path / "empty.py"
        py_file.write_text("", encoding="utf-8")
        imports = parse_python_imports(str(py_file))
        assert imports == []

    def test_mixed_imports(self, tmp_path):
        py_file = tmp_path / "mixed.py"
        py_file.write_text(
            "import json\nfrom os.path import join\nimport re\nfrom re import match\n",
            encoding="utf-8",
        )
        imports = parse_python_imports(str(py_file))
        assert "json" in imports
        assert "os.path" in imports
        assert "re" in imports


class TestParsePythonPublicApi:
    def test_parse_public_functions(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text(
            "def public_func():\n    return 1\n\ndef _private_func():\n    return 2\n",
            encoding="utf-8",
        )
        apis = parse_python_public_api(str(py_file))
        assert "public_func" in apis
        assert "_private_func" not in apis

    def test_nonexistent_file(self):
        apis = parse_python_public_api("/nonexistent/file.py")
        assert apis == []

    def test_empty_file(self, tmp_path):
        py_file = tmp_path / "empty.py"
        py_file.write_text("", encoding="utf-8")
        apis = parse_python_public_api(str(py_file))
        assert apis == []

    def test_only_private_functions(self, tmp_path):
        py_file = tmp_path / "priv.py"
        py_file.write_text("def _helper():\n    return 0\n", encoding="utf-8")
        apis = parse_python_public_api(str(py_file))
        assert apis == []


class TestDetectPythonDeadCode:
    def test_detect_dead_code(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text(
            "def unused_func():\n    return 0\n\ndef used_func():\n    return 1\n\nx = used_func()\n",
            encoding="utf-8",
        )
        dead = detect_python_dead_code(str(py_file))
        assert "unused_func" in dead
        assert "used_func" not in dead

    def test_nonexistent_file(self):
        dead = detect_python_dead_code("/nonexistent/file.py")
        assert dead == []

    def test_all_used_functions(self, tmp_path):
        py_file = tmp_path / "all_used.py"
        py_file.write_text(
            "def add(a, b):\n    return a + b\n\ndef main():\n    return add(1, 2)\n\nresult = main()\n",
            encoding="utf-8",
        )
        dead = detect_python_dead_code(str(py_file))
        assert "add" not in dead
        assert "main" not in dead

    def test_private_functions_excluded(self, tmp_path):
        py_file = tmp_path / "priv.py"
        py_file.write_text("def _internal():\n    return 0\n", encoding="utf-8")
        dead = detect_python_dead_code(str(py_file))
        assert "_internal" not in dead

    def test_empty_file(self, tmp_path):
        py_file = tmp_path / "empty.py"
        py_file.write_text("", encoding="utf-8")
        dead = detect_python_dead_code(str(py_file))
        assert dead == []


class TestDetectAiTrainingLoop:
    def test_no_patterns_returns_empty(self, tmp_path):
        events = detect_ai_training_loop(str(tmp_path))
        assert events == []

    def test_no_drift_data_dir_returns_empty(self, tmp_path):
        empty_root = tmp_path / "empty_project"
        empty_root.mkdir()
        events = detect_ai_training_loop(str(empty_root))
        assert events == []


class TestDetectCrossLanguageDrift:
    def test_no_src_dir_returns_empty(self, tmp_path):
        events = detect_cross_language_drift(str(tmp_path))
        assert events == []

    def test_empty_src_dir_returns_empty(self, tmp_path):
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        events = detect_cross_language_drift(str(tmp_path))
        assert events == []


class TestLanguageConstants:
    def test_agnostic_dimensions_count(self):
        assert len(LANGUAGE_AGNOSTIC_DIMENSIONS) == 9

    def test_python_interfaces_defined(self):
        assert "Python" in LANGUAGE_SPECIFIC_INTERFACES
        assert len(LANGUAGE_SPECIFIC_INTERFACES["Python"]) == 3
        assert "parse_python_imports" in LANGUAGE_SPECIFIC_INTERFACES["Python"]
