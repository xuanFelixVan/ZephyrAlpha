# [BLUEPRINT] MOD-ML-002 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-ML_test_ai_operator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ml_train.test_ai_operator
# [TESTS] src/zephyr/ml_train/ai_operator/operator.py
# [TTL] task_bound
"""MOD-ML-002 AI 操作员 toy 断言（上线/下线/巡检封装，全操作留痕+批准令牌）。

红线：全部操作 testing 封顶——online 只产"申请记录"不真生效（B-007/B-009）。
"""

from __future__ import annotations

import pytest

from zephyr.ml_train.ai_operator import (
    AIOperator,
    ApprovalToken,
    OperatorActionError,
)


def _token(scope: str = "model_online", valid: bool = True) -> ApprovalToken:
    return ApprovalToken(
        token_id="tok-1",
        approver="owner",
        scope=scope,
        valid=valid,
    )


class TestOnlineOffline:
    def test_online_requires_valid_token(self):
        op = AIOperator()
        with pytest.raises(OperatorActionError) as exc:
            op.request_online("ML-DENSITY-001", token=_token(valid=False))
        assert exc.value.error_code == "ZA-MLT-0005"

    def test_online_scope_mismatch_rejected(self):
        op = AIOperator()
        with pytest.raises(OperatorActionError, match="scope"):
            op.request_online("ML-DENSITY-001", token=_token(scope="model_offline"))

    def test_online_with_token_records_request_not_effective(self):
        """testing 封顶：即便令牌合法，online 也只产申请记录，模型永不真上线。"""
        op = AIOperator()
        rec = op.request_online("ML-DENSITY-001", token=_token())
        assert rec.action == "online"
        assert rec.effective is False  # 只记录不生效
        assert rec.status == "pending_owner_execution"

    def test_offline_with_token_records_request(self):
        op = AIOperator()
        rec = op.request_offline("ML-DENSITY-001", token=_token(scope="model_offline"))
        assert rec.action == "offline"
        assert rec.effective is False


class TestInspection:
    def test_inspect_returns_health_snapshot(self):
        op = AIOperator()
        snap = op.inspect("ML-DENSITY-001", metrics={"pinball_mean": 0.42})
        assert snap["model_id"] == "ML-DENSITY-001"
        assert snap["metrics"]["pinball_mean"] == 0.42
        assert "inspected_at" in snap

    def test_inspect_needs_no_token_but_is_logged(self):
        op = AIOperator()
        op.inspect("ML-DENSITY-001", metrics={})
        assert len(op.audit_log()) == 1


class TestAuditTrail:
    def test_all_actions_logged_in_order(self):
        op = AIOperator()
        op.request_online("m1", token=_token())
        op.inspect("m1", metrics={})
        op.request_offline("m1", token=_token(scope="model_offline"))
        log = op.audit_log()
        assert [r.action for r in log] == ["online", "inspect", "offline"]
        assert all(r.operator == "ai_operator" for r in log)

    def test_failed_token_attempt_also_logged(self):
        op = AIOperator()
        with pytest.raises(OperatorActionError):
            op.request_online("m1", token=_token(valid=False))
        log = op.audit_log()
        assert len(log) == 1
        assert log[0].status == "rejected"

    def test_audit_log_immutable_copy(self):
        op = AIOperator()
        op.inspect("m1", metrics={})
        log = op.audit_log()
        log.clear()
        assert len(op.audit_log()) == 1
