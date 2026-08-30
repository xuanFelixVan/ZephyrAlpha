# [BLUEPRINT] MOD-REFLEXION_AGENT | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/12_reflexion_multi_agent.md
# [MODULE] zephyr.intelligence.reflexion
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] L1 只规则化归因; 盘中零调用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/intelligence/test_reflexion_phase0.py
# [A_module] module_id=MOD-REFLEXION_AGENT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
自反Agent 包 —— 12号文 Phase 0(P0-1~P0-4) + Phase 1(P1-1/P1-2/P1-3)。

Phase 0 范围: L1 单轨迹反思(规则化归因 MVP)+三角色骨架。
Phase 1 已落地: ReflCtrl 频率闸门(P1-1)+投票评审壳(P1-2, 可选模式设施,
人手动触发)+PreFlect 失败模式库(P1-3)。
L2(N=5 累积)/L3(远期)归 Phase 2+, 本包不含。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations, Final
#   code: __init__.py import L53
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 annotations, Final（共 2 符号）
#   desc: __init__ import L53；__all__ 0 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（2 符号）
#   name_en: __all__
#   intro: annotations, Final
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from typing import Final

__all__: Final = [
    "batch_runner",
    "l1_reflector",
    "preflect_store",
    "reflctrl_gate",
    "reflection_schema",
    "roles",
    "vote_review_shell",
]
