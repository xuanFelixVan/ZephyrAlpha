# [A_test] module_id: SRC-TST-1737 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_test_fixture_checker
# [INVARIANTS] 测试夹具检查不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_drift.test_fixture_checker import (
    FixtureDriftEvent,
    run_fixture_check,
    scan_expected_output_drift,
    scan_fixture_schema_drift,
    scan_mock_target_drift,
)


class TestFixtureDriftEvent:
    def test_instantiation(self):
        evt = FixtureDriftEvent(
            event_id="fixture-dict-test-myvar",
            fixture_file="/tests/test_foo.py",
            fixture_type="dict_fixture",
            target_module="myvar",
        )
        assert evt.severity == "MAJOR"
        assert evt.detected_at is not None

    def test_custom_severity(self):
        evt = FixtureDriftEvent(
            event_id="test",
            fixture_file="/t.py",
            fixture_type="mock_target",
            target_module="mod",
            severity="MINOR",
        )
        assert evt.severity == "MINOR"


class TestScanFixtureSchemaDrift:
    def test_detects_dict_fixture_with_many_fields(self, tmp_path):
        test_file = tmp_path / "test_example.py"
        test_file.write_text(
            "my_data = {'name': 'x', 'age': 30, 'city': 'y', 'zip': 'z'}\n",
            encoding="utf-8",
        )
        events = scan_fixture_schema_drift(str(tmp_path), str(tmp_path))
        dict_events = [e for e in events if e.fixture_type == "dict_fixture"]
        assert len(dict_events) >= 1

    def test_ignores_small_dict_fixture(self, tmp_path):
        test_file = tmp_path / "test_small.py"
        test_file.write_text(
            "small = {'a': 1, 'b': 2}\n",
            encoding="utf-8",
        )
        events = scan_fixture_schema_drift(str(tmp_path), str(tmp_path))
        dict_events = [e for e in events if e.fixture_type == "dict_fixture"]
        assert len(dict_events) == 0

    def test_detects_mock_patch(self, tmp_path):
        test_file = tmp_path / "test_mock.py"
        test_file.write_text(
            "from unittest.mock import patch\n"
            "@patch('zephyr.some.module.ClassName')\n"
            "def test_something(mock_cls):\n    pass\n",
            encoding="utf-8",
        )
        events = scan_fixture_schema_drift(str(tmp_path), str(tmp_path))
        mock_events = [e for e in events if e.fixture_type == "mock_target"]
        assert len(mock_events) >= 1

    def test_empty_directory_returns_empty(self, tmp_path):
        events = scan_fixture_schema_drift(str(tmp_path), str(tmp_path))
        assert events == []

    def test_non_test_files_ignored(self, tmp_path):
        helper = tmp_path / "helper.py"
        helper.write_text(
            "big = {'a': 1, 'b': 2, 'c': 3, 'd': 4}\n",
            encoding="utf-8",
        )
        events = scan_fixture_schema_drift(str(tmp_path), str(tmp_path))
        assert events == []


class TestScanMockTargetDrift:
    def test_detects_orphan_mock(self, tmp_path):
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "real.py").write_text("x = 1", encoding="utf-8")
        test_file = test_dir / "test_orphan.py"
        test_file.write_text(
            "from unittest.mock import patch\n@patch('nonexistent.module.Class')\ndef test_x(m):\n    pass\n",
            encoding="utf-8",
        )
        events = scan_mock_target_drift(str(test_dir), str(src_dir))
        assert len(events) >= 1

    def test_no_events_for_simple_mock_without_dot(self, tmp_path):
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "app.py").write_text("class Foo: pass", encoding="utf-8")
        test_file = test_dir / "test_app.py"
        test_file.write_text(
            "from unittest.mock import patch\n@patch('simplemodule')\ndef test_x(m):\n    pass\n",
            encoding="utf-8",
        )
        events = scan_mock_target_drift(str(test_dir), str(src_dir))
        assert len(events) == 0

    def test_empty_dirs_return_empty(self, tmp_path):
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        events = scan_mock_target_drift(str(test_dir), str(src_dir))
        assert events == []


class TestScanExpectedOutputDrift:
    def test_detects_unannotated_long_assert(self, tmp_path):
        test_file = tmp_path / "test_output.py"
        test_file.write_text(
            "def test_long():\n"
            "    result = some_function()\n"
            "    assert result == 'this is a very long expected output value that exceeds fifty characters total'\n",
            encoding="utf-8",
        )
        events = scan_expected_output_drift(str(tmp_path))
        assert len(events) >= 1

    def test_annotated_assert_not_flagged(self, tmp_path):
        test_file = tmp_path / "test_annotated.py"
        test_file.write_text(
            "def test_annotated():\n"
            "    result = some_function()\n"
            "    assert result == 'this is a very long expected output value that exceeds fifty chars'  # from baseline\n",
            encoding="utf-8",
        )
        events = scan_expected_output_drift(str(tmp_path))
        assert len(events) == 0

    def test_short_assert_not_flagged(self, tmp_path):
        test_file = tmp_path / "test_short.py"
        test_file.write_text(
            "def test_short():\n    assert 1 + 1 == 2\n",
            encoding="utf-8",
        )
        events = scan_expected_output_drift(str(tmp_path))
        assert len(events) == 0

    def test_empty_dir_returns_empty(self, tmp_path):
        events = scan_expected_output_drift(str(tmp_path))
        assert events == []


class TestRunFixtureCheck:
    def test_returns_dict_with_required_keys(self, tmp_path):
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        results = run_fixture_check(str(tmp_path))
        assert "schema_drifts" in results
        assert "mock_drifts" in results
        assert "output_drifts" in results
        assert "summary" in results

    def test_summary_has_total(self, tmp_path):
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        results = run_fixture_check(str(tmp_path))
        assert "total" in results["summary"]
        assert "auto_fixable" in results["summary"]
        assert results["summary"]["auto_fixable"] is False

    def test_schema_drifts_is_list(self, tmp_path):
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        results = run_fixture_check(str(tmp_path))
        assert isinstance(results["schema_drifts"], list)
        assert isinstance(results["mock_drifts"], list)
        assert isinstance(results["output_drifts"], list)
