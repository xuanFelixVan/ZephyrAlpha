"""
ZephyrAlpha — shared/

跨层共享基础设施：契约（contracts）、工具（utils）、不可变核心（immutable_core）。

本包的内容**不绑定任何业务层**，所有 L00-L11 层均可 import。

实现状态图例（AI必读）：
  [STABLE]  = 生产就绪，可直接使用
  [BETA]    = 核心功能可用，边缘case待验证，使用时需包裹try/except
  [STUB]    = 仅有骨架（类型定义+占位），不可用于生产逻辑——导入不会报错但调用可能什么都不做
  [PLANNED] = 仅有接口声明，底层代码尚未撰写——导入可能 ImportError

SSoT 模块（所有路径/时间/解析/token 常量和函数的唯一真源）：
  - paths.py           → [STABLE] REPO_ROOT, DB_PATH, 路径常量
  - time_utils.py      → [STABLE] utc_now(), now_iso(), default_now()
  - frontmatter_utils.py → [STABLE] parse_frontmatter(), extract_body()
  - token_utils.py     → [STABLE] estimate_tokens()
  - errors.py          → [STABLE] ZephyrBaseError + 12 子类
  - constants.py       → [STABLE] 共享枚举集中 re-export
  - events/            → [BETA]  Observer 事件体 Pydantic V2 Schema
  - resilience/        → [STUB] 重试/熔断/降级韧性基类（CircuitBreaker等仅类型定义）
  - lifecycle/         → [STUB] 模块生命周期钩子 + 健康检查
  - flags.py           → [STUB] Feature Flag 功能开关系统
  - types.py           → [STABLE] 共享类型别名 NewType/Annotated
  - diff_utils.py      → [BETA] 统一 diff/patch 工具
  - file_utils.py      → [BETA] 安全文件操作——原子写/备份/rollback
  - config/            → [BETA] YAML 配置加载与 Pydantic 校验
  - health.py          → [BETA] 聚合健康检查
  - idempotency.py     → [STUB] 幂等性记录与存储
  - limiter.py         → [STUB] 速率限制（TokenBucketLimiter仅占位）
  - lock.py            → [STUB] 内存锁（仅测试用）
  - metrics.py         → [STUB] 指标注册表
  - outbox.py          → [STUB] 发件箱模式
  - schema_registry.py → [STUB] Schema版本注册表
  - secrets.py         → [BETA] 密钥管理（支持dotenv/env两种provider）
  - api_client.py      → [STUB] HTTP客户端（AioHttpProvider仅占位）
  - cache.py           → [STUB] 缓存（MemoryCache仅占位）
  - migration.py       → [STUB] 任务迁移框架
  - pagination.py      → [STUB] 分页工具
  - serialization.py   → [BETA] 序列化/反序列化
  - testing.py         → [STABLE] 测试工厂函数
  - context.py         → [STABLE] 请求上下文
  - logging.py         → [STABLE] 日志系统
  - deprecation.py     → [STABLE] 废弃API机制
  - env.py             → [STABLE] 环境检测

跨层数据契约（CTR-001 ~ CTR-006，承重墙，禁止在模块内自造等价类型）：
  - contracts.market_data    → [STABLE] NormalizedMarketData（L00→L02）
  - contracts.factor_signal  → [STABLE] FactorSignal（L02→L03/L04/L05）
  - contracts.risk_limits    → [STABLE] RiskLimits（L04→L05）
  - contracts.order          → [STABLE] Order, OrderSide, OrderType, OrderStatus（L05→L06）
  - contracts.fill           → [STABLE] Fill（L06→L07）
  - contracts.position       → [STABLE] PositionSnapshot（L06/L07→L04/L11）
  - contracts.instrument     → [STABLE] Instrument + 6子类
  - contracts.money          → [STABLE] Money + 货币精度表
  - contracts.timestamp      → [STABLE] Timestamp + utcnow/ensure_utc
  - contracts.runtime_plane_tag → [STABLE] RuntimePlaneTag + HOT/WARM/COLD
  - contracts.enforcer       → [BETA]  契约强制执行（enforce_input/enforce_output）

参见：
  - ADR-0009（shared 层定位）
  - cross-layer-contracts.yaml（CTR SSoT）
"""

