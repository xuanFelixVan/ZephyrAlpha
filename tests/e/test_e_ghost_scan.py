# [A_test] module_id: MOD-GOV_e_ghost_scan | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_ghost_scan
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.security_governance.ghost_scan import GhostScanner


class TestGhostScannerInit:
    def test_default_state(self):
        gs = GhostScanner()
        assert gs.registered_pids == set()


class TestGhostScannerRegister:
    def test_register_single(self):
        gs = GhostScanner()
        gs.register("pid-1")
        assert "pid-1" in gs.registered_pids

    def test_register_multiple(self):
        gs = GhostScanner()
        gs.register("pid-1")
        gs.register("pid-2")
        assert len(gs.registered_pids) == 2


class TestGhostScannerDetectGhosts:
    def test_no_ghosts_all_active(self):
        gs = GhostScanner()
        gs.register("pid-1")
        ghosts = gs.detect_ghosts({"pid-1"})
        assert ghosts == []

    def test_finds_ghosts(self):
        gs = GhostScanner()
        gs.register("pid-1")
        gs.register("pid-2")
        ghosts = gs.detect_ghosts({"pid-1"})
        assert ghosts == ["pid-2"]

    def test_empty_registered_no_ghosts(self):
        gs = GhostScanner()
        assert gs.detect_ghosts({"pid-1"}) == []


class TestGhostScannerCleanup:
    def test_cleanup_removes_pid(self):
        gs = GhostScanner()
        gs.register("pid-1")
        result = gs.cleanup("pid-1")
        assert result is True
        assert "pid-1" not in gs.registered_pids

    def test_cleanup_nonexistent(self):
        gs = GhostScanner()
        result = gs.cleanup("pid-1")
        assert result is True
