# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.base
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.factor_base
# [CONSUMERS] zephyr.governance.base
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
ZephyrAlpha — factor.base re-export shim.

5.143.6 修复：原文件是 codegen OCP-001 生成的 FactorBase/FactorMeta 副本，
与 zephyr/factor/factor_base.py 签名冲突 (compute(self)->list[FactorSignal] vs
compute(self, data, **kwargs)->pd.Series)。factor_base.py 是实际被消费的 SSoT
(被 factor/__init__.py + value_factor.py + momentum_factor.py + signal_fundamental 使用)。
本文件改为 re-export shim 消除签名冲突，保留 governance/base.py 的间接导入兼容性。

SSoT: zephyr.factor.factor_base (D_FACTOR 域, production)
"""

from zephyr.factor.factor_base import FactorBase, FactorMeta

__all__ = ["FactorBase", "FactorMeta"]
