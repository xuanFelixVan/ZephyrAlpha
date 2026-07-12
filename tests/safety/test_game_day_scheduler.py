# [A_test] module_id: SRC-TST-2129 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §16
# [MODULE] zephyr.security.adversarial_validation.game_day_scheduler
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_game_day_scheduler.py
# [TTL] task_bound

import pytest
import yaml
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch
from zephyr.shared.io.paths import REPO_ROOT

scheduler_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.game_day_scheduler",
    reason="game_day_scheduler not available",
)
GameDayScheduler = scheduler_mod.GameDayScheduler
ScheduleConflictError = scheduler_mod.ScheduleConflictError
_TRIGGER_MAP = scheduler_mod._TRIGGER_MAP

gameday_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.game_day_runner",
    reason="game_day_runner not available",
)
GameDayRunner = gameday_mod.GameDayRunner
GameDayFrequency = gameday_mod.GameDayFrequency

models_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.models",
    reason="models not available",
)
GameDayResult = models_mod.GameDayResult

scenario_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.scenario_loader",
    reason="scenario_loader not available",
)
ScenarioLoader = scenario_mod.ScenarioLoader

_PROJECT_ROOT = REPO_ROOT
_SCENARIO_REGISTRY_PATH = (
    _PROJECT_ROOT
    / "src"
    / "zephyr"
    / "security"
    / "adversarial_validation"
    / "_scenario-registry.yaml"
)


def _make_result(total=5, blocked=4, bypassed=1):
    return GameDayResult(total_attacks=total, passed=blocked, bypasses=bypassed)


@pytest.fixture
def mock_runner():
    runner = MagicMock()
    runner.run_game_day.return_value = _make_result()
    return runner


@pytest.fixture
def scheduler(tmp_path, mock_runner):
    state_path = tmp_path / "scheduler-state.yaml"
    with patch(
        "zephyr.security.adversarial_validation.game_day_scheduler.GameDayRunner",
        return_value=mock_runner,
    ):
        sched = GameDayScheduler(state_path=state_path)
    return sched


# ============================================================
# 导入与类结构验证
# ============================================================


class TestGameDaySchedulerImport:
    def test_import_success(self):
        assert GameDayScheduler is not None

    def test_schedule_conflict_error_class(self):
        assert issubclass(ScheduleConflictError, RuntimeError)

    def test_scheduler_has_trigger_method(self):
        assert hasattr(GameDayScheduler, "trigger")

    def test_scheduler_has_handle_webhook_method(self):
        assert hasattr(GameDayScheduler, "handle_webhook")

    def test_scheduler_has_last_run_method(self):
        assert hasattr(GameDayScheduler, "last_run")

    def test_scheduler_has_next_scheduled_method(self):
        assert hasattr(GameDayScheduler, "next_scheduled")

    def test_scheduler_has_should_run_method(self):
        assert hasattr(GameDayScheduler, "_should_run")

    def test_scheduler_has_is_running_method(self):
        assert hasattr(GameDayScheduler, "_is_running")

    def test_scheduler_has_record_run_method(self):
        assert hasattr(GameDayScheduler, "_record_run")


class TestTriggerMap:
    def test_trigger_map_contains_all_triggers(self):
        assert "git_push" in _TRIGGER_MAP
        assert "cron_daily" in _TRIGGER_MAP
        assert "cron_weekly" in _TRIGGER_MAP
        assert "cron_monthly" in _TRIGGER_MAP
        assert "full_cycle" in _TRIGGER_MAP

    def test_trigger_map_git_push_maps_to_per_commit(self):
        assert _TRIGGER_MAP["git_push"] == [GameDayFrequency.PER_COMMIT]

    def test_trigger_map_cron_daily_maps_to_daily(self):
        assert _TRIGGER_MAP["cron_daily"] == [GameDayFrequency.DAILY]

    def test_trigger_map_cron_weekly_maps_to_weekly(self):
        assert _TRIGGER_MAP["cron_weekly"] == [GameDayFrequency.WEEKLY]

    def test_trigger_map_cron_monthly_maps_to_monthly(self):
        assert _TRIGGER_MAP["cron_monthly"] == [GameDayFrequency.MONTHLY]

    def test_trigger_map_full_cycle_maps_to_all_four(self):
        assert _TRIGGER_MAP["full_cycle"] == [
            GameDayFrequency.PER_COMMIT,
            GameDayFrequency.DAILY,
            GameDayFrequency.WEEKLY,
            GameDayFrequency.MONTHLY,
        ]

    def test_trigger_map_has_five_entries(self):
        assert len(_TRIGGER_MAP) == 5


