# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.schema.base_config
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] BASE_CONFIG MUST align with ADR-0040 §4.2
# [MODIFY-GUARD] ADR-0040
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] N/A
# [TESTS] tests/test_schemas.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: base_config.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 BASE_CONFIG, Classification, EvolutionPolicy（共 3 符号）
#   desc: __init__ import L0；__all__ 3 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（2 类）
#   name_en: data classes
#   intro: Classification, EvolutionPolicy
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from enum import Enum
from typing import Final

from pydantic import ConfigDict

__all__ = [
    "BASE_CONFIG",
    "Classification",
    "EvolutionPolicy",
]


class Classification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"


class EvolutionPolicy(str, Enum):
    FROZEN = "frozen"
    EXTENDABLE = "extendable"
    REWRITABLE = "rewritable"


BASE_CONFIG: Final[ConfigDict] = ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
    populate_by_name=True,
    validate_assignment=True,
)
