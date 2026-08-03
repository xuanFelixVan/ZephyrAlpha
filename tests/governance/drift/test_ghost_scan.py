# [A_test] module_id: MOD-GOV_ghost_scan | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_ghost_scan
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_ghost_scan.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.security_governance.ghost_scan import GhostScanner


class TestGhostScannerInstantiation:
    def test_init_creates_empty_registered_pids(self):
        gs = GhostScanner()
        assert gs.registered_pids == set()

    def test_init_is_set_type(self):
        gs = GhostScanner()
        assert isinstance(gs.registered_pids, set)


class TestGhostScannerRegister:
    def test_register_single_pid(self):
        gs = GhostScanner()
        gs.register("1234")
        assert "1234" in gs.registered_pids

    def test_register_multiple_pids(self):
        gs = GhostScanner()
        gs.register("1234")
        gs.register("5678")
        assert gs.registered_pids == {"1234", "5678"}

    def test_register_duplicate_pid_idempotent(self):
        gs = GhostScanner()
        gs.register("1234")
        gs.register("1234")
        assert len(gs.registered_pids) == 1


class TestGhostScannerDetectGhosts:
    def test_no_ghosts_when_all_active(self):
        gs = GhostScanner()
        gs.register("1234")
        gs.register("5678")
        ghosts = gs.detect_ghosts({"1234", "5678"})
        assert ghosts == []

    def test_ghost_detected_when_pid_not_active(self):
        gs = GhostScanner()
        gs.register("1234")
        gs.register("5678")
        ghosts = gs.detect_ghosts({"1234"})
        assert ghosts == ["5678"]

    def test_all_ghosts_when_no_active(self):
        gs = GhostScanner()
        gs.register("1234")
        gs.register("5678")
        ghosts = gs.detect_ghosts(set())
        assert set(ghosts) == {"1234", "5678"}

    def test_no_ghosts_when_nothing_registered(self):
        gs = GhostScanner()
        ghosts = gs.detect_ghosts({"1234"})
        assert ghosts == []

    def test_no_ghosts_when_both_empty(self):
        gs = GhostScanner()
        ghosts = gs.detect_ghosts(set())
        assert ghosts == []

    def test_extra_active_pids_ignored(self):
        gs = GhostScanner()
        gs.register("1234")
        ghosts = gs.detect_ghosts({"1234", "9999", "0000"})
        assert ghosts == []

    def test_partial_ghost_detection(self):
        gs = GhostScanner()
        gs.register("1")
        gs.register("2")
        gs.register("3")
        gs.register("4")
        ghosts = gs.detect_ghosts({"1", "3"})
        assert set(ghosts) == {"2", "4"}


class TestGhostScannerCleanup:
    def test_cleanup_removes_registered_pid(self):
        gs = GhostScanner()
        gs.register("1234")
        result = gs.cleanup("1234")
        assert result is True
        assert "1234" not in gs.registered_pids

    def test_cleanup_nonexistent_pid_returns_true(self):
        gs = GhostScanner()
        result = gs.cleanup("9999")
        assert result is True

    def test_cleanup_then_detect_no_ghost(self):
        gs = GhostScanner()
        gs.register("1234")
        gs.register("5678")
        gs.cleanup("5678")
        ghosts = gs.detect_ghosts({"1234"})
        assert ghosts == []

    def test_cleanup_all_pids(self):
        gs = GhostScanner()
        gs.register("1")
        gs.register("2")
        gs.register("3")
        gs.cleanup("1")
        gs.cleanup("2")
        gs.cleanup("3")
        assert gs.registered_pids == set()