# ============================================================
# trigger() 4级频率触发验证
# ============================================================


class TestTriggerPerCommit:
    def test_trigger_git_push_returns_results(self, scheduler):
        results = scheduler.trigger("git_push")
        assert len(results) == 1
        assert results[0]["frequency"] == "per_commit"
        assert results[0]["total"] == 5
        assert results[0]["blocked"] == 4
        assert results[0]["bypassed"] == 1

    def test_trigger_git_push_calls_runner_with_per_commit(self, scheduler, mock_runner):
        scheduler.trigger("git_push")
        mock_runner.run_game_day.assert_called_once_with(GameDayFrequency.PER_COMMIT)

    def test_trigger_git_push_records_last_run(self, scheduler):
        scheduler.trigger("git_push")
        assert scheduler.last_run(GameDayFrequency.PER_COMMIT) is not None

    def test_trigger_git_push_records_history(self, scheduler):
        scheduler.trigger("git_push")
        assert len(scheduler._state["history"]) == 1
        entry = scheduler._state["history"][0]
        assert entry["frequency"] == "per_commit"


class TestTriggerDaily:
    def test_trigger_cron_daily_returns_results(self, scheduler):
        results = scheduler.trigger("cron_daily")
        assert len(results) == 1
        assert results[0]["frequency"] == "daily"

    def test_trigger_cron_daily_calls_runner_with_daily(self, scheduler, mock_runner):
        scheduler.trigger("cron_daily")
        mock_runner.run_game_day.assert_called_once_with(GameDayFrequency.DAILY)

    def test_trigger_cron_daily_records_last_run(self, scheduler):
        scheduler.trigger("cron_daily")
        assert scheduler.last_run(GameDayFrequency.DAILY) is not None


class TestTriggerWeekly:
    def test_trigger_cron_weekly_returns_results(self, scheduler):
        results = scheduler.trigger("cron_weekly")
        assert len(results) == 1
        assert results[0]["frequency"] == "weekly"

    def test_trigger_cron_weekly_calls_runner_with_weekly(self, scheduler, mock_runner):
        scheduler.trigger("cron_weekly")
        mock_runner.run_game_day.assert_called_once_with(GameDayFrequency.WEEKLY)

    def test_trigger_cron_weekly_records_last_run(self, scheduler):
        scheduler.trigger("cron_weekly")
        assert scheduler.last_run(GameDayFrequency.WEEKLY) is not None


class TestTriggerMonthly:
    def test_trigger_cron_monthly_returns_results(self, scheduler):
        results = scheduler.trigger("cron_monthly")
        assert len(results) == 1
        assert results[0]["frequency"] == "monthly"

    def test_trigger_cron_monthly_calls_runner_with_monthly(self, scheduler, mock_runner):
        scheduler.trigger("cron_monthly")
        mock_runner.run_game_day.assert_called_once_with(GameDayFrequency.MONTHLY)

    def test_trigger_cron_monthly_records_last_run(self, scheduler):
        scheduler.trigger("cron_monthly")
        assert scheduler.last_run(GameDayFrequency.MONTHLY) is not None


