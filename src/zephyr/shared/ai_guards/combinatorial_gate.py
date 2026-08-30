# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.ai_guards.combinatorial_gate
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
#   code: combinatorial_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① CombinatorialGate
#   name_en: CombinatorialGate
#   intro: class CombinatorialGate 源码 L76-L88
#   desc: 公共方法（定义序）: evaluate_and, evaluate_or, evaluate；源码 L76-L88
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: CombinatorialGate
#   downstream: zephyr.governance.__init__ ; zephyr.gov_enforcement.rule_enforcement.gate_engine
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CombineOp(Enum):
    AND = "and"
    OR = "or"


@dataclass
class GateCheck:
    name: str
    passed: bool
    message: str


@dataclass
class CombinedResult:
    operation: CombineOp
    checks: list[GateCheck]
    passed: bool


GateResult = GateCheck


class CombinatorialGate:
    def evaluate_and(self, checks: list[GateCheck]) -> CombinedResult:
        passed = all(c.passed for c in checks)
        return CombinedResult(CombineOp.AND, checks, passed)

    def evaluate_or(self, checks: list[GateCheck]) -> CombinedResult:
        passed = any(c.passed for c in checks)
        return CombinedResult(CombineOp.OR, checks, passed)

    def evaluate(self, checks: list[GateCheck], operation: CombineOp = CombineOp.AND) -> CombinedResult:
        if operation is CombineOp.OR:
            return self.evaluate_or(checks)
        return self.evaluate_and(checks)
