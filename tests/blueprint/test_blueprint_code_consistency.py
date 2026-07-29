# [A_test] module_id: MOD-GOV_blueprint_code_consistency | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §

# [MODULE] tests.test_blueprint_code_consistency

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] pytest

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] all tests must pass; no external dependencies beyond src tree

# [TESTS] python -m pytest tests/test_blueprint_code_consistency.py -q
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import patch

import pytest

from zephyr.governance.architecture_governance.blueprint_code_consistency import (
    DECISION_MAP,
    DecisionMapping,
    DecisionStatus,
    _file_exists,
    _verify_module_exists,
    check_blueprint_consistency,
    check_consistency,
    main,
)


class TestDecisionStatus:
    def test_enum_values(self):
        assert DecisionStatus.IMPLEMENTED.value == "implemented"
        assert DecisionStatus.IN_PROGRESS.value == "in_progress"
        assert DecisionStatus.BACKLOG.value == "backlog"
        assert DecisionStatus.OWNER_ONLY.value == "owner_only"
        assert DecisionStatus.PHASE_GATED.value == "phase_gated"

    def test_enum_is_str(self):
        for member in DecisionStatus:
            assert isinstance(member, str)
            assert isinstance(member.value, str)

    def test_enum_member_count(self):
        assert len(DecisionStatus) == 5

    def test_enum_from_value(self):
        assert DecisionStatus("implemented") is DecisionStatus.IMPLEMENTED
        assert DecisionStatus("backlog") is DecisionStatus.BACKLOG

    def test_enum_invalid_value_raises(self):
        with pytest.raises(ValueError):
            DecisionStatus("nonexistent")


class TestDecisionMapping:
    def test_instantiation_all_fields(self):
        dm = DecisionMapping(
            decision_id="D-TEST-01",
            title="Test Decision",
            status=DecisionStatus.IMPLEMENTED,
            code_module="zephyr.test.module",
            notes="test notes",
        )
        assert dm.decision_id == "D-TEST-01"
        assert dm.title == "Test Decision"
        assert dm.status is DecisionStatus.IMPLEMENTED
        assert dm.code_module == "zephyr.test.module"
        assert dm.notes == "test notes"

    def test_instantiation_defaults(self):
        dm = DecisionMapping(
            decision_id="D-TEST-02",
            title="Minimal",
            status=DecisionStatus.BACKLOG,
        )
        assert dm.code_module == ""
        assert dm.notes == ""

    def test_instantiation_missing_required_field_raises(self):
        with pytest.raises(TypeError):
            DecisionMapping(title="no id")
        with pytest.raises(TypeError):
            DecisionMapping(decision_id="D-X", status=DecisionStatus.BACKLOG)

    def test_is_dataclass(self):
        from dataclasses import fields

        field_names = [f.name for f in fields(DecisionMapping)]
        assert "decision_id" in field_names
        assert "status" in field_names
        assert "code_module" in field_names
        assert "notes" in field_names


class TestVerifyModuleExists:
    def test_existing_stdlib_module(self):
        assert _verify_module_exists("json") is True

    def test_empty_string_returns_false(self):
        assert _verify_module_exists("") is False

    def test_nonexistent_module_falls_back_to_file_check(self):
        with patch(
            "zephyr.governance.architecture_governance.blueprint_code_consistency.file_exists",
            return_value=False,
        ):
            assert _verify_module_exists("totally.fake.module.xyz") is False

    def test_import_error_triggers_file_check(self):
        with patch(
            "zephyr.governance.architecture_governance.blueprint_code_consistency.file_exists",
            return_value=True,
        ):
            assert _verify_module_exists("fake.module.that.cannot.import") is True

    def test_import_error_file_check_also_false(self):
        with patch(
            "zephyr.governance.architecture_governance.blueprint_code_consistency.file_exists",
            return_value=False,
        ):
            assert _verify_module_exists("fake.module.no.file") is False