class TestTriggerFullCycle:
    def test_trigger_full_cycle_returns_four_results(self, scheduler):
        results = scheduler.trigger("full_cycle")
        assert len(results) == 4

    def test_trigger_full_cycle_covers_all_frequencies(self, scheduler):
        results = scheduler.trigger("full_cycle")
        freqs = [r["frequency"] for r in results]
        assert "per_commit" in freqs
        assert "daily" in freqs
        assert "weekly" in freqs
        assert "monthly" in freqs

    def test_trigger_full_cycle_calls_runner_four_times(self, scheduler, mock_runner):
        scheduler.trigger("full_cycle")
        assert mock_runner.run_game_day.call_count == 4

    def test_trigger_full_cycle_records_all_last_runs(self, scheduler):
        scheduler.trigger("full_cycle")
        assert scheduler.last_run(GameDayFrequency.PER_COMMIT) is not None
        assert scheduler.last_run(GameDayFrequency.DAILY) is not None
        assert scheduler.last_run(GameDayFrequency.WEEKLY) is not None
        assert scheduler.last_run(GameDayFrequency.MONTHLY) is not None

    def test_trigger_full_cycle_history_has_four_entries(self, scheduler):
        scheduler.trigger("full_cycle")
        assert len(scheduler._state["history"]) == 4


class TestTriggerUnknown:
    def test_trigger_unknown_returns_empty_list(self, scheduler):
        results = scheduler.trigger("unknown_trigger")
        assert results == []

    def test_trigger_unknown_does_not_call_runner(self, scheduler, mock_runner):
        scheduler.trigger("unknown_trigger")
        mock_runner.run_game_day.assert_not_called()

    def test_trigger_empty_string_returns_empty_list(self, scheduler):
        results = scheduler.trigger("")
        assert results == []


# ============================================================
# _is_running() 防重叠机制验证
# ============================================================


class TestTriggerOverlapProtection:
    def test_trigger_raises_conflict_when_running(self, scheduler):
        scheduler._set_running(True)
        with pytest.raises(ScheduleConflictError):
            scheduler.trigger("cron_daily")

    def test_trigger_raises_conflict_for_git_push_when_running(self, scheduler):
        scheduler._set_running(True)
        with pytest.raises(ScheduleConflictError):
            scheduler.trigger("git_push")

    def test_trigger_raises_conflict_for_full_cycle_when_running(self, scheduler):
        scheduler._set_running(True)
        with pytest.raises(ScheduleConflictError):
            scheduler.trigger("full_cycle")

    def test_trigger_resets_running_flag_after_success(self, scheduler):
        scheduler.trigger("cron_daily")
        assert scheduler._is_running() is False

    def test_trigger_resets_running_flag_on_exception(self, scheduler, mock_runner):
        mock_runner.run_game_day.side_effect = RuntimeError("boom")
        with pytest.raises(RuntimeError):
            scheduler.trigger("cron_daily")
        assert scheduler._is_running() is False


class TestIsRunning:
    def test_is_running_default_false(self, scheduler):
        assert scheduler._is_running() is False

    def test_set_running_true(self, scheduler):
        scheduler._set_running(True)
        assert scheduler._is_running() is True

    def test_set_running_false_after_true(self, scheduler):
        scheduler._set_running(True)
        scheduler._set_running(False)
        assert scheduler._is_running() is False

    def test_set_running_persists_to_state_file(self, scheduler, tmp_path):
        scheduler._set_running(True)
        state_path = tmp_path / "scheduler-state.yaml"
        with open(state_path, encoding="utf-8") as f:
            state = yaml.safe_load(f)
        assert state["running"] is True

    def test_set_running_updates_updated_at(self, scheduler):
        old_updated = scheduler._state.get("updated_at", "")
        scheduler._set_running(True)
        assert scheduler._state["updated_at"] != old_updated


# ============================================================
# _should_run() 时间间隔判断验证
# ============================================================


