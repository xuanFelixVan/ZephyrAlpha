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
  - resilience/        → [STABLE] 重试/熔断/降级韧性基类（async_retry/CircuitBreaker/FallbackChain）
  - lifecycle/         → [STABLE] 模块生命周期钩子 + 健康检查（LifecycleAware/ModuleHealth）
  - flags.py           → [STABLE] Feature Flag 功能开关系统（FlagRegistry/global_flag_registry）
  - types.py           → [STABLE] 共享类型别名 NewType/Annotated
  - diff_utils.py      → [BETA] 统一 diff/patch 工具
  - file_utils.py      → [BETA] 安全文件操作——原子写/备份/rollback
  - config/            → [BETA] YAML 配置加载与 Pydantic 校验
  - health.py          → [BETA] 聚合健康检查
  - idempotency.py     → [STABLE] 幂等性记录与存储（IdempotencyStore/IdempotencyRecord）
  - limiter.py         → [STABLE] 速率限制（TokenBucketLimiter/async_limited）
  - lock.py            → [STABLE] 内存锁（MemoryLock/LockHandle）
  - metrics.py         → [STABLE] 指标注册表（MetricsRegistry/MetricSnapshot）
  - outbox.py          → [STABLE] 发件箱模式（OutboxStore/OutboxPublisher）
  - schema_registry.py → [STABLE] Schema版本注册表（SchemaRegistry/SchemaEntry）
  - secrets.py         → [BETA] 密钥管理（支持dotenv/env两种provider）
  - api_client.py      → [STABLE] HTTP客户端（AioHttpProvider/ApiClient/ApiCallMetrics）
  - cache.py           → [STABLE] 缓存（MemoryCache/CacheProvider/CacheStats）
  - migration.py       → [STABLE] 任务迁移框架（migrate_task/downgrade_task）
  - pagination.py      → [STABLE] 分页工具（OffsetPagination/CursorPagination）
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

