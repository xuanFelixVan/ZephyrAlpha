# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.behavioral_sampler
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.intelligence_governance.self_benchmark; tests/governance/delegation/test_behavioral_sampler.py
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
行为采样验证器 — Stage 0.25 低成本快速验证.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: behavioral_sampler.py
# 层: 算法
# - id: A1
#   name_zh: ① BehavioralSampler
#   name_en: BehavioralSampler
#   intro: 行为采样——生成测试输入并验证行为一致性.
#   desc: 行为采样——生成测试输入并验证行为一致性.；公共方法（定义序）: generate_samples, verify_behavior, is_pure_function；源码 L63-L101
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: BehavioralSampler
#   downstream: zephyr.governance.intelligence_governance.self_benchmark; tests/governance/dele…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import ast
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BehaviorSample:
    func_name: str = ""
    inputs: list[Any] = field(default_factory=list)
    output: object = None
    is_pure: bool = False
    passed: bool = False


class BehavioralSampler:
    """行为采样——生成测试输入并验证行为一致性."""

    _SAMPLE_COUNT: int = 3

    def generate_samples(self, source: str) -> list[dict]:
        """AST分析->生成采样输入."""
        try:
            tree = ast.parse(source.lstrip())
        except SyntaxError:
            return [{"input": None, "type": "unknown"}]

        samples: list[dict] = [{"input": i, "type": f"sample_{i}"} for i in range(self._SAMPLE_COUNT)]
        return samples

    def verify_behavior(self, func_a: callable, func_b: callable, samples: list[Any]) -> BehaviorSample:
        """对相同输入调用两个函数->输出一致=PASS."""
        passed = True
        for inp in samples[: self._SAMPLE_COUNT]:
            try:
                a = func_a(inp) if inp is not None else func_a()
                b = func_b(inp) if inp is not None else func_b()
                if a != b:
                    passed = False
                    break
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                passed = False
                break

        return BehaviorSample(
            func_name=getattr(func_a, "__name__", "?"),
            inputs=samples[: self._SAMPLE_COUNT],
            passed=passed,
        )

    def is_pure_function(self, source: str) -> bool:
        """启发式纯函数判定——无global/nonlocal/print/副作用."""
        keywords = {"global", "nonlocal", "print("}
        return not any(kw in source for kw in keywords)
