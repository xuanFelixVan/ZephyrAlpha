# [A_module] module_id=MOD-INF-script_system | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain-governance/governance-automation/blueprint.md
# [MODULE] zephyr.infrastructure.script_system
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: pathlib 子模块符号 1个
#   fields: Path
#   code: pathlib
# 层: 算法
# - id: A1
#   name_zh: ① 包级聚合再导出
#   name_en: zephyr.infrastructure.script_system.__init__
#   intro: 5.136.1 修复: __all__ 移除已删除的 GateBridge/KBBridge 幽灵符号
#   desc: MOD-INF-005 包入口，包级聚合再导出并声明 __all__（2项）
#   inputs: I1
#   outputs: zephyr.infrastructure.script_system 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（2项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.infrastructure.script_system 包公共 API
#   name_en: __all__ 2项
#   intro: 5.136.1 修复: __all__ 移除已删除的 GateBridge/KBBridge 幽灵符号——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

from pathlib import Path

_script_system_root = Path(__file__).parent

# 5.136.1 修复: __all__ 移除已删除的 GateBridge/KBBridge 幽灵符号
__all__ = ["finding", "gate_bridge"]
