# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.reliability.blast_radius
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
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
Blast Radius Detector — v0.12.0 R167

Blindspot: Repair side effects across subsystems not modeled.
Risk: R167 — Repair on subsystem A breaks subsystem B; cascading failure.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: blast_radius.py
# 层: 算法
# - id: A1
#   name_zh: ① BlastRadius
#   name_en: BlastRadius
#   intro: class BlastRadius 源码 L55-L59
#   desc: 公共方法（定义序）: estimate；源码 L55-L59
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: BlastRadius
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field


@dataclass
class BlastRadius:
    dependency_graph: dict[str, list[str]] = field(default_factory=dict)

    def estimate(self, target: str) -> list[str]:
        return self.dependency_graph.get(target, [])
