# [A_module] module_id=MOD-UNK_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.engine
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""D_FACTOR — Factors Package

D_FACTOR 因子实现包。每个因子独立一个模块，@FactorRegistry.register 自动注册。

Phase E 因子清单：
  - momentum_factor.py : 20 日动量因子
  - value_factor.py    : 估值因子（简单 PE proxy）
"""

__all__ = ["momentum_factor", "value_factor"]
