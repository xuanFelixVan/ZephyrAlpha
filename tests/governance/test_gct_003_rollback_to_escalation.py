# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.governance.test_gct_003_rollback_to_escalation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""G-CT-003 — Rollback → Escalation 集成测试."""
from __future__ import annotations

import pytest


class TestGCT003RollbackToEscalation:
    """验证 rollback/result_types.py 的 RollbackResult 可被 escalation/contracts.py 消费."""

    def test_rollback_result_creatable(self):
        from zephyr.rollback.result_types import RollbackResult
        r = RollbackResult(rollback_id="R001", target="test")
        assert r.status is not None

    def test_escalation_consumes_rollback(self):
        from zephyr.rollback.result_types import RollbackResult, RollbackStatus
        from zephyr.escalation_engine.contracts import EscalationContracts
        r = RollbackResult(rollback_id="R001", target="test", status=RollbackStatus.FAILED)
        esc = EscalationContracts()
        result = esc.on_rollback_failure(r)
        assert result is not None

    def test_status_enum_values(self):
        from zephyr.rollback.result_types import RollbackStatus
        assert RollbackStatus.SUCCESS is not None
        assert RollbackStatus.FAILED is not None
        assert RollbackStatus.PARTIAL is not None
