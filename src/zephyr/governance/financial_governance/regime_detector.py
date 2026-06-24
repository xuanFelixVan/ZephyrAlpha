# [BLUEPRINT] SRC-040 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.regime_detector
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.financial_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_regime_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

from __future__ import annotations

from enum import Enum

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


MACRO_INDICATORS: dict[MacroFactor, FactorSignal] = {
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

REGIME_ALLOCATIONS: dict[MacroRegime, str] = {
    MacroRegime.EXPANSION: "Momentum + Growth + SmallCap",
    MacroRegime.STAGFLATION: "Commodities + Quality + LowVol",
    MacroRegime.TIGHTENING: "Cash + ShortDuration + Defense",
    MacroRegime.CRISIS: "Cash + Gold + Volatility long",
}

REGIME_SWITCH_SIGNALS: list[str] = [
    "PMI crossing 50",
    "Credit spread widening > 200bp",
    "VIX > 30 sustained > 5d",
    "Fed rate direction change",
]
