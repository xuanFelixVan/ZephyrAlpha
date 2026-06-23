# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08._patterns
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.deprecation; zephyr.integration.shared_08.flags; zephyr.integration.shared_08.idempotency; zephyr.integration.shared_08.limiter; zephyr.integration.shared_08.lock; zephyr.integration.shared_08.migration; zephyr.integration.shared_08.outbox; zephyr.integration.shared_08.pagination; zephyr.integration.shared_08.resilience.__init__; zephyr.integration.shared_08.schema_registry; zephyr.integration.shared_08.testing
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
# [A_module] module_id=MOD-INT__patterns | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""_patterns — 设计模式 re-export 桥接层。

从 resilience/foundation/utils 子包及 shared.infra_06、integration.shared.schema 重新导出符号，
保持 shared_08.__init__ 向后兼容。
"""

# === 韧性/重试 ===
# === Schema 注册表（来自 integration.shared.schema） ===
from zephyr.integration.shared.schema.schema_registry import (
    SchemaEntry,
    SchemaRegistry,
    SchemaRegistryError,
    SchemaVersion,
    get_schema_registry,
)

# === 废弃 API ===
from zephyr.integration.shared_08.foundation.deprecation import (
    DeprecatedAPIError,
    DeprecationMode,
    deprecated,
    get_deprecation_mode,
    set_deprecation_mode,
)

# === 功能开关 ===
from zephyr.integration.shared_08.foundation.flags import (
    FeatureFlag,
    FlagNotFoundError,
    FlagRegistry,
    FlagState,
    global_flag_registry,
)
from zephyr.integration.shared_08.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
)
from zephyr.integration.shared_08.resilience.fallback import (
    FallbackChain,
    fallback,
)
from zephyr.integration.shared_08.resilience.retry import (
    RetryConfig,
    RetryExhaustedError,
    async_retry,
)

# === 任务迁移 ===
from zephyr.integration.shared_08.utils.migration import (
    MIGRATIONS,
    MigrationError,
    downgrade_task,
    latest_schema_version,
    migrate_task,
)

# === 分页 ===
from zephyr.integration.shared_08.utils.pagination import (
    CursorPage,
    CursorPagination,
    OffsetPagination,
    Page,
    paginate,
    paginate_cursor,
)

# === 测试工厂 ===
from zephyr.integration.shared_08.utils.testing import (
    make_completed_task,
    make_p0_task,
    make_valid_audit_report,
    make_valid_failure_pattern,
    make_valid_handoff_package,
    make_valid_knowledge_entry,
    make_valid_task,
)

# === 幂等性（来自 shared.infra_06） ===
from zephyr.shared.infra_06.idempotency import (
    IdempotencyError,
    IdempotencyRecord,
    IdempotencyStatus,
    IdempotencyStore,
)

# === 限流（来自 shared.infra_06） ===
from zephyr.shared.infra_06.limiter import (
    RateLimitError,
    RateLimiterStats,
    TokenBucketLimiter,
    async_limited,
)

# === 锁（来自 shared.infra_06） ===
from zephyr.shared.infra_06.lock import (
    LockError,
    LockHandle,
    MemoryLock,
)

# === 发件箱（来自 shared.infra_06） ===
from zephyr.shared.infra_06.outbox import (
    MemoryOutboxStore,
    OutboxEntry,
    OutboxError,
    OutboxPublisher,
    OutboxStatus,
    OutboxStore,
)

__all__ = [
    # 韧性/重试
    "CircuitBreaker",
    "CircuitOpenError",
    "CircuitState",
    "FallbackChain",
    "RetryConfig",
    "RetryExhaustedError",
    "async_retry",
    "fallback",
    # 限流
    "RateLimitError",
    "RateLimiterStats",
    "TokenBucketLimiter",
    "async_limited",
    # 锁
    "LockError",
    "LockHandle",
    "MemoryLock",
    # 发件箱
    "MemoryOutboxStore",
    "OutboxEntry",
    "OutboxError",
    "OutboxPublisher",
    "OutboxStatus",
    "OutboxStore",
    # 幂等性
    "IdempotencyError",
    "IdempotencyRecord",
    "IdempotencyStatus",
    "IdempotencyStore",
    # Schema 注册表
    "SchemaEntry",
    "SchemaRegistry",
    "SchemaRegistryError",
    "SchemaVersion",
    "get_schema_registry",
    "latest_schema_version",
    # 分页
    "CursorPage",
    "CursorPagination",
    "OffsetPagination",
    "Page",
    "paginate",
    "paginate_cursor",
    # 废弃 API
    "DeprecatedAPIError",
    "DeprecationMode",
    "deprecated",
    "get_deprecation_mode",
    "set_deprecation_mode",
    # 功能开关
    "FeatureFlag",
    "FlagNotFoundError",
    "FlagRegistry",
    "FlagState",
    "global_flag_registry",
    # 任务迁移
    "MIGRATIONS",
    "MigrationError",
    "downgrade_task",
    "migrate_task",
    # 测试工厂
    "make_completed_task",
    "make_p0_task",
    "make_valid_audit_report",
    "make_valid_failure_pattern",
    "make_valid_handoff_package",
    "make_valid_knowledge_entry",
    "make_valid_task",
]
