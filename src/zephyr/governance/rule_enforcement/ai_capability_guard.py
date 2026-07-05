# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.ai_capability_guard
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_ai_capability_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ZephyrAlpha — gates/ai_capability_guard.py

@require_capability 装饰器 + AI 能力边界运行时检查。

配合：
  - config/ai_capability_matrix.yaml（SSoT 定义）
  - scripts/governance/d7_code/check_ai_capability_boundary.py（CI 静态检查）
  - IRN-001~010 铁律（政策依据）

用法
----
    from zephyr.governance.rule_enforcement.ai_capability_guard import require_capability

    @require_capability("modify_factor_registry", min_level=CapabilityLevel.EXTEND)
    def register_new_factor(factor_def: dict) -> None:
        ...

设计原则
--------
- 装饰器标记而非拦截——标记违规操作让 CI 捕获
- 生产环境中可通过配置切换为运行时拦截
- 与 ContractEnforcer 互补：enforcer 管数据，capability guard 管行为

SSoT: config/ai_capability_matrix.yaml
"""

from __future__ import annotations

import functools
import logging
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Any

_logger = logging.getLogger("zephyr.governance.rule_enforcement.capability_guard")


class CapabilityLevel(str, Enum):
    IMMUTABLE = "IMMUTABLE"
    EXTEND = "EXTEND"
    FULL = "FULL"


def _level_meets_min(actual: CapabilityLevel, minimum: CapabilityLevel) -> bool:
    level_order = {
        CapabilityLevel.IMMUTABLE: 0,
        CapabilityLevel.EXTEND: 1,
        CapabilityLevel.FULL: 2,
    }
    return level_order[actual] >= level_order[minimum]


def _get_caller_file() -> str | None:
    import inspect

    for frame_info in inspect.stack():
        filename = frame_info.filename
        if not filename.startswith(str(Path(__file__).resolve().parent)):
            if "ai_capability_guard.py" not in filename:
                return filename
    return None


def require_capability(
    operation: str,
    min_level: CapabilityLevel = CapabilityLevel.EXTEND,
) -> Callable:
    """装饰器——标记函数需要的 AI 能力等级。

    在开发阶段，此装饰器记录操作需求到日志，供 CI 检查脚本分析。
    在生产模式 (ZEPHYR_ENFORCE_CAPABILITY=true) 下，运行时拦截越权操作。

    参数
    ----
    operation : str
        操作描述（如 "modify_contract", "delete_factor"）
    min_level : CapabilityLevel
        该操作所需的最低 AI 能力等级
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            caller_file = _get_caller_file() or "unknown"

            import os

            enforce = os.environ.get("ZEPHYR_ENFORCE_CAPABILITY", "").lower() == "true"

            _logger.debug(
                "[CapabilityGuard] %s 调用 '%s' — 需要等级=%s, 调用位置=%s",
                operation,
                func.__qualname__,
                min_level.value,
                caller_file,
            )

            if enforce:
                actual_level = _check_file_level(caller_file)
                if not _level_meets_min(actual_level, min_level):
                    raise PermissionError(
                        f"AI 越权操作: {func.__qualname__} 需要 "
                        f"{min_level.value} 级权限，但 {caller_file} "
                        f"仅有 {actual_level.value} 级权限"
                    )

            return func(*args, **kwargs)

        wrapper._capability_operation = operation
        wrapper._capability_min_level = min_level
        return wrapper

    return decorator


def _check_file_level(filepath: str) -> CapabilityLevel:
    rel = str(Path(filepath).resolve()).replace("\\", "/").lower()

    if "shared/contracts" in rel:
        return CapabilityLevel.IMMUTABLE

    if "governance/ai" in rel:
        return CapabilityLevel.IMMUTABLE
    if "_registry.yaml" in rel:
        return CapabilityLevel.IMMUTABLE

    if "tests/architecture" in rel or "scripts/governance" in rel:
        return CapabilityLevel.EXTEND
    if "factor_registry" in rel or "test_enforcer" in rel:
        return CapabilityLevel.EXTEND

    return CapabilityLevel.FULL
