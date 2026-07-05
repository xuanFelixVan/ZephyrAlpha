# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.annotations
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/governance_misc/test_annotations.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_annotations | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""共享函数注解引擎 — @shared / @known_dup / @intentional 三注解."""

import functools
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

SHARED_FUNCTIONS: dict[str, str] = {}
KNOWN_DUPLICATES: dict[str, list[str]] = {}
INTENTIONAL_DUPLICATES: dict[str, str] = {}


def shared(module: str = "", version: str = "1.0.0") -> Callable[[F], F]:
    """标记函数为共享实现."""

    def decorator(func: F) -> F:
        key = f"{module}::{func.__name__}" if module else func.__name__
        SHARED_FUNCTIONS[key] = version

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        wrapper._shared_info = {"module": module, "version": version}
        return wrapper  # type: ignore[return-value]

    return decorator


def known_dup(group_id: str = "", confidence: float = 0.0) -> Callable[[F], F]:
    """标记函数为已知重复."""

    def decorator(func: F) -> F:
        KNOWN_DUPLICATES.setdefault(group_id, []).append(func.__name__)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        wrapper._dup_info = {"group_id": group_id, "confidence": confidence}
        return wrapper  # type: ignore[return-value]

    return decorator


def intentional(reason: str = "") -> Callable[[F], F]:
    """标记函数为有意重复（设计模式等）."""

    def decorator(func: F) -> F:
        INTENTIONAL_DUPLICATES[func.__name__] = reason

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def get_shared_registry() -> dict[str, str]:
    return SHARED_FUNCTIONS


def get_known_duplicates() -> dict[str, list[str]]:
    return KNOWN_DUPLICATES