class TestShouldRun:
    def test_should_run_true_when_no_last_run(self, scheduler):
        assert scheduler._should_run(GameDayFrequency.DAILY) is True

    def test_should_run_true_when_no_last_run_per_commit(self, scheduler):
        assert scheduler._should_run(GameDayFrequency.PER_COMMIT) is True

    def test_should_run_true_when_no_last_run_weekly(self, scheduler):
        assert scheduler._should_run(GameDayFrequency.WEEKLY) is True

    def test_should_run_true_when_no_last_run_monthly(self, scheduler):
        assert scheduler._should_run(GameDayFrequency.MONTHLY) is True

    def test_should_run_false_when_within_daily_interval(self, scheduler):
        scheduler._state["last_runs"]["daily"] = datetime.now(UTC).isoformat()
        assert scheduler._should_run(GameDayFrequency.DAILY) is False

    def test_should_run_true_when_past_daily_interval(self, scheduler):
        scheduler._state["last_runs"]["daily"] = (
            datetime.now(UTC) - timedelta(days=2)
        ).isoformat()
        assert scheduler._should_run(GameDayFrequency.DAILY) is True

    def test_should_run_false_when_within_per_commit_interval(self, scheduler):
        scheduler._state["last_runs"]["per_commit"] = (
            datetime.now(UTC) - timedelta(minutes=1)
        ).isoformat()
        assert scheduler._should_run(GameDayFrequency.PER_COMMIT) is False

    def test_should_run_true_when_past_per_commit_interval(self, scheduler):
        scheduler._state["last_runs"]["per_commit"] = (
            datetime.now(UTC) - timedelta(minutes=6)
        ).isoformat()
        assert scheduler._should_run(GameDayFrequency.PER_COMMIT) is True

    def test_should_run_false_when_within_weekly_interval(self, scheduler):
        scheduler._state["last_runs"]["weekly"] = (
            datetime.now(UTC) - timedelta(days=1)
        ).isoformat()
        assert scheduler._should_run(GameDayFrequency.WEEKLY) is False

    def test_should_run_true_when_past_weekly_interval(self, scheduler):
        scheduler._state["last_runs"]["weekly"] = (
            datetime.now(UTC) - timedelta(days=8)
        ).isoformat()
        assert scheduler._should_run(GameDayFrequency.WEEKLY) is True

    def test_should_run_false_when_within_monthly_interval(self, scheduler):
        scheduler._state["last_runs"]["monthly"] = (
            datetime.now(UTC) - timedelta(days=10)
        ).isoformat()
        assert scheduler._should_run(GameDayFrequency.MONTHLY) is False

    def test_should_run_true_when_past_monthly_interval(self, scheduler):
        scheduler._state["last_runs"]["monthly"] = (
            datetime.now(UTC) - timedelta(days=31)
        ).isoformat()
        assert scheduler._should_run(GameDayFrequency.MONTHLY) is True


class TestTriggerShouldRunSkip:
    def test_trigger_skips_when_within_interval(self, scheduler, mock_runner):
        scheduler._state["last_runs"]["daily"] = datetime.now(UTC).isoformat()
        results = scheduler.trigger("cron_daily")
        assert results == []
        mock_runner.run_game_day.assert_not_called()

    def test_trigger_partial_skip_in_full_cycle(self, scheduler, mock_runner):
        scheduler._state["last_runs"]["daily"] = datetime.now(UTC).isoformat()
        results = scheduler.trigger("full_cycle")
        freqs = [r["frequency"] for r in results]
        assert "daily" not in freqs
        assert "per_commit" in freqs
        assert "weekly" in freqs
        assert "monthly" in freqs
        assert mock_runner.run_game_day.call_count == 3


# ============================================================
# handle_webhook() 事件处理验证
# ============================================================


