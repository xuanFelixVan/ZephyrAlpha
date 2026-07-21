# [A_test] module_id: MOD-GOV_toctou_guard_agent_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_toctou_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""测试 TOCTOU Guard — 竞态防护"""

from pathlib import Path

from zephyr.security.access_control.guards.toctou_guard import TOCTOUGuard


class TestTOCTOUGuard:
    def test_snapshot_and_verify(self, tmp_path: Path):
        guard = TOCTOUGuard()
        test_file = tmp_path / "test.txt"
        test_file.write_text("original", encoding="utf-8")
        str_path = str(test_file)
        guard.snapshot(str_path)
        ok, msg = guard.verify(str_path)
        assert ok

    def test_tamper_detected(self, tmp_path: Path):
        guard = TOCTOUGuard()
        test_file = tmp_path / "tamper.txt"
        test_file.write_text("original", encoding="utf-8")
        str_path = str(test_file)
        guard.snapshot(str_path)
        test_file.write_text("tampered!", encoding="utf-8")
        ok, msg = guard.verify(str_path)
        assert not ok

    def test_file_gone_detected(self, tmp_path: Path):
        guard = TOCTOUGuard()
        test_file = tmp_path / "gone.txt"
        test_file.write_text("original", encoding="utf-8")
        str_path = str(test_file)
        guard.snapshot(str_path)
        test_file.unlink()
        ok, msg = guard.verify(str_path)
        assert not ok

    def test_no_snapshot_fails(self):
        guard = TOCTOUGuard()
        ok, msg = guard.verify("/nonexistent/path")
        assert not ok

    def test_clear(self):
        guard = TOCTOUGuard()
        guard._pre_state["test"] = None
        guard.clear()
        assert len(guard._pre_state) == 0
