# [A_test] module_id: MOD-GOV_session_boundary | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-428 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_session_boundary
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] pytest tests/test_session_boundary.py
# [TTL] task_bound

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from zephyr.shared.session.session_boundary import (
    SessionBoundary,
    SessionBoundaryManager,
    SessionBudget,
)


class TestSessionBoundaryDataclass:
    def test_default_values(self):
        b = SessionBoundary(session_id="s-001", start_time="2026-01-01T00:00:00+00:00")
        assert b.session_id == "s-001"
        assert b.start_time == "2026-01-01T00:00:00+00:00"
        assert b.end_time == ""
        assert b.cards_processed == 0
        assert b.files_created == 0
        assert b.files_modified == 0
        assert b.tokens_used == 0

    def test_custom_values(self):
        b = SessionBoundary(
            session_id="s-002",
            start_time="2026-01-01T00:00:00+00:00",
            end_time="2026-01-01T01:00:00+00:00",
            cards_processed=5,
            files_created=3,
            files_modified=2,
            tokens_used=1000,
        )
        assert b.cards_processed == 5
        assert b.tokens_used == 1000


class TestSessionBudgetDataclass:
    def test_default_values(self):
        b = SessionBudget()
        assert b.max_cards == 115
        assert b.max_tokens == 200000
        assert b.used_cards == 0
        assert b.used_tokens == 0


class TestSessionBoundaryManager:
    def test_instantiation_with_tmp_path(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path / "sessions")
        assert mgr._data_dir == tmp_path / "sessions"

    def test_instantiation_default(self):
        mgr = SessionBoundaryManager()
        assert mgr._data_dir == Path("data/session")

    def test_open_session(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        boundary = mgr.open_session("session-20260522-001")
        assert boundary.session_id == "session-20260522-001"
        assert boundary.start_time != ""
        assert boundary.end_time == ""
        assert boundary in mgr._boundaries

    def test_open_session_empty_id(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        boundary = mgr.open_session("")
        assert boundary.session_id == ""

    def test_close_session(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        boundary = mgr.open_session("session-20260522-002")
        mgr.close_session(boundary)
        assert boundary.end_time != ""
        saved = tmp_path / "session_session-20260522-002.json"
        assert saved.exists()
        data = json.loads(saved.read_text(encoding="utf-8"))
        assert data["session_id"] == "session-20260522-002"
        assert data["end_time"] != ""

    def test_record_activity(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        boundary = mgr.open_session("session-20260522-003")
        mgr.record_activity(boundary, cards=2, files=1, tokens=500)
        assert boundary.cards_processed == 2
        assert boundary.files_created == 1
        assert boundary.tokens_used == 500
        assert mgr._budget.used_cards == 2
        assert mgr._budget.used_tokens == 500

    def test_record_activity_zero_values(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        boundary = mgr.open_session("session-20260522-004")
        mgr.record_activity(boundary, cards=0, files=0, tokens=0)
        assert boundary.cards_processed == 0
        assert mgr._budget.used_cards == 0

    def test_record_activity_accumulates(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        boundary = mgr.open_session("session-20260522-005")
        mgr.record_activity(boundary, cards=3, tokens=100)
        mgr.record_activity(boundary, cards=2, tokens=200)
        assert boundary.cards_processed == 5
        assert boundary.tokens_used == 300
        assert mgr._budget.used_cards == 5
        assert mgr._budget.used_tokens == 300

    def test_check_budget_within(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        boundary = mgr.open_session("session-20260522-006")
        mgr.record_activity(boundary, cards=10, tokens=1000)
        exhausted, msg = mgr.check_budget()
        assert exhausted is False
        assert msg == "Within budget"

    def test_check_budget_cards_exhausted(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        boundary = mgr.open_session("session-20260522-007")
        mgr.record_activity(boundary, cards=115, tokens=0)
        exhausted, msg = mgr.check_budget()
        assert exhausted is True
        assert "Card budget exhausted" in msg

    def test_check_budget_tokens_exhausted(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        boundary = mgr.open_session("session-20260522-008")
        mgr.record_activity(boundary, cards=0, tokens=200000)
        exhausted, msg = mgr.check_budget()
        assert exhausted is True
        assert "Token budget exhausted" in msg

    def test_get_active_boundary_none(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        assert mgr.get_active_boundary() is None

    def test_get_active_boundary_open(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        b1 = mgr.open_session("session-20260522-009")
        active = mgr.get_active_boundary()
        assert active is b1

    def test_get_active_boundary_closed_returns_none(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        b1 = mgr.open_session("session-20260522-010")
        mgr.close_session(b1)
        assert mgr.get_active_boundary() is None

    def test_get_active_boundary_multiple_returns_last(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        b1 = mgr.open_session("session-20260522-011")
        b2 = mgr.open_session("session-20260522-012")
        active = mgr.get_active_boundary()
        assert active is b2

    def test_clean_old_boundaries_no_files(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        cleared = mgr.clean_old_boundaries(max_age_days=30)
        assert cleared == 0

    def test_clean_old_boundaries_removes_old(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        old_boundary = SessionBoundary(
            session_id="old-session",
            start_time="2020-01-01T00:00:00+00:00",
            end_time=(datetime.now(UTC) - timedelta(days=60)).isoformat(),
        )
        mgr._save_boundary(old_boundary)
        cleared = mgr.clean_old_boundaries(max_age_days=30)
        assert cleared == 1

    def test_clean_old_boundaries_keeps_recent(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        recent_boundary = SessionBoundary(
            session_id="recent-session",
            start_time=datetime.now(UTC).isoformat(),
            end_time=datetime.now(UTC).isoformat(),
        )
        mgr._save_boundary(recent_boundary)
        cleared = mgr.clean_old_boundaries(max_age_days=30)
        assert cleared == 0

    def test_clean_old_boundaries_skips_malformed_json(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        tmp_path.mkdir(parents=True, exist_ok=True)
        bad_file = tmp_path / "session_bad.json"
        bad_file.write_text("not valid json{{{", encoding="utf-8")
        cleared = mgr.clean_old_boundaries(max_age_days=30)
        assert cleared == 0

    def test_clean_old_boundaries_skips_no_end_time(self, tmp_path):
        mgr = SessionBoundaryManager(data_dir=tmp_path)
        open_boundary = SessionBoundary(
            session_id="open-session",
            start_time="2020-01-01T00:00:00+00:00",
            end_time="",
        )
        mgr._save_boundary(open_boundary)
        cleared = mgr.clean_old_boundaries(max_age_days=30)
        assert cleared == 0
