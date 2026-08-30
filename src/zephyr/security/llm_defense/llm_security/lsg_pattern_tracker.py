# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md
# [MODULE] zephyr.security.llm_defense.llm_security.lsg_pattern_tracker
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
# [A_module] module_id=MOD-LLM_SECURITY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
lsg_pattern_tracker.py — LSG 模式逃逸追踪 (B20, DD94, TASK-017)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: lsg_pattern_tracker.py
# 层: 算法
# - id: A1
#   name_zh: ① LSGPatternTracker
#   name_en: LSGPatternTracker
#   intro: LSG rejection_reason_code tracking; 3x->retry; 10x cross-se…
#   desc: LSG rejection_reason_code tracking; 3x->retry; 10x cross-session -> escalate (DD94).；公共方法（定义序）: track_rejecti…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: LSGPatternTracker
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from collections import Counter
from dataclasses import dataclass


@dataclass
class LSGRejectionPattern:
    reason_code: str
    count: int
    same_pattern_3x: bool
    cross_session_10x: bool
    action_needed: str


class LSGPatternTracker:
    """LSG rejection_reason_code tracking; 3x->retry; 10x cross-session -> escalate (DD94)."""

    def __init__(self) -> None:
        self._counters: Counter[str] = Counter()
        self._cross_session: Counter[str] = Counter()

    def track_rejection(self, reason_code: str) -> LSGRejectionPattern:
        self._counters[reason_code] += 1
        count = self._counters[reason_code]
        return LSGRejectionPattern(
            reason_code=reason_code,
            count=count,
            same_pattern_3x=count >= 3,
            cross_session_10x=self._cross_session.get(reason_code, 0) >= 10,
            action_needed="rebuild" if count >= 3 else "retry" if count >= 2 else "none",
        )
