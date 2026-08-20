# [BLUEPRINT] MOD-POS-006 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TTL] permanent
"""

[A_module] module_id=MOD-POSITION | layer=infrastructure | stability=evolving | safety=L | ai_autonomy=ai_modifiable

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: position_reconciler 子模块
#   fields: 持仓对账子模块（__all__ 白名单唯一条目）
#   code: position/__init__.py L3
# 层: 算法
# - id: A1
#   name_zh: ① 包命名空间声明
#   name_en: zephyr.position __init__
#   intro: 声明 position 包的公共面（仅 position_reconciler），无计算逻辑
#   desc: docstring 标注 A_module 元数据（layer=infrastructure）+ __all__=['position_reconciler']（L1-3）
#   inputs: I1
#   outputs: 包级命名空间
# 层: 输出
# - id: O1
#   name_zh: zephyr.position 包入口
#   name_en: zephyr.position namespace
#   intro: 仓位域包级入口，对全仓暴露 position_reconciler 公共面
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

__all__: Final = ["position_reconciler"]
