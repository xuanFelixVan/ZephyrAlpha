# [BLUEPRINT] MOD-FE-012 | docs/03_modules/_domain_frontend/feishu_bot_sender/blueprint.md
# [MODULE] zephyr.frontend.implementations.feishu_bot_sender
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] 无（协议核心纯内存；webhook client/时钟全注入，密钥仅 secrets 引用不落地）
# [CONSUMERS] 运行时装配批（审批通知发送 / 告警推送微信备选通道装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] webhook_ref 仅 secrets:// 引用(明文URL拒绝); 按钮动作词表闭合(approve|reject|view); 告警级别词表闭合(info|warning|critical); 审批模板字段≥1且按钮≤3; client注入不真发(异常记失败不阻断); 发送回执全量留痕(receipt_id确定性); 时钟全注入; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_frontend/feishu_bot_sender/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] FeishuBotError(占位 ZA-FE-UNREGISTERED-FEISHU-BOT)——明文webhook/client未注入/模板字段非法/按钮非法/告警字段非法时抛
# [TESTS] tests/frontend/test_feishu_bot_sender.py
# [A_module] module_id=MOD-FE-012 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""FeishuBotSender — 飞书机器人推送器（MOD-FE-012）。

B9-10705（AUD-DRAFT-001-DIGEST P2 波 P2-W11，CAND-FE-013，B9 D-FRONTEND-24）：
飞书自定义机器人 webhook sender（EXT-004 REST 语义，client 注入不真发）+
**审批通知模板**（标题/字段/按钮 schema）+ **告警推送**（作为微信备选
通道路由标记 wechat_fallback）+ **发送回执记录**（receipt_id 确定性）。

查重分工：alert_senders=企业微信/邮件实发传输层（本件=飞书卡片载荷构造
与回执，webhook client 注入复用传输语义，不重建 HTTP）；notification_router
=通道路由与升级（本件=飞书单通道发送器，可被其 ChannelBinding 适配消费）。
"""

from __future__ import annotations

import datetime
import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "AlertLevel",
    "AlertPush",
    "ApprovalAction",
    "ApprovalButton",
    "ApprovalTemplate",
    "FeishuBotError",
    "FeishuBotSender",
    "SendReceipt",
]

#: 密钥引用唯一合法协议头（密钥不落地，仅 secrets 引用）
_SECRET_SCHEME: Final[str] = "secrets://"

#: 审批卡片字段/按钮上限（飞书卡片 schema 约束）
_MAX_FIELDS: Final[int] = 20
_MAX_BUTTONS: Final[int] = 3


class FeishuBotError(Exception):
    """飞书推送输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FE-UNREGISTERED-FEISHU-BOT。
    """


class ApprovalAction(str, Enum):
    """审批按钮动作（词表闭合）。"""

    APPROVE = "approve"
    REJECT = "reject"
    VIEW = "view"


class AlertLevel(str, Enum):
    """告警级别（词表闭合）。"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ApprovalButton:
    """审批按钮 schema。"""

    label: str
    action: ApprovalAction
    value: str = ""


@dataclass(frozen=True)
class ApprovalTemplate:
    """审批通知模板 schema（标题/字段/按钮）。"""

    approval_id: str
    title: str
    fields: tuple[tuple[str, str], ...]
    buttons: tuple[ApprovalButton, ...] = ()


@dataclass(frozen=True)
class AlertPush:
    """告警推送载荷（wechat_fallback=微信备选通道路由标记）。"""

    alert_id: str
    level: AlertLevel
    title: str
    content: str
    wechat_fallback: bool = False


@dataclass(frozen=True)
class SendReceipt:
    """发送回执（best-effort：ok=False 不阻断主链路）。"""

    receipt_id: str
    kind: str
    target_id: str
    ok: bool
    detail: str
    webhook_ref: str
    sent_at: datetime.datetime


