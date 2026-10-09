# [A_test] module_id: MOD-GOV_time_sync | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_time_sync
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.ops_governance.time_sync import (
    MAX_CLOCK_DRIFT_MS,
    NTP_SERVER,
    NTP_SYNC_INTERVAL_SECONDS,
    TIME_HIERARCHY,
    TIMESTAMP_FORMAT,
    TimeSource,
)


class TestTimeSource:
    def test_creation(self):
        ts = TimeSource(level=1, name="test", max_jitter_ms=5)
        assert ts.level == 1
        assert ts.name == "test"
        assert ts.max_jitter_ms == 5

    def test_frozen(self):
        ts = TimeSource(level=1, name="test", max_jitter_ms=5)
        with pytest.raises(AttributeError):
            ts.level = 2

    def test_equality(self):
        ts1 = TimeSource(level=1, name="a", max_jitter_ms=10)
        ts2 = TimeSource(level=1, name="a", max_jitter_ms=10)
        assert ts1 == ts2

    def test_inequality(self):
        ts1 = TimeSource(level=1, name="a", max_jitter_ms=10)
        ts2 = TimeSource(level=2, name="b", max_jitter_ms=20)
        assert ts1 != ts2


class TestConstants:
    def test_ntp_server(self):
        assert isinstance(NTP_SERVER, str)
        assert len(NTP_SERVER) > 0

    def test_ntp_sync_interval(self):
        assert isinstance(NTP_SYNC_INTERVAL_SECONDS, int)
        assert NTP_SYNC_INTERVAL_SECONDS > 0

    def test_max_clock_drift(self):
        assert isinstance(MAX_CLOCK_DRIFT_MS, int)
        assert MAX_CLOCK_DRIFT_MS > 0

    def test_timestamp_format(self):
        assert TIMESTAMP_FORMAT == "ISO8601"


class TestTimeHierarchy:
    def test_hierarchy_has_three_levels(self):
        assert len(TIME_HIERARCHY) == 3

    def test_hierarchy_sorted_by_level(self):
        levels = [ts.level for ts in TIME_HIERARCHY]
        assert levels == sorted(levels)

    def test_hierarchy_level_values(self):
        levels = [ts.level for ts in TIME_HIERARCHY]
        assert levels == [1, 2, 3]

    def test_hierarchy_names_not_empty(self):
        for ts in TIME_HIERARCHY:
            assert len(ts.name) > 0

    def test_hierarchy_jitter_positive(self):
        for ts in TIME_HIERARCHY:
            assert ts.max_jitter_ms > 0

    def test_hierarchy_entries_are_timesource(self):
        for ts in TIME_HIERARCHY:
            assert isinstance(ts, TimeSource)
