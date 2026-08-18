# [BLUEPRINT] MOD-POS_SERVICES | (pending)
# [MODULE] zephyr.position.services
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.services.position_audit_logger
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/position/test_position_audit_logger.py
# [A_module] module_id=MOD-POS_SERVICES | layer=infrastructure | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# position/services — 仓位审计记录

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 审计记录器子模块 包内导入
#   fields: PositionAuditLogger/PositionAuditRecord/PositionAuditReport/PositionAuditEventType/AuditSource/AuditChainError 共6个符号
#   code: zephyr.position.services.position_audit_logger L22
# 层: 算法
# - id: A1
#   name_zh: ① 包导出聚合
#   name_en: __init__ re-export
#   intro: 把审计子模块的6个符号聚成包级命名空间对外提供
#   desc: from position_audit_logger import 6符号并写入__all__，无业务逻辑
#   inputs: I1
#   outputs: 包级导出列表
# 层: 输出
# - id: O1
#   name_zh: 包命名空间导出
#   name_en: zephyr.position.services.__all__
#   intro: 仓位审计服务的统一入口，外部from包名即可拿到6个符号
#   downstream: 无下游/内部使用(CONSUMERS为空)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

from zephyr.position.services.position_audit_logger import (
    AuditChainError,
    AuditSource,
    PositionAuditEventType,
    PositionAuditLogger,
    PositionAuditRecord,
    PositionAuditReport,
)

__all__: Final = [
    "PositionAuditLogger",
    "PositionAuditRecord",
    "PositionAuditReport",
    "PositionAuditEventType",
    "AuditSource",
    "AuditChainError",
]
