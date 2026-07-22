# [A_test] module_id: MOD-GOV_skill_freshness | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_freshness
# [INVARIANTS] HOURS_TO_ZERO=720; WARNING_THRESHOLD=30.0; CRITICAL_THRESHOLD=10.0
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute returns 0.0 on invalid input
# [TESTS] pytest tests/test_skill_freshness.py -q
# [TTL] task_bound

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from zephyr.autonomy_core.skills.skill_freshness import FreshnessDecayModel


class TestFreshnessDecayModelInstantiation:
    def test_class_exists(self):
        assert FreshnessDecayModel is not None

    def test_can_instantiate(self):
        obj = FreshnessDecayModel()
        assert isinstance(obj, FreshnessDecayModel)

    def test_class_constants(self):
        assert FreshnessDecayModel.HOURS_TO_ZERO == 720
        assert FreshnessDecayModel.WARNING_THRESHOLD == 30.0
        assert FreshnessDecayModel.CRITICAL_THRESHOLD == 10.0

    def test_has_compute(self):
        assert callable(getattr(FreshnessDecayModel, "compute", None))

    def test_has_current_state(self):
        assert callable(getattr(FreshnessDecayModel, "current_state", None))

    def test_has_boost(self):
        assert callable(getattr(FreshnessDecayModel, "boost", None))


class TestCompute:
    def test_recent_timestamp_high_score(self):
        now = datetime.now(UTC).isoformat()
        score = FreshnessDecayModel.compute(now)
        assert score > 90.0

    def test_old_timestamp_low_score(self):
        old = (datetime.now(UTC) - timedelta(hours=600)).isoformat()
        score = FreshnessDecayModel.compute(old)
        assert score < 30.0

    def test_very_old_timestamp_zero(self):
        very_old = (datetime.now(UTC) - timedelta(hours=800)).isoformat()
        score = FreshnessDecayModel.compute(very_old)
        assert score == 0.0

    def test_invalid_string_returns_zero(self):
        score = FreshnessDecayModel.compute("not-a-date")
        assert score == 0.0

    def test_none_returns_zero(self):
        score = FreshnessDecayModel.compute(None)
        assert score == 0.0

    def test_empty_string_returns_zero(self):
        score = FreshnessDecayModel.compute("")
        assert score == 0.0

    def test_exactly_zero_hours(self):
        now = datetime.now(UTC).isoformat()
        score = FreshnessDecayModel.compute(now)
        assert score <= 100.0

    def test_half_life_approximate(self):
        half = (datetime.now(UTC) - timedelta(hours=360)).isoformat()
        score = FreshnessDecayModel.compute(half)
        assert 40.0 <= score <= 60.0


class TestCurrentState:
    def test_registered_skill(self):
        fdm = FreshnessDecayModel()
        now = datetime.now(UTC).isoformat()
        data = {"SKILL-REG": {"last_validated": now, "boost": 10.0}}
        with patch.object(fdm, "_load", return_value=data):
            state = fdm.current_state("SKILL-REG")
        assert state["registered"] is True
        assert state["freshness_score"] > 90.0
        assert state["skill_id"] == "SKILL-REG"

    def test_unregistered_skill(self):
        fdm = FreshnessDecayModel()
        with patch.object(fdm, "_load", return_value={}):
            state = fdm.current_state("SKILL-UNREG")
        assert state["registered"] is False
        assert state["freshness_score"] == 50.0

    def test_old_registered_skill(self):
        fdm = FreshnessDecayModel()
        old = (datetime.now(UTC) - timedelta(hours=700)).isoformat()
        data = {"SKILL-OLD": {"last_validated": old, "boost": 0.0}}
        with patch.object(fdm, "_load", return_value=data):
            state = fdm.current_state("SKILL-OLD")
        assert state["registered"] is True
        assert state["freshness_score"] < 10.0


class TestBoost:
    def test_boost_writes_to_history(self):
        fdm = FreshnessDecayModel()
        with patch.object(fdm, "_load", return_value={}), patch.object(fdm, "_save") as mock_save:
            fdm.boost("SKILL-BOOST", 25.0)
        mock_save.assert_called_once()
        saved_data = mock_save.call_args[0][0]
        assert "SKILL-BOOST" in saved_data
        assert saved_data["SKILL-BOOST"]["boost"] == 25.0

    def test_boost_default_amount(self):
        fdm = FreshnessDecayModel()
        with patch.object(fdm, "_load", return_value={}), patch.object(fdm, "_save") as mock_save:
            fdm.boost("SKILL-DEF-BOOST")
        saved_data = mock_save.call_args[0][0]
        assert saved_data["SKILL-DEF-BOOST"]["boost"] == 50.0

    def test_boost_sets_last_validated(self):
        fdm = FreshnessDecayModel()
        with patch.object(fdm, "_load", return_value={}), patch.object(fdm, "_save") as mock_save:
            fdm.boost("SKILL-LV")
        saved_data = mock_save.call_args[0][0]
        assert "last_validated" in saved_data["SKILL-LV"]


class TestLoadSave:
    def test_load_nonexistent_returns_empty(self, tmp_path):
        fdm = FreshnessDecayModel()
        with patch("zephyr.autonomy_core.skills.skill_freshness._HISTORY", tmp_path / "nonexistent.json"):
            result = fdm._load()
        assert result == {}

    def test_load_valid_json(self, tmp_path):
        hist = tmp_path / "freshness.json"
        hist.write_text(
            json.dumps({"SKILL-X": {"last_validated": "2025-01-01T00:00:00+00:00", "boost": 10}}), encoding="utf-8"
        )
        fdm = FreshnessDecayModel()
        with patch("zephyr.autonomy_core.skills.skill_freshness._HISTORY", hist):
            result = fdm._load()
        assert "SKILL-X" in result

    def test_load_corrupt_json_returns_empty(self, tmp_path):
        hist = tmp_path / "bad.json"
        hist.write_text("not valid json{{{", encoding="utf-8")
        fdm = FreshnessDecayModel()
        with patch("zephyr.autonomy_core.skills.skill_freshness._HISTORY", hist):
            result = fdm._load()
        assert result == {}

    def test_save_and_load_roundtrip(self, tmp_path):
        hist = tmp_path / "roundtrip.json"
        fdm = FreshnessDecayModel()
        data = {"SKILL-RT": {"last_validated": "2025-06-01T00:00:00+00:00", "boost": 30}}
        with patch("zephyr.autonomy_core.skills.skill_freshness._HISTORY", hist):
            fdm._save(data)
            loaded = fdm._load()
        assert loaded == data
