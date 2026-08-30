# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.contextual_fetch_api
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
contextual_fetch_api.py — HTTP FE 对外 API (DD115, TASK-020)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: contextual_fetch_api.py
# 层: 算法
# - id: A1
#   name_zh: ① ContextualFetchAPI
#   name_en: ContextualFetchAPI
#   intro: GET /api/ce/session/{id}?context_type=full|summary (DD115).
#   desc: GET /api/ce/session/{id}?context_type=full|summary (DD115).；公共方法（定义序）: fetch；源码 L60-L66
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ContextualFetchAPI
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field


@dataclass
class FetchSession:
    session_id: str
    context_type: str  # "full" | "summary"
    token_count: int
    sources: list[str] = field(default_factory=list)


class ContextualFetchAPI:
    """GET /api/ce/session/{id}?context_type=full|summary (DD115)."""

    def fetch(self, session_id: str, context_type: str = "full") -> FetchSession:
        return FetchSession(
            session_id=session_id, context_type=context_type, token_count=500, sources=["KE-001", "CT-001"]
        )
