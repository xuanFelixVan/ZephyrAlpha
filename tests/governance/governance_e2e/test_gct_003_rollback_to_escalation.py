# [A_test] module_id: MOD-GOV_gct_rollback_to_escalation | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-283 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_gct_003_rollback_to_escalation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""G-CT-003 — Rollback → Escalation 集成测试."""

from __future__ import annotations


class TestGCT003RollbackToEscalation:
    """验证 rollback/result_types.py 的 RollbackResult 可被 escalation/contracts.py 消费."""

    def test_rollback_result_creatable(self):
        from zephyr.governance.escalation.result_types import RollbackResult

        r = RollbackResult(rollback_id="R001", target="test")
        assert r.status is not None

    def test_escalation_consumes_rollback(self):
        from zephyr.governance.escalation.contracts import EscalationContracts
        from zephyr.governance.escalation.result_types import RollbackResult, RollbackStatus

        r = RollbackResult(rollback_id="R001", target="test", status=RollbackStatus.FAILED)
        esc = EscalationContracts()
        result = esc.on_rollback_failure(r)
        assert result is not None

    def test_status_enum_values(self):
        from zephyr.governance.escalation.result_types import RollbackStatus

        assert RollbackStatus.SUCCESS is not None
        assert RollbackStatus.FAILED is not None
        assert RollbackStatus.PARTIAL is not None
