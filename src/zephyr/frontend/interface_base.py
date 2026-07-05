# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain-frontend/hmi-core/blueprint.md
# [MODULE] zephyr.frontend.interface_base
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_interface_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
D_FRONTEND — Human-AI Interface Layer Skeleton

人机交互层抽象基类。定义仪表盘、通知分发、人工审批与交互协议的核心接口。

OCP 扩展点：
  - DashboardBase             — 监控面板渲染
  - NotificationManagerBase   — 通知/告警分发
  - ApprovalGatewayBase       — 人工审批闸门

消费契约：CTR-P1-008(RiskDashboardSnapshot) ← D_RISK, CTR-P1-009(PerformanceAttributionReport) ← D_REPORTING
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar


class NotificationLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ApprovalAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    DELEGATE = "delegate"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class Notification:
    """通知消息"""

    notification_id: str
    title: str
    body: str
    level: NotificationLevel = NotificationLevel.INFO
    source_layer: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ApprovalRequest:
    """人工审批请求"""

    request_id: str
    action: str
    reason: str
    requester: str
    context: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    status: str = "pending"


class DashboardBase(abc.ABC):
    """监控面板基类（OCP 扩展点）

    实现者要求：
      - render(data): 渲染仪表盘页面
      - refresh(interval_s): 定时刷新数据
      - 支持多页面/多组件组合
    """

    # 5.116.1 修复: 移除死 _registry 字段——无 __init_subclass__ 写入,无外部读取

    @abc.abstractmethod
    def render(self, data: dict[str, Any]) -> None:
        """渲染仪表盘"""
        ...

    def refresh(self, interval_s: float = 5.0) -> dict[str, Any]:
        """定时刷新数据（默认实现返回空 dict，子类覆盖）"""
        return {}


class NotificationManagerBase(abc.ABC):
    """通知分发管理器（OCP 扩展点）

    实现者要求：
      - send(notification): 发送通知到目标渠道
      - channels(): 返回可用通知渠道列表
      - 支持多渠道：飞书 / 邮件 / 钉钉 / 企业微信 / Slack
    """

    # 5.116.1 修复: 移除死 _registry 字段——无 __init_subclass__ 写入,无外部读取

    @abc.abstractmethod
    def send(self, notification: Notification, channels: list[str] | None = None) -> bool:
        """发送通知到指定渠道，返回是否全部成功"""
        ...

    @abc.abstractmethod
    def channels(self) -> list[str]:
        """返回可用通知渠道列表"""
        ...


class ApprovalGatewayBase(abc.ABC):
    """人工审批闸门（OCP 扩展点）

    实现者要求：
      - submit(request): 提交审批请求
      - decide(request_id, action): 执行审批决策
      - pending(): 返回待审批列表

    典型流程：
      1. D_PORTFOLIO_CORE/D_EXECUTION_CORE 触达风控硬限 → submit 审批请求
      2. 人工通过 D_FRONTEND Dashboard 查看 → decide approve/reject
      3. 审批结果写回 → D_PORTFOLIO_CORE/D_EXECUTION_CORE 继续或中止
    """

    # 5.116.1 修复: 移除死 _registry 字段——无 __init_subclass__ 写入,无外部读取

    @abc.abstractmethod
    def submit(self, request: ApprovalRequest) -> str:
        """提交审批请求，返回 request_id"""
        ...

    @abc.abstractmethod
    def decide(self, request_id: str, action: ApprovalAction, comment: str = "") -> bool:
        """执行审批决策"""
        ...

    @abc.abstractmethod
    def pending(self) -> list[ApprovalRequest]:
        """返回所有待审批请求"""
        ...


__all__ = [
    "ApprovalAction",
    "ApprovalGatewayBase",
    "ApprovalRequest",
    "DashboardBase",
    "Notification",
    "NotificationLevel",
    "NotificationManagerBase",
]
