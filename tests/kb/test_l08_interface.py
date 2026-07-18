# [A_test] module_id: SRC-TST-2042 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-659 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_l08_interface
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
L08 — Human-AI Interface Phase D 覆盖
========================================

验证 L08 层基础能力：Notification/ApprovalRequest 数据类构造、
ABC 子类化模式、DashboardApp 无依赖实例化。

Phase D | Safety: LOW（框架验证，无副作用）
"""


from datetime import datetime
from typing import Any

import pytest

from zephyr.frontend.dashboard.app import DashboardApp, create_app
from zephyr.frontend.interface_base import (
    ApprovalAction,
    ApprovalGatewayBase,
    ApprovalRequest,
    DashboardBase,
    Notification,
    NotificationLevel,
    NotificationManagerBase,
)


class TestNotificationDataclass:
    def test_notification_creation_defaults(self):
        n = Notification(notification_id="n-001", title="Test", body="Hello")
        assert n.notification_id == "n-001"
        assert n.title == "Test"
        assert n.body == "Hello"
        assert n.level == NotificationLevel.INFO
        assert isinstance(n.timestamp, datetime)
        assert n.source_layer == ""
        assert n.metadata == {}

    def test_notification_creation_full(self):
        ts = datetime(2026, 5, 5, 12, 0, 0)
        n = Notification(
            notification_id="n-002",
            title="Alert",
            body="Something happened",
            level=NotificationLevel.CRITICAL,
            source_layer="L04",
            timestamp=ts,
            metadata={"key": "value"},
        )
        assert n.level == NotificationLevel.CRITICAL
        assert n.source_layer == "L04"
        assert n.timestamp == ts
        assert n.metadata == {"key": "value"}

    def test_notification_immutable(self):
        n = Notification(notification_id="n-003", title="T", body="B")
        with pytest.raises(Exception):
            n.title = "Changed"  # type: ignore[misc]


class TestApprovalRequestDataclass:
    def test_approval_request_creation_defaults(self):
        req = ApprovalRequest(request_id="r-001", action="trade", reason="risk_override", requester="trader1")
        assert req.request_id == "r-001"
        assert req.action == "trade"
        assert req.reason == "risk_override"
        assert req.requester == "trader1"
        assert req.status == "pending"
        assert req.context == {}
        assert req.expires_at is None

    def test_approval_request_creation_full(self):
        ts = datetime(2026, 5, 5, 12, 0, 0)
        expires = datetime(2026, 5, 5, 13, 0, 0)
        req = ApprovalRequest(
            request_id="r-002",
            action="large_order",
            reason="position_limit",
            requester="algo1",
            context={"size": 100000},
            created_at=ts,
            expires_at=expires,
            status="pending",
        )
        assert req.context == {"size": 100000}
        assert req.expires_at == expires

    def test_approval_request_immutable(self):
        req = ApprovalRequest(request_id="r-003", action="a", reason="b", requester="c")
        with pytest.raises(Exception):
            req.status = "approved"  # type: ignore[misc]


class TestNotificationLevelEnum:
    def test_notification_level_values(self):
        assert NotificationLevel.INFO.value == "info"
        assert NotificationLevel.WARNING.value == "warning"
        assert NotificationLevel.ERROR.value == "error"
        assert NotificationLevel.CRITICAL.value == "critical"


class TestApprovalActionEnum:
    def test_approval_action_values(self):
        assert ApprovalAction.APPROVE.value == "approve"
        assert ApprovalAction.REJECT.value == "reject"
        assert ApprovalAction.DELEGATE.value == "delegate"
        assert ApprovalAction.ESCALATE.value == "escalate"


class TestABCPattern:
    """验证 ABC 子类化模式——确保接口可按预期扩展。"""

    def test_dashboard_base_subclass(self):
        class MyDashboard(DashboardBase):
            def render(self, data: dict[str, Any]) -> None:
                pass

        d = MyDashboard()
        assert d.refresh() == {}
        assert d is not None

    def test_notification_manager_subclass(self):
        class MyNotifier(NotificationManagerBase):
            def send(self, notification: Notification, channels: list[str] | None = None) -> bool:
                return True

            def channels(self) -> list[str]:
                return ["feishu", "email"]

        notifier = MyNotifier()
        n = Notification(notification_id="n-004", title="T", body="B")
        assert notifier.send(n) is True
        assert notifier.channels() == ["feishu", "email"]

    def test_approval_gateway_subclass(self):
        class MyGateway(ApprovalGatewayBase):
            def submit(self, request: ApprovalRequest) -> str:
                return request.request_id

            def decide(self, request_id: str, action: ApprovalAction, comment: str = "") -> bool:
                return True

            def pending(self) -> list[ApprovalRequest]:
                return []

        gw = MyGateway()
        req = ApprovalRequest(request_id="r-004", action="trade", reason="override", requester="trader")
        assert gw.submit(req) == "r-004"
        assert gw.decide("r-004", ApprovalAction.APPROVE) is True
        assert gw.pending() == []

    def test_cannot_instantiate_abstract(self):
        for cls in [DashboardBase, NotificationManagerBase, ApprovalGatewayBase]:
            with pytest.raises(TypeError):
                cls()  # type: ignore[abstract]


class TestDashboardApp:
    """DashboardApp 无外部依赖时基础实例化。"""

    def test_create_app_no_deps(self):
        app = create_app()
        assert isinstance(app, DashboardApp)

    def test_render_page_unknown(self):
        app = create_app()
        result = app.render_page("nonexistent")
        assert "error" in result

    def test_get_task_progress_no_deps(self):
        app = create_app()
        data = app.get_task_progress()
        assert data.overall_rate == 0.0

    def test_get_knowledge_overview_no_deps(self):
        app = create_app()
        data = app.get_knowledge_overview()
        assert data.total_entries == 0

    def test_render_page_task_progress_no_deps(self):
        app = create_app()
        result = app.render_page("task_progress")
        assert "overall_rate" in result
