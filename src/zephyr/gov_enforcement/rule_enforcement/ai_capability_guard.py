# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.ai_capability_guard
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
    from zephyr.gov_enforcement.rule_enforcement.ai_capability_guard import require_capability

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
import os
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import REPO_ROOT

_logger = logging.getLogger("zephyr.gov_enforcement.rule_enforcement.capability_guard")


# 治本(2026-07-17): _check_file_level 路径模式真源是 config/ai_capability_matrix.yaml
# 原代码 L135-151 硬编码 7 个子串模式（shared/contracts 等），违反 SSoT 真源唯一性。
# 加载失败时回退到 _LEGACY_FALLBACK_PATTERNS（保持原行为，避免 fail-open）。
_AI_CAPABILITY_MATRIX_PATH: Path = Path(
    os.environ.get("ZEPHYR_AI_CAPABILITY_MATRIX_PATH", "")
) if os.environ.get("ZEPHYR_AI_CAPABILITY_MATRIX_PATH") else (
    REPO_ROOT / "config" / "ai_capability_matrix.yaml"
)


def _load_capability_matrix_entries() -> list[tuple[str, "CapabilityLevel"]]:
    """从 SSoT 加载 (scope_pattern, level) 列表。

    YAML 结构: matrix.entries: [{scope: "...", level: "IMMUTABLE|EXTEND|FULL"}]
    失败时返回空列表，调用方回退 _LEGACY_FALLBACK_PATTERNS。
    """
    try:
        import yaml

        if not _AI_CAPABILITY_MATRIX_PATH.exists():
            _logger.warning(
                "ai_capability_matrix.yaml missing at %s; using legacy fallback",
                _AI_CAPABILITY_MATRIX_PATH,
            )
            return []
        with open(_AI_CAPABILITY_MATRIX_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            return []
        entries: list[tuple[str, CapabilityLevel]] = []
        for entry in data.get("matrix", {}).get("entries", []) or []:
            if not isinstance(entry, dict):
                continue
            scope = entry.get("scope")
            level_str = entry.get("level")
            if not scope or not level_str:
                continue
            try:
                level = CapabilityLevel(str(level_str).upper())
            except ValueError:
                continue
            entries.append((str(scope), level))
        return entries
    except Exception as exc:
        _logger.error(
            "Failed to load ai_capability_matrix.yaml: %s", exc, exc_info=True
        )
        return []


class CapabilityLevel(str, Enum):
    IMMUTABLE = "IMMUTABLE"
    EXTEND = "EXTEND"
    FULL = "FULL"


# 在 CapabilityLevel 类定义后调用，确保 _load_capability_matrix_entries 内部
# 引用的 CapabilityLevel 已就绪。
_MATRIX_ENTRIES: list[tuple[str, CapabilityLevel]] = _load_capability_matrix_entries()


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
        def wrapper(*args: Any, **kwargs: Any) -> object:
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
    """根据文件路径判定 AI 能力等级。

    治本(2026-07-17): 真源是 config/ai_capability_matrix.yaml 的 matrix.entries。
    原代码硬编码 7 个子串模式（shared/contracts 等），违反 SSoT 真源唯一性。

    匹配规则（保持与原 substring 行为等价）:
        - YAML scope 是 glob 模式（如 ``src/zephyr/shared/contracts/**/*.py``），
          转换为子串匹配：取 glob 通配符之前的目录前缀作子串匹配。
          例：``src/zephyr/shared/contracts/**/*.py`` → 子串 ``src/zephyr/shared/contracts``
        - 以 ``**/`` 开头的通配模式（如 ``**/_registry.yaml``）→ 取末段文件名
          作子串匹配（``_registry.yaml``）。
        - ``**/path/**`` 模式（如 ``**/factor_registry/**``）→ 取中间路径段
          作子串匹配（``factor_registry``）。
        - 第一匹配 entry 的 level 即返回值（顺序敏感，YAML entries 已按
          "特异性高→低" 排序）。
        - 无匹配 → FULL（默认允许，与原代码一致）。
        - YAML 加载失败（_MATRIX_ENTRIES 为空）→ 回退 _legacy_check_file_level，
          保持原 7 个硬编码子串的等价行为（fail-safe，避免 fail-open）。
    """
    rel = str(Path(filepath).resolve()).replace("\\", "/").lower()

    if _MATRIX_ENTRIES:
        for scope, level in _MATRIX_ENTRIES:
            pattern = scope.lower()
            # 提取子串匹配模式
            sub = _scope_to_substring(pattern)
            if sub and sub in rel:
                return level
        return CapabilityLevel.FULL

    # 回退：YAML 加载失败时保持原硬编码子串行为（fail-safe，避免 fail-open）
    return _legacy_check_file_level(rel)


def _scope_to_substring(scope: str) -> str:
    """将 YAML scope glob 模式转换为子串匹配字符串。

    保持与原 ``if "X" in rel`` substring 行为等价：
        - ``src/zephyr/shared/contracts/**/*.py`` → ``src/zephyr/shared/contracts``
        - ``**/_registry.yaml`` → ``_registry.yaml``
        - ``**/factor_registry/**`` → ``factor_registry``
        - ``scripts/governance/**`` → ``scripts/governance``
        - ``tests/test_enforcer.py`` → ``tests/test_enforcer.py``
    """
    # 以 ** 切分，取非空最长段（最具体的目录/文件名）
    parts = [p.strip("/").strip("\\") for p in scope.split("**")]
    parts = [p for p in parts if p]
    if not parts:
        return scope.strip("*").strip("/").strip("\\")
    # 取最长的 part（如 "src/zephyr/shared/contracts" > ".py"）
    return max(parts, key=len)


def _legacy_check_file_level(rel: str) -> CapabilityLevel:
    """YAML 加载失败时的回退实现（保持原 L196-207 硬编码行为，禁止新增条目）。

    仅在 _MATRIX_ENTRIES 为空（即 YAML 加载失败）时调用。
    新增路径模式必须改 config/ai_capability_matrix.yaml，禁止在此扩展。
    """
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