from zephyr.shared.__version__ import (
    MIN_COMPATIBLE_SHARED_VERSION,
    VersionMismatchError,
    __version__,
    __version_info__,
    check_shared_version,
    version_compatible,
    version_eq,
    version_gte,
    version_gt,
    version_lt,
    version_lte,
    version_major,
    version_minor,
    version_patch,
)
from zephyr.shared.api_client import (
    AioHttpProvider,
    ApiCallError,
    ApiCallMetrics,
    ApiClient,
    ApiClientConfig,
    ApiResponse,
    HttpMethod,
    HttpProvider,
)
from zephyr.shared.cache import (
    CacheError,
    CacheProvider,
    CacheStats,
    MemoryCache,
    cache_key,
)
from zephyr.shared.config import (
    ConfigLoadError,
    load_yaml_config,
    load_yaml_config_validated,
)
from zephyr.shared.contracts.enforcer import (
    ContractViolationError,
    EnforcementMode,
    enforce,
    enforce_input,
    enforce_output,
)
from zephyr.shared.contracts.factor_signal import FactorSignal
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.instrument import (
    ETF,
    FX,
    Bond,
    Crypto,
    Future,
    Instrument,
    Option,
    Stock,
)
from zephyr.shared.contracts.market_data import NormalizedMarketData
from zephyr.shared.contracts.money import Money, get_currency_precision
from zephyr.shared.contracts.order import Order, OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.shared.contracts.risk_limits import RiskLimits
from zephyr.shared.contracts.runtime_plane_tag import (
    COLD_PATH_LATENCY_BUDGET_MS,
    COLD_PATH_PARTIAL_ACTIVATED,
    HOT_PATH_ACTIVATED,
    HOT_PATH_LATENCY_BUDGET_MS,
    WARM_PATH_LATENCY_BUDGET_MS,
    RuntimePlane,
)
from zephyr.shared.contracts.timestamp import Timestamp, ensure_utc, utcnow
from zephyr.shared.context import (
    RequestContext,
    current_context,
    get_request_id,
    set_context,
    set_request_id,
)
from zephyr.shared.deprecation import (
    DeprecatedAPIError,
    DeprecationMode,
    deprecated,
    get_deprecation_mode,
    set_deprecation_mode,
)
from zephyr.shared.diff_utils import (
    PatchConflictError,
    apply_patch,
    compute_diff,
    compute_file_diff,
    similarity_ratio,
    try_apply_patch,
)
from zephyr.shared.errors import (
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
from zephyr.shared.events import (
    EVENT_PAYLOAD_MAP,
    FileEventPayload,
    ManualEventPayload,
    MetricEventPayload,
    TaskEventPayload,
    TimeEventPayload,
)
from zephyr.shared.events.dlq import (
    DeadLetter,
    DeadLetterQueue,
    attach_dlq_to_observer,
)
from zephyr.shared.env import (
    Env,
    current_env,
    is_debug,
    is_dev,
    is_prod,
    is_staging,
    is_test,
)
from zephyr.shared.file_utils import (
    AtomicWriteError,
    atomic_write,
    backup_and_rollback,
    backup_file,
    restore_backup,
    safe_read,
)
from zephyr.shared.flags import (
    FeatureFlag,
    FlagNotFoundError,
    FlagRegistry,
    FlagState,
    global_flag_registry,
)
from zephyr.shared.health import (
    AggregateHealth,
    HealthStatus,
    HealthSummary,
    collect_health,
)
from zephyr.shared.idempotency import (
    IdempotencyError,
    IdempotencyRecord,
    IdempotencyStatus,
    IdempotencyStore,
)
from zephyr.shared.lifecycle import (
    LifecycleAware,
    LifecycleManager,
    LifecycleState,
    ModuleHealth,
)
from zephyr.shared.limiter import (
    RateLimitError,
    RateLimiterStats,
    TokenBucketLimiter,
    async_limited,
)
from zephyr.shared.lock import (
    LockError,
    LockHandle,
    MemoryLock,
)
from zephyr.shared.logging import (
    TraceContext,
    ZephyrLogger,
    configure_root_logger,
    get_logger,
    trace_id_var,
)
from zephyr.shared.migration import (
    MIGRATIONS,
    MigrationError,
    downgrade_task,
    latest_schema_version,
    migrate_task,
)
from zephyr.shared.metrics import (
    MetricType,
    MetricSnapshot,
    MetricsRegistry,
    get_registry,
)
from zephyr.shared.outbox import (
    MemoryOutboxStore,
    OutboxEntry,
    OutboxError,
    OutboxPublisher,
    OutboxStatus,
    OutboxStore,
)
from zephyr.shared.pagination import (
    CursorPage,
    CursorPagination,
    OffsetPagination,
    Page,
    paginate,
    paginate_cursor,
)
from zephyr.shared.resilience import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
    FallbackChain,
    RetryConfig,
    RetryExhaustedError,
    async_retry,
    fallback,
)
from zephyr.shared.schema_registry import (
    SchemaEntry,
    SchemaRegistry,
    SchemaRegistryError,
    SchemaVersion,
    get_schema_registry,
)
from zephyr.shared.secrets import (
    DotEnvSecretProvider,
    EnvSecretProvider,
    SECRET_INDICATOR_PATTERNS,
    SecretProvider,
    SecretsError,
    sanitize_secret,
)
from zephyr.shared.serialization import (
    ENCODING_RULES,
    SerializationError,
    SerializationFormat,
    deserialize_datetime,
    deserialize_decimal,
    from_dict,
    from_json,
    serialize_datetime,
    serialize_decimal,
    to_dict,
    to_json,
)
from zephyr.shared.testing import (
    make_completed_task,
    make_p0_task,
    make_valid_audit_report,
    make_valid_failure_pattern,
    make_valid_handoff_package,
    make_valid_knowledge_entry,
    make_valid_task,
)
from zephyr.shared.types import (
    AbsPath,
    AgentId,
    BlueprintVersion,
    ContractId,
    DocumentId,
    FilePath,
    FingerprintHash,
    MetricName,
    ModuleId,
    SessionId,
    SSoT_Key,
    TaskId,
    TokenCount,
)
from zephyr.shared.time_utils import (
    MOCKED_TIME,
    format_iso,
    freeze_time,
    now_utc,
    parse_iso,
    seconds_since,
    seconds_until,
)