class TestHandleWebhook:
    def test_webhook_push_triggers_git_push(self, scheduler, mock_runner):
        results = scheduler.handle_webhook("push")
        assert len(results) == 1
        assert results[0]["frequency"] == "per_commit"
        mock_runner.run_game_day.assert_called_once_with(GameDayFrequency.PER_COMMIT)

    def test_webhook_schedule_triggers_cron_daily(self, scheduler, mock_runner):
        results = scheduler.handle_webhook("schedule")
        assert len(results) == 1
        assert results[0]["frequency"] == "daily"
        mock_runner.run_game_day.assert_called_once_with(GameDayFrequency.DAILY)

    def test_webhook_full_cycle_triggers_full_cycle(self, scheduler, mock_runner):
        results = scheduler.handle_webhook("full_cycle")
        assert len(results) == 4
        assert mock_runner.run_game_day.call_count == 4

    def test_webhook_unknown_event_returns_empty(self, scheduler, mock_runner):
        results = scheduler.handle_webhook("unknown_event")
        assert results == []
        mock_runner.run_game_day.assert_not_called()

    def test_webhook_push_with_payload(self, scheduler, mock_runner):
        results = scheduler.handle_webhook("push", {"ref": "refs/heads/main"})
        assert len(results) == 1
        assert results[0]["frequency"] == "per_commit"

    def test_webhook_schedule_with_none_payload(self, scheduler, mock_runner):
        results = scheduler.handle_webhook("schedule", None)
        assert len(results) == 1
        assert results[0]["frequency"] == "daily"

    def test_webhook_cron_daily_event(self, scheduler, mock_runner):
        results = scheduler.handle_webhook("cron_daily")
        assert len(results) == 1
        assert results[0]["frequency"] == "daily"


# ============================================================
# _record_run() 历史记录验证
# ============================================================


class TestRecordRun:
    def test_record_run_sets_last_run(self, scheduler):
        result = _make_result()
        scheduler._record_run(GameDayFrequency.DAILY, result)
        assert "daily" in scheduler._state["last_runs"]

    def test_record_run_appends_history(self, scheduler):
        result = _make_result()
        scheduler._record_run(GameDayFrequency.DAILY, result)
        assert len(scheduler._state["history"]) == 1

    def test_record_run_history_has_correct_fields(self, scheduler):
        result = _make_result(total=10, blocked=8, bypassed=2)
        scheduler._record_run(GameDayFrequency.WEEKLY, result)
        entry = scheduler._state["history"][0]
        assert entry["frequency"] == "weekly"
        assert entry["total"] == 10
        assert entry["blocked"] == 8
        assert entry["bypassed"] == 2
        assert "timestamp" in entry

    def test_record_run_history_capped_at_50(self, scheduler):
        result = _make_result()
        with patch.object(scheduler, "_save_state"):
            for _ in range(60):
                scheduler._record_run(GameDayFrequency.DAILY, result)
        assert len(scheduler._state["history"]) == 50

    def test_record_run_persists_to_state_file(self, scheduler, tmp_path):
        result = _make_result()
        scheduler._record_run(GameDayFrequency.DAILY, result)
        state_path = tmp_path / "scheduler-state.yaml"
        with open(state_path, encoding="utf-8") as f:
            state = yaml.safe_load(f)
        assert len(state["history"]) == 1
        assert "daily" in state["last_runs"]

    def test_record_run_overwrites_last_run_for_same_frequency(self, scheduler):
        result1 = _make_result(total=3, blocked=2, bypassed=1)
        result2 = _make_result(total=7, blocked=6, bypassed=1)
        scheduler._record_run(GameDayFrequency.DAILY, result1)
        scheduler._record_run(GameDayFrequency.DAILY, result2)
        assert len(scheduler._state["history"]) == 2
        assert scheduler._state["history"][0]["total"] == 3
        assert scheduler._state["history"][1]["total"] == 7
        assert "daily" in scheduler._state["last_runs"]
        daily_keys = [k for k in scheduler._state["last_runs"] if k == "daily"]
        assert len(daily_keys) == 1


# ============================================================
# next_scheduled() 与 last_run() 验证
# ============================================================


