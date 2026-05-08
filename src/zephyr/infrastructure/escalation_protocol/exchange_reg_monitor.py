"""Exchange Reg Monitor — v0.11.0 交易所规则变更监控器。"""
from __future__ import annotations

class ExchangeRegMonitor:
    EXCHANGES=["SSE","SZSE","HKEX","NYSE","NASDAQ"]

    def register_change(self, exchange:str, rule_name:str, effective_date:str):
        return {"exchange":exchange,"rule":rule_name,"effective":effective_date,"requires_escalation":True}

    def list_exchanges(self)->list[str]:
        return self.EXCHANGES
