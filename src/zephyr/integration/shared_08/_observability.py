# [A_module] module_id=MOD-INT__observability | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08._observability
# [INVARIANTS] backward_compat: all exports must remain available from zephyr.shared
# [MODIFY-GUARD] zephyr.shared.__init__
# [CONSUMERS] zephyr.shared.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.shared"

from zephyr.integration.shared_08.errors import (
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
from zephyr.integration.shared.events import (
    EVENT_PAYLOAD_MAP,
    FileEventPayload,
    ManualEventPayload,
    MetricEventPayload,
    TaskEventPayload,
    TimeEventPayload,
)
from zephyr.integration.shared.events.dlq import (
    DeadLetter,
    DeadLetterQueue,
    attach_dlq_to_observer,
)
from zephyr.integration.shared_08.health import (
    AggregateHealth,
    HealthStatus,
    HealthSummary,
    collect_health,
)
from zephyr.integration.shared_08.lifecycle import (
    LifecycleAware,
    LifecycleManager,
    LifecycleState,
    ModuleHealth,
)
from zephyr.integration.shared_08.logging import (
    TraceContext,
    ZephyrLogger,
    configure_root_logger,
    get_logger,
    trace_id_var,
)
from zephyr.integration.shared_08.metrics import (
    MetricType,
    MetricSnapshot,
    MetricsRegistry,
    get_registry,
)
from zephyr.integration.shared_08.context import (
    RequestContext,
    current_context,
    get_request_id,
    set_context,
    set_request_id,
)