class TestNextScheduled:
    def test_next_scheduled_returns_now_when_no_last_run(self, scheduler):
        next_run = scheduler.next_scheduled(GameDayFrequency.DAILY)
        assert next_run is not None
        now = datetime.now(UTC)
        assert abs((next_run - now).total_seconds()) < 10

    def test_next_scheduled_daily_one_day_after_last(self, scheduler):
        last = datetime.now(UTC) - timedelta(hours=1)
        scheduler._state["last_runs"]["daily"] = last.isoformat()
        next_run = scheduler.next_scheduled(GameDayFrequency.DAILY)
        expected = last + timedelta(days=1)
        assert abs((next_run - expected).total_seconds()) < 10

    def test_next_scheduled_weekly_seven_days_after_last(self, scheduler):
        last = datetime.now(UTC) - timedelta(hours=1)
        scheduler._state["last_runs"]["weekly"] = last.isoformat()
        next_run = scheduler.next_scheduled(GameDayFrequency.WEEKLY)
        expected = last + timedelta(days=7)
        assert abs((next_run - expected).total_seconds()) < 10

    def test_next_scheduled_monthly_thirty_days_after_last(self, scheduler):
        last = datetime.now(UTC) - timedelta(hours=1)
        scheduler._state["last_runs"]["monthly"] = last.isoformat()
        next_run = scheduler.next_scheduled(GameDayFrequency.MONTHLY)
        expected = last + timedelta(days=30)
        assert abs((next_run - expected).total_seconds()) < 10

    def test_next_scheduled_per_commit_five_minutes_after_last(self, scheduler):
        last = datetime.now(UTC) - timedelta(minutes=1)
        scheduler._state["last_runs"]["per_commit"] = last.isoformat()
        next_run = scheduler.next_scheduled(GameDayFrequency.PER_COMMIT)
        expected = last + timedelta(minutes=5)
        assert abs((next_run - expected).total_seconds()) < 10


class TestLastRun:
    def test_last_run_returns_none_when_no_history(self, scheduler):
        assert scheduler.last_run(GameDayFrequency.DAILY) is None

    def test_last_run_returns_datetime_after_trigger(self, scheduler):
        scheduler.trigger("cron_daily")
        last = scheduler.last_run(GameDayFrequency.DAILY)
        assert last is not None
        assert isinstance(last, datetime)

    def test_last_run_returns_none_for_untriggered_frequency(self, scheduler):
        scheduler.trigger("cron_weekly")
        assert scheduler.last_run(GameDayFrequency.WEEKLY) is not None
        assert scheduler.last_run(GameDayFrequency.DAILY) is None

    def test_last_run_returns_correct_value_after_full_cycle(self, scheduler):
        scheduler.trigger("full_cycle")
        assert scheduler.last_run(GameDayFrequency.PER_COMMIT) is not None
        assert scheduler.last_run(GameDayFrequency.DAILY) is not None
        assert scheduler.last_run(GameDayFrequency.WEEKLY) is not None
        assert scheduler.last_run(GameDayFrequency.MONTHLY) is not None


# ============================================================
# 状态持久化验证
# ============================================================


