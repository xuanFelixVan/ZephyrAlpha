# [A_module] module_id=MOD-CMP-implementations | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export wrapper: implementations has migrated to zephyr.governance.implementations.

5.60.8 治本（2026-07-20）：替代 ``from ... import *``，改用 PEP 562 惰性转发，
保留向后兼容（``from zephyr.compliance.implementations import X`` 仍可用），
同时消除 namespace 污染并避免 eager import 副作用。
"""
from __future__ import annotations

import importlib
import sys
from typing import Any

_TARGET = "zephyr.governance.implementations"


def __getattr__(name: str) -> Any:
    """PEP 562 惰性转发：从目标模块获取符号并缓存到模块属性。"""
    if name.startswith("__"):
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    target = importlib.import_module(_TARGET)
    try:
        value = getattr(target, name)
    except AttributeError as exc:
        raise AttributeError(
            f"module {__name__!r}: re-export target {_TARGET!r} has no attribute {name!r}"
        ) from exc
    setattr(sys.modules[__name__], name, value)
    return value


def __dir__() -> list[str]:
    target = importlib.import_module(_TARGET)
    target_all = getattr(target, "__all__", [])
    return sorted(set(globals()) | set(target_all))

__all__: list[str] = []
