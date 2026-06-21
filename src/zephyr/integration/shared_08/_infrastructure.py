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

from zephyr.integration.shared.api_03.api_client import (
    AioHttpProvider,
    ApiCallError,
    ApiCallMetrics,
    ApiClient,
    ApiClientConfig,
    ApiResponse,
    HttpMethod,
    HttpProvider,
)
from zephyr.integration.shared_08.cache import (
    CacheError,
    CacheProvider,
    CacheStats,
    MemoryCache,
    cache_key,
)
# STUB: from zephyr.shared.config import (ConfigLoadError, load_yaml_config, load_yaml_config_validated)
# Reason: zephyr.shared package does not exist; canonical is zephyr.infrastructure.config.shared.config.loader
# NOTE: lazy import to break circular: loader → shared_08 → _infrastructure → loader
def __getattr__(name):
    if name in ("ConfigLoadError", "load_yaml_config", "load_yaml_config_validated"):
        from zephyr.shared.config import loader as _loader
        return getattr(_loader, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
from zephyr.integration.shared_08.diff_utils import (
    PatchConflictError,
    apply_patch,
    compute_diff,
    compute_file_diff,
    similarity_ratio,
    try_apply_patch,
)
from zephyr.integration.shared_08.file_utils import (
    AtomicWriteError,
    atomic_write,
    backup_and_rollback,
    backup_file,
    restore_backup,
    safe_read,
)
from zephyr.integration.shared_08.secrets import (
    DotEnvSecretProvider,
    EnvSecretProvider,
    SECRET_INDICATOR_PATTERNS,
    SecretProvider,
    SecretsError,
    sanitize_secret,
)
from zephyr.integration.shared_08.serialization import (
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
