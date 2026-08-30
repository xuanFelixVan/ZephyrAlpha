# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.annotations
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/governance_misc/test_annotations.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
共享函数注解引擎 — @shared / @known_dup / @intentional 三注解.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: module 参数
#   fields: 参数 module，类型注解 str
#   code: annotations.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: version 参数
#   fields: 参数 version，类型注解 str
#   code: annotations.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: group_id 参数
#   fields: 参数 group_id，类型注解 str
#   code: annotations.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: confidence 参数
#   fields: 参数 confidence，类型注解 float
#   code: annotations.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① shared
#   name_en: shared
#   intro: 标记函数为共享实现.
#   desc: 标记函数为共享实现.；源码 L111-L125
#   inputs: module version
#   outputs: Callable[[F], F]
# - id: A2
#   name_zh: ② known_dup
#   name_en: known_dup
#   intro: 标记函数为已知重复.
#   desc: 标记函数为已知重复.；源码 L128-L141
#   inputs: group_id confidence
#   outputs: Callable[[F], F]
# - id: A3
#   name_zh: ③ intentional
#   name_en: intentional
#   intro: 标记函数为有意重复（设计模式等）.
#   desc: 标记函数为有意重复（设计模式等）.；源码 L144-L156
#   inputs: reason
#   outputs: Callable[[F], F]
# - id: A4
#   name_zh: ④ get_shared_registry
#   name_en: get_shared_registry
#   intro: get_shared_registry() 源码 L159-L160
#   desc: 源码 L159-L160
#   inputs: 无参数
#   outputs: dict[str, str]
# - id: A5
#   name_zh: ⑤ get_known_duplicates
#   name_en: get_known_duplicates
#   intro: get_known_duplicates() 源码 L163-L164
#   desc: 源码 L163-L164
#   inputs: 无参数
#   outputs: dict[str, list[str]]
# 层: 输出
# - id: O1
#   name_zh: Callable[[F], F]
#   name_en: Callable[[F], F]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/governance/governance_misc/test_annotations.py
# - id: O2
#   name_zh: dict[str, str]
#   name_en: dict[str, str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/governance/governance_misc/test_annotations.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

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
        def wrapper(*args: Any, **kwargs: Any) -> object:
            return func(*args, **kwargs)

        wrapper._shared_info = {"module": module, "version": version}
        return wrapper  # type: ignore[return-value]

    return decorator


def known_dup(group_id: str = "", confidence: float = 0.0) -> Callable[[F], F]:
    """标记函数为已知重复."""

    def decorator(func: F) -> F:
        KNOWN_DUPLICATES.setdefault(group_id, []).append(func.__name__)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> object:
            return func(*args, **kwargs)

        wrapper._dup_info = {"group_id": group_id, "confidence": confidence}
        return wrapper  # type: ignore[return-value]

    return decorator


def intentional(reason: str = "") -> Callable[[F], F]:
    """标记函数为有意重复（设计模式等）."""

    def decorator(func: F) -> F:
        INTENTIONAL_DUPLICATES[func.__name__] = reason

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> object:
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def get_shared_registry() -> dict[str, str]:
    return SHARED_FUNCTIONS


def get_known_duplicates() -> dict[str, list[str]]:
    return KNOWN_DUPLICATES
