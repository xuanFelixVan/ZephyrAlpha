"""Arbitrage Asymmetry Detector — v0.11.0 跨交易所套利不对称检测器。"""
from __future__ import annotations

class ArbitrageAsymmetryDetector:
    def detect(self, prices:dict[str,dict[str,float]], threshold_pct:float=0.5)->list[dict]:
        opportunities=[]
        exchanges=list(prices.keys())
        for i,a in enumerate(exchanges):
            for b in exchanges[i+1:]:
                for symbol in set(prices[a].keys())&set(prices[b].keys()):
                    pa=prices[a][symbol]
                    pb=prices[b][symbol]
                    spread=abs(pa-pb)/min(pa,pb)*100
                    if spread>threshold_pct:
                        opportunities.append({"a":a,"b":b,"symbol":symbol,"spread_pct":round(spread,2)})
        return opportunities
