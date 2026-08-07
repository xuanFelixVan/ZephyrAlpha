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
        ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.lstrip().startswith("#")
    ]


class TestNoGuardUsesWaitForExit:
    """$proc.WaitForExit() is the zombie root cause (main-thread deadlock). All guards
    must poll $proc.HasExited instead. WaitForExit may appear in comments only."""

    def test_no_active_waitforexit_call(self):
        for script in GUARD_SCRIPTS:
            for ln in _non_comment_lines(script):
                assert ".WaitForExit()" not in ln, (
                    f"{script.name}: active WaitForExit() call found (zombie root cause, fix #ARCH-BOOT-001): {ln!r}"
                )

    def test_all_guards_poll_hasexited(self):
        for script in GUARD_SCRIPTS:
            text = script.read_text(encoding="utf-8")
            assert "$proc.HasExited" in text, f"{script.name}: missing $proc.HasExited polling (fix #ARCH-BOOT-001)"


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
            assert "$HeartbeatFile = " in text, f"{script.name}: missing $HeartbeatFile constant"

    def test_write_heartbeat_function(self):
        for script in GUARD_SCRIPTS:
            text = script.read_text(encoding="utf-8")
            assert "function Write-Heartbeat" in text, f"{script.name}: missing Write-Heartbeat function"

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


DEADMAN_SWITCH = SCRIPTS / "deadman_switch.ps1"


class TestDeadmanSwitchInvariants:
    """Dead-man switch (#ARCH-BOOT-002 E) must be a stateless one-shot task, NOT a guard.
    It reads heartbeat files written by others and alerts if stale -- independent of the
    3 monitored services. These invariants pin the independence principle so an AI cannot
    'normalize' it into a while-true guard (which would re-introduce zombie risk) or couple
    it to the Python stack (which would die if Python is broken)."""

    def test_deadman_script_exists(self):
        assert DEADMAN_SWITCH.exists(), "scripts/deadman_switch.ps1 must exist (#ARCH-BOOT-002 E)"

    def test_not_a_guard_no_while_true(self):
        text = DEADMAN_SWITCH.read_text(encoding="utf-8")
        assert "while ($true)" not in text and "while($true)" not in text, (
            "deadman_switch.ps1 must be one-shot, NOT a while-true guard "
            "(one-shot = no zombie risk, #ARCH-BOOT-002 E independence principle)"
        )

    def test_no_waitforexit_no_child_process(self):
        for ln in _non_comment_lines(DEADMAN_SWITCH):
            assert ".WaitForExit()" not in ln, (
                f"deadman_switch.ps1: WaitForExit() found (no child process, one-shot): {ln!r}"
            )

    def test_reads_all_three_heartbeats(self):
        text = DEADMAN_SWITCH.read_text(encoding="utf-8")
        for hb in ("scheduler.heartbeat", "tick_subscriber.heartbeat", "ch_health_probe.heartbeat"):
            assert hb in text, f"deadman_switch.ps1: must read {hb} (monitors all 3 permanent services)"

    def test_has_stale_threshold(self):
        text = DEADMAN_SWITCH.read_text(encoding="utf-8")
        assert "DEADMAN_STALE_MIN" in text, "deadman_switch.ps1: missing DEADMAN_STALE_MIN config (stale threshold)"

    def test_has_cooldown(self):
        text = DEADMAN_SWITCH.read_text(encoding="utf-8")
        assert "Cooldown" in text or "cooldown" in text, (
            "deadman_switch.ps1: missing cooldown (would spam Feishu during multi-hour outage)"
        )

    def test_has_feishu_webhook_alert(self):
        text = DEADMAN_SWITCH.read_text(encoding="utf-8")
        assert "ZEPHYR_FEISHU_WEBHOOK" in text, (
            "deadman_switch.ps1: must alert via Feishu webhook (push to phone, survives service failure)"
        )


class TestDeadmanSwitchRegistered:
    """register_guard_tasks.ps1 must register ZephyrAlpha_DeadmanSwitch as 4th task."""

    def test_deadman_registered(self):
        text = REGISTER_GUARD.read_text(encoding="utf-8")
        assert "ZephyrAlpha_DeadmanSwitch" in text, (
            "register_guard_tasks.ps1: must register ZephyrAlpha_DeadmanSwitch (#ARCH-BOOT-002 E)"
        )

    def test_deadman_script_in_services(self):
        text = REGISTER_GUARD.read_text(encoding="utf-8")
        assert "deadman_switch.ps1" in text, "register_guard_tasks.ps1: must reference deadman_switch.ps1"


class TestAtomicHeartbeatWrite:
    """#ARCH-BOOT-002 D: all guard scripts must write heartbeat atomically (tmp + Move-Item).
    Out-File truncates+writes non-atomically; a new guard polling in the 5min window could
    read a half-written heartbeat -> false stale -> kill healthy guard."""

    def test_uses_move_item_for_atomic_write(self):
        for script in GUARD_SCRIPTS:
            text = script.read_text(encoding="utf-8")
            assert "Move-Item" in text and "HeartbeatFile.tmp" in text, (
                f"{script.name}: Write-Heartbeat must use tmp + Move-Item atomic write (#ARCH-BOOT-002 D)"
            )


class TestWaitForExitRootCauseDocumented:
    """#ARCH-BOOT-002 F: all guard scripts must document the WaitForExit deadlock root cause
    (PowerShell redirected output pipe buffer fills -> WaitForExit never returns). Pins the
    knowledge so an AI does not 'optimize' back to WaitForExit."""

    def test_pipe_buffer_root_cause_documented(self):
        for script in GUARD_SCRIPTS:
            text = script.read_text(encoding="utf-8")
            assert "pipe buffer" in text.lower() or "管道" in text, (
                f"{script.name}: must document 'pipe buffer fills' root cause (#ARCH-BOOT-002 F)"
            )


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
