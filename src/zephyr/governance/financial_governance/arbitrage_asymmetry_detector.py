# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.financial_governance.arbitrage_asymmetry_detector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 套利不对称检测不可跳过;自动平仓必须可用
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_arbitrage_asymmetry_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Arbitrage Asymmetry Detector — v0.11.0 跨交易所套利不对称检测器。
"""

from __future__ import annotations


class ArbitrageAsymmetryDetector:
    def detect(self, prices: dict[str, dict[str, float]], threshold_pct: float = 0.5) -> list[dict]:
        opportunities = []
        exchanges = list(prices.keys())
        for i, a in enumerate(exchanges):
            for b in exchanges[i + 1 :]:
                for symbol in set(prices[a].keys()) & set(prices[b].keys()):
                    pa = prices[a][symbol]
                    pb = prices[b][symbol]
                    spread = abs(pa - pb) / min(pa, pb) * 100
                    if spread > threshold_pct:
                        opportunities.append({"a": a, "b": b, "symbol": symbol, "spread_pct": round(spread, 2)})
        return opportunities
