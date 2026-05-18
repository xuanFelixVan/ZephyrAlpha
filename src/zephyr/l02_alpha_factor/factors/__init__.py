# [BLUEPRINT] MOD-L02-001 | 03_modules/l02_alpha_factor/alpha-factor-core/blueprint.md | §
"""L02 — Factors Package

L02 因子实现包。每个因子独立一个模块，@FactorRegistry.register 自动注册。

Phase E 因子清单：
  - momentum_factor.py : 20 日动量因子
  - value_factor.py    : 估值因子（简单 PE proxy）
"""

__all__ = ['momentum_factor', 'value_factor']
