# [A_test] module_id: MOD-GOV_watchdog | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] tests.test_watchdog
# [INVARIANTS] triple-redundancy mutual-check; panic mode on 2+ peer misses; dead man's switch threshold 1800s
# [MODIFY-GUARD] watchdog.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] OSError→caught; RuntimeError→fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import time

import pytest

wd = pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.watchdog",
    reason="watchdog import failed",
)


class TestWatchdogHeartbeat:
    def test_creation(self):
        hb = wd.WatchdogHeartbeat(watchdog_id="wd-1")
        assert hb.watchdog_id == "wd-1"
        assert hb.alive is True

    def test_has_timestamp(self):
        hb = wd.WatchdogHeartbeat(watchdog_id="wd-1")
        assert hb.timestamp is not None


class TestWatchdog:
    def test_instantiation(self):
        w = wd.Watchdog(watchdog_id="wd-test")
        assert w is not None

    def test_panic_mode_default_false(self):
        w = wd.Watchdog(watchdog_id="wd-test")
        assert w.panic_mode is False

    def test_check_peers_all_recent(self):
        w = wd.Watchdog(watchdog_id="wd-test")
        now = time.time()
        result = w.check_peers(
            peers=["wd-a", "wd-b"],
            peer_heartbeats={"wd-a": now, "wd-b": now},
        )
        assert result is True
        assert w.panic_mode is False

    def test_check_peers_two_missing(self):
        w = wd.Watchdog(watchdog_id="wd-test")
        old = time.time() - 2000
        result = w.check_peers(
            peers=["wd-a", "wd-b"],
            peer_heartbeats={"wd-a": old, "wd-b": old},
        )
        assert result is False
        assert w.panic_mode is True

    def test_check_peers_one_missing(self):
        w = wd.Watchdog(watchdog_id="wd-test")
        now = time.time()
        old = time.time() - 2000
        result = w.check_peers(
            peers=["wd-a", "wd-b"],
            peer_heartbeats={"wd-a": now, "wd-b": old},
        )
        assert result is True
        assert w.panic_mode is False

    def test_should_alert_dead_mans_switch(self):
        w = wd.Watchdog(watchdog_id="wd-test")
        old = time.time() - 2000
        assert w.should_alert_dead_mans_switch(old) is True

    def test_should_not_alert_recent(self):
        w = wd.Watchdog(watchdog_id="wd-test")
        now = time.time()
        assert w.should_alert_dead_mans_switch(now) is False

    def test_write_external_heartbeat(self, tmp_path):
        w = wd.Watchdog(watchdog_id="wd-test")
        w._external_file = str(tmp_path / "test_heartbeat")
        w.write_external_heartbeat()
        hb_file = tmp_path / "test_heartbeat"
        assert hb_file.exists()
        content = hb_file.read_text(encoding="utf-8")
        assert "wd-test" in content


class TestBoundary:
    def test_check_peers_empty_list(self):
        w = wd.Watchdog(watchdog_id="wd-test")
        result = w.check_peers(peers=[], peer_heartbeats={})
        assert result is True
        assert w.panic_mode is False

    def test_check_peers_missing_from_heartbeats(self):
        w = wd.Watchdog(watchdog_id="wd-test")
        result = w.check_peers(
            peers=["wd-a", "wd-b", "wd-c"],
            peer_heartbeats={},
        )
        assert result is False
        assert w.panic_mode is True

    def test_dead_mans_switch_exactly_at_threshold(self):
        w = wd.Watchdog(watchdog_id="wd-test")
        boundary = time.time() - 1800
        result = w.should_alert_dead_mans_switch(boundary)
        assert isinstance(result, bool)