class TestStateLoadSave:
    def test_load_state_creates_default_when_missing(self, tmp_path):
        state_path = tmp_path / "nonexistent.yaml"
        with patch(
            "zephyr.security.adversarial_validation.game_day_scheduler.GameDayRunner"
        ):
            sched = GameDayScheduler(state_path=state_path)
        assert sched._state["running"] is False
        assert sched._state["last_runs"] == {}
        assert sched._state["history"] == []
        assert state_path.exists()

    def test_load_state_reads_existing(self, tmp_path):
        state_path = tmp_path / "existing.yaml"
        existing = {
            "running": True,
            "last_runs": {"daily": "2026-01-01T00:00:00+00:00"},
            "history": [],
            "updated_at": "",
        }
        state_path.write_text(
            yaml.safe_dump(existing, allow_unicode=True), encoding="utf-8"
        )
        with patch(
            "zephyr.security.adversarial_validation.game_day_scheduler.GameDayRunner"
        ):
            sched = GameDayScheduler(state_path=state_path)
        assert sched._state["running"] is True
        assert "daily" in sched._state["last_runs"]

    def test_save_state_writes_to_file(self, scheduler, tmp_path):
        scheduler._state["running"] = True
        scheduler._save_state()
        state_path = tmp_path / "scheduler-state.yaml"
        with open(state_path, encoding="utf-8") as f:
            state = yaml.safe_load(f)
        assert state["running"] is True

    def test_state_path_uses_custom_path(self, tmp_path):
        state_path = tmp_path / "custom-state.yaml"
        with patch(
            "zephyr.security.adversarial_validation.game_day_scheduler.GameDayRunner"
        ):
            sched = GameDayScheduler(state_path=state_path)
        assert sched._state_path == state_path


# ============================================================
# 46个攻击场景加载与执行验证
# ============================================================


