# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md
# [MODULE] zephyr.governance.drift_detector_core.regime_detector
# [DOMAIN] D_BEHAVIORAL_AUDIT
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
# [A_module] module_id=MOD-SEC_regime_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
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
