# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.context_outcome_tracker
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
context_outcome_tracker.py — 因果链追踪 (B14, DD88, TASK-017)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: context_outcome_tracker.py
# 层: 算法
# - id: A1
#   name_zh: ① ContextOutcomeTracker
#   name_en: ContextOutcomeTracker
#   intro: ContextBlock -> Agent Action -> Action Success 三级因果关联 (DD88…
#   desc: ContextBlock -> Agent Action -> Action Success 三级因果关联 (DD88).；公共方法（定义序）: links, record, low_success_ke；源码 L61…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ContextOutcomeTracker
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class ContextOutcomeLink:
    context_block_id: str
    agent_actions: list[str]
    action_successes: list[bool]
    success_rate: float = 0.0
    suspect: bool = False


class ContextOutcomeTracker:
    """ContextBlock -> Agent Action -> Action Success 三级因果关联 (DD88)."""

    def __init__(self) -> None:
        self._links: dict[str, ContextOutcomeLink] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def links(self) -> dict[str, ContextOutcomeLink]:
        """只读：links（Stage 4 公共化）。"""
        return self._links

    @links.setter
    def links(self, value):
        """写入：links（Stage 4 公共化）。"""
        self._links = value

    def record(self, context_id: str, actions: list[str], successes: list[bool]) -> ContextOutcomeLink:
        rate = sum(successes) / max(1, len(successes))
        link = ContextOutcomeLink(
            context_block_id=context_id,
            agent_actions=actions,
            action_successes=successes,
            success_rate=round(rate, 3),
            suspect=rate < 0.5,
        )
        self._links[context_id] = link
        return link

    def low_success_ke(self) -> list[str]:
        return [k for k, v in self._links.items() if v.suspect]
