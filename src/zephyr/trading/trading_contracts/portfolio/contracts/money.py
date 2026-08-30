# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.trading.trading_contracts.portfolio.contracts.money
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.contracts.portfolio.money
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L00-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [DEPRECATED] 5.99.22/23 克隆收敛——canonical 真源已收敛至 zephyr.shared.contracts.portfolio.money；本文件为向后兼容过渡 re-export 层，全量消费者改指真源后删除
# [TTL] task_bound
"""
过渡兼容层（DEPRECATED）—— Money 契约 canonical 真源已收敛至 shared 侧。

5.99.22/5.99.23 治本：本文件原与
``src/zephyr/shared/contracts/portfolio/money.py`` 是 60 行 diff 的克隆副本
（仅头部 + CurrencyCode 导入方式 + error_code 不同），5 处 raise 全同。
裁定 canonical = shared 侧（无依赖 + shared 是契约真源位置）。

本文件现在只做具名 re-export，保持旧 import 路径可用：

- ``Money`` / ``MoneyPrecisionError`` / ``MoneyCurrencyMismatchError`` /
  ``get_currency_precision`` —— 真源在 shared 侧
- ``CurrencyCode`` —— 由 shared 侧 money 模块的 PEP 562 ``__getattr__``
  惰性解析到 ``zephyr.trading.trading_contracts.market.instrument``

注意：异常类的 ``error_code`` 以真源为准（ZA-SH-0031/ZA-SH-0032），
原 trading 侧副本的 ZA-TR-0002/ZA-TR-0003 随克隆消除退役。

新代码 MUST 直接 import 真源：``zephyr.shared.contracts.portfolio.money``。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: money.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 CurrencyCode, Money, MoneyCurrencyMismatchError, MoneyPrecisionError, get_c…
#   desc: __init__ import L0；__all__ 5 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（5 符号）
#   name_en: __all__
#   intro: CurrencyCode, Money, MoneyCurrencyMismatchError, MoneyPrecisionError, get_curre…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.shared.contracts.portfolio.money import (
    CurrencyCode,
    Money,
    MoneyCurrencyMismatchError,
    MoneyPrecisionError,
    get_currency_precision,
)

__all__ = [
    "CurrencyCode",
    "Money",
    "MoneyCurrencyMismatchError",
    "MoneyPrecisionError",
    "get_currency_precision",
]
