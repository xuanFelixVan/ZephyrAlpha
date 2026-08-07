"""Unit tests for guard watchdog heartbeat logic (fix #ARCH-BOOT-001).

These tests mirror the lock-block heartbeat logic in:
  - scripts/start_scheduler.ps1
  - scripts/start_tick_subscriber.ps1

The PowerShell guard is not directly callable from pytest, so the heartbeat
format parsing and stale-detection are reimplemented here in pure Python with
byte-for-byte equivalent semantics. Each helper docstring cites the
corresponding ps1 line so a future change to either side stays in sync.

Corresponds to docs/03_modules/_domain_data/boot_autostart_architecture.md
section 8.3 step 3 (4 test cases).
"""

from datetime import datetime, timedelta, timezone

import pytest

# ps1: if (((Get-Date) - ([datetime]$hbTs)).TotalMinutes -lt 5) { $stale = $false }
HEARTBEAT_STALE_THRESHOLD_MIN = 5


def parse_heartbeat(line: str) -> "tuple[datetime, int, int]":
    """Parse '<ISO8601>|<guard_pid>|<child_pid>' line.

    Mirrors ps1:
        $hb = (Get-Content $HeartbeatFile ... | Select-Object -First 1).Trim()
        $hbTs = ($hb -split '\\|')[0]
        [datetime]$hbTs   # parses ISO 8601 with timezone
    """
    parts = line.split("|")
    if len(parts) < 3:
        raise ValueError(f"bad heartbeat format: {line!r}")
    ts_str, guard_pid, child_pid = parts[0], parts[1], parts[2]
    ts = datetime.fromisoformat(ts_str)  # handles '2026-08-07T11:30:00+08:00'
    return ts, int(guard_pid), int(child_pid)


def is_stale(hb_line: str, now: datetime) -> bool:
    """Return True if heartbeat is stale (>= threshold minutes old).

    Mirrors ps1 (stale defaults True; only set False if heartbeat fresh):
        $stale = $true
        if (Test-Path $HeartbeatFile) {
            try { ... if (age.TotalMinutes -lt 5) { $stale = $false } } catch { }
        }
    A malformed / missing heartbeat leaves $stale = $true (takeover).
    """
    try:
        ts, _guard_pid, _child_pid = parse_heartbeat(hb_line)
    except (ValueError, TypeError):
        return True  # ps1: catch {} leaves $stale = $true
    # Normalize tz awareness for subtraction (ps1 Get-Date is tz-aware)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    age_min = (now - ts).total_seconds() / 60.0
    # ps1: -lt 5 => fresh; >= 5 => stale
    return age_min >= HEARTBEAT_STALE_THRESHOLD_MIN


def format_heartbeat(now: datetime, guard_pid: int, child_pid: int) -> str:
    """Format heartbeat line '<ISO8601>|<guard_pid>|<child_pid>'.

    Mirrors ps1 Write-Heartbeat:
        $ts = (Get-Date).ToString("o")  # ISO 8601, with timezone
        "$ts|$PID|$ChildPid" | Out-File ...
    """
    return f"{now.isoformat()}|{guard_pid}|{child_pid}"


class GuardDecision:
    """Decision-tree outcomes mirroring the ps1 lock block.

    ps1 flow (after lock file exists):
      - lock PID dead        -> TAKEOVER_DEAD_PID (cleanup lock + orphan cleanup, no exit)
      - lock PID alive + stale -> TAKEOVER_STALE  (kill zombie + orphan cleanup, no exit)
      - lock PID alive + fresh -> EXIT_FRESH       (exit 0, NO orphan cleanup)
    """

    EXIT_FRESH = "exit_fresh"
    TAKEOVER_STALE = "takeover_stale"
    TAKEOVER_DEAD_PID = "takeover_dead_pid"
    TAKEOVER_NO_LOCK = "takeover_no_lock"


def guard_decision(
    lock_exists: bool,
    lock_pid_alive: bool,
    hb_line: str,
    now: datetime,
) -> str:
    """Mirror the ps1 single-instance-lock decision tree.

    The key invariant under test: the stale-takeover path does NOT exit and
    therefore falls through to orphan cleanup (same as the dead-PID path),
    whereas the fresh path exits immediately without orphan cleanup.
    """
    if not lock_exists:
        return GuardDecision.TAKEOVER_NO_LOCK
    if not lock_pid_alive:
        return GuardDecision.TAKEOVER_DEAD_PID
    # lock_pid_alive is True: branch on heartbeat staleness
    if is_stale(hb_line, now):
        return GuardDecision.TAKEOVER_STALE  # kill zombie guard + orphan cleanup
    return GuardDecision.EXIT_FRESH  # exit 0


# Fixed test clock + timezones
TZ_CN = timezone(timedelta(hours=8))
NOW = datetime(2026, 8, 7, 11, 30, 0, tzinfo=TZ_CN)


