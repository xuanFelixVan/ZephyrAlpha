# [A_test] module_id: SRC-TST-1251 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-406 | docs/03_modules/_domain_governance/blueprint.md | §3.11
# [MODULE] tests.test_mcp_result_push
# [INVARIANTS] PushError carries task_id; ResultPushManager state persists via JSON
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PushError;CallbackConnectionError
# [TESTS] tests/test_mcp_result_push.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.gov_enforcement.behavioral_admission.mcp_result_push import (
    CallbackConnectionError,
    PushError,
    PushStatus,
    ResultPushManager,
)


@pytest.fixture
def tmp_state_dir(tmp_path):
    return str(tmp_path / "push_state")


@pytest.fixture
def manager(tmp_state_dir):
    return ResultPushManager(state_dir=tmp_state_dir, max_retries=3, retry_delay=0.01, callback_timeout=1.0)


class TestPushError:
    def test_creation(self):
        err = PushError("T1", "something failed")
        assert err.task_id == "T1"
        assert "T1" in str(err)
        assert "something failed" in str(err)


class TestCallbackConnectionError:
    def test_creation(self):
        err = CallbackConnectionError("T1", "http://x", "timeout")
        assert err.task_id == "T1"
        assert err.url == "http://x"
        assert "http://x" in str(err)


class TestPushStatus:
    def test_all_statuses(self):
        expected = {"pending", "pushed", "failed", "callback_error"}
        actual = {s.value for s in PushStatus}
        assert actual == expected


class TestResultPushManager:
    def test_creation(self, manager):
        assert isinstance(manager, ResultPushManager)

    def test_register_task(self, manager):
        manager.register_task("T1")
        status = manager.get_task_status("T1")
        assert status == PushStatus.PENDING

    def test_register_task_with_callback(self, manager):
        manager.register_task("T2", callback_url="http://localhost:9999/hook")
        status = manager.get_task_status("T2")
        assert status == PushStatus.PENDING

    def test_push_result_no_callback_returns_pushed(self, manager):
        manager.register_task("T3")
        status = manager.push_result("T3", {"key": "value"})
        assert status == PushStatus.PUSHED

    def test_push_result_unregistered_raises(self, manager):
        with pytest.raises(PushError):
            manager.push_result("UNKNOWN", {"key": "value"})

    def test_get_pending_tasks(self, manager):
        manager.register_task("T4")
        manager.register_task("T5")
        pending = manager.get_pending_tasks()
        assert "T4" in pending
        assert "T5" in pending

    def test_get_task_status_unknown(self, manager):
        status = manager.get_task_status("NONEXISTENT")
        assert status is None

    def test_get_all_tasks(self, manager):
        manager.register_task("T6")
        tasks = manager.get_all_tasks()
        assert "T6" in tasks

    def test_push_via_event_bus(self, tmp_state_dir):
        mgr = ResultPushManager(state_dir=tmp_state_dir, max_retries=1, retry_delay=0.01)
        received = []
        mgr.subscribe_event(lambda e: received.append(e))
        mgr.register_task("T7", push_mode="event_bus")
        status = mgr.push_result("T7", {"result": 42})
        assert status == PushStatus.PUSHED
        assert len(received) == 1
        assert received[0]["task_id"] == "T7"

    def test_push_via_event_bus_no_subscribers(self, tmp_state_dir):
        mgr = ResultPushManager(state_dir=tmp_state_dir, max_retries=1, retry_delay=0.01)
        mgr.register_task("T8", push_mode="event_bus")
        status = mgr.push_result("T8", {"result": 1})
        assert status == PushStatus.PUSHED

    def test_push_via_file_watcher(self, tmp_state_dir):
        mgr = ResultPushManager(state_dir=tmp_state_dir, max_retries=1, retry_delay=0.01)
        mgr.register_task("T9", push_mode="file_watcher")
        status = mgr.push_result("T9", {"result": "data"})
        assert status == PushStatus.PUSHED

    def test_retry_failed_unregistered_raises(self, manager):
        with pytest.raises(PushError):
            manager.retry_failed("UNKNOWN")

    def test_retry_already_pushed(self, manager):
        manager.register_task("T10")
        manager.push_result("T10", {"ok": True})
        status = manager.retry_failed("T10")
        assert status == PushStatus.PUSHED


class TestBoundary:
    def test_push_result_with_none_callback_url(self, manager):
        manager.register_task("T11", callback_url=None)
        status = manager.push_result("T11", {"data": 1})
        assert status == PushStatus.PUSHED

    def test_set_file_watcher_path(self, tmp_state_dir, tmp_path):
        mgr = ResultPushManager(state_dir=tmp_state_dir, max_retries=1, retry_delay=0.01)
        watch_dir = tmp_path / "watch"
        mgr.set_file_watcher_path(watch_dir)
        mgr.register_task("T12", push_mode="file_watcher")
        status = mgr.push_result("T12", {"data": 1})
        assert status == PushStatus.PUSHED