MODULE_ID = "MOD-SHARED-001"

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
from zephyr.shared.api.api_client import (
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
from zephyr.shared.constitutional_update import (
    ConstitutionalAutoUpdate,
    Learning,
    ProposedUpdate,
)
from zephyr.shared.config import (
    ConfigLoadError,
    load_yaml_config,
    load_yaml_config_validated,
)
from zephyr.shared.contracts.core.enforcer import (
    ContractViolationError,
    EnforcementMode,
    enforce,
    enforce_input,
    enforce_output,
)
from zephyr.shared.contracts.market.factor_signal import FactorSignal
from zephyr.shared.contracts.execution.fill import Fill
from zephyr.shared.contracts.market.instrument import (
    ETF,
    FX,
    Bond,
    Crypto,
    Future,
    Instrument,
    Option,
    Stock,
)
from zephyr.shared.contracts.market.market_data import NormalizedMarketData
from zephyr.shared.contracts.portfolio.money import Money, get_currency_precision
from zephyr.shared.contracts.execution.order import Order, OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.portfolio.position import PositionSnapshot
from zephyr.shared.contracts.risk.risk_limits import RiskLimits
from zephyr.shared.contracts.core.runtime_plane_tag import (
    COLD_PATH_LATENCY_BUDGET_MS,
    COLD_PATH_PARTIAL_ACTIVATED,
    HOT_PATH_ACTIVATED,
    HOT_PATH_LATENCY_BUDGET_MS,
    WARM_PATH_LATENCY_BUDGET_MS,
    RuntimePlane,
)
from zephyr.shared.contracts.core.timestamp import Timestamp, ensure_utc, utcnow
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
from zephyr.shared.multi_agent import (
    AgentCard,
    AgentRole,
    DispatchedTask,
    MergeStrategy,
    ResultMerge,
    TaskDispatch,
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
from zephyr.shared.post_process import (
    HookResult,
    HookStrategy,
    PipelineResult,
    PostProcessHook,
    PostProcessPipeline,
    format_hook,
    lint_hook,
    typecheck_hook,
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
from zephyr.shared.session_audit import (
    CostRecord,
    DecisionRecord,
    ErrorRecord,
    OutcomeRecord,
    PromptRecord,
    SessionAuditTrail,
    SessionRecord,
    ToolCallRecord,
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
from zephyr.shared.skill_registry import (
    PromptTemplate,
    PromptVariable,
    SkillCategory,
    SkillDefinition,
    SkillOutput,
    SkillParameter,
)
from zephyr.shared.cost_budget import (
    CostBudget,
    CostBudgetExceededError,
    PricingTier,
)
from zephyr.shared.context_budget import (
    BudgetEntry,
    ContextBudget,
    QuotaTracker,
    TruncationStrategy,
)
from zephyr.shared.observability.token_utils import (
    DEFAULT_CONTEXT_TOKEN_BUDGET,
    estimate_tokens,
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
from zephyr.shared.io.paths import (
    DB_PATH,
    REPO_ROOT,
)
from zephyr.shared.schema.schemas import (
    Priority,
    SafetyLevel,
    Task,
    TaskNamespace,
    TaskStatus,
    normalize_execution_model,
)

__all__ = ['API_INDEX', 'AbsPath', 'AgentCard', 'AgentId', 'AgentRole', 'AggregateHealth', 'AioHttpProvider', 'ApiCallError', 'ApiCallMetrics', 'ApiClient', 'ApiClientConfig', 'ApiResponse', 'AtomicWriteError', 'BlueprintVersion', 'Bond', 'BudgetEntry', 'COLD_PATH_LATENCY_BUDGET_MS', 'COLD_PATH_PARTIAL_ACTIVATED', 'CacheError', 'CacheProvider', 'CacheStats', 'CircuitBreaker', 'CircuitOpenError', 'CircuitState', 'ConfigError', 'ConfigLoadError', 'ConstitutionalAutoUpdate', 'ContextBudget', 'ContextError', 'ContractError', 'ContractId', 'ContractViolationError', 'CostBudget', 'CostBudgetExceededError', 'CostRecord', 'Crypto', 'CursorPage', 'CursorPagination', 'DB_PATH', 'DEFAULT_CONTEXT_TOKEN_BUDGET', 'DataError', 'DeadLetter', 'DeadLetterQueue', 'DecisionRecord', 'DeprecatedAPIError', 'DeprecationMode', 'DispatchedTask', 'DocumentId', 'DotEnvSecretProvider', 'ENCODING_RULES', 'ETF', 'EVENT_PAYLOAD_MAP', 'EnforcementMode', 'Env', 'EnvSecretProvider', 'ErrorRecord', 'FX', 'FactorSignal', 'FallbackChain', 'FeatureFlag', 'FeedbackError', 'FileEventPayload', 'FilePath', 'Fill', 'FingerprintHash', 'FlagNotFoundError', 'FlagRegistry', 'FlagState', 'Future', 'GateError', 'HOT_PATH_ACTIVATED', 'HOT_PATH_LATENCY_BUDGET_MS', 'HealthStatus', 'HealthSummary', 'HookResult', 'HookStrategy', 'HttpMethod', 'HttpProvider', 'IOError', 'IdempotencyError', 'IdempotencyRecord', 'IdempotencyStatus', 'IdempotencyStore', 'Instrument', 'Learning', 'LifecycleAware', 'LifecycleManager', 'LifecycleState', 'LockError', 'LockHandle', 'MIGRATIONS', 'MIN_COMPATIBLE_SHARED_VERSION', 'MOCKED_TIME', 'ManualEventPayload', 'MemoryCache', 'MemoryLock', 'MemoryOutboxStore', 'MergeStrategy', 'MetricEventPayload', 'MetricName', 'MetricSnapshot', 'MetricType', 'MetricsRegistry', 'MigrationError', 'ModuleHealth', 'ModuleId', 'Money', 'NormalizedMarketData', 'OffsetPagination', 'Option', 'Order', 'OrderSide', 'OrderStatus', 'OrderType', 'OutboxEntry', 'OutboxError', 'OutboxPublisher', 'OutboxStatus', 'OutboxStore', 'OutcomeRecord', 'Page', 'PatchConflictError', 'PipelineError', 'PipelineResult', 'PositionSnapshot', 'PostProcessHook', 'PostProcessPipeline', 'PricingTier', 'Priority', 'PromptRecord', 'PromptVariable', 'ProposedUpdate', 'QuotaTracker', 'REPO_ROOT', 'RateLimitError', 'RateLimiterStats', 'RequestContext', 'ResultMerge', 'RetryConfig', 'RetryExhaustedError', 'RiskLimits', 'RuntimePlane', 'SECRET_INDICATOR_PATTERNS', 'SSoT_Key', 'SafetyLevel', 'SchemaEntry', 'SchemaRegistry', 'SchemaRegistryError', 'SchemaVersion', 'SecretProvider', 'SecretsError', 'SecurityError', 'SerializationError', 'SerializationFormat', 'SessionAuditTrail', 'SessionId', 'SessionRecord', 'SkillCategory', 'SkillDefinition', 'SkillOutput', 'SkillParameter', 'Stock', 'Task', 'TaskDispatch', 'TaskError', 'TaskEventPayload', 'TaskId', 'TaskNamespace', 'TaskStatus', 'TimeEventPayload', 'Timestamp', 'TokenBucketLimiter', 'TokenCount', 'ToolCallRecord', 'TraceContext', 'TruncationStrategy', 'UnimplementedError', 'ValidationError', 'VersionMismatchError', 'WARM_PATH_LATENCY_BUDGET_MS', 'ZephyrBaseError', 'ZephyrLogger', '__version__', '__version_info__', 'adaptive_sampler', 'ai_audit_guard', 'ai_understandability_constraint', 'alert_escalation', 'alert_manager', 'alert_precision_tracker', 'apply_patch', 'async_limited', 'async_retry', 'atomic_write', 'attach_dlq_to_observer', 'backup_and_rollback', 'backup_file', 'blueprint_code_auditor', 'blueprint_scorer', 'budget_aware_prompt', 'cache', 'cache_key', 'capability', 'capacity_calibrator', 'capacity_digital_twin', 'capacity_fingerprint', 'capacity_governance_loop', 'capacity_runbook_generator', 'check_shared_version', 'code_economy_analyzer', 'collect_health', 'combinatorial_gate', 'compute_diff', 'compute_file_diff', 'config_validator', 'configure_root_logger', 'constants', 'constitutional_update', 'content_fingerprint', 'context', 'context_budget', 'contract_bus', 'contract_tester', 'core_integrity_guard', 'cost_budget', 'cost_estimator', 'current_context', 'current_env', 'degradation_chain', 'dependency_capacity_guard', 'deprecated', 'deprecation', 'deserialize_datetime', 'deserialize_decimal', 'diff_utils', 'dos_launcher', 'downgrade_task', 'dual_channel_alert', 'durable_execution', 'enforce', 'enforce_input', 'enforce_output', 'ensure_utc', 'error_budget_tracker', 'errors', 'estimate_tokens', 'evals', 'event_bus', 'event_bus_upgrade', 'fallback', 'fault_isolator', 'file_utils', 'flags', 'format_hook', 'format_iso', 'freeze_time', 'from_dict', 'from_json', 'frontmatter_utils', 'get_currency_precision', 'get_deprecation_mode', 'get_logger', 'get_registry', 'get_request_id', 'get_schema_registry', 'global_flag_registry', 'health', 'heartbeat_server', 'idempotency', 'is_debug', 'is_dev', 'is_prod', 'is_staging', 'is_test', 'kill_switch', 'latest_schema_version', 'limiter', 'lint_hook', 'load_yaml_config', 'load_yaml_config_validated', 'lock', 'logging', 'longevity_monitor', 'make_completed_task', 'make_p0_task', 'make_valid_audit_report', 'make_valid_failure_pattern', 'make_valid_handoff_package', 'make_valid_knowledge_entry', 'make_valid_task', 'metrics', 'migrate_task', 'migration', 'model_capacity_probe', 'module_birth_registry', 'multi_agent', 'normalize_execution_model', 'now_utc', 'observer', 'outbox', 'owner_trust_gauge', 'paginate', 'paginate_cursor', 'pagination', 'parse_iso', 'path_resolver', 'paths', 'post_process', 'pydantic_v2_migrator', 'reasoning_spans', 'restore_backup', 'safe_read', 'sandbox_executor', 'sanitize_secret', 'schemas', 'seconds_since', 'seconds_until', 'secrets', 'semantic_cache', 'serialization', 'serialize_datetime', 'serialize_decimal', 'session_audit', 'set_context', 'set_deprecation_mode', 'set_request_id', 'similarity_ratio', 'skill_registry', 'slo_review_assistant', 'ssot_guard', 'task_heartbeat', 'testing', 'time_utils', 'to_dict', 'to_json', 'token_utils', 'trace_id_var', 'tracing', 'try_apply_patch', 'ttl_cleanup_engine', 'typecheck_hook', 'types', 'utcnow', 'version_compatible', 'version_eq', 'version_gt', 'version_gte', 'version_lt', 'version_lte', 'version_major', 'version_minor', 'version_negotiation', 'version_patch', 'vibe_experiment_tracker', 'warm_hot_gate']
