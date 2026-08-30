# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.risk.risk_metrics
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] risk; pf_core; pf_core; ops; l10-compliance
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODGEN:CTR-P1-011 ====

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: risk_metrics.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: RiskMetricsReport
#   desc: 数据契约/异常/枚举声明共 1 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（1 类）
#   name_en: data classes
#   intro: RiskMetricsReport
#   downstream: risk; pf_core; pf_core; ops; l10-compliance
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RiskMetricsReport:
    as_of_date: datetime
    beta: float
    calculation_method: str
    confidence_level: float
    current_drawdown: float
    cvar_1d_95: float
    cvar_1d_99: float
    idempotency_key: str
    lookback_period: int
    max_drawdown: float
    portfolio_id: str
    sharpe_ratio: float
    sortino_ratio: float
    var_1d_95: float
    var_1d_99: float
    volatility_1d: float
    volatility_1m: float
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-011 ====
