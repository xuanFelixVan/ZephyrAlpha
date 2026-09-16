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

# [ALGO_FLOW] external: docs/03_modules/_domain_fundamental_signal/algo_flow/audit__init__.yaml
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
