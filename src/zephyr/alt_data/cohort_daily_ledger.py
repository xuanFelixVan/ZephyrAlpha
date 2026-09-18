# [BLUEPRINT] MOD-L00-004 | docs/_working/residual_construction/wo5_cohort_ledger_workbook.md §2/§4
# [MODULE] zephyr.alt_data.cohort_daily_ledger
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry; schemas.categories.cohort_daily_ledger; stdlib; pandas
# [CONSUMERS] cohort_ledger_daily 调度任务(二期接线,deps=[money_flow_incremental,margin_trading_incremental,dragon_tiger_incremental,block_trade_incremental]);
#   next_day_forecaster 特征集(二期); 老蔡对账 e4_cohort_reconciliation.md(一期)
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 五人群日频聚合器——只读 CH(禁写任何生产表,一期 CH insert 归总统筹批);
#              build_cohort_daily 纯计算返回行不落库; 金额单位=万元(裁定S4,源表元口径折算);
#              state 一期纯规则阈值=0(裁定S3,禁语义态); 缺源/滞后日降级 proxy_source=missing 不抛;
#              PIT=trade_date 仅用 ≤当日收盘数据; 表名经 TableRegistry 派生(#ARCH-CH-024 禁硬编码);
#              SQL 全部集中为 _SQL_* 模板常量(§5.160.2); 产出行结构与
#              schemas.categories.cohort_daily_ledger INSERT_COLUMNS 一一对应(禁复制列名)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单源查询失败/空数据->该 metric 降级 proxy_source=missing 行,不拖垮其他人群
# [TESTS] tests/alt_data/test_cohort_daily_ledger.py
# [A_module] module_id=MOD-DATA-COHORT-LEDGER-BUILDER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""CohortDailyLedger — 五人群（投资者行为）日频聚合器，WO-5 一期结算层.

施工真源：docs/_working/residual_construction/wo5_cohort_ledger_workbook.md
（§2 六向台账原料表 + §3 Schema 裁定 S1-S4 + §4 一期验收/老蔡对账）。

人群位 -> 数据源（全部已落库，零新数据依赖）：
    retail      money_flow.small_net_inflow（等权求和+截面中位数，万元）
                + alt_stock_comment.attention_index 中位数（独立 metric）
    leverage    margin_trading 融资买入额合计 + 融资余额日变化（对前一交易日）
    hot_money   dragon_tiger net_buy 合计（detail 记申万板块分布 top3）
                + dragon_tiger_seat 席位行数 + daban_board_event 当日 max(consec_limit)
    inst_config block_trade 当日合计金额（万元）+ 折价率均值
                （折价率 = 1 - price/当日 kline_daily close，JOIN 算，%）
    industry    一期留行位不产出（长尾 M-8，增减持/回购公告表未盘点）

一期定位=结算层（盘后日频，回测唯一真源，裁定 S2）：build_cohort_daily 纯计算，
禁写库；CH insert 主路径归总统筹批。已知代理偏差逐行 bias_note 强制标注
（红蓝预登记：机构拆单藏单偏差缓解纪律）。

CLI（对账/抽查用，零写库）：
    python -m zephyr.alt_data.cohort_daily_ledger --sample 2026-09-16
