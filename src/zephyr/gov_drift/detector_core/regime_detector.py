# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md
# [MODULE] zephyr.gov_drift.detector_core.regime_detector
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] MOD-GATE_ENGINE;MOD-INF-021;MOD-INF-020
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/_domain-governance/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_behavioral_auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: regime_detector.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: MacroFactor, MacroRegime, FactorSignal
#   desc: 数据契约/异常/枚举声明共 3 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（3 类）
#   name_en: data classes
#   intro: MacroFactor, MacroRegime, FactorSignal
#   downstream: MOD-GATE_ENGINE;MOD-INF-021;MOD-INF-020
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from enum import Enum
from typing import Final

from pydantic import BaseModel


class MacroFactor(str, Enum):
    ECONOMIC_GROWTH = "ECONOMIC_GROWTH"
    MONETARY_POLICY = "MONETARY_POLICY"
    INFLATION = "INFLATION"
    CREDIT_CONDITIONS = "CREDIT_CONDITIONS"
    RISK_APPETITE = "RISK_APPETITE"


class MacroRegime(str, Enum):
    EXPANSION = "EXPANSION"
    STAGFLATION = "STAGFLATION"
    TIGHTENING = "TIGHTENING"
    CRISIS = "CRISIS"


class FactorSignal(BaseModel):
    factor: MacroFactor
    indicator: str
    current_value: str = ""


MACRO_INDICATORS: Final[dict[MacroFactor, FactorSignal]] = {
    MacroFactor.ECONOMIC_GROWTH: FactorSignal(
        factor=MacroFactor.ECONOMIC_GROWTH,
        indicator="PMI / GDP nowcast / 工业用电",
    ),
    MacroFactor.MONETARY_POLICY: FactorSignal(
        factor=MacroFactor.MONETARY_POLICY,
        indicator="Fed Funds / 央行资产负债表 / 利率期货隐含概率",
    ),
    MacroFactor.INFLATION: FactorSignal(
        factor=MacroFactor.INFLATION,
        indicator="CPI/PCE + TIPS盈亏平衡 + 商品指数",
    ),
    MacroFactor.CREDIT_CONDITIONS: FactorSignal(
        factor=MacroFactor.CREDIT_CONDITIONS,
        indicator="HY-OAS / IG spread / CDX",
    ),
    MacroFactor.RISK_APPETITE: FactorSignal(
        factor=MacroFactor.RISK_APPETITE,
        indicator="VIX term structure / SKEW / 资金流动",
    ),
}

REGIME_ALLOCATIONS: Final[dict[MacroRegime, str]] = {
    MacroRegime.EXPANSION: "Momentum + Growth + SmallCap",
    MacroRegime.STAGFLATION: "Commodities + Quality + LowVol",
    MacroRegime.TIGHTENING: "Cash + ShortDuration + Defense",
    MacroRegime.CRISIS: "Cash + Gold + Volatility long",
}

REGIME_SWITCH_SIGNALS: Final[list[str]] = [
    "PMI crossing 50",
    "Credit spread widening > 200bp",
    "VIX > 30 sustained > 5d",
    "Fed rate direction change",
]
