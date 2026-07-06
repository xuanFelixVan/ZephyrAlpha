# [A_test] module_id: SRC-TST-0925 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_fix_scheduler
# [INVARIANTS] 测试覆盖start/stop/submit_event/get_status;边界:空输入/None/异常
# [MODIFY-GUARD] blueprint.md §3
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.auto_fix_engine.fix_scheduler import FixScheduler, SchedulerMode
from zephyr.infrastructure.auto_fix_engine.models import FixAction, FixLevel, FixReport


def _make_action(target: str = "t.py") -> FixAction:
    return FixAction(action_type="drift_fix", target=target, level=FixLevel.L1_RULE)


def _make_report(actions=None):
    return FixReport(actions=actions or [])


class TestFixSchedulerInstantiation:
    def test_default_mode(self):
        s = FixScheduler()
        assert s.mode == SchedulerMode.EVENT_DRIVEN

    def test_custom_mode(self):
        s = FixScheduler(mode=SchedulerMode.EVENT_DRIVEN)
        assert s.mode == SchedulerMode.EVENT_DRIVEN

    def test_default_not_running(self):
        s = FixScheduler()
        assert not s.is_running

    def test_batch_count_starts_zero(self):
        s = FixScheduler()
        assert s.batch_count == 0


class TestStartStop:
    def test_start_continuous(self):
        s = FixScheduler(mode=SchedulerMode.CONTINUOUS, batch_interval_sec=9999)
        s.start()
        assert s.is_running
        s.stop()

    def test_start_event_driven(self):
        s = FixScheduler(mode=SchedulerMode.EVENT_DRIVEN)
        s.start()
        assert s.is_running
        s.stop()

    def test_start_idempotent(self):
        s = FixScheduler(mode=SchedulerMode.EVENT_DRIVEN)
        s.start()
        s.start()
        assert s.is_running
        s.stop()

    def test_stop_when_not_running(self):
        s = FixScheduler()
        s.stop()
        assert not s.is_running


class TestSubmitEvent:
    def test_submit_event_event_driven(self):
        processed = []

        def fake_fix(actions):
            processed.extend(actions)

        s = FixScheduler(
            mode=SchedulerMode.EVENT_DRIVEN,
            fix_fn=fake_fix,
        )
        action = _make_action()
        s.submit_event(action)
        assert len(processed) == 1
        assert processed[0].action_id == action.action_id

    def test_submit_event_continuous_queues(self):
        s = FixScheduler(mode=SchedulerMode.CONTINUOUS, batch_interval_sec=9999)
        action = _make_action()
        s.submit_event(action)
        status = s.get_status()
        assert status["pending_events"] == 1

    def test_submit_event_no_fix_fn(self):
        s = FixScheduler(mode=SchedulerMode.EVENT_DRIVEN)
        action = _make_action()
        s.submit_event(action)
        assert s.batch_count == 0


class TestGetStatus:
    def test_status_continuous(self):
        s = FixScheduler(mode=SchedulerMode.CONTINUOUS)
        status = s.get_status()
        assert status["mode"] == "continuous"
        assert status["running"] is False
        assert status["batch_count"] == 0
        assert status["pending_events"] == 0
        assert status["last_batch"] is None

    def test_status_event_driven(self):
        s = FixScheduler(mode=SchedulerMode.EVENT_DRIVEN)
        status = s.get_status()
        assert status["mode"] == "event_driven"

    def test_status_after_event(self):
        s = FixScheduler(mode=SchedulerMode.EVENT_DRIVEN, fix_fn=lambda a: _make_report())
        s.submit_event(_make_action())
        status = s.get_status()
        assert status["batch_count"] == 1


class TestSchedulerModeEnum:
    def test_continuous_value(self):
        assert SchedulerMode.CONTINUOUS.value == "continuous"

    def test_event_driven_value(self):
        assert SchedulerMode.EVENT_DRIVEN.value == "event_driven"
