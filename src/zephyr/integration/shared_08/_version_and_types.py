# [A_module] module_id=MOD-INT__version_and_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08._version_and_types
# [INVARIANTS] backward_compat: all exports must remain available from zephyr.shared
# [MODIFY-GUARD] zephyr.shared.__init__
# [CONSUMERS] zephyr.shared.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.shared"

from zephyr.integration.shared_08.__version__ import (
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
from zephyr.integration.shared_08.types import (
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
from zephyr.integration.shared_08.io.paths import (
    DB_PATH,
    REPO_ROOT,
)
from zephyr.integration.shared.schema.schemas import (
    ExecutionModel,
    Priority,
    SafetyLevel,
    Task,
    TaskNamespace,
    TaskStatus,
    normalize_execution_model,
)
from zephyr.shared.shared_services.observability_02.token_utils import (
    DEFAULT_CONTEXT_TOKEN_BUDGET,
    estimate_tokens,
)
from zephyr.integration.shared_08.time_utils import (
    MOCKED_TIME,
    format_iso,
    freeze_time,
    now_utc,
    parse_iso,
    seconds_since,
    seconds_until,
)
from zephyr.integration.shared_08.env import (
    Env,
    current_env,
    is_debug,
    is_dev,
    is_prod,
    is_staging,
    is_test,
)
