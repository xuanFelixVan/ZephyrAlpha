from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DataLeakCheck(str, Enum):
    C1_FACTOR_DATE_GT_MARKET = "C1_FACTOR_DATE_GT_MARKET"
    C2_TRAIN_TEST_OVERLAP = "C2_TRAIN_TEST_OVERLAP"
    C3_FUTURE_ACCESS_FACTOR_STORE = "C3_FUTURE_ACCESS_FACTOR_STORE"
    C4_FACTOR_ANALYSIS_FUTURE_IC = "C4_FACTOR_ANALYSIS_FUTURE_IC"
    C5_INTRA_GROUP_SIGNAL_EARLY = "C5_INTRA_GROUP_SIGNAL_EARLY"
    C6_EARNINGS_SPLIT_EX_POST = "C6_EARNINGS_SPLIT_EX_POST"


LEAK_CHECKS: dict[DataLeakCheck, str] = {
    DataLeakCheck.C1_FACTOR_DATE_GT_MARKET: "factor_date > market_date → NEVER",
    DataLeakCheck.C2_TRAIN_TEST_OVERLAP: "train < test — time ordering",
    DataLeakCheck.C3_FUTURE_ACCESS_FACTOR_STORE: "不可达 — future barrier",
    DataLeakCheck.C4_FACTOR_ANALYSIS_FUTURE_IC: "用历史IC only — look-forward prevention",
    DataLeakCheck.C5_INTRA_GROUP_SIGNAL_EARLY: "延后1日 — signal delay",
    DataLeakCheck.C6_EARNINGS_SPLIT_EX_POST: "ex-ante only —前瞻性保证",
}


class MarketRegime(str, Enum):
    BULL = "BULL"
    RANGE_BOUND = "RANGE_BOUND"
    BEAR = "BEAR"


FEATURE_STORE_SCHEMA: dict[str, str] = {
    "symbol": "TEXT NOT NULL",
    "date": "DATE NOT NULL",
    "factor_name": "TEXT NOT NULL",
    "value": "REAL",
    "computed_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    "pk": "PRIMARY KEY (symbol, date, factor_name)",
}
