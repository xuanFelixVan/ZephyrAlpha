# [A_test] module_id: MOD-GOV_l08_human_ai_interface | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md | §test
# [MODULE] zephyr.l08_human_ai_interface
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_l08_human_ai_interface.py
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime

import pytest

l08 = pytest.importorskip("zephyr.l08_human_ai_interface", reason="l08-human-ai-interface not importable")

from zephyr.frontend.interface_base import (
    ApprovalAction,
    ApprovalGatewayBase,
    ApprovalRequest,
    DashboardBase,
    Notification,
    NotificationLevel,
    NotificationManagerBase,
)


class _ConcreteDashboard(DashboardBase):
    def __init__(self):
        self.rendered_data = None
        self._refresh_data = {}

    def render(self, data):
        self.rendered_data = data

    def refresh(self, interval_s=5.0):
        return self._refresh_data


class _ConcreteNotificationManager(NotificationManagerBase):
    def __init__(self):
        self._channels = ["email", "slack"]
        self._sent = []

    def send(self, notification, channels=None):
        targets = channels or self._channels
        self._sent.append((notification, targets))
        return True

    def channels(self):
        return list(self._channels)


class _ConcreteApprovalGateway(ApprovalGatewayBase):
    def __init__(self):
        self._pending = {}
        self._decisions = {}

    def submit(self, request):
        self._pending[request.request_id] = request
        return request.request_id

    def decide(self, request_id, action, comment=""):
        if request_id not in self._pending:
            return False
        self._decisions[request_id] = (action, comment)
        del self._pending[request_id]
        return True

    def pending(self):
        return list(self._pending.values())


class TestNotificationLevel:
    def test_values(self):
        assert NotificationLevel.INFO.value == "info"
        assert NotificationLevel.WARNING.value == "warning"
        assert NotificationLevel.ERROR.value == "error"
        assert NotificationLevel.CRITICAL.value == "critical"

    def test_string_enum(self):
        assert isinstance(NotificationLevel.INFO, str)
        assert NotificationLevel.INFO == "info"


class TestApprovalAction:
    def test_values(self):
        assert ApprovalAction.APPROVE.value == "approve"
        assert ApprovalAction.REJECT.value == "reject"
        assert ApprovalAction.DELEGATE.value == "delegate"
        assert ApprovalAction.ESCALATE.value == "escalate"

    def test_string_enum(self):
        assert isinstance(ApprovalAction.APPROVE, str)


class TestNotification:
    def test_creation_required_fields(self):
        n = Notification(
            notification_id="n-001",
            title="Test Alert",
            body="Something happened",
        )
        assert n.notification_id == "n-001"
        assert n.title == "Test Alert"
        assert n.body == "Something happened"
        assert n.level == NotificationLevel.INFO

    def test_creation_with_level(self):
        n = Notification(
            notification_id="n-002",
            title="Critical",
            body="System failure",
            level=NotificationLevel.CRITICAL,
        )
        assert n.level == NotificationLevel.CRITICAL

    def test_frozen(self):
        n = Notification(
            notification_id="n-001",
            title="Test",
            body="Body",
        )
        with pytest.raises(AttributeError):
            n.title = "changed"

    def test_default_timestamp(self):
        n = Notification(
            notification_id="n-001",
            title="Test",
            body="Body",
        )
        assert isinstance(n.timestamp, datetime)

    def test_source_layer(self):
        n = Notification(
            notification_id="n-001",
            title="Test",
            body="Body",
            source_layer="l04-risk-management",
        )
        assert n.source_layer == "l04-risk-management"

    def test_metadata(self):
        n = Notification(
            notification_id="n-001",
            title="Test",
            body="Body",
            metadata={"key": "value"},
        )
        assert n.metadata["key"] == "value"

    def test_empty_metadata_default(self):
        n = Notification(
            notification_id="n-001",
            title="Test",
            body="Body",
        )
        assert n.metadata == {}


