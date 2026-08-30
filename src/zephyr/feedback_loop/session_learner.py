# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md
# [MODULE] zephyr.feedback_loop.session_learner
# [DOMAIN] D_FEEDBACK_LOOP
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
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""



session_learner.py — 在线学习 (DD114, TASK-020)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: session_learner.py
# 层: 算法
# - id: A1
#   name_zh: ① SessionLearner
#   name_en: SessionLearner
#   intro: Per-session Reinforcement Learning: citation + outcome (DD1…
#   desc: Per-session Reinforcement Learning: citation + outcome (DD114).；公共方法（定义序）: record, get_weight；源码 L62-L75
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: SessionLearner
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class LearningEvent:
    ke_id: str
    cited: bool
    success: bool
    timestamp: str


class SessionLearner:
    """Per-session Reinforcement Learning: citation + outcome (DD114)."""

    def __init__(self) -> None:
        self._events: list[LearningEvent] = []
        self._ke_weights: dict[str, float] = {}

    def record(self, ke_id: str, cited: bool, success: bool, timestamp: str = "") -> None:
        self._events.append(LearningEvent(ke_id=ke_id, cited=cited, success=success, timestamp=timestamp))
        delta = 0.1 if cited and success else (-0.05 if not cited else 0.0)
        self._ke_weights[ke_id] = max(0.0, min(1.0, self._ke_weights.get(ke_id, 0.5) + delta))

    def get_weight(self, ke_id: str) -> float:
        return self._ke_weights.get(ke_id, 0.5)
