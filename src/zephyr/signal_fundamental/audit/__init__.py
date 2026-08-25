# [BLUEPRINT] MOD-SIG-006 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.audit
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SIG-006 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


D-SIGNAL-06 信号审计日志子域

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: signal_audit_logger 子模块符号 7个
#   fields: AuditLogConfig / AuditLogEntry / AuditLogQueryError / AuditLogWriteError / SignalAuditEvent / SignalAuditLogger 等7个
#   code: zephyr.signal_fundamental.audit.signal_audit_logger
# 层: 算法
# - id: A1
#   name_zh: ① 包级聚合再导出
#   name_en: zephyr.signal_fundamental.audit.__init__
#   intro: D-SIGNAL-06 信号审计日志子域
#   desc: MOD-SIG-006 包入口，包级聚合再导出并声明 __all__（7项）
#   inputs: I1
#   outputs: zephyr.signal_fundamental.audit 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（7项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.signal_fundamental.audit 包公共 API
#   name_en: __all__ 7项
#   intro: D-SIGNAL-06 信号审计日志子域——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.signal_fundamental.audit.signal_audit_logger import (
    AuditLogConfig,
    AuditLogEntry,
    AuditLogQueryError,
    AuditLogWriteError,
    SignalAuditEvent,
    SignalAuditLogger,
    SignalEventType,
)

# NOTE(P1W25 2026-08-25): scaffold 注册器写入斜杠非法 import（#ARCH-228 同款 bug
# 第 11 次复发），按本包既有"点号 import + __all__ 入列"约定归一。
from zephyr.signal_fundamental.audit.trace_context_store import TraceContextStore

__all__ = [
    "AuditLogConfig",
    "AuditLogEntry",
    "AuditLogQueryError",
    "AuditLogWriteError",
    "SignalAuditEvent",
    "SignalAuditLogger",
    "SignalEventType",
]

__all__.append("TraceContextStore")
