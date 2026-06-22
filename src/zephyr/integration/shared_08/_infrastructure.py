# [A_module] module_id=MOD-INT__infrastructure | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08._infrastructure
# [INVARIANTS] backward_compat: all exports must remain available from zephyr.shared
# [MODIFY-GUARD] zephyr.shared.__init__
# [CONSUMERS] zephyr.shared.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.shared"
"""_infrastructure — 基础设施 re-export 桥接层。

从 io/security/utils/session_audit/lifecycle 子包及 zephyr.shared 重新导出符号，
保持 shared_08.__init__ 向后兼容。
"""

# === 序列化 ===
# === 文件工具 ===
from zephyr.integration.shared_08.io.file_utils import (
    AtomicWriteError,
    atomic_write,
    backup_and_rollback,
    backup_file,
    restore_backup,
    safe_read,
)
from zephyr.integration.shared_08.io.serialization import (
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

# === 密钥/安全 ===
from zephyr.integration.shared_08.security.secrets import (
    SECRET_INDICATOR_PATTERNS,
    DotEnvSecretProvider,
    EnvSecretProvider,
    SecretProvider,
    SecretsError,
    sanitize_secret,
)

# === 会话审计 ===
from zephyr.integration.shared_08.session_audit import (
    CostRecord,
    DecisionRecord,
    ErrorRecord,
    OutcomeRecord,
    PromptRecord,
    SessionAuditTrail,
    SessionRecord,
    ToolCallRecord,
)

# === Diff/Patch 工具 ===
from zephyr.integration.shared_08.utils.diff_utils import (
    PatchConflictError,
    apply_patch,
    compute_diff,
    compute_file_diff,
    similarity_ratio,
    try_apply_patch,
)

# === API 客户端（来自 zephyr.shared.api） ===
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

# === 缓存（来自 zephyr.shared.infra） ===
from zephyr.shared.infra.cache import (
    CacheError,
    CacheProvider,
    CacheStats,
    MemoryCache,
    cache_key,
)

__all__ = [
    # 序列化
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
    # 文件工具
    "AtomicWriteError",
    "atomic_write",
    "backup_and_rollback",
    "backup_file",
    "restore_backup",
    "safe_read",
    # Diff/Patch
    "PatchConflictError",
    "apply_patch",
    "compute_diff",
    "compute_file_diff",
    "similarity_ratio",
    "try_apply_patch",
    # 密钥/安全
    "SECRET_INDICATOR_PATTERNS",
    "DotEnvSecretProvider",
    "EnvSecretProvider",
    "SecretProvider",
    "SecretsError",
    "sanitize_secret",
    # 会话审计
    "CostRecord",
    "DecisionRecord",
    "ErrorRecord",
    "OutcomeRecord",
    "PromptRecord",
    "SessionAuditTrail",
    "SessionRecord",
    "ToolCallRecord",
    # API 客户端
    "AioHttpProvider",
    "ApiCallError",
    "ApiCallMetrics",
    "ApiClient",
    "ApiClientConfig",
    "ApiResponse",
    "HttpMethod",
    "HttpProvider",
    # 缓存
    "CacheError",
    "CacheProvider",
    "CacheStats",
    "MemoryCache",
    "cache_key",
]


# Lazy imports to break circular: loader → shared_08 → _infrastructure → loader
def __getattr__(name):
    if name in ("ConfigLoadError", "load_yaml_config", "load_yaml_config_validated"):
        from zephyr.shared.config import loader as _loader

        return getattr(_loader, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
