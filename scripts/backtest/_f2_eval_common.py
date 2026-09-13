#!/usr/bin/env python
# [BLUEPRINT] MOD-BT-033 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest._f2_eval_common
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.factor.fundamentals
# [CONSUMERS] eval_f2_fundamental_ic.py; eval_f2_layers_styles.py; eval_f2_narrow_backtest.py（F2 出证三件公共装载）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] PIT as-of 装载口径唯一真源：面板=financial_derived FINAL 哨兵过滤+同键最新公告版本；
#              价格=kline_daily 收盘；日历=kline_daily 交易日 distinct；
#              FUNCTION-DUP 防重复：三出证器共享本模块，禁止各自复制装载器
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 数据缺失->RuntimeError
# [TESTS] 消费方 CLI --check / tests/factor/test_fundamentals.py 面板语义
# [TTL] permanent
"""_f2_eval_common — F2 出证三件公共装载器（面板/再平衡价格/交易日历）。

消费端 F2 出证脚本（IC/分层/窄回测）共享的 PIT 装载口径唯一实现
（FUNCTION-DUP 门禁治本：装载器单拷贝，语义变更一处生效）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
for _p in (str(ROOT / "src"), str(ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from zephyr.data import ch_reader  # noqa: E402
from zephyr.data.table_registry import get_registry  # noqa: E402

# 表名走 TableRegistry 真源（#ARCH-CH-024，禁硬编码）
_TBL_KLINE_DAILY = get_registry().table("market_kline_daily")
_TBL_KLINE_INDEX = get_registry().table("market_index_kline")
_TBL_FIN_DERIVED = get_registry().table("fund_financial_derived")

_FACTOR_COLS = [
    "fq01_accrual", "fq02_cash_conversion", "fq03_gpoa", "fq04_delta_roe_q",
    "gr01_rev_q_yoy", "gr02_np_q_qoq", "fq05_info_quality", "fq06_fscore",
]


_SQL_CAL = (
    "SELECT DISTINCT trade_date FROM " + _TBL_KLINE_DAILY + " "
    "WHERE trade_date >= '{start}' AND trade_date <= '{end}' ORDER BY trade_date FORMAT TSV"
)
_SQL_PANEL = (
    "SELECT {cols} FROM " + _TBL_FIN_DERIVED + " FINAL "
    "WHERE announce_date > toDate('1970-01-02') "
    "ORDER BY symbol, report_period, announce_date"
)
_SQL_PRICES = (
    "SELECT trade_date, symbol, toFloat64(close) AS close FROM " + _TBL_KLINE_DAILY + " "
    "WHERE trade_date IN ({quoted})"
)


def is_month_end(d: str, cal: list[str]) -> bool:
    """日历内下一交易日是否跨月（月末日判定）。"""
    i = cal.index(d)
    nxt = cal[i + 1] if i + 1 < len(cal) else None
    return nxt is None or nxt[:7] != d[:7]


def ch_reader_cal(start: str = "2019-01-01", end: str = "2026-09-11") -> list[str]:
    """交易日历（kline_daily distinct，升序 iso str 列表）。"""
    tsv = ch_reader.query(_SQL_CAL.format(start=start, end=end))
    return [line.strip() for line in (tsv or "").split("\n") if line.strip()]


def load_factor_panel() -> pd.DataFrame:
    """派生面板 → 因子面板（每 (symbol, report_period) 一行=最新公告版本，含 total_shares）。"""
    from zephyr.factor import fundamentals as F  # ORPHAN-CONSUMER: 直连导入

    cols = ("symbol, report_period, announce_date, accrual_ttm, np_ttm, ocf_ttm, total_assets, "
            "gpoa_ttm, np_q, equity_incl_minority, rev_q_yoy, np_q_qoq, accounts_receivable, "
            "rev_ttm, eff_tax_rate_ttm, total_liabilities, total_current_assets, "
            "total_current_liabilities, total_shares, gross_margin_q")
    tsv = ch_reader.query(_SQL_PANEL.format(cols=cols))
    if not tsv or not tsv.strip():
        raise RuntimeError("financial_derived 无数据")
    rows = [line.split("\t") for line in tsv.strip().split("\n")]
    names = cols.split(", ")
    df = pd.DataFrame(rows, columns=names)
    for c in df.columns:
        if c not in ("symbol", "report_period", "announce_date"):
            df[c] = pd.to_numeric(df[c].replace("\\N", np.nan), errors="coerce")
    # 同报告期多公告版本 → 取最新公告版本（FINAL 后仍可能多版本行）
    df = df.sort_values(["symbol", "report_period", "announce_date"]).drop_duplicates(
        subset=["symbol", "report_period"], keep="last")
    panel = df.set_index(["symbol", "report_period"]).sort_index()
    panel["fq01_accrual"] = F.fq01_accrual(panel["accrual_ttm"])
    panel["fq02_cash_conversion"] = F.fq02_cash_conversion(
        panel["np_ttm"], panel["ocf_ttm"], panel["total_assets"])
    panel["fq03_gpoa"] = F.fq03_gpoa(panel["gpoa_ttm"])
    panel["fq04_delta_roe_q"] = F.fq04_delta_roe_q(panel["np_q"], panel["equity_incl_minority"])
    panel["gr01_rev_q_yoy"] = F.gr01_rev_q_yoy(panel["rev_q_yoy"])
    panel["gr02_np_q_qoq"] = F.gr02_np_q_qoq(panel["np_q_qoq"])
    panel["fq05_info_quality"] = F.fq05_info_quality(
        panel["accounts_receivable"], panel["rev_ttm"], panel["eff_tax_rate_ttm"])
    panel["fq06_fscore"] = F.fq06_fscore(
        panel["np_ttm"], panel["ocf_ttm"], panel["total_assets"], panel["total_liabilities"],
        panel["total_current_assets"], panel["total_current_liabilities"], panel["total_shares"],
        panel["rev_ttm"], panel["gross_margin_q"])
    panel["announce_date"] = pd.to_datetime(panel["announce_date"])
    return panel[["announce_date", "total_shares"] + _FACTOR_COLS]


def load_rebalance_prices(dates: list[str]) -> pd.DataFrame:
    """指定交易日的全市场收盘价（再平衡日+前向收益日两套日期）。"""
    quoted = ",".join(f"'{d}'" for d in dates)
    tsv = ch_reader.query(_SQL_PRICES.format(quoted=quoted))
    rows = [line.split("\t") for line in (tsv or "").strip().split("\n") if line]
    return pd.DataFrame(rows, columns=["td", "symbol", "close"]).assign(
        close=lambda d: pd.to_numeric(d["close"], errors="coerce"))
