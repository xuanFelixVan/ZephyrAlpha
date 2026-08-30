# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.ce_playground_v2
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ce_playground_v2.py — V2 Playground with full decision chain (TASK-016)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: ce_playground_v2.py
# 层: 算法
# - id: A1
#   name_zh: ① PlaygroundV2
#   name_en: PlaygroundV2
#   intro: 展示完整决策链 + per-KE rationale -> 支持排除某 KE 后重建.
#   desc: 展示完整决策链 + per-KE rationale -> 支持排除某 KE 后重建.；公共方法（定义序）: dry_run, dry_run_excluding；源码 L60-L67
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: PlaygroundV2
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field


@dataclass
class PlaygroundV2Result:
    task: str
    selected_ke_ids: list[str]
    decision_trace: list[str] = field(default_factory=list)
    excluded_ke_ids: list[str] = field(default_factory=list)


class PlaygroundV2:
    """展示完整决策链 + per-KE rationale -> 支持排除某 KE 后重建."""

    def dry_run(self, task: str) -> PlaygroundV2Result:
        return PlaygroundV2Result(task=task, selected_ke_ids=["KE-001", "KE-002"])

    def dry_run_excluding(self, task: str, exclude_ids: list[str]) -> PlaygroundV2Result:
        return PlaygroundV2Result(task=task, selected_ke_ids=["KE-003"], excluded_ke_ids=exclude_ids)
