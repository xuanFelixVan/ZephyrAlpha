# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.foundation.deprecation
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_deprecation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
deprecation.py —— ZephyrAlpha API 废弃策略

Phase 5 新增（盲点 B5）——解决 shared/ 中旧 API 无法安全标记废弃、
AI 不确定是否可以删除旧代码的问题。

设计原则：
  - @deprecated 装饰器——标注废弃函数/类/方法
  - since / remove_in / replacement 三参数——明确时间线和迁移路径
  - DeprecationWarning 集成——Python warnings 模块标准机制
  - 可配置行为——开发环境 warn，CI 环境可 fail，生产环境 silent
  - 零运行时开销（no-op 模式）——生产环境跳过所有检查

对标：
  - Google ABSL_DEPRECATED 宏——编译时警告 + 文档自动生成
  - Python warnings.deprecated (3.13+)——标准库内置支持
  - Django deprecation timeline——2 版本警告 + 1 版本移除

SSoT: MOD-INF-016 §2.13 shared-deprecation
Version: 0.1.0
"""

from __future__ import annotations

import functools
import os
import warnings
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

__all__ = [
    "DeprecatedAPIError",
    "DeprecationMode",
    "deprecated",
    "get_deprecation_mode",
    "set_deprecation_mode",
]


class DeprecatedAPIError(FutureWarning):
    """废弃 API 仍被调用的运行时异常（仅在 strict 模式下抛出）。"""


_DEPRECATION_MODE = os.environ.get("ZEPHYR_DEPRECATION_MODE", "warn")


class DeprecationMode:
    WARN = "warn"
    STRICT = "strict"
    SILENT = "silent"


def set_deprecation_mode(mode: str) -> None:
    """设置全局废弃策略模式。

    Args:
        mode: "warn" (默认——发出 DeprecationWarning)
              "strict" (CI 模式——抛出 DeprecatedAPIError)
              "silent" (生产模式——完全静默)
    """
    global _DEPRECATION_MODE
    valid = {DeprecationMode.WARN, DeprecationMode.STRICT, DeprecationMode.SILENT}
    if mode not in valid:
        raise ValueError(f"_DEPRECATION_MODE 必须是 {valid} 之一，收到: {mode}")
    _DEPRECATION_MODE = mode


def get_deprecation_mode() -> str:
    """获取当前废弃策略模式。"""
    return _DEPRECATION_MODE


def deprecated(
    since: str,
    remove_in: str | None = None,
    replacement: str | None = None,
    *,
    reason: str | None = None,
) -> Callable[[F], F]:
    """标记函数/类/方法为废弃。

    Args:
        since: 废弃起始版本（如 "0.6.0"）
        remove_in: 计划移除版本（如 "0.8.0"）。None = 暂无移除计划
        replacement: 替代方案（如 "new_function_name"）
        reason: 废弃原因（可选补充说明）

    Returns:
        包装后的函数/类

    用法:
        @deprecated(since="0.6.0", remove_in="0.8.0", replacement="new_func")
        def old_func(x):
            return x * 2

        @deprecated(since="0.5.0", reason="Use TaskCard directly instead")
        class OldTaskModel:
            ...

    行为:
        - "warn" 模式: 首次调用发 DeprecationWarning（后续调用静默）
        - "strict" 模式: 首次调用抛出 DeprecatedAPIError
        - "silent" 模式: 完全跳过，零开销
    """

    def decorator(obj: F) -> F:
        message_parts = [f"'{obj.__name__}' is deprecated since {since}"]
        if remove_in:
            message_parts.append(f"and will be removed in {remove_in}")
        if replacement:
            message_parts.append(f"(use '{replacement}' instead)")
        if reason:
            message_parts.append(f"— {reason}")
        message = " ".join(message_parts)

        @functools.wraps(obj)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            mode = get_deprecation_mode()

            if mode == DeprecationMode.SILENT:
                return obj(*args, **kwargs)

            if mode == DeprecationMode.STRICT:
                raise DeprecatedAPIError(message)

            if mode == DeprecationMode.WARN:
                if not getattr(wrapper, "_zephyr_deprecation_warned", False):
                    warnings.warn(message, DeprecatedAPIError, stacklevel=2)
                    wrapper._zephyr_deprecation_warned = True  # type: ignore[attr-defined]

            return obj(*args, **kwargs)

        wrapper._zephyr_deprecated = True  # type: ignore[attr-defined]
        wrapper._zephyr_deprecated_since = since  # type: ignore[attr-defined]
        wrapper._zephyr_deprecated_remove_in = remove_in  # type: ignore[attr-defined]
        wrapper._zephyr_deprecated_replacement = replacement  # type: ignore[attr-defined]

        return wrapper  # type: ignore[return-value]

    # 支持无参数调用: @deprecated vs @deprecated(since="...", ...)
    if callable(since):
        fn = since
        since = "unknown"
        return decorator(fn)

    return decorator
