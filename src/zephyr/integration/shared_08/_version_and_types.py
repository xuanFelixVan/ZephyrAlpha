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
"""_version_and_types — 版本与类型 re-export 桥接层。

从 foundation/__version__/io/utils 子包及外部模块重新导出符号，
保持 shared_08.__init__ 向后兼容。
"""

# === 版本 ===
# === Token 预算（来自 zephyr.autonomy_core） ===
from zephyr.autonomy_core.token_budget import (
    DEFAULT_CONTEXT_TOKEN_BUDGET,
    estimate_tokens,
)

# === 任务类型（来自 zephyr.governance.rule_enforcement） ===
from zephyr.governance.rule_enforcement.task_types import (
    Task,
    TaskNamespace,
    TaskStatus,
)

# === 执行模型（来自 zephyr.integration.shared.schema） ===
from zephyr.integration.shared.schema.execution_model import (
    ExecutionModel,
    normalize_execution_model,
)

# === 严重性/优先级枚举（来自 zephyr.integration.shared.schema） ===
from zephyr.integration.shared.schema.severity_types import (
    Priority,
    SafetyLevel,
)
from zephyr.integration.shared_08.__version__ import (
    MIN_COMPATIBLE_SHARED_VERSION,
    VersionMismatchError,
    __version__,
    __version_info__,
    check_shared_version,
    version_compatible,
    version_eq,
    version_gt,
    version_gte,
    version_lt,
    version_lte,
    version_major,
    version_minor,
    version_patch,
)

# === 环境枚举与函数 ===
from zephyr.integration.shared_08.foundation.env import (
    Env,
    current_env,
    is_debug,
    is_dev,
    is_prod,
    is_staging,
    is_test,
)

# === 类型别名 ===
from zephyr.integration.shared_08.foundation.types import (
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

# === 路径常量 ===
from zephyr.integration.shared_08.io.paths import (
    DB_PATH,
    REPO_ROOT,
)

# === 时间工具 ===
from zephyr.integration.shared_08.utils.time_utils import (
    MOCKED_TIME,
    format_iso,
    freeze_time,
    now_utc,
    parse_iso,
    seconds_since,
    seconds_until,
)

__all__ = [
    # 版本
    "MIN_COMPATIBLE_SHARED_VERSION",
    "VersionMismatchError",
    "__version__",
    "__version_info__",
    "check_shared_version",
    "version_compatible",
    "version_eq",
    "version_gt",
    "version_gte",
    "version_lt",
    "version_lte",
    "version_major",
    "version_minor",
    "version_patch",
    # 路径常量
    "DB_PATH",
    "REPO_ROOT",
    # 时间工具
    "MOCKED_TIME",
    "format_iso",
    "freeze_time",
    "now_utc",
    "parse_iso",
    "seconds_since",
    "seconds_until",
    # 类型别名
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
    # 环境枚举与函数
    "Env",
    "current_env",
    "is_debug",
    "is_dev",
    "is_prod",
    "is_staging",
    "is_test",
    # 执行模型
    "ExecutionModel",
    "normalize_execution_model",
    # 严重性/优先级枚举
    "Priority",
    "SafetyLevel",
    # Token 预算
    "DEFAULT_CONTEXT_TOKEN_BUDGET",
    "estimate_tokens",
    # 任务类型
    "Task",
    "TaskNamespace",
    "TaskStatus",
]
