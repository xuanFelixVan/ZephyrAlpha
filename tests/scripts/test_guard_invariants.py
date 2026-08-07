# [BLUEPRINT] MOD-INF-021 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""Invariant tests for guard watchdog scripts (fix #ARCH-BOOT-001 Phase 3).

These tests pin the root-cause fix as EXECUTABLE invariants so a future AI session
cannot silently regress the watchdog. The project is 100% AI-developed; without
these gates, an AI could "optimize" $proc.WaitForExit() back into a guard script
or flip the Task Scheduler policy to IgnoreNew, re-introducing the exact 2-day
intraday download outage of 08-06/08-07.

Invariants enforced:
  - guard scripts must poll $proc.HasExited, never call $proc.WaitForExit()
    (WaitForExit is the zombie root cause: main-thread deadlock)
  - register_guard_tasks.ps1 must use MultipleInstances=Parallel (Task Scheduler
    is a DUMB periodic launcher; single-instance SSoT lives in the script-level
    PID lock + heartbeat. IgnoreNew blocks a new guard while a zombie holds the
    slot, defeating heartbeat takeover)
  - register_aux_tasks.ps1 intentionally keeps IgnoreNew (one-shot AtLogOn tasks,
    no while-true guard, no zombie risk). This documents the intentional asymmetry.
  - all three guard scripts define $HeartbeatFile + Write-Heartbeat + the 5min
    stale threshold + finally cleanup, so takeover logic is uniform.

Corresponds to docs/03_modules/_domain_data/boot_autostart_architecture.md §8.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"

# The three watchdog-tier guard scripts (AGENTS.md "watchdog 三服务").
GUARD_SCRIPTS = [
    SCRIPTS / "start_scheduler.ps1",
    SCRIPTS / "start_tick_subscriber.ps1",
    SCRIPTS / "start_ch_health_probe.ps1",
]
REGISTER_GUARD = SCRIPTS / "register_guard_tasks.ps1"
REGISTER_AUX = SCRIPTS / "register_aux_tasks.ps1"


def _non_comment_lines(path: Path) -> list[str]:
    """Lines that are not comments (do not start with '#' after lstrip).

    PowerShell comments start with '#'. Active code lines are returned so pattern
    checks distinguish real calls from documentation mentions.
    """
    return [
        ln for ln in path.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")
    ]


class TestNoGuardUsesWaitForExit:
    """$proc.WaitForExit() is the zombie root cause (main-thread deadlock). All guards
    must poll $proc.HasExited instead. WaitForExit may appear in comments only."""

    def test_no_active_waitforexit_call(self):
        for script in GUARD_SCRIPTS:
            for ln in _non_comment_lines(script):
                assert ".WaitForExit()" not in ln, (
                    f"{script.name}: active WaitForExit() call found (zombie root cause, "
                    f"fix #ARCH-BOOT-001): {ln!r}"
                )

    def test_all_guards_poll_hasexited(self):
        for script in GUARD_SCRIPTS:
            text = script.read_text(encoding="utf-8")
            assert "$proc.HasExited" in text, (
                f"{script.name}: missing $proc.HasExited polling (fix #ARCH-BOOT-001)"
            )


class TestRegisterGuardUsesParallel:
    """register_guard_tasks.ps1 must use Parallel, not IgnoreNew. IgnoreNew blocks a new
    guard from launching while a zombie guard holds the slot, defeating heartbeat takeover
    (root cause of the 08-06/08-07 2-day intraday outage)."""

    def test_uses_parallel(self):
        lines = _non_comment_lines(REGISTER_GUARD)
        assert any("-MultipleInstances Parallel" in ln for ln in lines), (
            "register_guard_tasks.ps1 must set -MultipleInstances Parallel "
            "(script-level lock is the single-instance SSoT)"
        )

    def test_not_ignorenew(self):
        for ln in _non_comment_lines(REGISTER_GUARD):
            assert "-MultipleInstances IgnoreNew" not in ln, (
                f"register_guard_tasks.ps1 must NOT use IgnoreNew (blocks zombie takeover): {ln!r}"
            )


class TestRegisterAuxKeepsIgnoreNew:
    """register_aux_tasks.ps1 intentionally keeps IgnoreNew: RSSHub/TraeCache are one-shot
    AtLogOn tasks (not while-true guards), no zombie risk, IgnoreNew prevents double-fire.
    This test documents the intentional asymmetry so an AI does not 'normalize' both
    registers to the same policy."""

    def test_aux_uses_ignorenew(self):
        lines = _non_comment_lines(REGISTER_AUX)
        assert any("-MultipleInstances IgnoreNew" in ln for ln in lines), (
            "register_aux_tasks.ps1 should keep IgnoreNew (one-shot tasks, no while-true guard)"
        )


class TestGuardsDefineHeartbeat:
    """All three guard scripts must define $HeartbeatFile + Write-Heartbeat + the 5min stale
    threshold + finally cleanup, so takeover logic is uniformly present across the watchdog tier."""

    def test_heartbeat_file_constant(self):
        for script in GUARD_SCRIPTS:
            text = script.read_text(encoding="utf-8")
            assert "$HeartbeatFile = " in text, (
                f"{script.name}: missing $HeartbeatFile constant"
            )

    def test_write_heartbeat_function(self):
        for script in GUARD_SCRIPTS:
            text = script.read_text(encoding="utf-8")
            assert "function Write-Heartbeat" in text, (
                f"{script.name}: missing Write-Heartbeat function"
            )

    def test_stale_threshold_5min(self):
        for script in GUARD_SCRIPTS:
            text = script.read_text(encoding="utf-8")
            # ps1: if (((Get-Date) - ([datetime]$hbTs)).TotalMinutes -lt 5) { $stale = $false }
            assert "TotalMinutes -lt 5" in text, (
                f"{script.name}: missing 5min stale threshold "
                f"(must match HEARTBEAT_STALE_THRESHOLD_MIN=5 in test_guard_watchdog.py)"
            )

    def test_heartbeat_written_in_poll_loop(self):
        for script in GUARD_SCRIPTS:
            text = script.read_text(encoding="utf-8")
            assert "Write-Heartbeat -ChildPid $proc.Id" in text, (
                f"{script.name}: poll loop must call Write-Heartbeat -ChildPid $proc.Id every iteration"
            )

    def test_finally_cleans_heartbeat(self):
        for script in GUARD_SCRIPTS:
            text = script.read_text(encoding="utf-8")
            assert "Remove-Item $LockFile, $HeartbeatFile" in text, (
                f"{script.name}: finally block must clean both lock and heartbeat files"
            )


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
