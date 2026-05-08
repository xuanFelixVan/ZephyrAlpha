"""Economic Guard — D-022-03 经济护栏。单次操作成本上限 + 24h累计成本上限 + 熔断。"""
from __future__ import annotations

class EconomicGuard:
    MAX_SINGLE_COST=5.0
    MAX_DAILY_COST=50.0

    def __init__(self):
        self._daily_total=0.0

    def check_single(self, estimated_cost:float)->tuple[bool,str]:
        if estimated_cost>self.MAX_SINGLE_COST:
            return False,f"Single cost {estimated_cost} > {self.MAX_SINGLE_COST}"
        if self._daily_total+estimated_cost>self.MAX_DAILY_COST:
            return False,f"Daily budget exceeded: {self._daily_total+estimated_cost} > {self.MAX_DAILY_COST}"
        self._daily_total+=estimated_cost
        return True,"OK"

    def daily_consumed(self)->float:
        return self._daily_total

    def reset_daily(self):
        self._daily_total=0.0