class TestApprovalRequest:
    def test_creation_required_fields(self):
        r = ApprovalRequest(
            request_id="ar-001",
            action="override_risk_limit",
            reason="Market conditions require higher limit",
            requester="agent-1",
        )
        assert r.request_id == "ar-001"
        assert r.action == "override_risk_limit"
        assert r.status == "pending"

    def test_frozen(self):
        r = ApprovalRequest(
            request_id="ar-001",
            action="override",
            reason="test",
            requester="agent",
        )
        with pytest.raises(AttributeError):
            r.status = "approved"

    def test_context_default(self):
        r = ApprovalRequest(
            request_id="ar-001",
            action="override",
            reason="test",
            requester="agent",
        )
        assert r.context == {}

    def test_with_context(self):
        r = ApprovalRequest(
            request_id="ar-001",
            action="override",
            reason="test",
            requester="agent",
            context={"symbol": "AAPL", "weight": 0.15},
        )
        assert r.context["symbol"] == "AAPL"

    def test_expires_at_none_default(self):
        r = ApprovalRequest(
            request_id="ar-001",
            action="override",
            reason="test",
            requester="agent",
        )
        assert r.expires_at is None

    def test_with_expiry(self):
        future = datetime(2030, 1, 1, tzinfo=UTC)
        r = ApprovalRequest(
            request_id="ar-001",
            action="override",
            reason="test",
            requester="agent",
            expires_at=future,
        )
        assert r.expires_at == future


class TestDashboardBase:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            DashboardBase()

    def test_render(self):
        d = _ConcreteDashboard()
        d.render({"key": "value"})
        assert d.rendered_data == {"key": "value"}

    def test_refresh_default(self):
        d = _ConcreteDashboard()
        result = d.refresh()
        assert result == {}

    def test_refresh_with_data(self):
        d = _ConcreteDashboard()
        d.refresh_data = {"risk_score": 0.8}
        result = d.refresh()
        assert result["risk_score"] == 0.8

    def test_render_empty_data(self):
        d = _ConcreteDashboard()
        d.render({})
        assert d.rendered_data == {}


class TestNotificationManagerBase:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            NotificationManagerBase()

    def test_send_default_channels(self):
        m = _ConcreteNotificationManager()
        n = Notification(notification_id="n-1", title="T", body="B")
        result = m.send(n)
        assert result is True
        assert len(m.sent) == 1

    def test_send_specific_channels(self):
        m = _ConcreteNotificationManager()
        n = Notification(notification_id="n-1", title="T", body="B")
        m.send(n, channels=["slack"])
        assert m.sent[0][1] == ["slack"]

    def test_channels_list(self):
        m = _ConcreteNotificationManager()
        channels = m.channels()
        assert "email" in channels
        assert "slack" in channels


class TestApprovalGatewayBase:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            ApprovalGatewayBase()

    def test_submit(self):
        g = _ConcreteApprovalGateway()
        r = ApprovalRequest(
            request_id="ar-1",
            action="override",
            reason="test",
            requester="agent",
        )
        request_id = g.submit(r)
        assert request_id == "ar-1"

    def test_decide_approve(self):
        g = _ConcreteApprovalGateway()
        r = ApprovalRequest(
            request_id="ar-1",
            action="override",
            reason="test",
            requester="agent",
        )
        g.submit(r)
        result = g.decide("ar-1", ApprovalAction.APPROVE, "looks good")
        assert result is True

    def test_decide_reject(self):
        g = _ConcreteApprovalGateway()
        r = ApprovalRequest(
            request_id="ar-1",
            action="override",
            reason="test",
            requester="agent",
        )
        g.submit(r)
        result = g.decide("ar-1", ApprovalAction.REJECT, "too risky")
        assert result is True

    def test_decide_nonexistent(self):
        g = _ConcreteApprovalGateway()
        result = g.decide("nonexistent", ApprovalAction.APPROVE)
        assert result is False

    def test_pending(self):
        g = _ConcreteApprovalGateway()
        r1 = ApprovalRequest(
            request_id="ar-1",
            action="override",
            reason="test",
            requester="agent",
        )
        r2 = ApprovalRequest(
            request_id="ar-2",
            action="escalate",
            reason="test2",
            requester="agent",
        )
        g.submit(r1)
        g.submit(r2)
        pending = g.pending()
        assert len(pending) == 2

    def test_pending_empty(self):
        g = _ConcreteApprovalGateway()
        assert g.pending() == []

    def test_decide_removes_from_pending(self):
        g = _ConcreteApprovalGateway()
        r = ApprovalRequest(
            request_id="ar-1",
            action="override",
            reason="test",
            requester="agent",
        )
        g.submit(r)
        g.decide("ar-1", ApprovalAction.APPROVE)
        assert len(g.pending()) == 0
