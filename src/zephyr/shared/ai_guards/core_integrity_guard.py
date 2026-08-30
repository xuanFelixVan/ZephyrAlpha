# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.ai_guards.core_integrity_guard
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.governance.__init__ ; zephyr.gov_enforcement.rule_enforcement.gate_engine
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
#   code: core_integrity_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① CoreIntegrityGuard
#   name_en: CoreIntegrityGuard
#   intro: class CoreIntegrityGuard 源码 L61-L84
#   desc: 公共方法（定义序）: freeze, register_frozen, check, is_frozen；源码 L61-L84
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: CoreIntegrityGuard
#   downstream: zephyr.governance.__init__ ; zephyr.gov_enforcement.rule_enforcement.gate_engine
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IntegrityCheck:
    component: str
    is_valid: bool
    intact: bool
    message: str


class CoreIntegrityGuard:
    def __init__(self):
        self._frozen_components: set[str] = set()
        self._checksums: dict[str, str] = {}

    def freeze(self, component: str, checksum: str) -> None:
        self._frozen_components.add(component)
        self._checksums[component] = checksum

    def register_frozen(self, component: str, checksum: str) -> None:
        self.freeze(component, checksum)

    def check(self, component: str, current_checksum: str) -> IntegrityCheck:
        if component not in self._frozen_components:
            return IntegrityCheck(
                component, False, False, "not_frozen: integrity check requires component to be frozen first"
            )
        expected = self._checksums.get(component, "")
        valid = current_checksum == expected
        msg = "checksum_match" if valid else f"expected {expected}, got {current_checksum}"
        return IntegrityCheck(component, valid, valid, msg)

    def is_frozen(self, component: str) -> bool:
        return component in self._frozen_components
