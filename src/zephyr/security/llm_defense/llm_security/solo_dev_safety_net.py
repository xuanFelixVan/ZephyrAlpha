# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md
# [MODULE] zephyr.security.llm_defense.llm_security.solo_dev_safety_net
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-LLM_SECURITY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
solo_dev_safety_net.py — 单人无审查安全网 (B15, DD89, TASK-017)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: solo_dev_safety_net.py
# 层: 算法
# - id: A1
#   name_zh: ① SoloDevSafetyNet
#   name_en: SoloDevSafetyNet
#   intro: P0 task injection confirmation gate + 5min timeout auto-pro…
#   desc: P0 task injection confirmation gate + 5min timeout auto-proceed (DD89).；公共方法（定义序）: check_injection；源码 L61-L71
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: SoloDevSafetyNet
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class SafetyNetCheck:
    task_id: str
    is_p0: bool
    confirmation_needed: bool
    context_summary: str
    timeout_auto_proceed: bool = False


class SoloDevSafetyNet:
    """P0 task injection confirmation gate + 5min timeout auto-proceed (DD89)."""

    def check_injection(self, task_id: str, priority: str, context_preview: str) -> SafetyNetCheck:
        is_p0 = priority.upper() == "P0"
        return SafetyNetCheck(
            task_id=task_id,
            is_p0=is_p0,
            confirmation_needed=is_p0,
            context_summary=context_preview[:200],
        )
