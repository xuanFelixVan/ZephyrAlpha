# [A_test] module_id: SRC-TST-1745 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_timezone_semantic_reasoner
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.reliability.timezone_semantic_reasoner
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_timezone_semantic_reasoner.py
# [TTL] task_bound

from datetime import UTC, datetime

from zephyr.feedback_loop.diagnosers.reliability.timezone_semantic_reasoner import (
    TimezoneSemanticReasoner,
    VenueTZ,
)


class TestVenueTZ:
    def test_nyse_value(self):
        assert VenueTZ.NYSE.value == "America/New_York"

    def test_lse_value(self):
        assert VenueTZ.LSE.value == "Europe/London"

    def test_tse_value(self):
        assert VenueTZ.TSE.value == "Asia/Tokyo"

    def test_sse_value(self):
        assert VenueTZ.SSE.value == "Asia/Shanghai"

    def test_hkex_value(self):
        assert VenueTZ.HKEX.value == "Asia/Hong_Kong"

    def test_all_venues_count(self):
        assert len(VenueTZ) == 5


class TestTimezoneSemanticReasonerInstantiation:
    def test_default_params(self):
        tsr = TimezoneSemanticReasoner()
        assert "NYSE" in tsr.venue_active_windows
        assert "LSE" in tsr.venue_active_windows
        assert tsr.venue_holidays == {}

    def test_custom_windows(self):
        custom = {"CUSTOM": (9, 17)}
        tsr = TimezoneSemanticReasoner(venue_active_windows=custom)
        assert "CUSTOM" in tsr.venue_active_windows
        assert tsr.venue_active_windows["CUSTOM"] == (9, 17)

    def test_custom_holidays(self):
        holidays = {"NYSE": {"2026-01-01"}}
        tsr = TimezoneSemanticReasoner(venue_holidays=holidays)
        assert "2026-01-01" in tsr.venue_holidays["NYSE"]


class TestIsMarketActive:
    def test_active_during_window(self):
        tsr = TimezoneSemanticReasoner(venue_active_windows={"TEST": (0, 24)})
        dt = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
        assert tsr.is_market_active("TEST", dt) is True

    def test_inactive_outside_window(self):
        tsr = TimezoneSemanticReasoner(venue_active_windows={"TEST": (22, 23)})
        dt = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
        assert tsr.is_market_active("TEST", dt) is False

    def test_unknown_venue_inactive(self):
        tsr = TimezoneSemanticReasoner()
        dt = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
        assert tsr.is_market_active("UNKNOWN", dt) is False

    def test_boundary_start_hour_active(self):
        tsr = TimezoneSemanticReasoner(venue_active_windows={"TEST": (10, 20)})
        dt = datetime(2026, 1, 1, 10, 0, tzinfo=UTC)
        assert tsr.is_market_active("TEST", dt) is True

    def test_boundary_end_hour_inactive(self):
        tsr = TimezoneSemanticReasoner(venue_active_windows={"TEST": (10, 20)})
        dt = datetime(2026, 1, 1, 20, 0, tzinfo=UTC)
        assert tsr.is_market_active("TEST", dt) is False

    def test_none_dt_uses_now(self):
        tsr = TimezoneSemanticReasoner(venue_active_windows={"TEST": (0, 24)})
        result = tsr.is_market_active("TEST")
        assert isinstance(result, bool)


class TestAnyMarketActive:
    def test_returns_bool(self):
        tsr = TimezoneSemanticReasoner()
        result = tsr.any_market_active()
        assert isinstance(result, bool)

    def test_all_closed_with_narrow_windows(self):
        tsr = TimezoneSemanticReasoner(venue_active_windows={"TEST": (25, 26)})
        result = tsr.any_market_active()
        assert result is False


class TestActiveVenues:
    def test_returns_list(self):
        tsr = TimezoneSemanticReasoner()
        result = tsr.active_venues()
        assert isinstance(result, list)

    def test_empty_windows_returns_empty(self):
        tsr = TimezoneSemanticReasoner(venue_active_windows={})
        result = tsr.active_venues()
        assert result == []


class TestNextTransition:
    def test_returns_float(self):
        tsr = TimezoneSemanticReasoner()
        result = tsr.next_transition("NYSE")
        assert isinstance(result, float)

    def test_unknown_venue_returns_day(self):
        tsr = TimezoneSemanticReasoner()
        result = tsr.next_transition("UNKNOWN")
        assert result == 86400.0

    def test_positive_value(self):
        tsr = TimezoneSemanticReasoner()
        result = tsr.next_transition("NYSE")
        assert result > 0
