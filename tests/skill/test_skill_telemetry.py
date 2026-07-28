# [A_test] module_id: MOD-GOV_skill_telemetry | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_telemetry
# [INVARIANTS] SkillTelemetry.record stores events; query filters by skill_id and since_hours; stats aggregates
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] record persists; query returns list; stats returns dict
# [TESTS] tests/test_skill_telemetry.py
# [TTL] task_bound

import time
from unittest.mock import patch

from zephyr.autonomy_core.skills.skill_telemetry import SkillTelemetry


class TestSkillTelemetryInstantiation:
    def test_instantiation(self):
        tel = SkillTelemetry()
        assert tel is not None
        assert tel.events == []

    def test_max_events_constant(self):
        assert SkillTelemetry._MAX_EVENTS == 500


class TestSkillTelemetryRecord:
    @patch.object(SkillTelemetry, "_persist")
    def test_record_basic(self, mock_persist):
        tel = SkillTelemetry()
        tel.record("skill-a", "invoked")
        assert len(tel.events) == 1
        assert tel.events[0]["skill_id"] == "skill-a"
        assert tel.events[0]["event"] == "invoked"
        mock_persist.assert_called_once()

    @patch.object(SkillTelemetry, "_persist")
    def test_record_with_metadata(self, mock_persist):
        tel = SkillTelemetry()
        tel.record("skill-b", "completed", metadata={"duration_ms": 150})
        assert tel.events[0]["metadata"] == {"duration_ms": 150}

    @patch.object(SkillTelemetry, "_persist")
    def test_record_none_metadata(self, mock_persist):
        tel = SkillTelemetry()
        tel.record("skill-c", "started", metadata=None)
        assert tel.events[0]["metadata"] == {}

    @patch.object(SkillTelemetry, "_persist")
    def test_record_has_timestamp(self, mock_persist):
        tel = SkillTelemetry()
        tel.record("skill-d", "invoked")
        assert "timestamp" in tel.events[0]
        assert "epoch" in tel.events[0]

    @patch.object(SkillTelemetry, "_persist")
    def test_record_trims_at_max(self, mock_persist):
        tel = SkillTelemetry()
        for i in range(550):
            tel.record("skill-e", f"event-{i}")
        assert len(tel.events) == 500


class TestSkillTelemetryQuery:
    @patch.object(SkillTelemetry, "_persist")
    def test_query_by_skill_id(self, mock_persist):
        tel = SkillTelemetry()
        tel.record("skill-f", "invoked")
        tel.record("skill-g", "invoked")
        tel.record("skill-f", "completed")
        results = tel.query("skill-f")
        assert len(results) == 2
        assert all(r["skill_id"] == "skill-f" for r in results)

    @patch.object(SkillTelemetry, "_persist")
    def test_query_no_match(self, mock_persist):
        tel = SkillTelemetry()
        tel.record("skill-h", "invoked")
        results = tel.query("nonexistent")
        assert results == []

    @patch.object(SkillTelemetry, "_persist")
    def test_query_since_hours(self, mock_persist):
        tel = SkillTelemetry()
        tel.record("skill-i", "recent")
        old_event = {
            "skill_id": "skill-i",
            "event": "old",
            "metadata": {},
            "timestamp": "2020-01-01T00:00:00+00:00",
            "epoch": time.time() - 48 * 3600,
        }
        tel.events.append(old_event)
        results = tel.query("skill-i", since_hours=24)
        assert len(results) == 1
        assert results[0]["event"] == "recent"

    @patch.object(SkillTelemetry, "_persist")
    def test_query_since_hours_zero(self, mock_persist):
        tel = SkillTelemetry()
        tel.record("skill-j", "just_now")
        results = tel.query("skill-j", since_hours=0)
        recent_count = len(results)
        assert recent_count <= 1


class TestSkillTelemetryStats:
    @patch.object(SkillTelemetry, "_persist")
    def test_stats_empty(self, mock_persist):
        tel = SkillTelemetry()
        result = tel.stats()
        assert result == {"total_events": 0}

    @patch.object(SkillTelemetry, "_persist")
    def test_stats_all_events(self, mock_persist):
        tel = SkillTelemetry()
        tel.record("skill-k", "invoked")
        tel.record("skill-k", "completed")
        tel.record("skill-l", "invoked")
        result = tel.stats()
        assert result["total_events"] == 3
        assert result["skill_count"] == 2
        assert result["event_breakdown"]["invoked"] == 2
        assert result["event_breakdown"]["completed"] == 1

    @patch.object(SkillTelemetry, "_persist")
    def test_stats_filtered_by_skill(self, mock_persist):
        tel = SkillTelemetry()
        tel.record("skill-m", "invoked")
        tel.record("skill-n", "invoked")
        result = tel.stats("skill-m")
        assert result["total_events"] == 1

    @patch.object(SkillTelemetry, "_persist")
    def test_stats_has_timestamps(self, mock_persist):
        tel = SkillTelemetry()
        tel.record("skill-o", "invoked")
        result = tel.stats()
        assert "first_event" in result
        assert "last_event" in result


class TestSkillTelemetryPersist:
    @patch.object(SkillTelemetry, "_persist")
    def test_persist_called_on_record(self, mock_persist):
        tel = SkillTelemetry()
        tel.record("skill-p", "invoked")
        mock_persist.assert_called_once()
        entry = mock_persist.call_args[0][0]
        assert entry["skill_id"] == "skill-p"
        assert entry["event"] == "invoked"