class TestScenarioRegistry:
    def test_scenario_registry_file_exists(self):
        assert _SCENARIO_REGISTRY_PATH.exists()

    def test_scenario_registry_has_46_scenarios(self):
        with open(_SCENARIO_REGISTRY_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        scenarios = data.get("scenarios", [])
        assert len(scenarios) == 46

    def test_scenario_registry_summary_total_46(self):
        with open(_SCENARIO_REGISTRY_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["summary"]["total"] == 46

    def test_all_scenarios_have_required_fields(self):
        with open(_SCENARIO_REGISTRY_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        required_fields = [
            "scenario_id",
            "name",
            "tier",
            "severity",
            "injection_vector",
            "target_module",
            "defense",
            "steady_state_verification",
            "status",
        ]
        for i, scenario in enumerate(data["scenarios"]):
            for field in required_fields:
                assert field in scenario, (
                    f"scenario[{i}] ({scenario.get('scenario_id', '?')}) missing field: {field}"
                )

    def test_all_scenarios_are_active(self):
        with open(_SCENARIO_REGISTRY_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for scenario in data["scenarios"]:
            assert scenario["status"] == "active", (
                f"{scenario['scenario_id']} status={scenario['status']}"
            )

    def test_scenario_ids_sequential_001_to_046(self):
        with open(_SCENARIO_REGISTRY_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        ids = [s["scenario_id"] for s in data["scenarios"]]
        expected = [f"RB-SCEN-{i:03d}" for i in range(1, 47)]
        assert ids == expected

    def test_scenarios_cover_all_tiers(self):
        with open(_SCENARIO_REGISTRY_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        tiers = {s["tier"] for s in data["scenarios"]}
        assert "L1" in tiers
        assert "L2" in tiers
        assert "L3" in tiers

    def test_scenarios_cover_critical_severity(self):
        with open(_SCENARIO_REGISTRY_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        severities = {s["severity"] for s in data["scenarios"]}
        assert "critical" in severities
        assert "high" in severities

    def test_scenarios_have_non_empty_names(self):
        with open(_SCENARIO_REGISTRY_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for scenario in data["scenarios"]:
            assert scenario["name"], f"{scenario['scenario_id']} has empty name"

    def test_scenarios_have_non_empty_injection_vectors(self):
        with open(_SCENARIO_REGISTRY_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for scenario in data["scenarios"]:
            assert scenario["injection_vector"], (
                f"{scenario['scenario_id']} has empty injection_vector"
            )

    def test_scenarios_have_non_empty_defense(self):
        with open(_SCENARIO_REGISTRY_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for scenario in data["scenarios"]:
            assert scenario["defense"], f"{scenario['scenario_id']} has empty defense"

    def test_scenarios_have_non_empty_target_module(self):
        with open(_SCENARIO_REGISTRY_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for scenario in data["scenarios"]:
            assert scenario["target_module"], (
                f"{scenario['scenario_id']} has empty target_module"
            )


class TestScenarioLoaderIntegration:
    def test_loader_loads_scenarios_from_custom_path(self):
        loader = ScenarioLoader(registry_path=_SCENARIO_REGISTRY_PATH)
        scenarios = loader.load()
        assert len(scenarios) == 46

    def test_loader_scenario_count(self):
        loader = ScenarioLoader(registry_path=_SCENARIO_REGISTRY_PATH)
        assert loader.scenario_count == 46

    def test_loader_list_all_returns_46(self):
        loader = ScenarioLoader(registry_path=_SCENARIO_REGISTRY_PATH)
        scenarios = loader.list_all()
        assert len(scenarios) == 46

    def test_loader_list_active_returns_46(self):
        loader = ScenarioLoader(registry_path=_SCENARIO_REGISTRY_PATH)
        active = loader.list_active()
        assert len(active) == 46

    def test_loader_get_returns_scenario_by_id(self):
        loader = ScenarioLoader(registry_path=_SCENARIO_REGISTRY_PATH)
        scenario = loader.get("RB-SCEN-001")
        assert scenario is not None
        assert scenario.scenario_id == "RB-SCEN-001"

    def test_loader_get_returns_none_for_unknown_id(self):
        loader = ScenarioLoader(registry_path=_SCENARIO_REGISTRY_PATH)
        assert loader.get("RB-SCEN-999") is None

    def test_loader_list_by_tier_returns_filtered(self):
        loader = ScenarioLoader(registry_path=_SCENARIO_REGISTRY_PATH)
        from zephyr.security.adversarial_validation.models import AttackTier

        l1_scenarios = loader.list_by_tier(AttackTier.TIER_1)
        assert len(l1_scenarios) > 0
        for s in l1_scenarios:
            assert s.tier == AttackTier.TIER_1

    def test_loader_tier_counts(self):
        loader = ScenarioLoader(registry_path=_SCENARIO_REGISTRY_PATH)
        counts = loader.tier_counts()
        total = sum(counts.values())
        assert total == 46


class TestSchedulerScenarioExecution:
    """验证 scheduler 触发后能执行场景覆盖的游戏日。"""

    def test_trigger_full_cycle_executes_all_frequency_tiers(self, scheduler, mock_runner):
        scheduler.trigger("full_cycle")
        called_freqs = [
            call.args[0] for call in mock_runner.run_game_day.call_args_list
        ]
        assert GameDayFrequency.PER_COMMIT in called_freqs
        assert GameDayFrequency.DAILY in called_freqs
        assert GameDayFrequency.WEEKLY in called_freqs
        assert GameDayFrequency.MONTHLY in called_freqs

    def test_trigger_result_has_correct_structure(self, scheduler):
        results = scheduler.trigger("cron_daily")
        assert len(results) == 1
        result = results[0]
        assert "frequency" in result
        assert "total" in result
        assert "blocked" in result
        assert "bypassed" in result

    def test_trigger_full_cycle_results_have_all_frequencies(self, scheduler):
        results = scheduler.trigger("full_cycle")
        freqs = [r["frequency"] for r in results]
        assert sorted(freqs) == sorted(
            ["per_commit", "daily", "weekly", "monthly"]
        )

    def test_trigger_with_mocked_46_attacks(self, tmp_path, mock_runner):
        mock_runner.run_game_day.return_value = _make_result(
            total=46, blocked=40, bypassed=6
        )
        state_path = tmp_path / "scheduler-state.yaml"
        with patch(
            "zephyr.security.adversarial_validation.game_day_scheduler.GameDayRunner",
            return_value=mock_runner,
        ):
            sched = GameDayScheduler(state_path=state_path)
        results = sched.trigger("cron_daily")
        assert results[0]["total"] == 46
        assert results[0]["blocked"] == 40
        assert results[0]["bypassed"] == 6
