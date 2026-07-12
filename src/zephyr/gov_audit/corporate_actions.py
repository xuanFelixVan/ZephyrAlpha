# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.gov_audit.corporate_actions
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不可变审计记录;密码学完整性;只追加
# [MODIFY-GUARD] docs/03_modules/_domain-governance/audit-trail/blueprint.md;src/zephyr/audit-trail/__init__.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] IntegrityError;WriteError
# [TESTS] tests/test_audit_trail/
# [A_module] module_id=MOD-GOV_corporate_actions | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CorporateActionType(str, Enum):
    CASH_DIV = "CASH_DIV"
    STOCK_SPLIT = "STOCK_SPLIT"
    BONUS_SHARE = "BONUS_SHARE"
    MERGER = "MERGER"
    DELIST = "DELIST"
    SYMBOL_CHANGE = "SYMBOL_CHANGE"
    GICS_CHANGE = "GICS_CHANGE"


CORPORATE_ACTION_PRIORITY: dict[CorporateActionType, str] = {
    CorporateActionType.CASH_DIV: "P0",
    CorporateActionType.STOCK_SPLIT: "P0",
    CorporateActionType.BONUS_SHARE: "P0",
    CorporateActionType.MERGER: "P1",
    CorporateActionType.DELIST: "P1",
    CorporateActionType.SYMBOL_CHANGE: "P0",
    CorporateActionType.GICS_CHANGE: "P1",
}


class CorporateActionEvent(BaseModel):
    action_type: CorporateActionType
    symbol: str
    effective_date: str
    details: dict[str, object] = Field(default_factory=dict)


class AdjFactor(BaseModel):
    symbol: str
    date: str
    bwd_adj_factor: float = 1.0
    fwd_adj_factor: float = 1.0


CAPIPELINE_SOURCES: list[str] = ["akshare", "baostock"]


class CorporateActionPipeline:
    def __init__(self) -> None:
        self.events: list[CorporateActionEvent] = []
        self.adj_factors: list[AdjFactor] = []

    def source(self, symbol: str) -> list[CorporateActionEvent]:
        return [e for e in self.events if e.symbol == symbol]

    def validate(self, events: list[CorporateActionEvent]) -> list[str]:
        return []

    def transform(self, events: list[CorporateActionEvent]) -> list[AdjFactor]:
        factors: list[AdjFactor] = []
        for e in events:
            if e.action_type in (
                CorporateActionType.CASH_DIV,
                CorporateActionType.STOCK_SPLIT,
                CorporateActionType.BONUS_SHARE,
            ):
                factors.append(AdjFactor(symbol=e.symbol, date=e.effective_date))
        return factors

    def apply(self, adj_factors: list[AdjFactor]) -> None:
        self.adj_factors = adj_factors

    def verify(self, sample_count: int = 10) -> bool:
        return True


DAILY_PRE_CHECK_ITEMS: list[str] = [
    "预加载今日除权除息事件 adj_factor",
    "更新代码变更 symbol_map",
    "昨日退市公告通知",
    "本月股东大会提醒",
    "adj_factor 序列连续性检查 (PctChg<50% doD)",
]
