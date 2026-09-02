# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md | §test
# [MODULE] tests.frontend.test_default_approval_gateway
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.frontend.implementations.default_approval_gateway
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_default_approval_gateway.py
# [A_test] module_id: MOD-L08-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-L08-001 单元测试: DefaultApprovalGateway — 默认审批网关 (B-007 审批载体)。

蓝图验收: import 成功, submit 返回 request_id, decide 返回 bool, pending 返回 list。
覆盖: 提交/审批/拒绝闭环, 到期不可批(fail-closed), 未知单号, 重复提交,
DELEGATE/ESCALATE 非终态, 决策留痕(B-016 审计友好), 注入时钟确定性。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

pytest.importorskip(
    "zephyr.frontend.implementations.default_approval_gateway",
    reason="default_approval_gateway not importable",
)

from zephyr.frontend.implementations.default_approval_gateway import (  # noqa: E402
    DefaultApprovalGateway,
    InvalidApprovalRequestError,
)
from zephyr.frontend.interface_base import (  # noqa: E402
    ApprovalAction,
    ApprovalRequest,
)

_NOW = datetime(2026, 8, 21, 12, 0, tzinfo=UTC)


def _request(
    request_id: str = "req-1",
    *,
    expires_at: datetime | None = None,
) -> ApprovalRequest:
    return ApprovalRequest(
        request_id=request_id,
        action="deploy_strategy",
        reason="新策略上线需人工审批（B-007）",
        requester="strategy_factory",
        created_at=_NOW,
        expires_at=expires_at,
    )


def _gateway() -> DefaultApprovalGateway:
    return DefaultApprovalGateway(clock=lambda: _NOW)


class TestSubmit:
    def test_submit_returns_request_id(self):
        gw = _gateway()
        assert gw.submit(_request()) == "req-1"
        assert isinstance(gw.pending(), list)
        assert len(gw.pending()) == 1

    def test_duplicate_request_id_rejected(self):
        gw = _gateway()
        gw.submit(_request())
        with pytest.raises(InvalidApprovalRequestError):
            gw.submit(_request())

    def test_empty_action_rejected(self):
        gw = _gateway()
        with pytest.raises(InvalidApprovalRequestError):
            gw.submit(
                _request().__class__(
                    request_id="req-x",
                    action="",
                    reason="r",
                    requester="q",
                )
            )


class TestDecide:
    def test_approve_pending_request(self):
        gw = _gateway()
        gw.submit(_request())
        assert gw.decide("req-1", ApprovalAction.APPROVE, comment="ok") is True
        assert gw.pending() == []

    def test_reject_pending_request(self):
        gw = _gateway()
        gw.submit(_request())
        assert gw.decide("req-1", ApprovalAction.REJECT) is True
        assert gw.pending() == []

    def test_decide_unknown_request_false(self):
        gw = _gateway()
        assert gw.decide("no-such", ApprovalAction.APPROVE) is False

    def test_double_decide_false(self):
        gw = _gateway()
        gw.submit(_request())
        gw.decide("req-1", ApprovalAction.APPROVE)
        assert gw.decide("req-1", ApprovalAction.REJECT) is False

    def test_expired_request_cannot_approve(self):
        gw = _gateway()
        gw.submit(_request(expires_at=_NOW - timedelta(seconds=1)))
        assert gw.decide("req-1", ApprovalAction.APPROVE) is False
        # 到期后不再出现于 pending（fail-closed: 过期即不可批）
        assert gw.pending() == []

    def test_delegate_keeps_pending(self):
        gw = _gateway()
        gw.submit(_request())
        assert gw.decide("req-1", ApprovalAction.DELEGATE, comment="转上级") is True
        assert len(gw.pending()) == 1

    def test_escalate_keeps_pending(self):
        gw = _gateway()
        gw.submit(_request())
        assert gw.decide("req-1", ApprovalAction.ESCALATE) is True
        assert len(gw.pending()) == 1


class TestDecisionAuditTrail:
    def test_decisions_logged(self):
        gw = _gateway()
        gw.submit(_request())
        gw.decide("req-1", ApprovalAction.APPROVE, comment="复核通过")
        log = gw.decision_log()
        assert len(log) == 1
        assert log[0].request_id == "req-1"
        assert log[0].action == ApprovalAction.APPROVE
        assert log[0].comment == "复核通过"

    def test_log_immutable_copy(self):
        gw = _gateway()
        gw.submit(_request())
        gw.decide("req-1", ApprovalAction.APPROVE)
        log = gw.decision_log()
        assert isinstance(log, tuple)
