# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.financial_governance.strategy_portfolio
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.financial_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: max_vol 参数
#   fields: 参数 max_vol，类型注解 float
#   code: strategy_portfolio.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: signal_decay 参数
#   fields: 参数 signal_decay，类型注解 float
#   code: strategy_portfolio.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: liq_util 参数
#   fields: 参数 liq_util，类型注解 float
#   code: strategy_portfolio.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: impact_ratio 参数
#   fields: 参数 impact_ratio，类型注解 float
#   code: strategy_portfolio.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① estimate_capacity
#   name_en: estimate_capacity
#   intro: estimate_capacity(max_vol, signal_decay, liq_util, impact_r…
#   desc: 源码 L82-L83
#   inputs: max_vol signal_decay liq_util impact_ratio
#   outputs: float
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

from enum import Enum


class StrategyMethod(str, Enum):
    ONE_OVER_N = "1/N"
    RISK_PARITY = "RiskParity"
    KELLY = "Kelly"
    MAX_DD_LIMIT = "MaxDDLimit"


class RetirementTrigger(str, Enum):
    SHARPE_12M_NEGATIVE = "Sharpe 12m < 0"
    CALMAR_12M_LOW = "Calmar 12m < 0.3"
    SIX_MONTH_NEGATIVE = "6-month consecutive negative"


def estimate_capacity(max_vol: float, signal_decay: float, liq_util: float, impact_ratio: float) -> float:
    return min(signal_decay, liq_util * impact_ratio) * max(10_000_000, max_vol)
