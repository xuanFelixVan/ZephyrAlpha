# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.protocols.module_birth_registry
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.governance.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: module_birth_registry.py
# 层: 算法
# - id: A1
#   name_zh: ① ModuleBirthRegistry
#   name_en: ModuleBirthRegistry
#   intro: class ModuleBirthRegistry 源码 L62-L78
#   desc: 公共方法（定义序）: register, get, get_children, list_all；源码 L62-L78
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ModuleBirthRegistry
#   downstream: zephyr.governance.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class BirthRecord:
    module_id: str
    created_at: float
    parent_module: str
    scaffold_method: str


class ModuleBirthRegistry:
    def __init__(self):
        self._records: dict[str, BirthRecord] = {}

    def register(self, module_id: str, parent_module: str = "", scaffold_method: str = "scaffold.py") -> BirthRecord:
        record = BirthRecord(module_id, time.time(), parent_module, scaffold_method)
        self._records[module_id] = record
        return record

    def get(self, module_id: str) -> BirthRecord | None:
        return self._records.get(module_id)

    def get_children(self, parent_module: str) -> list[BirthRecord]:
        return [r for r in self._records.values() if r.parent_module == parent_module]

    def list_all(self) -> list[BirthRecord]:
        return list(self._records.values())