"""

from __future__ import annotations

import argparse
import datetime
import decimal
import io
import json
import logging
from typing import Final, Any

import pandas as pd

from zephyr.data.table_registry import get_registry

from schemas.categories.cohort_daily_ledger import (
    COHORT_HOT_MONEY,
    COHORT_INST_CONFIG,
    COHORT_LEVERAGE,
    COHORT_RETAIL,
    PROXY_MISSING,
    STATE_NET_NEG,
    STATE_NET_POS,
    STATE_NEUTRAL,
)

log = logging.getLogger(__name__)

# noqa: m11-perm-manual-legitimate  一期结算层真接口=build_cohort_daily(库函数,二期由总统筹接线cohort_ledger_daily事件任务); --sample CLI 仅为对账/审计人工面(对账报告 e4_cohort_reconciliation.md 即其产物),非生产触发路径
__all__: Final = ["build_cohort_daily", "main"]

# 表名唯一真源（#ARCH-CH-024：禁硬编码，TableRegistry 派生全限定名）
_TBL = get_registry()
TBL_MONEY_FLOW = _TBL.table("market_money_flow")
TBL_STOCK_COMMENT = _TBL.table("market_alt_stock_comment")
TBL_MARGIN = _TBL.table("market_margin_trading")
TBL_DRAGON = _TBL.table("market_dragon_tiger")
TBL_DRAGON_SEAT = _TBL.table("market_dragon_tiger_seat")
TBL_DABAN = _TBL.table("market_daban_board_event")
TBL_BLOCK_TRADE = _TBL.table("market_block_trade")
TBL_KLINE_DAILY = _TBL.table("market_kline_daily")
TBL_INDUSTRY = _TBL.table("market_industry_class")

# SQL 模板常量集中化（NO-BARE-SQL 豁免：_SQL_* 前缀约定，对齐 ch_reader）
_SQL_MONEY_FLOW_SMALL = "SELECT small_net_inflow FROM {tbl} WHERE trade_date = '{day}'"
_SQL_ATTENTION = "SELECT attention_index FROM {tbl} WHERE trade_date = '{day}'"
_SQL_MARGIN_DATES = (
    "SELECT DISTINCT trade_date FROM {tbl} "
    "WHERE trade_date <= '{day}' ORDER BY trade_date DESC LIMIT 2"
)
_SQL_MARGIN_BUY = "SELECT margin_buy FROM {tbl} WHERE trade_date = '{day}'"
_SQL_MARGIN_BALANCE = "SELECT margin_balance FROM {tbl} WHERE trade_date = '{day}'"
_SQL_DRAGON_NET_BUY = "SELECT net_buy FROM {tbl} WHERE trade_date = '{day}'"
_SQL_DRAGON_SECTOR_TOP3 = (
    "SELECT ic.industry_sw AS sector_label, sum(d.net_buy) AS sector_net_buy "
    "FROM {tbl_dragon} AS d FINAL "
    "INNER JOIN {tbl_industry} AS ic FINAL "
    "ON d.symbol_canonical = ic.symbol_canonical "
    "WHERE d.trade_date = '{day}' AND ic.valid_to IS NULL AND ic.industry_sw != '' "
    "GROUP BY ic.industry_sw ORDER BY sector_net_buy DESC LIMIT 3"
)
_SQL_SEAT_COUNT = "SELECT count() AS cnt FROM {tbl} WHERE trade_date = '{day}'"
_SQL_DABAN_HEIGHT = (
    "SELECT count() AS cnt, max(consec_limit) AS hmax FROM {tbl} "
    "WHERE trade_date = '{day}' AND close_sealed = 1"
)
_SQL_BLOCK_JOIN = (
    "SELECT bt.amount AS amount, bt.price AS price, k.close AS kclose "
    "FROM {tbl_bt} AS bt FINAL "
    "INNER JOIN {tbl_k} AS k FINAL "
    "ON bt.symbol_canonical = k.symbol_canonical AND k.trade_date = bt.trade_date "
    "WHERE bt.trade_date = '{day}'"
)

# 一期产出的四人群（industry 留行位不产出，M-8）
_COHORTS: tuple[str, ...] = (COHORT_RETAIL, COHORT_LEVERAGE, COHORT_HOT_MONEY, COHORT_INST_CONFIG)

# 已知偏差短注（红蓝预登记缓解纪律：逐行 bias_note 强制标注）
_BIAS_RETAIL_FLOW = "机构算法拆单藏小单:系统性低估机构/高估散户"
_BIAS_RETAIL_ATTN = "股吧关注度代理,2026-09-11起无历史回补"
_BIAS_LEVERAGE = "融资盘追涨属性强,极端日失真"
_BIAS_HOT_MONEY = "龙虎榜只覆盖异动股;席位聚合活跃度不依赖身份分类(G5)"
_BIAS_INST = "大宗=机构存量调仓代理,非全部机构行为;ETF份额缺位(G4)"

# 口径单位（裁定 S4：金额一律万元；detail JSON 记单位）
_UNIT_WAN = "万元"
_UNIT_PCT = "%"
_UNIT_COUNT = "行"
_UNIT_BOARD = "板"
_UNIT_INDEX = "指数分"


def _q(v: float | None) -> decimal.Decimal:
    """float 安全转 Decimal(18,4)：None/NaN -> Decimal 0（缺值行降级用，不抛）。"""
    if v is None or v != v:
        return decimal.Decimal("0.0000")
    return decimal.Decimal(str(round(float(v), 4))).quantize(decimal.Decimal("0.0001"))


def _state(v: float | None) -> str:
    """一期状态规则（裁定 S3）：每 metric 阈值=0；缺值=中性。"""
    if v is None or v != v:
        return STATE_NEUTRAL
    if v > 0:
        return STATE_NET_POS
    if v < 0:
        return STATE_NET_NEG
    return STATE_NEUTRAL


def _row(day: str, cohort_id: str, metric_id: str, value: float | None, proxy_source: str,
         bias_note: str, detail: dict[str, Any]) -> dict[str, Any]:
    """构造一行长表记录（与 INSERT_COLUMNS 列序一一对应，不写库）。"""
    missing = proxy_source == PROXY_MISSING
    return {
        "trade_date": day,
        "cohort_id": cohort_id,
        "metric_id": metric_id,
        "metric_value": decimal.Decimal("0.0000") if missing else _q(value),
        "state": STATE_NEUTRAL if missing else _state(value),
        "proxy_source": proxy_source,
        "bias_note": bias_note,
        "detail": json.dumps({**detail, **({"missing": True} if missing else {})},
                             ensure_ascii=False, sort_keys=True, default=str),
    }


def _missing(day: str, cohort_id: str, metric_id: str, reason: str,
             bias_note: str = "", unit: str = _UNIT_WAN) -> dict[str, Any]:
    """缺源日降级行：如实标注 proxy_source=missing，metric_value=0（不抛）。"""
    return _row(day, cohort_id, metric_id, None, PROXY_MISSING, bias_note,
                {"unit": unit, "reason": reason})


def _query_df(reader: Any, sql: str, columns: list[str]) -> pd.DataFrame:
    """经 reader 执行查询（真源 ch_reader 自动 FINAL）转 DataFrame；空/失败返回空表。

    reader 抽象为本模块唯一数据面（单测以 fake reader 注入，同构口径）。
    单表查询不带 FINAL——由 ch_reader.inject_final 对 ReplacingMergeTree 自动注入；
    JOIN 查询自带 FINAL（置于表别名后，规避注入器"表名后直插"的语法冲突）。
    """
    try:
        tsv = reader.query(sql)
    except Exception as e:  # noqa: BLE001 — 缺源降级契约：单源失败不拖垮其他人群
        log.warning("cohort_daily_ledger 查询失败降级 missing: %s", e)
        return pd.DataFrame(columns=columns)
    if not tsv or not tsv.strip():
        return pd.DataFrame(columns=columns)
    try:
        return pd.read_csv(io.StringIO(tsv), sep="\t", header=None, names=columns,
                           na_values=["\\N", "NULL"], keep_default_na=True, dtype=str)
    except Exception as e:  # noqa: BLE001 — 解析失败同降级
        log.warning("cohort_daily_ledger TSV 解析失败降级 missing: %s", e)
        return pd.DataFrame(columns=columns)


def _col_float(df: pd.DataFrame, col: str) -> pd.Series:
    """字符串列转 float（\\N/空 -> NaN），供求和/中位数。"""
    if col not in df.columns or df.empty:
        return pd.Series(dtype=float)
    return pd.to_numeric(df[col].replace({"\\N": None, "NULL": None}), errors="coerce")


def _valid_day(day: str) -> str:
    """入库前日期格式校验（YYYY-MM-DD），兼防 SQL 注入。"""
    return datetime.date.fromisoformat(day).isoformat()


# ================= 人群聚合（每人群独立纯函数，可独立单测） =================

def _build_retail(day: str, reader: Any) -> list[dict[str, Any]]:
    """散户：小单净流入 全市场等权求和+截面中位数（万元）+ 关注指数中位数（独立 metric）。"""
    rows: list[dict[str, Any]] = []
    df = _query_df(reader, _SQL_MONEY_FLOW_SMALL.format(tbl=TBL_MONEY_FLOW, day=day),
                   ["small_net_inflow"])
    vals = _col_float(df, "small_net_inflow").dropna()
    if vals.empty:
        rows.append(_missing(day, COHORT_RETAIL, "net_inflow_sum", "money_flow_absent",
                             _BIAS_RETAIL_FLOW))
        rows.append(_missing(day, COHORT_RETAIL, "net_inflow_median", "money_flow_absent",
                             _BIAS_RETAIL_FLOW))
    else:
        src = f"{TBL_MONEY_FLOW}.small_net_inflow"
        rows.append(_row(day, COHORT_RETAIL, "net_inflow_sum", float(vals.sum()), src,
                         _BIAS_RETAIL_FLOW, {"unit": _UNIT_WAN, "samples": int(len(vals)),
                                             "method": "equal_weight_sum"}))
        rows.append(_row(day, COHORT_RETAIL, "net_inflow_median", float(vals.median()), src,
                         _BIAS_RETAIL_FLOW, {"unit": _UNIT_WAN, "samples": int(len(vals)),
                                             "method": "cross_section_median"}))
    # 注意力代理（独立 metric，源从 2026-09-11 起零积累，缺源如实 missing）
    dfa = _query_df(reader, _SQL_ATTENTION.format(tbl=TBL_STOCK_COMMENT, day=day),
                    ["attention_index"])
    av = _col_float(dfa, "attention_index").dropna()
    if av.empty:
        rows.append(_missing(day, COHORT_RETAIL, "attention_median", "alt_stock_comment_absent",
                             _BIAS_RETAIL_ATTN, _UNIT_INDEX))
    else:
        rows.append(_row(day, COHORT_RETAIL, "attention_median", float(av.median()),
                         f"{TBL_STOCK_COMMENT}.attention_index", _BIAS_RETAIL_ATTN,
                         {"unit": _UNIT_INDEX, "samples": int(len(av)),
                          "method": "cross_section_median"}))
    return rows


def _build_leverage(day: str, reader: Any) -> list[dict[str, Any]]:
    """杠杆：融资买入额合计 + 融资余额日变化（对前一交易日；源表单位=元折万元 S4）。"""
    dates = _query_df(reader, _SQL_MARGIN_DATES.format(tbl=TBL_MARGIN, day=day), ["trade_date"])
    if dates.empty:
        return [
            _missing(day, COHORT_LEVERAGE, "margin_buy_sum", "margin_trading_absent", _BIAS_LEVERAGE),
            _missing(day, COHORT_LEVERAGE, "margin_balance_delta", "margin_trading_absent", _BIAS_LEVERAGE),
        ]
    d0 = str(dates.iloc[0]["trade_date"])[:10]
    buy = _col_float(
        _query_df(reader, _SQL_MARGIN_BUY.format(tbl=TBL_MARGIN, day=d0), ["margin_buy"]),
        "margin_buy",
    ).dropna()
    if buy.empty:
        return [
            _missing(day, COHORT_LEVERAGE, "margin_buy_sum", "margin_buy_absent", _BIAS_LEVERAGE),
            _missing(day, COHORT_LEVERAGE, "margin_balance_delta", "margin_buy_absent", _BIAS_LEVERAGE),
        ]
    src = f"{TBL_MARGIN}.margin_buy/margin_balance"
    if d0 != day:
        # 源数据滞后(d0<day, 两融 T+1/断供): 账本行锚 day, 不冒名顶替, 如实 missing
        return [
            _missing(day, COHORT_LEVERAGE, "margin_buy_sum", f"margin_lag_latest={d0}", _BIAS_LEVERAGE),
            _missing(day, COHORT_LEVERAGE, "margin_balance_delta", f"margin_lag_latest={d0}", _BIAS_LEVERAGE),
        ]
    rows = [_row(day, COHORT_LEVERAGE, "margin_buy_sum", float(buy.sum()) / 1e4, src, _BIAS_LEVERAGE,
                 {"unit": _UNIT_WAN, "input_unit": "元", "samples": int(len(buy)),
                  "method": "equal_weight_sum_div_1e4"})]  # 源表单位=元,折万元(S4)
    if len(dates) < 2:
        rows.append(_missing(day, COHORT_LEVERAGE, "margin_balance_delta",
                             "margin_prev_day_absent", _BIAS_LEVERAGE))
        return rows
    d1 = str(dates.iloc[1]["trade_date"])[:10]
    bal_today = _col_float(
        _query_df(reader, _SQL_MARGIN_BALANCE.format(tbl=TBL_MARGIN, day=d0), ["margin_balance"]),
        "margin_balance",
    ).dropna()
    bal_prev = _col_float(
        _query_df(reader, _SQL_MARGIN_BALANCE.format(tbl=TBL_MARGIN, day=d1), ["margin_balance"]),
        "margin_balance",
    ).dropna()
    if bal_today.empty or bal_prev.empty:
        rows.append(_missing(day, COHORT_LEVERAGE, "margin_balance_delta",
                             "margin_balance_absent", _BIAS_LEVERAGE))
        return rows
    delta = (float(bal_today.sum()) - float(bal_prev.sum())) / 1e4
    rows.append(_row(day, COHORT_LEVERAGE, "margin_balance_delta", delta, src, _BIAS_LEVERAGE,
                     {"unit": _UNIT_WAN, "input_unit": "元", "prev_date": d1,
                      "method": "sum_delta_div_1e4"}))  # 源表单位=元,折万元(S4)
    return rows


def _build_hot_money(day: str, reader: Any) -> list[dict[str, Any]]:
    """游资：龙虎榜 net_buy 合计（detail 记申万板块分布 top3）+ 席位行数 + 连板高度。"""
    df = _query_df(reader, _SQL_DRAGON_NET_BUY.format(tbl=TBL_DRAGON, day=day), ["net_buy"])
    vals = _col_float(df, "net_buy").dropna()
    if vals.empty:
        return [
            _missing(day, COHORT_HOT_MONEY, "net_buy_sum", "dragon_tiger_absent", _BIAS_HOT_MONEY),
            _missing(day, COHORT_HOT_MONEY, "activity_count", "dragon_tiger_absent", _BIAS_HOT_MONEY, _UNIT_COUNT),
            _missing(day, COHORT_HOT_MONEY, "board_height_max", "daban_absent", _BIAS_HOT_MONEY, _UNIT_BOARD),
        ]
    # 板块分布 top3（申万行业 industry_class 桥接 symbol_canonical，名称全覆盖；
    # 880 板块轮动口径归二期游资转移矩阵件，G5 词表坑不依赖）
    top3: list[dict[str, Any]] = []
    dfs = _query_df(
        reader,
        _SQL_DRAGON_SECTOR_TOP3.format(tbl_dragon=TBL_DRAGON, tbl_industry=TBL_INDUSTRY, day=day),
        ["sector_label", "sector_net_buy"],
    )
    for i in range(len(dfs)):
        label = str(dfs.iloc[i]["sector_label"])
        nb = pd.to_numeric(pd.Series([dfs.iloc[i]["sector_net_buy"]]), errors="coerce").iloc[0]
        nb_wan = float(nb) / 1e4 if nb == nb else 0.0  # 源表单位=元,折万元(S4)
        top3.append({"sector": label if label and label != "nan" else "unknown",
                     "net_buy": _q(nb_wan)})
    src = f"{TBL_DRAGON}.net_buy"
    rows = [_row(day, COHORT_HOT_MONEY, "net_buy_sum", float(vals.sum()) / 1e4, src, _BIAS_HOT_MONEY,
                 {"unit": _UNIT_WAN, "input_unit": "元", "samples": int(len(vals)),
                  "method": "equal_weight_sum_div_1e4", "sector_top3": top3})]
    # 席位行数（聚合活跃度，不依赖身份分类——G5 词表坑绕行）
    n = _query_df(reader, _SQL_SEAT_COUNT.format(tbl=TBL_DRAGON_SEAT, day=day), ["cnt"])
    if n.empty or n.iloc[0]["cnt"] is None:
        rows.append(_missing(day, COHORT_HOT_MONEY, "activity_count", "dragon_tiger_seat_absent",
                             _BIAS_HOT_MONEY, _UNIT_COUNT))
    else:
        rows.append(_row(day, COHORT_HOT_MONEY, "activity_count", float(n.iloc[0]["cnt"]),
                         TBL_DRAGON_SEAT, _BIAS_HOT_MONEY,
                         {"unit": _UNIT_COUNT, "method": "seat_row_count"}))
    # 连板高度（daban_board_event 当日 max(consec_limit)，封住日链式计数）
    h = _query_df(reader, _SQL_DABAN_HEIGHT.format(tbl=TBL_DABAN, day=day), ["cnt", "hmax"])
    cnt_sealed = pd.to_numeric(h["cnt"], errors="coerce") if not h.empty else pd.Series(dtype=float)
    cnt_sealed = cnt_sealed.dropna()
    if cnt_sealed.empty or int(cnt_sealed.iloc[0]) == 0:
        # 当日无封板事件行: 板高 0 与无数据语义不同, 如实 missing(数据线回补后转正)
        rows.append(_missing(day, COHORT_HOT_MONEY, "board_height_max", "daban_absent",
                             _BIAS_HOT_MONEY, _UNIT_BOARD))
    else:
        rows.append(_row(day, COHORT_HOT_MONEY, "board_height_max", float(h.iloc[0]["hmax"]),
                         f"{TBL_DABAN}.consec_limit", _BIAS_HOT_MONEY,
                         {"unit": _UNIT_BOARD, "method": "max_consec_sealed"}))
    return rows


def _build_inst_config(day: str, reader: Any) -> list[dict[str, Any]]:
    """机构配置盘：大宗当日合计金额（万元）+ 折价率均值（1-price/close，%，正=折价）。"""
    df = _query_df(
        reader,
        _SQL_BLOCK_JOIN.format(tbl_bt=TBL_BLOCK_TRADE, tbl_k=TBL_KLINE_DAILY, day=day),
        ["amount", "price", "kclose"],
    )
    if df.empty:
        return [
            _missing(day, COHORT_INST_CONFIG, "block_amount_sum", "block_trade_absent", _BIAS_INST),
            _missing(day, COHORT_INST_CONFIG, "discount_rate_avg", "block_trade_absent", _BIAS_INST, _UNIT_PCT),
        ]
    amount = _col_float(df, "amount").dropna()
    rows: list[dict[str, Any]] = []
    src = f"{TBL_BLOCK_TRADE} JOIN {TBL_KLINE_DAILY}"
    if amount.empty:
        rows.append(_missing(day, COHORT_INST_CONFIG, "block_amount_sum", "block_amount_absent", _BIAS_INST))
    else:
        rows.append(_row(day, COHORT_INST_CONFIG, "block_amount_sum", float(amount.sum()) / 1e4, src,
                         _BIAS_INST, {"unit": _UNIT_WAN, "input_unit": "元",
                                      "samples": int(len(amount)),
                                      "method": "equal_weight_sum_div_1e4"}))
    price = _col_float(df, "price")
    close = _col_float(df, "kclose")
    disc = (1.0 - price / close) * 100.0
    disc = disc[(close > 0) & price.notna() & close.notna()].dropna()
    if disc.empty:
        rows.append(_missing(day, COHORT_INST_CONFIG, "discount_rate_avg", "kline_close_absent",
                             _BIAS_INST, _UNIT_PCT))
    else:
        rows.append(_row(day, COHORT_INST_CONFIG, "discount_rate_avg", float(disc.mean()), src,
                         _BIAS_INST, {"unit": _UNIT_PCT, "samples": int(len(disc)),
                                      "method": "mean_1_minus_price_over_close",
                                      "note": "正=折价,负=溢价"}))
    return rows


# ================= 主入口（纯计算，不写库） =================

def build_cohort_daily(day: str, reader: Any = None) -> list[dict[str, Any]]:
    """构建指定交易日的五人群账本行（长表，行=人群×指标）。

    Args:
        day: 业务交易日 YYYY-MM-DD（PIT：仅用 ≤当日收盘数据）。
        reader: CH 读取器（默认 zephyr.data.ch_reader；单测注入 fake reader）。

    Returns:
        行 dict 列表，键与 schemas.categories.cohort_daily_ledger.INSERT_COLUMNS 一一对应；
        industry 一期留行位不产出（M-8）。纯计算，禁写库——CH insert 归总统筹批。
    """
    day = _valid_day(day)
    if reader is None:
        from zephyr.data import ch_reader  # 延迟导入：单测无需 CH 连接
        reader = ch_reader
    rows: list[dict[str, Any]] = []
    for cohort in _COHORTS:
        builder = {
            COHORT_RETAIL: _build_retail,
            COHORT_LEVERAGE: _build_leverage,
            COHORT_HOT_MONEY: _build_hot_money,
            COHORT_INST_CONFIG: _build_inst_config,
        }[cohort]
        try:
            rows.extend(builder(day, reader))
        except Exception as e:  # noqa: BLE001 — 降级契约：单人群失败不拖垮整表
            log.exception("cohort %s 构建失败，整组降级 missing", cohort)
            rows.append(_missing(day, cohort, f"{cohort}_degraded", f"builder_error:{e}"))
    return rows


def main() -> None:
    """CLI：--sample 打印指定日全行 JSON（对账/抽查用，零写库）。"""
    ap = argparse.ArgumentParser(description="五人群投资者行为日账本聚合器（一期结算层,纯计算）")
    ap.add_argument("--sample", metavar="DAY", required=True,
                    help="业务交易日 YYYY-MM-DD，打印该日全行 JSON")
    args = ap.parse_args()
    rows = build_cohort_daily(args.sample)
    print(json.dumps(
        [{"trade_date": r["trade_date"], "cohort_id": r["cohort_id"], "metric_id": r["metric_id"],
          "metric_value": str(r["metric_value"]), "state": r["state"],
          "proxy_source": r["proxy_source"], "bias_note": r["bias_note"],
          "detail": json.loads(r["detail"])} for r in rows],
        ensure_ascii=False, indent=2,
    ))


if __name__ == "__main__":
    main()
