# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.governance.base
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.factor.base
# [CONSUMERS] zephyr.governance.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_base | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
ZephyrAlpha — governance.base re-export shim.

Phase 2 P1-b 修复（M05 文件复制对）：原文件是 codegen OCP-001 误放到 governance 根的
FactorBase/FactorMeta 副本（与 zephyr/factor/base.py 93.2% AST 相似度）。
canonical 真源为 zephyr.factor.factor_base（D_FACTOR 域，production），本文件改为 re-export shim
保留 zephyr.governance.__init__ 的导入兼容性，消除文件复制违规。

5.143.6 修复：SSoT 从 factor.base 改为 factor.factor_base (factor.base 现为 shim),
消除 FactorBase 签名冲突 (compute(self)->list[FactorSignal] vs compute(self,data,**kwargs)->pd.Series)

SSoT: zephyr.factor.factor_base（D_FACTOR 域, production）
"""

from zephyr.factor.factor_base import FactorBase, FactorMeta

__all__ = ["FactorBase", "FactorMeta"]
