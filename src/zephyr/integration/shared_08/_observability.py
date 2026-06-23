# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08._observability
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.errors; zephyr.integration.shared.events.__init__; zephyr.integration.shared.events.dlq; zephyr.integration.shared_08.health; zephyr.integration.shared_08.lifecycle.__init__; zephyr.integration.shared_08.logging; zephyr.integration.shared_08.metrics; zephyr.integration.shared_08.context
# [CONSUMERS] zephyr.shared.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] backward_compat: all exports must remain available from zephyr.shared
# [MODIFY-GUARD] zephyr.shared.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.shared"
# [A_module] module_id=MOD-INT__observability | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""_observability — 可观测性 re-export 桥接层。

从 foundation/lifecycle/contracts 子包及 ops/observability、integration/shared/events 重新导出符号，
保持 shared_08.__init__ 向后兼容。
"""

# === 错误类 ===
# === 事件（来自 integration.shared.events） ===
from zephyr.integration.shared.events.dlq import (
    DeadLetter,
    DeadLetterQueue,
    attach_dlq_to_observer,
)
from zephyr.integration.shared.events.event_schemas import (
    EVENT_PAYLOAD_MAP,
    FileEventPayload,
    ManualEventPayload,
    MetricEventPayload,
    TaskEventPayload,
    TimeEventPayload,
)

# === 请求上下文 ===
from zephyr.integration.shared_08.context import (
    RequestContext,
    current_context,
    get_request_id,
    set_context,
    set_request_id,
)

# === get_registry（来自 contract_versions，__init__ 期望从此处导出） ===
from zephyr.integration.shared_08.contract_versions import get_registry

# === TraceContext（shared_08 内部 SSoT） ===
from zephyr.integration.shared_08.contracts.core.trace_context import TraceContext
from zephyr.integration.shared_08.foundation.errors import (
    ConfigError,
    ContextError,
    ContractError,
    DataError,
    FeedbackError,
    GateError,
    IOError,
    PipelineError,
    SecurityError,
    TaskError,
    UnimplementedError,
    ValidationError,
    ZephyrBaseError,
)

# === 生命周期 ===
from zephyr.integration.shared_08.lifecycle.hooks import (
    LifecycleAware,
    LifecycleManager,
    LifecycleState,
    ModuleHealth,
)

# === 健康（来自 ops.observability） ===
from zephyr.ops.observability.health import (
    AggregateHealth,
    HealthStatus,
    HealthSummary,
    collect_health,
)

# === 日志 + trace_id_var（来自 ops.observability） ===
from zephyr.ops.observability.logging import (
    ZephyrLogger,
    configure_root_logger,
    get_logger,
    trace_id_var,
)

# === 指标（来自 ops.observability） ===
from zephyr.ops.observability.metrics import (
    MetricSnapshot,
    MetricsRegistry,
    MetricType,
)

__all__ = [
    # 错误类
    "ConfigError",
    "ContextError",
    "ContractError",
    "DataError",
    "FeedbackError",
    "GateError",
    "IOError",
    "PipelineError",
    "SecurityError",
    "TaskError",
    "UnimplementedError",
    "ValidationError",
    "ZephyrBaseError",
    # 生命周期
    "LifecycleAware",
    "LifecycleManager",
    "LifecycleState",
    "ModuleHealth",
    # 健康
    "AggregateHealth",
    "HealthStatus",
    "HealthSummary",
    "collect_health",
    # 指标
    "MetricSnapshot",
    "MetricType",
    "MetricsRegistry",
    # 日志
    "ZephyrLogger",
    "configure_root_logger",
    "get_logger",
    "trace_id_var",
    # 请求上下文
    "RequestContext",
    "current_context",
    "get_request_id",
    "set_context",
    "set_request_id",
    # 事件
    "DeadLetter",
    "DeadLetterQueue",
    "attach_dlq_to_observer",
    "EVENT_PAYLOAD_MAP",
    "FileEventPayload",
    "ManualEventPayload",
    "MetricEventPayload",
    "TaskEventPayload",
    "TimeEventPayload",
    # 追踪
    "TraceContext",
    # 注册表
    "get_registry",
]