class TestHeartbeatFormat:
    """Case 1 (test_heartbeat_format): Write-Heartbeat writes ISO|guard|child 3-part format."""

    def test_format_has_three_pipe_parts(self):
        line = format_heartbeat(NOW, guard_pid=24040, child_pid=25488)
        assert line.count("|") == 2
        assert len(line.split("|")) == 3

    def test_format_roundtrip_parses_back(self):
        line = format_heartbeat(NOW, guard_pid=24040, child_pid=25488)
        ts, gpid, cpid = parse_heartbeat(line)
        assert gpid == 24040
        assert cpid == 25488
        assert ts == NOW

    def test_format_is_iso8601_with_timezone(self):
        # ps1 ToString("o") emits offset like +08:00
        line = format_heartbeat(NOW, guard_pid=24040, child_pid=25488)
        ts_str = line.split("|")[0]
        assert "+08:00" in ts_str


class TestStaleHeartbeatTriggersTakeover:
    """Case 2 (test_stale_heartbeat_triggers_takeover): >5min old heartbeat => stale=True => takeover."""

    def test_old_heartbeat_is_stale(self):
        old = NOW - timedelta(minutes=6)
        hb = format_heartbeat(old, guard_pid=24040, child_pid=25488)
        assert is_stale(hb, NOW) is True

    def test_exactly_5min_is_stale(self):
        # ps1: -lt 5 => fresh; exactly 5min is NOT <5 => stale (boundary is stale)
        hb = format_heartbeat(NOW - timedelta(minutes=5), 24040, 25488)
        assert is_stale(hb, NOW) is True

    def test_malformed_heartbeat_is_stale(self):
        # ps1: catch {} leaves $stale = $true
        assert is_stale("garbage-no-pipes", NOW) is True

    def test_decision_is_takeover_when_stale(self):
        old = NOW - timedelta(minutes=6)
        hb = format_heartbeat(old, guard_pid=24040, child_pid=25488)
        assert guard_decision(True, True, hb, NOW) == GuardDecision.TAKEOVER_STALE


class TestFreshHeartbeatExits:
    """Case 3 (test_fresh_heartbeat_exits): <5min new heartbeat => stale=False => exit 0."""

    def test_recent_heartbeat_not_stale(self):
        # guard polls every 15s, so a 15s-old heartbeat is fresh
        recent = NOW - timedelta(seconds=15)
        hb = format_heartbeat(recent, guard_pid=24040, child_pid=25488)
        assert is_stale(hb, NOW) is False

    def test_just_under_5min_not_stale(self):
        hb = format_heartbeat(NOW - timedelta(minutes=4, seconds=59), 24040, 25488)
        assert is_stale(hb, NOW) is False

    def test_decision_is_exit_when_fresh(self):
        recent = NOW - timedelta(seconds=15)
        hb = format_heartbeat(recent, guard_pid=24040, child_pid=25488)
        assert guard_decision(True, True, hb, NOW) == GuardDecision.EXIT_FRESH


class TestZombieTakeoverRunsOrphanCleanup:
    """Case 4 (test_zombie_takeover_runs_orphan_cleanup): stale takeover does NOT exit,
    falls through to orphan cleanup (same as dead-PID path); fresh path exits WITHOUT cleanup."""

    def test_stale_takeover_does_not_exit(self):
        # The takeover path must not be EXIT_FRESH (which would skip orphan cleanup)
        old = NOW - timedelta(minutes=6)
        hb = format_heartbeat(old, guard_pid=24040, child_pid=25488)
        decision = guard_decision(True, True, hb, NOW)
        assert decision == GuardDecision.TAKEOVER_STALE
        assert decision != GuardDecision.EXIT_FRESH

    def test_stale_takeover_same_outcome_class_as_dead_pid(self):
        # Both stale-takeover and dead-PID paths fall through to orphan cleanup
        # (neither returns EXIT_FRESH), so they are "cleanup-eligible".
        old = NOW - timedelta(minutes=6)
        hb_stale = format_heartbeat(old, guard_pid=24040, child_pid=25488)
        cleanup_eligible = {
            GuardDecision.TAKEOVER_STALE,
            GuardDecision.TAKEOVER_DEAD_PID,
        }
        assert guard_decision(True, True, hb_stale, NOW) in cleanup_eligible
        assert guard_decision(True, False, hb_stale, NOW) in cleanup_eligible

    def test_fresh_path_exits_without_orphan_cleanup(self):
        # Fresh heartbeat => exit 0 immediately, orphan cleanup NOT reached
        recent = NOW - timedelta(seconds=15)
        hb = format_heartbeat(recent, guard_pid=24040, child_pid=25488)
        decision = guard_decision(True, True, hb, NOW)
        assert decision == GuardDecision.EXIT_FRESH
        assert decision not in {
            GuardDecision.TAKEOVER_STALE,
            GuardDecision.TAKEOVER_DEAD_PID,
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
