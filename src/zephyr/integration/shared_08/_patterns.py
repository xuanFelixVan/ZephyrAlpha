# [A_module] module_id=MOD-INT__patterns | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08._patterns
# [INVARIANTS] backward_compat: all exports must remain available from zephyr.shared
# [MODIFY-GUARD] zephyr.shared.__init__
# [CONSUMERS] zephyr.shared.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.shared"

from zephyr.integration.shared_08.deprecation import (
    DeprecatedAPIError,
    DeprecationMode,
    deprecated,
    get_deprecation_mode,
    set_deprecation_mode,
)
from zephyr.integration.shared_08.flags import (
    FeatureFlag,
    FlagNotFoundError,
    FlagRegistry,
    FlagState,
    global_flag_registry,
)
from zephyr.integration.shared_08.idempotency import (
    IdempotencyError,
    IdempotencyRecord,
    IdempotencyStatus,
    IdempotencyStore,
)
from zephyr.integration.shared_08.limiter import (
    RateLimitError,
    RateLimiterStats,
    TokenBucketLimiter,
    async_limited,
)
from zephyr.integration.shared_08.lock import (
    LockError,
    LockHandle,
    MemoryLock,
)
from zephyr.integration.shared_08.migration import (
    MIGRATIONS,
    MigrationError,
    downgrade_task,
    latest_schema_version,
    migrate_task,
)
from zephyr.integration.shared_08.outbox import (
    MemoryOutboxStore,
    OutboxEntry,
    OutboxError,
    OutboxPublisher,
    OutboxStatus,
    OutboxStore,
)
from zephyr.integration.shared_08.pagination import (
    CursorPage,
    CursorPagination,
    OffsetPagination,
    Page,
    paginate,
    paginate_cursor,
)
from zephyr.integration.shared_08.resilience import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
    FallbackChain,
    RetryConfig,
    RetryExhaustedError,
    async_retry,
    fallback,
)
from zephyr.integration.shared_08.schema_registry import (
    SchemaEntry,
    SchemaRegistry,
    SchemaRegistryError,
    SchemaVersion,
    get_schema_registry,
)
from zephyr.integration.shared_08.testing import (
    make_completed_task,
    make_p0_task,
    make_valid_audit_report,
    make_valid_failure_pattern,
    make_valid_handoff_package,
    make_valid_knowledge_entry,
    make_valid_task,
)