class FeishuBotSender:
    """飞书机器人推送器（webhook client 注入不真发 + 回执留痕）。

    Args:
        webhook_ref: 机器人 webhook 的 secrets 引用（密钥不落地）。
        client: webhook client 注入（(webhook_ref, payload) → 响应 Mapping，不真发）。
        clock: 时钟注入（回执时间戳确定性）。
    """

    def __init__(
        self,
        *,
        webhook_ref: str,
        client: Callable[[str, Mapping[str, Any]], Mapping[str, Any]],
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not isinstance(webhook_ref, str) or not webhook_ref:
            raise FeishuBotError("webhook_ref 为空")
        if not webhook_ref.startswith(_SECRET_SCHEME) or len(webhook_ref) <= len(_SECRET_SCHEME):
            raise FeishuBotError(
                f"webhook_ref 非法: {webhook_ref!r}（密钥仅 {_SECRET_SCHEME} 引用，不落地）"
            )
        if "http" in webhook_ref.lower():
            raise FeishuBotError(f"webhook_ref 疑似明文 URL: {webhook_ref!r}（禁止落地）")
        if not callable(client):
            raise FeishuBotError("client 未注入（webhook 发送 Fail-Closed）")
        self._webhook_ref = webhook_ref
        self._client = client
        self._clock = clock or datetime.datetime.now
        self._counter = 0
        self._receipts: list[SendReceipt] = []

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _dispatch(self, kind: str, target_id: str, payload: Mapping[str, Any]) -> SendReceipt:
        now = self._clock()
        self._counter += 1
        try:
            response = self._client(self._webhook_ref, payload)
            ok = isinstance(response, Mapping) and (
                response.get("code") == 0 or response.get("StatusCode") == 0
            )
            detail = "sent" if ok else "rejected_by_webhook"
        except Exception:  # noqa: BLE001 — 发送 best-effort，client 异常不阻断
            _log.exception("飞书 webhook client 异常: %s", target_id)
            ok, detail = False, "client_exception"
        if not ok:
            _log.warning("飞书推送失败: %s %s (%s)", kind, target_id, detail)
        receipt = SendReceipt(
            receipt_id=f"fs-{self._counter:06d}",
            kind=kind,
            target_id=target_id,
            ok=ok,
            detail=detail,
            webhook_ref=self._webhook_ref,
            sent_at=now,
        )
        self._receipts.append(receipt)
        return receipt

    @staticmethod
    def _validate_template(template: ApprovalTemplate) -> None:
        if not isinstance(template, ApprovalTemplate):
            raise FeishuBotError(f"审批模板类型非法: {template!r}")
        if not isinstance(template.approval_id, str) or not template.approval_id:
            raise FeishuBotError("approval_id 为空")
        if not isinstance(template.title, str) or not template.title:
            raise FeishuBotError("审批标题为空")
        if isinstance(template.fields, (str, bytes)) or not template.fields:
            raise FeishuBotError("审批字段为空（至少 1 项）")
        if len(template.fields) > _MAX_FIELDS:
            raise FeishuBotError(f"审批字段超限: {len(template.fields)} > {_MAX_FIELDS}")
        for pair in template.fields:
            if (
                not isinstance(pair, tuple)
                or len(pair) != 2
                or not all(isinstance(v, str) and v for v in pair)
            ):
                raise FeishuBotError(f"审批字段非法: {pair!r}（须二元非空字符串组）")
        if len(template.buttons) > _MAX_BUTTONS:
            raise FeishuBotError(f"审批按钮超限: {len(template.buttons)} > {_MAX_BUTTONS}")
        for button in template.buttons:
            if not isinstance(button, ApprovalButton):
                raise FeishuBotError(f"按钮类型非法: {button!r}")
            if not isinstance(button.label, str) or not button.label:
                raise FeishuBotError("按钮文案为空")
            if not isinstance(button.action, ApprovalAction):
                raise FeishuBotError(f"按钮动作非法: {button.action!r}")

    # ── 发送 ─────────────────────────────────────────────────────────────

    def send_approval(self, template: ApprovalTemplate) -> SendReceipt:
        """审批通知：模板 schema 校验（Fail-Closed）→ 卡片 payload → client 投递。"""
        self._validate_template(template)
        elements: list[dict[str, Any]] = [
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": True,
                        "text": {"tag": "lark_md", "content": f"**{label}**\n{value}"},
                    }
                    for label, value in template.fields
                ],
            }
        ]
        if template.buttons:
            elements.append({
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": button.label},
                        "type": {
                            ApprovalAction.APPROVE: "primary",
                            ApprovalAction.REJECT: "danger",
                            ApprovalAction.VIEW: "default",
                        }[button.action],
                        "value": {
                            "approval_id": template.approval_id,
                            "action": button.action.value,
                            "extra": button.value,
                        },
                    }
                    for button in template.buttons
                ],
            })
        payload: dict[str, Any] = {
            "msg_type": "interactive",
            "card": {
                "header": {"title": {"tag": "plain_text", "content": template.title}},
                "elements": elements,
            },
        }
        return self._dispatch("approval", template.approval_id, payload)

    def send_alert(self, alert: AlertPush) -> SendReceipt:
        """告警推送：级别词表校验 → 文本 payload（含微信备选通道标记）→ client。"""
        if not isinstance(alert, AlertPush):
            raise FeishuBotError(f"告警载荷类型非法: {alert!r}")
        if not isinstance(alert.alert_id, str) or not alert.alert_id:
            raise FeishuBotError("alert_id 为空")
        if not isinstance(alert.level, AlertLevel):
            raise FeishuBotError(f"告警级别非法: {alert.level!r}")
        if not isinstance(alert.title, str) or not alert.title:
            raise FeishuBotError("告警标题为空")
        if not isinstance(alert.content, str) or not alert.content:
            raise FeishuBotError("告警内容为空")
        if not isinstance(alert.wechat_fallback, bool):
            raise FeishuBotError(f"wechat_fallback 类型非法: {alert.wechat_fallback!r}")
        payload: dict[str, Any] = {
            "msg_type": "text",
            "content": {"text": f"[{alert.level.value.upper()}] {alert.title}\n{alert.content}"},
            "za_route": {"wechat_fallback": alert.wechat_fallback},
        }
        return self._dispatch("alert", alert.alert_id, payload)

    # ── 查询 ─────────────────────────────────────────────────────────────

    def receipts(self) -> tuple[SendReceipt, ...]:
        """发送回执序列（按发送先后，receipt_id 确定性）。"""
        return tuple(self._receipts)