class TestFileExists:
    def test_existing_file(self, tmp_path, monkeypatch):
        pkg_dir = tmp_path / "src" / "zephyr" / "mypkg"
        pkg_dir.mkdir(parents=True)
        (pkg_dir / "mymod.py").write_text("x = 1", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        assert _file_exists("zephyr.mypkg.mymod") is True

    def test_nonexistent_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert _file_exists("zephyr.nonexistent.module") is False

    def test_empty_path_raises(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError):
            _file_exists("")


class TestCheckConsistency:
    def test_returns_tuple(self):
        result = check_consistency()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_drift_count_is_int(self):
        drift_count, results = check_consistency()
        assert isinstance(drift_count, int)
        assert drift_count >= 0

    def test_results_is_list_of_dicts(self):
        _, results = check_consistency()
        assert isinstance(results, list)
        assert len(results) > 0
        for r in results:
            assert isinstance(r, dict)
            assert "decision_id" in r
            assert "title" in r
            assert "status" in r
            assert "code_module" in r
            assert "module_found" in r
            assert "drift" in r

    def test_drift_flag_logic(self):
        _, results = check_consistency()
        for r in results:
            if r["status"] == "implemented" and not r["module_found"]:
                assert r["drift"] is True
            else:
                assert r["drift"] is False

    def test_all_decision_map_entries_checked(self):
        _, results = check_consistency()
        assert len(results) == len(DECISION_MAP)

    def test_backlog_without_module_not_drift(self):
        dm = DecisionMapping(
            decision_id="D-BKLG-01",
            title="Backlog item",
            status=DecisionStatus.BACKLOG,
            code_module="",
        )
        with patch(
            "zephyr.governance.architecture_governance.blueprint_code_consistency.DECISION_MAP",
            [dm],
        ):
            drift_count, results = check_consistency()
            assert drift_count == 0
            assert results[0]["drift"] is False

    def test_implemented_missing_module_is_drift(self):
        dm = DecisionMapping(
            decision_id="D-DRFT-01",
            title="Drift item",
            status=DecisionStatus.IMPLEMENTED,
            code_module="totally.nonexistent.module",
        )
        with patch(
            "zephyr.governance.architecture_governance.blueprint_code_consistency.DECISION_MAP",
            [dm],
        ):
            drift_count, results = check_consistency()
            assert drift_count == 1
            assert results[0]["drift"] is True

    def test_implemented_with_module_no_drift(self):
        dm = DecisionMapping(
            decision_id="D-OK-01",
            title="OK item",
            status=DecisionStatus.IMPLEMENTED,
            code_module="json",
        )
        with patch(
            "zephyr.governance.architecture_governance.blueprint_code_consistency.DECISION_MAP",
            [dm],
        ):
            drift_count, results = check_consistency()
            assert drift_count == 0
            assert results[0]["drift"] is False

    def test_in_progress_not_drift(self):
        dm = DecisionMapping(
            decision_id="D-IP-01",
            title="In progress",
            status=DecisionStatus.IN_PROGRESS,
            code_module="totally.nonexistent.module",
        )
        with patch(
            "zephyr.governance.architecture_governance.blueprint_code_consistency.DECISION_MAP",
            [dm],
        ):
            drift_count, results = check_consistency()
            assert drift_count == 0
            assert results[0]["drift"] is False

    def test_empty_decision_map(self):
        with patch(
            "zephyr.governance.architecture_governance.blueprint_code_consistency.DECISION_MAP",
            [],
        ):
            drift_count, results = check_consistency()
            assert drift_count == 0
            assert results == []


class TestCheckBlueprintConsistencyAlias:
    def test_alias_is_same_function(self):
        assert check_blueprint_consistency is check_consistency

    def test_alias_returns_same_result(self):
        assert check_blueprint_consistency() == check_consistency()


class TestMain:
    def test_main_no_drift_returns_zero(self, capsys):
        dm = DecisionMapping(
            decision_id="D-OK",
            title="OK",
            status=DecisionStatus.IMPLEMENTED,
            code_module="json",
        )
        with patch(
            "zephyr.governance.architecture_governance.blueprint_code_consistency.DECISION_MAP",
            [dm],
        ):
            ret = main()
        assert ret == 0
        captured = capsys.readouterr()
        assert "OK" in captured.out or "1 decisions" in captured.out

    def test_main_with_drift_returns_one(self, capsys):
        dm = DecisionMapping(
            decision_id="D-DRIFT",
            title="Drift",
            status=DecisionStatus.IMPLEMENTED,
            code_module="totally.nonexistent.module",
        )
        with patch(
            "zephyr.governance.architecture_governance.blueprint_code_consistency.DECISION_MAP",
            [dm],
        ):
            ret = main()
        assert ret == 1
        captured = capsys.readouterr()
        assert "Drift alerts: 1" in captured.out

    def test_main_json_flag(self, capsys):
        dm = DecisionMapping(
            decision_id="D-OK",
            title="OK",
            status=DecisionStatus.IMPLEMENTED,
            code_module="json",
        )
        with (
            patch(
                "zephyr.governance.architecture_governance.blueprint_code_consistency.DECISION_MAP",
                [dm],
            ),
            patch("sys.argv", ["prog", "--json"]),
        ):
            ret = main()
        assert ret == 0
        import json

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "drift_count" in data
        assert "decisions" in data

    def test_main_empty_map_returns_zero(self, capsys):
        with patch(
            "zephyr.governance.architecture_governance.blueprint_code_consistency.DECISION_MAP",
            [],
        ):
            ret = main()
        assert ret == 0
        captured = capsys.readouterr()
        assert "0 decisions" in captured.out

    def test_main_output_status_counts(self, capsys):
        dms = [
            DecisionMapping("D-1", "A", DecisionStatus.IMPLEMENTED, "json"),
            DecisionMapping("D-2", "B", DecisionStatus.IN_PROGRESS, "fake.mod"),
            DecisionMapping("D-3", "C", DecisionStatus.BACKLOG),
            DecisionMapping("D-4", "D", DecisionStatus.OWNER_ONLY),
            DecisionMapping("D-5", "E", DecisionStatus.PHASE_GATED),
        ]
        with patch(
            "zephyr.governance.architecture_governance.blueprint_code_consistency.DECISION_MAP",
            dms,
        ):
            ret = main()
        captured = capsys.readouterr()
        assert "Implemented:  1" in captured.out
        assert "In Progress:  1" in captured.out
        assert "Backlog:      1" in captured.out
        assert "Owner/Phase:  2" in captured.out
