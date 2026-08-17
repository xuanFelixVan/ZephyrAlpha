# [A_module] module_id=MOD-GOV_CODE_QUALITY_DOMAIN | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_CODE_QUALITY_DOMAIN | docs/03_modules/_domain_governance/code_quality/blueprint.md
# [MODULE] zephyr.gov_code_quality
# [DOMAIN] D_GOV_CODE_QUALITY
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""

gov_code_quality domain package — code quality governance (D_GOV_CODE_QUALITY).

Migrated from src/zephyr/governance/code_dedup/ in batch 11.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 域包内子模块 Python源码
#   fields: code_dedup 子包等 D_GOV_CODE_QUALITY 域内模块
#   code: zephyr/gov_code_quality/ 目录
# 层: 算法
# - id: A1
#   name_zh: ① 域包标记占位
#   name_en: __init__ (gov_code_quality 域包初始化)
#   intro: 声明 gov_code_quality 代码质量治理域包身份，不导出任何符号
#   desc: 仅 docstring 说明域职责（batch 11 从 governance/code_dedup 迁入）+ 空 __all__；无运行逻辑
#   inputs: I1
#   outputs: 空命名空间
# 层: 输出
# - id: O1
#   name_zh: 域包空导出
#   name_en: __all__ 空列表
#   intro: 不对外导出符号，域内模块由使用方直接按路径 import
#   downstream: 无下游/内部使用（域内 code_dedup 子包被 zephyr.governance 引用）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