__all__ = [
    "NormalizedMarketData",
    "FactorSignal",
    "RiskLimits",
    "Order",
    "OrderSide",
    "OrderType",
    "OrderStatus",
    "Fill",
    "PositionSnapshot",
    "Instrument",
    "Stock",
    "ETF",
    "Future",
    "Option",
    "Bond",
    "FX",
    "Crypto",
    "Money",
    "get_currency_precision",
    "Timestamp",
    "utcnow",
    "ensure_utc",
    "RuntimePlane",
    "HOT_PATH_LATENCY_BUDGET_MS",
    "WARM_PATH_LATENCY_BUDGET_MS",
    "COLD_PATH_LATENCY_BUDGET_MS",
    "HOT_PATH_ACTIVATED",
    "COLD_PATH_PARTIAL_ACTIVATED",
    "enforce_output",
    "enforce_input",
    "enforce",
    "ContractViolationError",
    "EnforcementMode",
    "ZephyrBaseError",
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
    "EVENT_PAYLOAD_MAP",
    "FileEventPayload",
    "ManualEventPayload",
    "MetricEventPayload",
    "TaskEventPayload",
    "TimeEventPayload",
    "FeatureFlag",
    "FlagNotFoundError",
    "FlagRegistry",
    "FlagState",
    "global_flag_registry",
    "LifecycleAware",
    "LifecycleManager",
    "LifecycleState",
    "ModuleHealth",
    "CircuitBreaker",
    "CircuitOpenError",
    "CircuitState",
    "FallbackChain",
    "RetryConfig",
    "RetryExhaustedError",
    "async_retry",
    "fallback",
    "ConfigLoadError",
    "load_yaml_config",
    "load_yaml_config_validated",
    "PatchConflictError",
    "apply_patch",
    "compute_diff",
    "compute_file_diff",
    "similarity_ratio",
    "try_apply_patch",
    "AtomicWriteError",
    "atomic_write",
    "backup_and_rollback",
    "backup_file",
    "restore_backup",
    "safe_read",
    "AbsPath",
    "AgentId",
    "BlueprintVersion",
    "ContractId",
    "DocumentId",
    "FilePath",
    "FingerprintHash",
    "MetricName",
    "ModuleId",
    "SessionId",
    "SSoT_Key",
    "TaskId",
    "TokenCount",
    "TraceContext",
    "ZephyrLogger",
    "configure_root_logger",
    "get_logger",
    "trace_id_var",
    "DeprecatedAPIError",
    "DeprecationMode",
    "deprecated",
    "get_deprecation_mode",
    "set_deprecation_mode",
    "MIGRATIONS",
    "MigrationError",
    "downgrade_task",
    "latest_schema_version",
    "migrate_task",
    "make_completed_task",
    "make_p0_task",
    "make_valid_audit_report",
    "make_valid_failure_pattern",
    "make_valid_handoff_package",
    "make_valid_knowledge_entry",
    "make_valid_task",
    "AggregateHealth",
    "HealthStatus",
    "HealthSummary",
    "collect_health",
    "MIN_COMPATIBLE_SHARED_VERSION",
    "VersionMismatchError",
    "__version__",
    "__version_info__",
    "check_shared_version",
    "DeadLetter",
    "DeadLetterQueue",
    "attach_dlq_to_observer",
    "Env",
    "current_env",
    "is_debug",
    "is_dev",
    "is_prod",
    "is_staging",
    "is_test",
    "IdempotencyError",
    "IdempotencyRecord",
    "IdempotencyStatus",
    "IdempotencyStore",
    "RateLimitError",
    "RateLimiterStats",
    "TokenBucketLimiter",
    "async_limited",
    "LockError",
    "LockHandle",
    "MemoryLock",
    "MetricType",
    "MetricSnapshot",
    "MetricsRegistry",
    "get_registry",
    "MemoryOutboxStore",
    "OutboxEntry",
    "OutboxError",
    "OutboxPublisher",
    "OutboxStatus",
    "OutboxStore",
    "CursorPage",
    "CursorPagination",
    "OffsetPagination",
    "Page",
    "paginate",
    "paginate_cursor",
    "SchemaEntry",
    "SchemaRegistry",
    "SchemaRegistryError",
    "SchemaVersion",
    "get_schema_registry",
    "DotEnvSecretProvider",
    "EnvSecretProvider",
    "SECRET_INDICATOR_PATTERNS",
    "SecretProvider",
    "SecretsError",
    "sanitize_secret",
    "ENCODING_RULES",
    "SerializationError",
    "SerializationFormat",
    "deserialize_datetime",
    "deserialize_decimal",
    "from_dict",
    "from_json",
    "serialize_datetime",
    "serialize_decimal",
    "to_dict",
    "to_json",
    "version_compatible",
    "version_eq",
    "version_gte",
    "version_gt",
    "version_lt",
    "version_lte",
    "version_major",
    "version_minor",
    "version_patch",
    "AioHttpProvider",
    "ApiCallError",
    "ApiCallMetrics",
    "ApiClient",
    "ApiClientConfig",
    "ApiResponse",
    "HttpMethod",
    "HttpProvider",
    "CacheError",
    "CacheProvider",
    "CacheStats",
    "MemoryCache",
    "cache_key",
    "MOCKED_TIME",
    "format_iso",
    "freeze_time",
    "now_utc",
    "parse_iso",
    "seconds_since",
    "seconds_until",
    "score_blueprint_route",
    "score_and_rank_routes",
    "RequestContext",
    "current_context",
    "get_request_id",
    "set_context",
    "set_request_id",
]
