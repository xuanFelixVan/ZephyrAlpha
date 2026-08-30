# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.health.self_benchmark
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
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
Self Benchmark — v0.9.0 R115

Blindspot: FLE performance trends invisible without historical comparison.
Risk: R115 — Gradual degradation invisible without baseline comparison.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: self_benchmark.py
# 层: 算法
# - id: A1
#   name_zh: ① SelfBenchmark
#   name_en: SelfBenchmark
#   intro: class SelfBenchmark 源码 L55-L60
#   desc: 公共方法（定义序）: compare；源码 L55-L60
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SelfBenchmark
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field


@dataclass
class SelfBenchmark:
    baselines: dict[str, float] = field(default_factory=dict)

    def compare(self, metric: str, current: float) -> float:
        baseline = self.baselines.get(metric, current)
        return current - baseline
