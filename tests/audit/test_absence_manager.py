# [A_test] module_id: SRC-TST-0259 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §

# [MODULE] tests.test_absence_manager

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] none

# [TESTS] python -m pytest tests/test_absence_manager.py -q
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from tempfile import TemporaryDirectory

import pytest

from zephyr.gov_drift.absence_manager import (
    CONFIG,
    EscalationEntry,
    OwnerStatus,
    _load_absence_state,
    _save_absence_state,
    check_absence,
    detect_owner_return,
    escalate_if_absent,
    record_activity,
    set_severity_limit,
)


@pytest.fixture(autouse=True)
def _reset_config():
    old_dir = CONFIG.state_dir
    old_threshold = CONFIG.threshold_days
    old_list = CONFIG.escalation_list.copy()
    yield
    CONFIG.state_dir = old_dir
    CONFIG.threshold_days = old_threshold
    CONFIG.escalation_list = old_list


@pytest.fixture()
def tmp_state():
    with TemporaryDirectory() as tmp:
        CONFIG.state_dir = tmp
        yield tmp


class TestOwnerStatus:
    def test_defaults(self):
        s = OwnerStatus(owner_id="o1", last_active=datetime.now(UTC))
        assert s.is_present is True
        assert s.absent_days == 0
        assert s.escalated_to is None

    def test_absent(self):
        s = OwnerStatus(owner_id="o1", last_active=datetime.now(UTC), is_present=False, absent_days=10)
        assert s.is_present is False
        assert s.absent_days == 10


class TestEscalationEntry:
    def test_creation(self):
        e = EscalationEntry(owner_id="o1", escalated_to="admin", reason="absent")
        assert e.owner_id == "o1"
        assert e.escalated_to == "admin"
        assert e.reason == "absent"

    def test_auto_timestamp(self):
        e = EscalationEntry(owner_id="o1", escalated_to="admin")
        assert e.escalated_at is not None


class TestLoadSaveState:
    def test_load_empty_dir(self, tmp_state):
        state = _load_absence_state()
        assert state == {}

    def test_save_and_load(self, tmp_state):
        data = {"owners": {"o1": {"last_active": "2026-01-01T00:00:00+00:00"}}}
        _save_absence_state(data)
        loaded = _load_absence_state()
        assert loaded["owners"]["o1"]["last_active"] == "2026-01-01T00:00:00+00:00"

    def test_save_no_state_dir(self):
        CONFIG.state_dir = ""
        _save_absence_state({"test": True})

    def test_load_nonexistent_path(self):
        CONFIG.state_dir = "/nonexistent/path"
        state = _load_absence_state()
        assert state == {}


class TestRecordActivity:
    def test_records_owner(self, tmp_state):
        record_activity("owner-1")
        state = _load_absence_state()
        assert "owner-1" in state["owners"]
        assert "last_active" in state["owners"]["owner-1"]

    def test_updates_existing(self, tmp_state):
        record_activity("owner-1")
        state1 = _load_absence_state()
        first_active = state1["owners"]["owner-1"]["last_active"]
        record_activity("owner-1")
        state2 = _load_absence_state()
        assert state2["owners"]["owner-1"]["last_active"] >= first_active

    def test_no_state_dir(self):
        CONFIG.state_dir = ""
        record_activity("owner-1")


class TestCheckAbsence:
    def test_present_owner(self, tmp_state):
        record_activity("owner-1")
        status = check_absence("owner-1")
        assert status.is_present is True
        assert status.absent_days == 0

    def test_absent_owner(self, tmp_state):
        old_time = (datetime.now(UTC) - timedelta(days=10)).isoformat()
        state = {"owners": {"owner-1": {"last_active": old_time}}}
        _save_absence_state(state)
        status = check_absence("owner-1")
        assert status.is_present is False
        assert status.absent_days >= 7

    def test_unknown_owner(self, tmp_state):
        status = check_absence("unknown")
        assert status.is_present is True
        assert status.absent_days == 0

    def test_exactly_at_threshold(self, tmp_state):
        CONFIG.threshold_days = 7
        old_time = (datetime.now(UTC) - timedelta(days=7)).isoformat()
        state = {"owners": {"owner-1": {"last_active": old_time}}}
        _save_absence_state(state)
        status = check_absence("owner-1")
        assert status.is_present is False

    def test_one_day_below_threshold(self, tmp_state):
        CONFIG.threshold_days = 7
        old_time = (datetime.now(UTC) - timedelta(days=6)).isoformat()
        state = {"owners": {"owner-1": {"last_active": old_time}}}
        _save_absence_state(state)
        status = check_absence("owner-1")
        assert status.is_present is True


class TestEscalateIfAbsent:
    def test_present_no_escalation(self):
        status = OwnerStatus(owner_id="o1", last_active=datetime.now(UTC), is_present=True)
        result = escalate_if_absent(status)
        assert result is None

    def test_absent_with_escalation_list(self):
        CONFIG.escalation_list = ["admin-1", "admin-2"]
        status = OwnerStatus(owner_id="o1", last_active=datetime.now(UTC), is_present=False, absent_days=10)
        result = escalate_if_absent(status)
        assert result is not None
        assert result.escalated_to == "admin-1"
        assert "absent" in result.reason.lower() or "10" in result.reason

    def test_absent_without_escalation_list(self):
        CONFIG.escalation_list = []
        status = OwnerStatus(owner_id="o1", last_active=datetime.now(UTC), is_present=False, absent_days=10)
        result = escalate_if_absent(status)
        assert result is None


class TestDetectOwnerReturn:
    def test_recent_activity(self):
        recent = datetime.now(UTC) - timedelta(hours=1)
        assert detect_owner_return("o1", recent) is True

    def test_old_activity(self):
        old = datetime.now(UTC) - timedelta(days=5)
        assert detect_owner_return("o1", old) is False

    def test_exactly_one_day(self):
        boundary = datetime.now(UTC) - timedelta(days=1)
        result = detect_owner_return("o1", boundary)
        assert isinstance(result, bool)


class TestSetSeverityLimit:
    def test_non_admin_rejected(self, tmp_state):
        result = set_severity_limit("o1", "MINOR", admin=False)
        assert result is False

    def test_admin_sets_limit(self, tmp_state):
        result = set_severity_limit("o1", "CRITICAL", admin=True)
        assert result is True
        state = _load_absence_state()
        assert state["severity_limits"]["o1"]["max_severity"] == "CRITICAL"

    def test_default_severity(self, tmp_state):
        result = set_severity_limit("o1", admin=True)
        assert result is True
        state = _load_absence_state()
        assert state["severity_limits"]["o1"]["max_severity"] == "MINOR"

    def test_no_state_dir(self):
        CONFIG.state_dir = ""
        result = set_severity_limit("o1", admin=True)
        assert result is True
