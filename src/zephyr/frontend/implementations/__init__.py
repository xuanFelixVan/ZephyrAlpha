# [A_module] module_id=MOD-L08-001_implementations | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.implementations
# [DOMAIN] D_FRONTEND
# [TTL] permanent
"""D_FRONTEND — Human-AI Interface 具体实现包

interface_base 抽象基类的默认生产实现：
  - DefaultNotificationManager : NotificationManagerBase 的具体实现（通知/告警分发）
  - DefaultApprovalGateway     : ApprovalGatewayBase 的具体实现（B-007 人工审批载体）

通知渠道发送器（2026-08-29 自 frontend/ 根迁入，trae_024 单一类型归位）：
  - FeishuBotSender    : 飞书机器人推送器（MOD-FE-012，审批通知/告警微信备选通道）
  - WeChatBotHandler   : 企业微信机器人处理器（MOD-FE-013）
"""

from typing import Final

__all__: Final = [
    "default_approval_gateway",
    "default_notification_manager",
    "feishu_bot_sender",
    "wechat_bot_handler",
]
