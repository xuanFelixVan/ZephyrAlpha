# [A_module] module_id=MOD-L08-001_implementations | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.implementations
# [DOMAIN] D_FRONTEND
# [TTL] permanent
"""D_FRONTEND — Human-AI Interface 具体实现包

interface_base 抽象基类的默认生产实现：
  - DefaultNotificationManager : NotificationManagerBase 的具体实现（通知/告警分发）
  - DefaultApprovalGateway     : ApprovalGatewayBase 的具体实现（B-007 人工审批载体）
"""

from typing import Final

__all__: Final = [
    "default_approval_gateway",
    "default_notification_manager",
]
