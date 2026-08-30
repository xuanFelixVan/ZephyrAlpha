# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.verifiers.golden_test_external
# [DOMAIN] D_FBL_VERIFICATION
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Golden Test External — v0.15.0 R214

Blindspot: FLE internal tests biased toward own logic; golden tests invisible externally.
Risk: R214 — FLE passes self-tests but fails independent golden test suite.

Mitigation: Externally-defined golden tests with known inputs/expected outputs for FLE validation.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: golden_test_external.py
# 层: 算法
# - id: A1
#   name_zh: ① GoldenTestExternal
#   name_en: GoldenTestExternal
#   intro: class GoldenTestExternal 源码 L68-L86
#   desc: 公共方法（定义序）: register, evaluate, pass_rate；源码 L68-L86
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: GoldenTestExternal
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GoldenTest:
    test_id: str
    input_symptoms: dict
    expected_diagnosis: str
    expected_action: str


@dataclass
class GoldenTestExternal:
    tests: list[GoldenTest] = field(default_factory=list)
    results: dict[str, bool] = field(default_factory=dict)

    def register(self, test: GoldenTest) -> None:
        self.tests.append(test)

    def evaluate(self, test_id: str, actual_diagnosis: str, actual_action: str) -> bool:
        for t in self.tests:
            if t.test_id == test_id:
                passed = actual_diagnosis == t.expected_diagnosis and actual_action == t.expected_action
                self.results[test_id] = passed
                return passed
        return False

    def pass_rate(self) -> float:
        if not self.results:
            return 1.0
        return sum(1 for v in self.results.values() if v) / len(self.results)
