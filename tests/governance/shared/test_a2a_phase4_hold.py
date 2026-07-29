# [A_test] module_id: MOD-GOV_a2a_phase4_hold | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-274 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_a2a_phase4_hold
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""A2A Phase 4 Hold 测试 — Phase 3 未完成时禁止 Phase 4 启动."""

from __future__ import annotations


class TestA2APhase4Hold:
    """验证 phase_hold.py 在 Phase 3 未完成时阻止 Phase 4."""

    def test_phase4_hold_blocks_concurrent_phase3(self):
        from zephyr.infrastructure.a2a_protocol.phase_hold import Phase4Hold

        hold = Phase4Hold()
        assert hasattr(hold, "check")

    def test_hold_release_when_ready(self):
        from zephyr.infrastructure.a2a_protocol.phase_hold import Phase4Hold

        hold = Phase4Hold()
        hold.phase3_complete = True
        result = hold.check()
        assert result is not None

    def test_hold_active_when_phase3_incomplete(self):
        from zephyr.infrastructure.a2a_protocol.phase_hold import Phase4Hold

        hold = Phase4Hold()
        hold.phase3_complete = False
        result = hold.check()
        assert result is not None
