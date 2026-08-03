# [A_test] module_id: MOD-GOV_owner_absent | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_owner_absent
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] AbsentStatus.level in {0,1,3};OwnerPing.attempts >= 0
# [MODIFY-GUARD] src/zephyr/rollback/owner_absent.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AbsentStatus on check failure;json.JSONDecodeError on corrupted state
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from zephyr.governance.escalation.owner_absent import (
    EXIT_OWNER_ABSENT_L1,
    EXIT_OWNER_ABSENT_L3,
    AbsentStatus,
    OwnerAbsent,
    OwnerPing,
)


class TestOwnerAbsentInstantiation:
    def test_default_data_dir(self):
        oa = OwnerAbsent()
        assert oa.data_dir == Path("data/rollback/owner")

    def test_custom_data_dir(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path / "owner_data")
        assert oa.data_dir == tmp_path / "owner_data"

    def test_state_path_derived(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        assert oa.state_path == tmp_path / "owner_absent_state.json"


class TestCheckOwnerStatus:
    def test_recent_interaction_level0(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        now = datetime.now(UTC).isoformat()
        status = oa.check_owner_status(now)
        assert status.level == 0
        assert status.exit_code == 0
        assert "OK" in status.action

    def test_l3_timeout_30min_absent(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        past = (datetime.now(UTC) - timedelta(minutes=35)).isoformat()
        status = oa.check_owner_status(past)
        assert status.level == 3
        assert status.exit_code == EXIT_OWNER_ABSENT_L3
        assert "DEFER" in status.action

    def test_l1_timeout_7day_absent(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        past = (datetime.now(UTC) - timedelta(days=8)).isoformat()
        status = oa.check_owner_status(past)
        assert status.level == 1
        assert status.exit_code == EXIT_OWNER_ABSENT_L1
        assert "ESCALATE" in status.action

    def test_invalid_timestamp_defaults_to_now(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        status = oa.check_owner_status("not-a-timestamp")
        assert status.level == 0
        assert status.exit_code == 0

    def test_none_timestamp_handled_gracefully(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        status = oa.check_owner_status(None)
        assert isinstance(status, AbsentStatus)
        assert status.level == 0

    def test_exactly_30min_boundary(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        past = (datetime.now(UTC) - timedelta(seconds=1800)).isoformat()
        status = oa.check_owner_status(past)
        assert status.level >= 3 or status.level == 0


class TestRecordOwnerInteraction:
    def test_record_creates_state_file(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        timestamp = oa.record_owner_interaction()
        assert oa.state_path.exists()
        assert isinstance(timestamp, str)
        assert len(timestamp) > 0

    def test_record_updates_state_json(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        oa.record_owner_interaction()
        data = json.loads(oa.state_path.read_text(encoding="utf-8"))
        assert "last_owner_interaction" in data
        assert data["ping_attempts"] == 0

    def test_record_creates_parent_dirs(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path / "deep" / "nested")
        oa.record_owner_interaction()
        assert (tmp_path / "deep" / "nested").is_dir()


class TestRecordPingAttempt:
    def test_failed_ping_increments_attempts(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        oa.record_owner_interaction()
        ping = oa.record_ping_attempt(success=False)
        assert isinstance(ping, OwnerPing)
        assert ping.attempts >= 1
        assert ping.last_response is None

    def test_successful_ping_records_response(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        oa.record_owner_interaction()
        oa.record_ping_attempt(success=False)
        oa.record_ping_attempt(success=False)
        ping = oa.record_ping_attempt(success=True)
        assert ping.last_response is not None

    def test_ping_without_prior_interaction(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        ping = oa.record_ping_attempt(success=False)
        assert isinstance(ping, OwnerPing)
        assert ping.attempts >= 1


class TestGetAbsentStatus:
    def test_no_data_returns_level0(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        status = oa.get_absent_status()
        assert isinstance(status, AbsentStatus)
        assert status.level == 0
        assert "NO_DATA" in status.action

    def test_with_recent_interaction(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        oa.record_owner_interaction()
        status = oa.get_absent_status()
        assert status.level == 0
        assert "OK" in status.action

    def test_with_old_interaction(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        old_ts = (datetime.now(UTC) - timedelta(days=10)).isoformat()
        oa.data_dir.mkdir(parents=True, exist_ok=True)
        oa.state_path.write_text(
            json.dumps({"last_owner_interaction": old_ts, "ping_attempts": 5}),
            encoding="utf-8",
        )
        status = oa.get_absent_status()
        assert status.level == 1
        assert status.exit_code == EXIT_OWNER_ABSENT_L1


class TestGenerateEscalationMessage:
    def test_level3_escalation(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        status = AbsentStatus(
            level=3,
            absent_since="2026-01-01T00:00:00+00:00",
            last_ping_attempt="2026-01-01T01:00:00+00:00",
            ping_attempts=5,
            exit_code=EXIT_OWNER_ABSENT_L3,
            action="DEFER",
        )
        msg = oa.generate_escalation_message(status)
        assert msg["absent_level"] == 3
        assert msg["exit_code"] == EXIT_OWNER_ABSENT_L3
        assert "suspended" in msg["recommendation"]

    def test_level0_no_escalation(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        status = AbsentStatus(
            level=0,
            absent_since="",
            last_ping_attempt="",
            ping_attempts=0,
            exit_code=0,
            action="OK",
        )
        msg = oa.generate_escalation_message(status)
        assert msg["absent_level"] == 0
        assert "Normal" in msg["recommendation"]

    def test_escalation_id_format(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        status = AbsentStatus(
            level=1,
            absent_since="2026-01-01T00:00:00+00:00",
            last_ping_attempt="2026-01-08T00:00:00+00:00",
            ping_attempts=10,
            exit_code=EXIT_OWNER_ABSENT_L1,
            action="ESCALATE",
        )
        msg = oa.generate_escalation_message(status)
        assert msg["escalation_id"].startswith("ESC-")
        assert "timestamp_utc" in msg


class TestCorruptedStateFile:
    def test_corrupted_state_returns_defaults(self, tmp_path: Path):
        oa = OwnerAbsent(data_dir=tmp_path)
        oa.data_dir.mkdir(parents=True, exist_ok=True)
        oa.state_path.write_text("BROKEN JSON{{{", encoding="utf-8")
        status = oa.get_absent_status()
        assert isinstance(status, AbsentStatus)
