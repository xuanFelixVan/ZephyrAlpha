# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.progressive_disclosure_injector
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
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""



progressive_disclosure_injector.py — 渐进式披露 (B7, DD81, TASK-015 beta w)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: progressive_disclosure_injector.py
# 层: 算法
# - id: A1
#   name_zh: ① ProgressiveDisclosureInjector
#   name_en: ProgressiveDisclosureInjector
#   intro: 摘要先注->agent 请求展开完整 KE (DD81).
#   desc: 摘要先注->agent 请求展开完整 KE (DD81).；公共方法（定义序）: inject_summary, expand；源码 L61-L68
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ProgressiveDisclosureInjector
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class DisclosureResult:
    summary_injected: bool
    ke_ids_available: list[str]
    expanded_ke_id: str = ""


class ProgressiveDisclosureInjector:
    """摘要先注->agent 请求展开完整 KE (DD81)."""

    def inject_summary(self, ke_ids: list[str]) -> DisclosureResult:
        return DisclosureResult(summary_injected=True, ke_ids_available=ke_ids)

    def expand(self, ke_id: str) -> str:
        return f"Full content for {ke_id}"
