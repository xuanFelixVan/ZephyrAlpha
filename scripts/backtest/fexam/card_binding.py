# [BLUEPRINT] MOD-BT-248 | docs/03_modules/_domain_backtest/blueprint.md | §考试卡取数绑定层
# [MODULE] scripts.backtest.fexam.card_binding
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; yaml; stdlib(argparse/json/re/sys/pathlib/datetime);
#   scripts/backtest/fexam/ch_data（ch_query_df/table_columns，经 TableRegistry 表名真源）;
#   scripts/backtest/fexam/calibration_exam（run_card，判据零裁量面）
# [CONSUMERS] 矿考循环班 T1 考试车道批量开考（人工 CLI 触发）；
#   docs/_working/mineloop_campaign/ 绑定普查台账；tests/backtest/test_card_binding.py
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 本件只供数不改判——门柱/窗口/分桶全部从卡内读，零自创判据；
#   分类面（classify）零 CH 零写分数册，运行面（run）仅跑 --approve-list 点名卡；
#   绑不上/口径不齐/目标周期不符=如实 binding_unresolved 并计入普查，禁降级喂近似数据出分；
#   出分前后对卡面判据集做内容级断言（仅 status/lineage 允许变化），不一致即抛错且不改册（反挪门柱自闸）；
#   CH 让路窗（21:00–22:30 W1 v2 提前窗真源=docs/_working/examcard_campaign/00_campaign_ledger.md 20:55 段；
#   01:00–04:00 夜跑窗）内 run 面默认拒绝，须 --override-ch-window-with-reason 显式留痕；
#   分数册只经 run_card 的 only-add 追加，本件绝不直写 exam_scores_v1.yaml；
#   聚合去重口径 anyLast(argMax 同义) per day，禁把多版本原始行当唯一行（在册 30 倍放大事故）。
# [MODIFY-GUARD] 配方表 RECIPES 增删必须同步 tests/backtest/test_card_binding.py 的分类断言与拒绝路径用例
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 卡无 data_binding=归 class U（不抛，计入普查）；CH 不可达由 ch_data 抛 CHAccessError 上抛
#   （fail-closed，禁伪造空数据冒充分数）；signal 空/NaN 占比>0.5 → binding_rejected_quality 不出分；
#   判据集前后不一致 → BindingIntegrityError（整卡中止，分数册不动）
# [TESTS] tests/backtest/test_card_binding.py
# [A_module] module_id=MOD-BT-248 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  人工 CLI 批量开考驱动器（按需触发），非常驻自动系统
# create-guard-not-dup: 本件是考试卡 data_binding 段→执行器 signal/target 的唯一通用绑定层
#   （配方表+分类器+反挪门柱自闸），非 ch_data 装载层的第二实现、非 calibration_exam 判据核的第二实现——
#   前役两件 .runtime/tmp 一次性驱动器（run_exam_batch.py 硬编码 card_id→lambda、run_card_l209.py 单卡脚本）
#   由本件内收替代（根宪法 §4.1 净零：新增=替代旧临时件，临时件随 TTL 自然退役）。
"""card_binding — 考试卡取数绑定层（MOD-BT-248，矿考循环班 T1 主交付）。

背景：`calibration_exam.run_card` 明示"缺省 CH 取数面未接（signal_spec/target_spec 绑定属
W4 运行期配置）——请注入 signal/target 或先行落绑定册（防误绑数据面）"。卡面自立法起带
`data_binding` 段（signal_table/signal_column/signal_derivation/target_source/
data_window_evidence），但全仓零代码消费该段——本件补这一层。

两形：
  classify  只读卡，出绑定普查（class A/D 可绑候选 + class B/C/U 拒绝原因），零 CH 零分数写。
  run       只对 --approve-list 点名卡取数并调 run_card 出分；每张写绑定凭据（用的表/列/算子/SQL）。

分类判据（机判，禁自创）：
  A  series 单表单列 + 算子命中配方表（index/valuation/news/sector/csv）→ 可绑
  D  信号面=本仓已入库派生序列 CSV（广度七序列）→ 可绑（零 CH）
  B  panel 宽表 → 本班后置（去重与撮合口径须逐表面核，禁批量近似）
  C  target/derivation 需要重放引擎（NAV/window_metrics/权重帧/双臂 arm_protocol）→ 属 T3 实现面
  U  无 data_binding 段或表名解析失败 → 未冻结接线，不考
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from zephyr.data.table_registry import get_registry

HERE = Path(__file__).resolve().parent
RUN_ROOT = HERE.parents[2]
if str(RUN_ROOT / "scripts" / "backtest") not in sys.path:
    sys.path.insert(0, str(RUN_ROOT / "scripts" / "backtest"))

CARDS_DIR = RUN_ROOT / "docs" / "03_modules" / "_domain_backtest" / "exam_cards"
#: 本地派生序列根＝研究资产搬迁后的永久区真源（在册登记位 docs/04_research_records/_index/index.yaml
#: 的 `dir: mining/ledgers/nightmine_20261010/series`）。旧路 `docs/_working/nightmine_campaign/series`
#: 已随搬迁整目录删除，本件是 [TTL] permanent 件、禁引临时区（根宪法 §9.4），故不留候选位：
#: 留旧路作 fallback＝给已废止的临时区留活口，且"读到哪一根目录"从此无从在凭据面复现。
SERIES_DIR = RUN_ROOT / "docs" / "04_research_records" / "mining" / "ledgers" / "nightmine_20261010" / "series"

#: 表名面唯一真源=TableRegistry（品类 id 派生全限定名；业务代码禁字面量表名——TABLE-NAME-REGISTRY 门约束）
_TBL = {
    c: get_registry().table(c)
    for c in (
        "market_index_kline",
        "market_index_valuation_daily",
        "market_news_sentiment_window",
        "backtest_regime_state_anchored",
        "market_sector_kline_880",
    )
}

# §5.160.2 SQL 集中化面：全部参数化模板收本块 SQL_* 常量（AST 豁免面），函数体零裸 SQL；
# 表名一律经 _TBL 品类派生注入，禁字面量表名。
SQL_INDEX_NEXT_DAY = (
    "SELECT toDate(trade_date) AS d, anyLast(close) AS c FROM {tbl} WHERE symbol='{sym}' GROUP BY d ORDER BY d"
)
SQL_FACE_DAILY = "SELECT toDate({date_col}) AS d, anyLast({col}) AS v FROM {tbl} WHERE {where} GROUP BY d ORDER BY d"
SQL_DAILY_AGG = "SELECT toDate({time_col}{tz}) AS d, {agg}({col}) AS v FROM {tbl} GROUP BY d ORDER BY d"
SQL_SECTOR_TOP_N = (
    "SELECT d, sumIf(amt, rk <= {n}) / nullIf(sum(amt), 0) AS v FROM ("
    "SELECT d, code, amt, row_number() OVER (PARTITION BY d ORDER BY amt DESC) AS rk FROM ("
    "SELECT toDate(s.trade_date) AS d, s.sector_code AS code, anyLast(s.{col}) AS amt "
    "FROM {tbl} AS s WHERE s.period = {period} AND s.sector_code IN ("
    "SELECT sector_code FROM {map_table} WHERE code_family IN ({families})) "
    "GROUP BY d, code)) GROUP BY d ORDER BY d"
)
SQL_SECTOR_FAMILY_PANEL = (
    "SELECT toDate(s.trade_date) AS d, s.sector_code AS code, "
    "anyLast(s.{close_col}) AS close, anyLast(s.{amount_col}) AS amount "
    "FROM {tbl} AS s WHERE s.period = '{period}' AND s.sector_code IN ("
    "SELECT sector_code FROM {map_table} WHERE code_family IN ({families})) "
    "GROUP BY d, code ORDER BY d"
)
SQL_MACRO_SCISSORS = (
    "SELECT report_date, m1_yoy, m2_yoy FROM {tbl} WHERE m1_yoy IS NOT NULL AND m2_yoy IS NOT NULL ORDER BY report_date"
)
SQL_MARGIN_BALANCE = (
    "SELECT d, exchange, sum(v) AS bal FROM ("
    "SELECT toDate({date_col}) AS d, exchange, {symbol_col} AS sym, "
    "anyLast({col}) AS v FROM {tbl} WHERE exchange IS NOT NULL "
    "GROUP BY d, exchange, sym) GROUP BY d, exchange ORDER BY d"
)
SQL_INDEX_AMOUNT_SUM = (
    "SELECT toDate({date_col}) AS d, sum({col}) AS v FROM {tbl} "
    "WHERE symbol IN ({symbols}) GROUP BY d HAVING uniqExact(symbol) = {n_sym} ORDER BY d"
)
#: 绑定分类类号面（本件自有机判分类，与 governance_family 词表值 A-D 仅词法同形、语义无关：
#: A=单表单列可绑／D=本仓派生序列 CSV；F7 上下文豁免通道标注非复制语境）
_BINDABLE_CLASSES = ("A", "D")  # gate-vocab-context: governance_family
_CENSUS_CLASSES = ("A", "A?", "B", "C", "D", "U")  # gate-vocab-context: governance_family
SQL_DOWNSIDE_DEV = (
    "SELECT toDate({date_col}) AS d, anyLast({col}) AS v FROM {tbl} WHERE symbol='{sym}' GROUP BY d ORDER BY d"
)
#: 涨停面板日度聚合底座（卡 05/06 共用；卡面 signal_derivation 逐字冻结式，禁自创容差/门槛）：
#:   ret_close = close/lag(close)-1、ret_open = open/lag(close)-1（全部比值在后复权空间，卡面原文）；
#:   is_lu = ret_close >= limit_pct - {tol}；lag 缺失（新股首日/停牌无前一交易日）与 limit_pct 缺失
#:   （无涨跌幅限制）一律取哨兵值⇒永不判涨停，禁 inf/NULL 冒充；(日,票) 先 FINAL 去版本行。
SQL_LIMIT_UP_PANEL = (
    "WITH k AS ("
    "SELECT symbol AS sym, trade_date AS d, toFloat64(close) AS c, toFloat64(open) AS o "
    "FROM {hfq_tbl} FINAL WHERE trade_date >= '{lo}' AND trade_date <= '{hi}' AND c > 0 AND o > 0), "
    "l AS ("
    "SELECT symbol AS sym, trade_date AS d, toFloat64(ifNull(limit_pct, 9.9)) AS lp "
    "FROM {lim_tbl} FINAL WHERE trade_date >= '{lo}' AND trade_date <= '{hi}'), "
    "j AS ("
    "SELECT k.sym AS sym, k.d AS d, k.c AS c, k.o AS o, l.lp AS lp, "
    "lagInFrame(k.c, 1, 0) OVER (PARTITION BY k.sym ORDER BY k.d "
    "ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS lag_c "
    "FROM k INNER JOIN l ON k.sym = l.sym AND k.d = l.d), "
    "r AS ("
    "SELECT sym, d, lp, if(lag_c > 0, c / lag_c - 1, -99.0) AS ret_close, "
    "if(lag_c > 0, o / lag_c - 1, -99.0) AS ret_open FROM j), "
    "f AS (SELECT sym, d, ret_close, ret_open, if(ret_close >= lp - {tol}, 1, 0) AS lu FROM r), "
    "p AS ("
    "SELECT sym, d, ret_close, ret_open, lu, "
    "lagInFrame(lu, 1, 0) OVER (PARTITION BY sym ORDER BY d "
    "ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS lu_prev FROM f) "
    "SELECT d, countIf(lu = 1) AS n_lu, countIf(lu_prev = 1) AS n_lu_prev, "
    "countIf(lu = 1 AND lu_prev = 1) AS n_promo, avgIf(ret_close, lu_prev = 1) AS prem_close, "
    "avgIf(ret_open, lu_prev = 1) AS prem_open, count() AS n_rows "
    "FROM p GROUP BY d ORDER BY d"
)

#: 判据面键集（出分前后必须逐键内容相等；只允许 status/lineage 变化）
JUDGMENT_KEYS = (
    "card_id",
    "node_id",
    "family",
    "signal_kind",
    "window",
    "buckets",
    "pillars",
    "pillars_numeric",
    "target",
    "oos_window_ref",
    "hypothesis",
)

_TABLE_RE = re.compile(r"\b(?:c\d+|backtest)_[a-z0-9_]+\.[a-z0-9_]+", re.I)
_CSV_HINTS = {
    "limit_up_count": "limit_up_count.csv",
    "limit_down_count": "limit_down_count.csv",
    "blast_ratio": "blast_ratio.csv",
    "broken_board": "blast_ratio.csv",
    "seal_ratio": "seal_ratio.csv",
    "max_streak_height": "max_streak_height.csv",
    "net_breadth": "net_breadth.csv",
    "streak": "streak_distribution.csv",
    # 聚合 8 卡（挖矿二班，物化件=scripts/audit/agg8_series_materialize.py，agg8-v1）：
    # 信号侧 6 枚逐日市场面序列＋目标侧 2 枚前向序列，形制与上列在册 CSV 一致（trade_date,value）。
    "lu_count": "lu_count.csv",
    "lu_count_z20": "lu_count_z20.csv",
    "lu_ratio": "lu_ratio.csv",
    "lu_ratio_z20": "lu_ratio_z20.csv",
    "avg_abs_ret": "avg_abs_ret.csv",
    "avg_abs_ret_z20": "avg_abs_ret_z20.csv",
    "mkt_fwd5": "mkt_fwd5.csv",
    "mkt_fwd10": "mkt_fwd10.csv",
}


def load_named_series(name: str) -> pd.Series | None:
    """按卡面申报的序列名取在册本地序列（class D 同一装载口；未申报/缺件=None 交调用方 fail-closed）。"""
    key = str(name or "").strip()
    if not key:
        return None
    return _load_csv_series(_CSV_HINTS.get(key, f"{key}.csv"))


#: 目标面：执行器 _series_metrics 硬编码 shift(-1)=次日目标（在册缺口），故只允许次日指数收益
#: 措辞变体（csi300/沪深300/000300/宽基）一律归一，防分类尺自造假阴（11 张实测被漏，2 张实为指数次日收益）
_INDEX_TARGET_RE = re.compile(
    r"(next_day_index_return|next_day_csi300|csi300[_ ]?next|次日(指数|沪深\s*300|000300)?收益"
    r"|CSI\s*300\s*次日|000300\s*次日)",
    re.I,
)
_TARGET_FACE_KINDS = (
    ("engine_replay", re.compile(r"(NAV|window_metrics|daily_net_returns|权重帧|portfolio_return)", re.I)),
    ("panel_stock", re.compile(r"(个股|stock_return|hfq 收盘|car_|事件窗)", re.I)),
    ("sector_series", re.compile(r"(板块|sector)", re.I)),
    ("probability_hit", re.compile(r"(prob|hit|命中|概率|兑现率)", re.I)),
    ("emotion_state", re.compile(r"(emotion|情绪|六段|状态转移)", re.I)),
)
_HORIZON_RE = re.compile(r"next[_ ]?(?:[2-9]\d*|1\d|20|60|5|10)d|_([2-9]\d*)day|(\d+)\s*日前(收益)", re.I)
_MULTI_ARM_RE = re.compile(r"(arm_protocol|daily_net_returns|window_metrics|权重帧|NAV)", re.I)
_INDEX_SYMBOL = "000300"


class BindingIntegrityError(RuntimeError):
    """出分前后卡面判据集被改动=挪门柱形态，整卡中止。"""


def _declared_forward_face(card: dict) -> tuple[int | None, str | None]:
    """卡面多日前向面申报的绑定侧校核（与 calibration_exam._forward_face 同一形态，零复制判据）。

    返回 (horizon, err)：
      (None, None)  = 未申报 ⇒ 现行"指数次日收益"单面门槛逐字照旧（既有 178 张卡零影响）；
      (h, None)     = 成对申报且自洽 ⇒ 目标面这一环放行，**后续数据面门槛一概不放宽**
                      （配方册/滚动窗/z-score/多表复合照拦）；
      (None, err)   = 半申报/拼错/两处 horizon 不同值 ⇒ 照拦，reason 点名缺陷。
    本函数不引入任何阈值，只消费卡面冻结值（裁定#501/G4-5：门柱在数据前钉死，事后挪=作废）。
    """
    face = str(card.get("target_forward_face") or "").strip()
    hraw = card.get("target_horizon_days")
    if face == "" and hraw is None:
        return None, None
    if face != "precomputed":
        return None, f"declared_forward_face_bad_marker:{face[:24]}"
    if isinstance(hraw, bool) or not isinstance(hraw, int) or not 2 <= hraw <= 252:
        return None, f"declared_forward_face_bad_horizon:{str(hraw)[:12]}"
    primary = str((card.get("target") or {}).get("primary") or "")
    m = re.search(r"mkt_fwd(\d+)", primary)
    if not m:
        return None, "declared_forward_face_missing_mkt_fwd_tag"
    if int(m.group(1)) != hraw:
        return None, f"declared_forward_face_horizon_mismatch:{hraw}vs{m.group(1)}"
    return int(hraw), None


def _norm(df: pd.DataFrame, date_pos: int, val_pos: int) -> pd.Series:
    """ch_query_df 位置协议（列名 c1..cN、NULL=空串、dtype=str）⇒ 按列位取数＋to_numeric 强制。"""
    dates = pd.to_datetime(df.iloc[:, date_pos])
    vals = pd.to_numeric(df.iloc[:, val_pos], errors="coerce")
    s = pd.Series(vals.to_numpy(dtype=float), index=dates)
    s = s[~s.index.duplicated(keep="last")]
    return s.sort_index()


def index_next_day_return() -> pd.Series:
    """CSI300 日收益（runner 侧 shift(-1) 前向；t→t+1 PIT 由执行器负责）。"""
    from fexam.ch_data import ch_query_df

    df = ch_query_df(SQL_INDEX_NEXT_DAY.format(tbl=_TBL["market_index_kline"], sym=_INDEX_SYMBOL))
    close = _norm(df, 0, 1)
    return (close / close.shift(1) - 1.0).dropna()


def _load_csv_series(fname: str) -> pd.Series | None:
    p = SERIES_DIR / fname
    if not p.exists():
        return None
    df = pd.read_csv(p, index_col=0, parse_dates=True)
    col = "value" if "value" in df.columns else df.columns[0]
    return df[col].astype(float)


def tables_of(text: str) -> list[str]:
    return sorted({t.lower() for t in _TABLE_RE.findall(text or "")})


def _card_text(card: dict) -> str:
    b = card.get("data_binding") or {}
    if not isinstance(b, dict):
        return ""
    return " ".join(str(b.get(k, "")) for k in ("signal_table", "signal_column", "signal_derivation", "target_source"))


def _target_face_kind(text: str) -> str:
    """目标面分型（供普查给出"缺什么"的可执行清单，而非一句"绑不上"）。"""
    for name, rx in _TARGET_FACE_KINDS:
        if rx.search(text or ""):
            return name
    return "other"


def classify_card(card: dict) -> dict:
    """机判绑定分类；返回 {cls, reason, recipe, op, tables}（零 CH）。"""
    b = card.get("data_binding")
    if not isinstance(b, dict) or not b.get("signal_table"):
        return {"cls": "U", "reason": "no_data_binding_section", "recipe": None, "op": None, "tables": []}
    blob = _card_text(card)
    tl = tables_of(str(b.get("signal_table")))
    arm_hit = bool(_MULTI_ARM_RE.search(blob))
    kind = card.get("signal_kind")
    tgt = str(b.get("target_source") or "")
    primary_txt = str((card.get("target") or {}).get("primary") or "")
    fwd_h, fwd_err = _declared_forward_face(card)
    if fwd_err:
        return {
            "cls": "C",
            "reason": fwd_err,
            "recipe": None,
            "op": None,
            "tables": tl,
            "declared_horizon": card.get("target_horizon_days"),
        }
    # 已申报且自洽 ⇒ horizon 扫描先摘掉被申报的 mkt_fwd<h> 记号，其余多日措辞照拦（不弱化）。
    horizon_src = primary_txt if fwd_h is None else re.sub(r"mkt_fwd\d+", " ", primary_txt)
    horizon = _HORIZON_RE.search(horizon_src)
    if fwd_h is None and not _INDEX_TARGET_RE.search(tgt) and not _INDEX_TARGET_RE.search(primary_txt):
        return {
            "cls": "C",
            "reason": "target_face_not_index_next_day",
            "recipe": None,
            "op": None,
            "tables": tl,
            "target_face_kind": _target_face_kind(str((card.get("target") or {}).get("primary") or "") + " " + tgt),
        }
    if horizon:
        return {
            "cls": "C",
            "reason": f"executor_horizon_mismatch:{horizon.group(0)}",
            "recipe": None,
            "op": None,
            "tables": tl,
        }
    if arm_hit:
        return {
            "cls": "C",
            "reason": "needs_replay_engine(NAV/window_metrics/双臂 arm_protocol)",
            "recipe": None,
            "op": None,
            "tables": tl,
        }
    if kind == "panel":
        return {
            "cls": "B",
            "reason": "panel_deferred(去重/撮合口径须逐表面核)",
            "recipe": None,
            "op": None,
            "tables": tl,
        }
    # class D：信号面=本仓已入库派生序列 CSV（只认 signal_column 精确名或 derived_series 声明，
    #           禁全文关键词匹配——曾把 margin_flow 卡误牵到连板分布序列＝误绑形态）
    col_raw = str(b.get("signal_column") or "").strip()
    declared = str(b.get("derived_series") or "").strip()
    for hint, fname in _CSV_HINTS.items():
        exact = col_raw == hint or declared == hint
        # 卡面申报 `<hint>_derived`（导生口径）而本仓只有母序列 CSV＝名称回落：
        # 绑的是母序列、口径并未换。该事实以前只存在于代码分支里（卡面/册面/码面三面均无声明），
        # 令平行卡与母卡读同一枚序列在分数册上读不出来（⑨席 08 班 修⑪）。本层不改变绑定结果，
        # 只把它如实写进机判输出（观测面，非判据；不改 |corr| 阈值、不挪门柱、不禁绑）。
        alias = (not exact) and col_raw.startswith(hint + "_derived")
        if exact or alias:
            if (SERIES_DIR / fname).exists():
                out: dict[str, Any] = {
                    "cls": "D",
                    "reason": None,
                    "recipe": "local_series_csv",
                    "op": f"file={fname}",
                    "tables": tl,
                }
                if alias:
                    out["caliber_fallback"] = {
                        "declared_signal_column": col_raw,
                        "resolved_file": fname,
                        "series_root": str(SERIES_DIR),
                        "statement": "卡面申报 *_derived 口径，装载面命中同名母序列⇒口径未换（平行卡与母卡同一枚 CSV）",
                    }
                return out
            return {"cls": "U", "reason": f"series_csv_absent:{fname}", "recipe": None, "op": None, "tables": tl}
    # class A：单表单列 + 算子（表必须已在配方册，未登记者拒绑而非猜粒度）
    low = blob.lower()
    if len(tl) == 1:
        t = tl[0]
        if t not in _REGISTERED_TABLES:
            return {"cls": "A?", "reason": f"table_not_in_recipe_book:{t}", "recipe": None, "op": None, "tables": tl}
        col = str(b.get("signal_column") or "").strip()
        col_id = re.fullmatch(r"[a-z_][a-z0-9_]{1,40}", col)
        op = "anyLast_per_day"
        m_delta = re.search(r"(\d+)\s*(?:个)?交?易?日?(?:差|增量|delta|变化)", low)
        if m_delta:
            op = f"delta_{m_delta.group(1)}"
        elif re.search(r"(滚动|rolling|均值 ?\d+|过去 ?\d+ ?(交易)?日)", low):
            return {
                "cls": "A?",
                "reason": "rolling_window_needs_explicit_n_or_refuse",
                "recipe": None,
                "op": None,
                "tables": tl,
            }
        elif re.search(r"(z[- ]?score|标准化|分位)", low):
            return {"cls": "A?", "reason": "normalization_recipe_undecided", "recipe": None, "op": None, "tables": tl}
        if not col_id:
            return {
                "cls": "U",
                "reason": f"signal_column_not_a_single_identifier:{col[:40]}",
                "recipe": None,
                "op": op,
                "tables": tl,
            }
        return {"cls": "A", "reason": None, "recipe": f"single_table_series:{t}", "op": f"{col}|{op}", "tables": tl}
    return {"cls": "U", "reason": f"multi_table_needs_composite_recipe:{tl}", "recipe": None, "op": None, "tables": tl}


#: 配方册已核面（未登记者一律拒绑，禁按猜测拼 SQL 出分）：过滤条件逐条抄自前役实跑原文，非自创
_REGISTERED_TABLES: dict[str, dict] = {
    _TBL["market_index_kline"]: {
        "date_col": "trade_date",
        "where": f"symbol='{_INDEX_SYMBOL}'",
        "grain_evidence": "前役 run_exam_batch.py:target_index_return 同式（TDM-E-L1-S1 已出分在册）",
    },
    _TBL["market_index_valuation_daily"]: {
        "date_col": "trade_date",
        "where": f"symbol='{_INDEX_SYMBOL}'",
        "grain_evidence": "前役 load_erp_delta 同式（TDM-E-L9-A04 已出分在册）",
    },
    _TBL["market_news_sentiment_window"]: {
        "date_col": "window_ts",
        "where": "scope='market' AND window_type='1d'",
        "grain_evidence": "前役 load_news_sentiment 同式（TDM-E-L1-S0-1 已出分在册；PIT 日度段=夜矿 T0a 治本面 2,421 行/2,421 uniq 日）",
    },
    # 复合族入口批-A 第 1 张（L1-AGG/02）新登记表：三要素全部抄自在册真源，本班零新 CH 查。
    _TBL["backtest_regime_state_anchored"]: {
        "date_col": "trade_date",
        "where": "data_source='anchored_state_machine'",
        "grain_evidence": "DDL 真源 schemas/categories/backtest/backtest_regime_state_anchored.py 原文："
        "ENGINE=ReplacingMergeTree(ingest_ts)＋ORDER BY trade_date（日频一键，多版本行按 anyLast 取末版，"
        "禁把两版当两天）；data_source 列 DEFAULT 'anchored_state_machine'（过滤式取该字面值，非自拟名单）；"
        "覆盖与行数为在册引用＝卡面 data_window_evidence（2017-07-11..2026-10-09／4,488 行，列实测 "
        "close/ma20/ma60/ma120/vol_pct/dominant/data_source/ingest_ts）＋22 册 evidence_a 同指该 ORDER_BY",
    },
    # 复合族入口批-A 第 2 支装载形（880 板块截面形）新登记表：三要素同样抄自真源，非自拟。
    _TBL["market_sector_kline_880"]: {
        "date_col": "trade_date",
        "where": "period='1d'",
        "grain_evidence": "DDL 真源 schemas/categories/kline/market_kline_sector_880.py :65-67 原文："
        "ENGINE = ReplacingMergeTree(fetched_at)／PARTITION BY (period, toYYYYMM(trade_date))／"
        "ORDER BY period, sector_code, timestamp ⇒ 该表粒度是 (周期, 板块, 时点) 而非 (日, 板块)，"
        "日频腿必须先把版本行收敛：本形用在册模板 SQL_SECTOR_FAMILY_PANEL（GROUP BY d, code ＋ "
        "anyLast 去版本，与两张已批在册板块卡 sector_adjustment_progress/sector_relay_retreat 同式），"
        "where 的 period='1d' 字面值取自在册读取件常量（scripts/backtest/p1_conditional_tables.py，"
        '22 册 evidence_b 同指）与册内 args period: "1d"；'
        "族宇宙经 sector_code_name_map.code_family 在册映射界定（禁自拟名单，卡面明令）",
    },
}


def build_signal(card: dict, cls: dict) -> tuple[pd.Series | None, dict]:
    """按分类结果取数（run 面专用；返回 series + 凭据）。"""
    from fexam.ch_data import ch_query_df

    b = card["data_binding"]
    ev: dict = {"recipe": cls["recipe"], "op": cls["op"], "tables": cls["tables"]}
    if cls["recipe"] == "local_series_csv":
        fname = cls["op"].split("=", 1)[1]
        ev.update(source="local_csv", file=str(SERIES_DIR / fname), series_root=str(SERIES_DIR))
        if cls.get("caliber_fallback"):
            # 回落声明随出分凭据一起走（run 面 results 行与普查行同字段名，⑨席行级回核可 grep）
            ev["caliber_fallback"] = cls["caliber_fallback"]
        return _load_csv_series(fname), ev
    face = _REGISTERED_TABLES[cls["tables"][0]]
    table = cls["tables"][0]
    col = str(b["signal_column"]).strip()
    sql = SQL_FACE_DAILY.format(date_col=face["date_col"], col=col, tbl=table, where=face["where"])
    df = ch_query_df(sql)
    ser = _norm(df, 0, 1)
    m = re.match(r"delta_(\d+)", cls["op"] or "")
    if m:
        ser = (ser - ser.shift(int(m.group(1)))).dropna()
    ev.update(source="ch", sql=sql, rows=int(len(ser)), grain_evidence=face["grain_evidence"])
    return ser, ev


#: 聚合白名单（算子面只允许卡面声明过的聚合形，禁在此之外自创）
_AGG_WHITELIST = {"avg": "AVG", "sum": "SUM", "uniqExact": "uniqExact", "count": "COUNT"}


def op_daily_agg(card: dict, args: dict) -> tuple[pd.Series, dict]:
    """卡面原文声明的"按日聚合某列"形（如「按 toDate(publish_time, 'Asia/Shanghai') 聚合 AVG(polarity)」）。
    聚合函数/时区/列全部来自绑定册 args（args 内容由卡面原文逐字引用而来，非自创）。"""
    from fexam.ch_data import ch_query_df

    agg = _AGG_WHITELIST.get(str(args["agg"]))
    if agg is None:
        raise ValueError(f"agg_not_whitelisted:{args['agg']}")
    tz = f", '{args['tz']}'" if args.get("tz") else ""
    sql = SQL_DAILY_AGG.format(time_col=args["time_col"], tz=tz, agg=agg, col=args["col"], tbl=args["table"])
    df = ch_query_df(sql)
    ser = _norm(df, 0, 1)
    if args.get("dropna"):
        ser = ser.dropna()
    return ser, {
        "sql": sql,
        "rows": int(len(ser)),
        "agg": agg,
        "tz": args.get("tz"),
        "dup_share_note": args.get("dup_share_note", ""),
    }


def op_sector_top_n_amount_share(card: dict, args: dict) -> tuple[pd.Series, dict]:
    """卡面原文「集中度=rank(amount) 前 3 板块的 amount 之和 / 全族 amount 之和」，
    分母族=code_family IN (industry_l1, industry_ths)（卡面明令"由 sector_code_name_map.code_family
    在册映射界定，禁自拟名单"）。族内先按 (日,板块) anyLast 去版本，再按日排名取前 N。"""
    from fexam.ch_data import ch_query_df

    fams = ",".join(f"'{f}" + "'" for f in args["families"])
    n = int(args["top_n"])
    sql = SQL_SECTOR_TOP_N.format(
        n=n,
        col=args["col"],
        tbl=args["table"],
        period=repr(args.get("period", "1d")),
        map_table=args["map_table"],
        families=fams,
    )
    df = ch_query_df(sql)
    ser = _norm(df, 0, 1).dropna()
    return ser, {
        "sql": sql,
        "rows": int(len(ser)),
        "top_n": n,
        "families": list(args["families"]),
        "axis_note": "只绑主信号面（集中度日序列）；卡面辅轴（头部/非头部 5 日超额）本次未考",
    }


def load_sector_family_panel(args: dict) -> pd.DataFrame:
    """族面板底座（一次取数，多卡复用）：(日 × 板块) 的 close/amount 宽帧。
    族=code_family IN (...)（卡面明令经 sector_code_name_map 在册映射界定，禁自拟名单）；
    (日,板块) 先 anyLast 去版本行（在册多版本行=聚合放大事故面）。"""
    from fexam.ch_data import ch_query_df

    fams = ",".join(f"'{f}'" for f in args["families"])
    sql = SQL_SECTOR_FAMILY_PANEL.format(
        close_col=args["close_col"],
        amount_col=args["amount_col"],
        tbl=args["table"],
        period=args.get("period", "1d"),
        map_table=args["map_table"],
        families=fams,
    )
    df = ch_query_df(sql)
    df.columns = ["d", "code", "close", "amount"][: len(df.columns)]
    df["d"] = pd.to_datetime(df["d"])
    for c in ("close", "amount"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def op_sector_adjustment_progress(card: dict, args: dict) -> tuple[pd.Series, dict]:
    """卡面原文「时间维=min(1, 距 60 日高点交易日数 / 8)；回撤维=min(1, (高点−close)/高点 / 0.15)；
    量能维=min(1, max(0, 1 − roll_mean(amount,5)/roll_max(amount,60)×3))；进度=0.4/0.3/0.3 加权
    （三维重归一，与在码"时间0.4+回撤0.3+扩散0.3"不同源，差异卡面已声明）」。
    series 面=当日跨板块进度均值。"""
    panel = load_sector_family_panel(args)
    w_t, w_dd, w_vol = (float(x) for x in args["weights"])
    win = int(args["high_window"])
    out = {}
    for code, g in panel.groupby("code"):
        g = g.sort_values("d").set_index("d")
        hi = g["close"].rolling(win, min_periods=win).max()
        # 距 60 日高点的"交易日序号差"（禁自然日差）：高点当日 close==rolling max
        idx_pos = pd.Series(range(len(g)), index=g.index)
        hi_pos = idx_pos.where(g["close"] >= hi * (1 - 1e-12))
        last_hi = hi_pos.ffill()
        t_dim = (idx_pos - last_hi) / float(args["t_div"])
        dd_dim = (hi - g["close"]) / hi / float(args["dd_div"])
        vol_dim = 1 - (g["amount"].rolling(5, min_periods=5).mean() / g["amount"].rolling(60, min_periods=60).max() * 3)
        prog = w_t * t_dim.clip(0, 1) + w_dd * dd_dim.clip(0, 1) + w_vol * vol_dim.clip(0, 1)
        out[code] = prog.where(hi.notna() & last_hi.notna())
    wide = pd.DataFrame(out)
    ser = wide.mean(axis=1, skipna=True).dropna()
    ev = {
        "panel_rows": int(len(panel)),
        "codes": int(panel["code"].nunique()),
        "window": win,
        "weights": [w_t, w_dd, w_vol],
        "family": list(args["families"]),
        "days_from_hi_method": "交易日序号差（禁自然日）",
        "rows": int(len(ser)),
    }
    return ser, ev


def _rolling_pctile(ser: pd.Series, window: int) -> pd.Series:
    """过去 window 交易日滚动分位（含当日，rank/(n)；min_periods=window 防暖机段假读数）。"""
    return ser.rolling(window, min_periods=window).apply(lambda a: float((a <= a[-1]).mean()), raw=True)


def op_macro_scissors(card: dict, args: dict) -> tuple[pd.Series, dict]:
    """卡面原文「剪刀差 = m1_yoy - m2_yoy（按 report_date 月度）；日频化 = 以 report_date + 45 自然天
    为可见日起做前向填充；缺月不插值（缺失即 NaN，禁 ffill 掩盖断供）」。"""
    from fexam.ch_data import ch_query_df

    sql = SQL_MACRO_SCISSORS.format(tbl=args["table"])
    df = ch_query_df(sql)
    m1 = pd.to_numeric(df.iloc[:, 1], errors="coerce").to_numpy(dtype=float)
    m2 = pd.to_numeric(df.iloc[:, 2], errors="coerce").to_numpy(dtype=float)
    monthly = pd.Series(m1 - m2, index=pd.to_datetime(df.iloc[:, 0]))
    monthly = monthly[~pd.isna(monthly)]
    lag = int(args["lag_days"])
    avail = monthly.copy()
    avail.index = avail.index.to_period("M")
    avail = avail[~avail.index.duplicated(keep="last")].sort_index()
    grid = pd.date_range(monthly.index.min(), monthly.index.max(), freq="B")
    # 可见日=report_date+lag ⇒ 该日的源月=(day-lag) 所在自然月；源月无 print 即 NaN（卡面「禁 ffill 掩盖断供」）
    src_month_of_day = (grid.to_series() - pd.Timedelta(days=lag)).dt.to_period("M")
    values = [
        float(avail[sm]) if sm in avail.index and pd.notna(avail[sm]) else float("nan") for sm in src_month_of_day
    ]
    ser = pd.Series(values, index=grid).dropna()
    expected = set(pd.period_range(avail.index.min(), avail.index.max(), freq="M"))
    return ser, {
        "sql": sql,
        "rows": int(len(ser)),
        "lag_days": lag,
        "missing_months_in_span": int(len(expected - set(avail.index))),
    }


def op_margin_balance_5d(card: dict, args: dict) -> tuple[pd.Series, dict]:
    """卡面原文「日度加总 sum(margin_balance)（按 exchange 分别加总再合并，禁混算口径）；
    5 日环比 = balance_t/balance_{t-5} - 1」。"""
    from fexam.ch_data import ch_query_df

    sql = SQL_MARGIN_BALANCE.format(
        date_col=args["date_col"], symbol_col=args["symbol_col"], col=args["col"], tbl=args["table"]
    )
    df = ch_query_df(sql)
    # ch_query_df 位置协议⇒显式命名＋强制数值化（NULL 为空串，to_numeric 归 NaN）
    df.columns = ["d", "exchange", "bal"][: len(df.columns)]
    df["d"] = pd.to_datetime(df["d"])
    df["bal"] = pd.to_numeric(df["bal"], errors="coerce")
    wide = df.pivot_table(index="d", columns="exchange", values="bal", aggfunc="sum")
    bal = wide.sum(axis=1, skipna=True).sort_index()
    ser = (bal / bal.shift(int(args["n"])) - 1.0).dropna()
    return ser, {
        "sql": sql,
        "exchanges": [str(c) for c in wide.columns],
        "rows": int(len(ser)),
        "balance_days": int(len(bal)),
    }


def op_index_amount_sum_pctile(card: dict, args: dict) -> tuple[pd.Series, dict]:
    """卡面原文「两市成交额=SUM(kline_index.amount) WHERE symbol IN ('000001','399001') 同日相加；
    signal=该和的 20 日滚动分位（当日不含未来）」。分位读数与单位（元/亿元）无关。"""
    from fexam.ch_data import ch_query_df

    syms = ",".join(f"'{s}'" for s in args["symbols"])
    n_sym = len(args["symbols"])
    sql = SQL_INDEX_AMOUNT_SUM.format(
        date_col=args["date_col"], col=args["col"], tbl=args["table"], symbols=syms, n_sym=n_sym
    )
    df = ch_query_df(sql)
    amt = _norm(df, 0, 1)
    ser = _rolling_pctile(amt, int(args["window"])).dropna()
    return ser, {"sql": sql, "days_with_both_symbols": int(len(amt)), "rows": int(len(ser))}


def op_downside_dev_pctile(card: dict, args: dict) -> tuple[pd.Series, dict]:
    """卡面原文「r_t = close_t/close_{t-1} - 1；下行半偏差 = sqrt(244 × mean(min(r_t,0)^2 over 20 日窗))；
    synthetic_vix_pct = 该值在过去 250 个交易日中的分位」。禁改回全波动口径（改了就是另一张卡）。"""
    from fexam.ch_data import ch_query_df

    sql = SQL_DOWNSIDE_DEV.format(date_col=args["date_col"], col=args["col"], tbl=args["table"], sym=args["symbol"])
    df = ch_query_df(sql)
    close = _norm(df, 0, 1)
    r = close / close.shift(1) - 1.0
    neg = r.clip(upper=0.0) ** 2
    dev = (244.0 * neg.rolling(int(args["dev_window"]), min_periods=int(args["dev_window"])).mean()).pow(0.5)
    ser = _rolling_pctile(dev, int(args["pctile_window"])).dropna()
    return ser, {
        "sql": sql,
        "rows": int(len(ser)),
        "span": [str(close.index.min().date()), str(close.index.max().date())],
    }


def op_sector_relay_retreat_ratio(card: dict, args: dict) -> tuple[pd.Series, dict]:
    """卡面原文「接棒=连续 3 日 close.pct_change>0 且 amount 3 日滑动均值>前 5 日均值；撤离=对称反向；
    series 面=当日(接棒板块数−撤离板块数)/板块总数」。

    口径选择登记在绑定册 review_note（不动判据面）：「前 5 日均值」＝amount.rolling(5).mean().shift(3)
    （"前"=当前 3 日窗之前的 5 日）；改读作同期 rolling(5) 是另一条序列，须另立卡重考。
    资金面按卡面自我声明用 amount 环比代理（主力净流入不可得），本读数是榜单强度非资金流结论。
    分桶协议相容性已核：该卡 buckets.type=quantile_quintile（单级）＝执行器 _bucket_response 支持面。"""
    panel = load_sector_family_panel(args)
    relay: dict = {}
    retreat: dict = {}
    for code, g in panel.groupby("code"):
        g = g.sort_values("d").set_index("d")
        pc = g["close"].pct_change()
        up3 = (pc > 0).rolling(3, min_periods=3).sum() == 3
        dn3 = (pc < 0).rolling(3, min_periods=3).sum() == 3
        a3 = g["amount"].rolling(3, min_periods=3).mean()
        prev5 = g["amount"].rolling(5, min_periods=5).mean().shift(3)
        relay[code] = up3 & (a3 > prev5)
        retreat[code] = dn3 & (a3 < prev5)
    r = pd.DataFrame(relay)
    t = pd.DataFrame(retreat)
    denom = r.notna().sum(axis=1)
    ser = ((r.sum(axis=1) - t.sum(axis=1)) / denom.where(denom > 0)).dropna()
    return ser, {
        "panel_rows": int(len(panel)),
        "codes": int(panel["code"].nunique()),
        "rows": int(len(ser)),
        "caliber_choice": "prev5=rolling(5).mean().shift(3)",
        "family": list(args["families"]),
    }


_PANEL_COLS = ["d", "n_lu", "n_lu_prev", "n_promo", "prem_close", "prem_open", "n_rows"]


def load_limit_up_panel(args: dict) -> pd.DataFrame:
    """涨停面板底座（卡 05/06 共用一次日度聚合）：逐日出涨停家数/昨板在架家数/晋级数/两式溢价均值。

    分母口径纪律（卡 06 hardest_step 原文）：den=昨日涨停家数 n_lu_prev，不是当日在市家数；
    num 与 den 在同一次 lag 结构上分别取，避免把"晋级率"算成"涨停占比"。"""
    from fexam.ch_data import ch_query_df

    sql = SQL_LIMIT_UP_PANEL.format(
        hfq_tbl=args["hfq_table"],
        lim_tbl=args["limit_table"],
        lo=args["warmup_start"],
        hi=args["end"],
        tol=float(args["limit_tol"]),
    )
    df = ch_query_df(sql)
    df.columns = _PANEL_COLS[: len(df.columns)]
    df["d"] = pd.to_datetime(df["d"])
    for c in _PANEL_COLS[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.sort_values("d").set_index("d")


def _apply_set_floor(panel: pd.DataFrame, value_col: str, min_set: int) -> tuple[pd.Series, dict]:
    """卡面 "|S_{t-1}|<20 的日置 NaN"／"分母 <20 置 NaN" 同形闸（分母=昨板在架家数）。

    停牌缺失机械计数=在册昨日涨停家数 n_lu(t-1) 减今日在架 n_lu_prev(t) 的正部之和
    （卡 05 原文「停牌股（t 日无行）不入截面均值并在 run 附注计缺失数」）。"""
    ser = panel[value_col].where(panel["n_lu_prev"] >= min_set)
    miss = (panel["n_lu"].shift(1) - panel["n_lu_prev"]).clip(lower=0)
    ev = {
        "min_set_size": int(min_set),
        "rows_kept": int(len(ser.dropna())),
        "days_below_set_floor": int((panel["n_lu_prev"] < min_set).sum()),
        "suspended_missing_symbol_days": int(miss.sum()),
        "days_with_missing": int((miss > 0).sum()),
        "mean_daily_limit_up": float(panel["n_lu"].mean()),
        "max_daily_limit_up": int(panel["n_lu"].max()),
    }
    return ser.dropna(), ev


def op_limit_up_premium_close_mean(card: dict, args: dict) -> tuple[pd.Series, dict]:
    """卡 05 主信号=昨日涨停集合当日收盘溢价的截面均值 mean_{i∈S_{t-1}}(close_{i,t}/close_{i,t-1}-1)。

    开盘口径 open_{i,t}/close_{i,t-1}-1 按卡面 two_form_spread 另档建档：只把统计量写进附注，
    不占 run_card 单信号入口（卡面自记该柱"不作一票否决门柱"，且"显著低于全样本"无冻结检验量）。"""
    panel = load_limit_up_panel(args)
    min_set = int(args["min_set_size"])
    ser, ev = _apply_set_floor(panel, "prem_close", min_set)
    open_ser, _ = _apply_set_floor(panel, "prem_open", min_set)
    ev.update(
        signal_col="limit_up_premium_close_derived",
        panel_rows=int(len(panel)),
        warmup_start=str(args["warmup_start"]),
        limit_tol=float(args["limit_tol"]),
        open_form_days=int(len(open_ser)),
        open_form_median=float(open_ser.median()) if len(open_ser) else float("nan"),
        unjudged_pillar_note="开盘口径仅建档未占机判入口",
    )
    return ser, ev


def promotion_rate_from_panel(panel: pd.DataFrame, min_set: int) -> tuple[pd.Series, dict]:
    """promotion_rate_t = countIf(is_lu_t AND is_lu_{t-1}) / nullIf(countIf(is_lu_{t-1}),0)，分母 <20 置 NaN。

    分母必须=昨板在架家数 n_lu_prev（卡面 hardest_step 原文：错取当日在市家数＝把晋级率算成涨停占比）。"""
    den = panel["n_lu_prev"].where(panel["n_lu_prev"] > 0)
    rate = (panel["n_promo"] / den).where(den >= min_set).dropna()
    ev = {
        "min_set_size": int(min_set),
        "rows_kept": int(len(rate)),
        "days_below_set_floor": int((panel["n_lu_prev"] < min_set).sum()),
        "suspended_missing_symbol_days": int((panel["n_lu"].shift(1) - panel["n_lu_prev"]).clip(lower=0).sum()),
        "mean_daily_limit_up": float(panel["n_lu"].mean()),
        "max_daily_limit_up": int(panel["n_lu"].max()),
        "den_col": "n_lu_prev（=countIf(is_lu_{t-1})，非当日在市家数）",
    }
    return rate, ev


def op_promotion_rate(card: dict, args: dict) -> tuple[pd.Series, dict]:
    """卡 06 主信号=晋级率（卡面原文式，见 promotion_rate_from_panel）。分板率 ladder 档
    （1→2/2→3/>=3→+1）需卡 13/14 streak 串＝另一建档面，本绑定只交主信号，
    缺档如实写进附注（未判柱清单面）。"""
    panel = load_limit_up_panel(args)
    rate, ev = promotion_rate_from_panel(panel, int(args["min_set_size"]))
    ev.update(
        signal_col="promotion_rate_derived",
        panel_rows=int(len(panel)),
        warmup_start=str(args["warmup_start"]),
        limit_tol=float(args["limit_tol"]),
        unjudged_pillar_note="分板率 ladder 档需卡 13/14 streak 串，本绑定未实现",
    )
    return rate, ev


def _event_base_series(card: dict, args: dict) -> tuple[pd.Series, dict]:
    """事件底座的基序列取数：base_op=已在册算子名，base_csv=本仓已入库派生序列文件名（二选一）。

    禁在此重写第三条取数路（第二真源）；基算子自己的绑定凭据原样并入 ev（前缀 base_）。"""
    op, csv = args.get("base_op"), args.get("base_csv")
    if bool(op) == bool(csv):
        raise ValueError("event_flag 底座需 base_op 与 base_csv 恰选其一")
    if op:
        spec = OPS.get(op)
        if spec is None:
            raise ValueError(f"base_op_not_in_ops_book:{op}")
        ser, ev = spec["fn"](card, args.get("base_args") or {})
        return ser, {
            "base": f"op:{op}",
            "base_prose_quote": spec["quote_key"],
            "base_rows": int(len(ser)),
            "base_op_evidence": {k: v for k, v in ev.items() if k in ("rows", "rows_kept", "codes", "panel_rows")},
        }
    ser = _load_csv_series(csv)
    if ser is None or len(ser) == 0:
        raise ValueError(f"base_csv_absent_or_empty:{csv}")
    return ser, {"base": f"csv:{csv}", "base_rows": int(len(ser))}


def op_event_flag_rolling_pctile(card: dict, args: dict) -> tuple[pd.Series, dict]:
    """事件开关底座（日班总令 T1·四换②的机判底座）：基序列二值化为「过去 window 日滚动分位 > p」的 0/1 事件日。

    分位一律用**历史滚动**（含当日，min_periods=window，暖机段无读数不冒充事件）：
    全样本分位＝用未来数据定过去的门槛，翻成事后挪门柱，禁。
    基序列/窗/分位阈三个量都由绑定册显式给出并在卡面有原文凭据（本算子零自创）。"""
    ser, ev = _event_base_series(card, args)
    ser = ser.sort_index().dropna()
    win, thr = int(args["pctile_window"]), float(args["pct_threshold"])
    pct = _rolling_pctile(ser, win)
    flag = pd.Series(0.0, index=ser.index).where(pct.isna(), (pct > thr).astype(float))
    flag = flag[pct.notna()]
    ev.update(
        signal_col=card.get("data_binding", {}).get("signal_column"),
        pctile_window=win,
        pct_threshold=thr,
        rows=len(flag),
        n_event_days=int((flag > 0).sum()),
        event_share=float((flag > 0).mean()),
        pit_statement="事件判定只用 t 及以前的基序列（rolling 窗含当日），次日收益由执行器 shift(-1) 吃",
        warmup_dropped_days=int(len(ser) - len(flag)),
    )
    return flag, ev


#: 复合族入口（CW-MINELOOP-001 批-A，统筹 2026-10-13 D5 放行）的对齐形；新增形须先在设计稿登记
_COMBINE_ALIGNS = ("inner_on_keys",)


def _norm_text(df: pd.DataFrame, date_pos: int, val_pos: int) -> pd.Series:
    """`_norm` 的文本值版（dominant 这类 LowCardinality(String) 列经 to_numeric 会全列变 NaN）。

    同位置协议（列名 c1..cN、NULL=空串）＋同日多版本 keep=last；空串原样留着，
    由映射侧的"态名不在登记表内即红"接住——禁在这里替空值编一个档位。
    """
    dates = pd.to_datetime(df.iloc[:, date_pos])
    vals = df.iloc[:, val_pos].astype(str)
    s = pd.Series(vals.to_numpy(), index=dates)
    s = s[~s.index.duplicated(keep="last")]
    return s.sort_index()


def _card_composite_pairs(card: dict) -> list[dict]:
    """卡面 composite_join_rules.pairs＝22 册（examunlock 班冻结）的卡面镜像，本段的唯一键面真源。"""
    rules = (card.get("data_binding") or {}).get("composite_join_rules") or {}
    return [p for p in (rules.get("pairs") or []) if isinstance(p, dict)]


def _check_legs_keys_on_card_face(card: dict, legs: list[dict]) -> None:
    """R2：每条腿声明的共键必须在卡面镜像里逐字存在（禁本班替 examunlock 拍键、禁自补一个键）。"""
    pairs = _card_composite_pairs(card)
    if not pairs:
        raise ValueError("composite_card_face_rules_absent（卡面无 composite_join_rules 块＝不许走复合口）")
    for leg in legs:
        t = str(leg.get("table") or "").strip().lower()
        lk = {str(k) for k in (leg.get("keys") or [])}
        hit = [p for p in pairs if t in {str(x).lower() for x in (p.get("tables") or [])}]
        if not hit:
            raise ValueError(f"composite_leg_absent_on_card_face_pairs:{t}")
        if not any({str(k) for k in (p.get("keys") or [])} >= lk for p in hit):
            raise ValueError(f"composite_leg_keys_not_on_card_face:{t}:{sorted(lk)}")


#: 复合口在册装载形清单（每加一支都须：①该表在 `_REGISTERED_TABLES` 有 date_col/where/grain_evidence
#: 三要素；②一支红证用例。第二支 `sector_family_panel` 由 D10 甲批文解锁（RRG 要按板块算象限
#: 再出日截面占比，单列日频腿承载不了），装载口与 SQL 模板全复用在册件，非本班新写形。
_COMPOSITE_LOADERS = ("face_daily", "sector_family_panel")


def _load_panel_leg(leg: dict, table: str, face: dict, name: str) -> tuple[pd.DataFrame, dict]:
    """(日 × 板块) 长帧腿：装载口与 SQL 模板全复用在册件（`load_sector_family_panel` 与
    `SQL_SECTOR_FAMILY_PANEL`），族名单／映射表／周期／列名四要素整表取自册 args——本函数不写
    任何族名或表名（卡面明令"由 sector_code_name_map.code_family 在册映射界定，禁自拟名单"）。
    """
    a = leg.get("args") or {}
    missing = [k for k in ("map_table", "families", "close_col", "amount_col") if not a.get(k)]
    if missing:
        raise ValueError(f"panel_leg_args_incomplete:{sorted(missing)}（族面板四要素须整表来自册 args）")
    if str(a.get("table") or table).strip().lower() != table:
        raise ValueError(f"panel_leg_table_mismatch:{str(a.get('table'))[:60]}!={table}")
    for k in ("close_col", "amount_col"):
        if not re.fullmatch(r"[a-z_][a-z0-9_]{1,40}", str(a[k])):
            raise ValueError(f"panel_leg_col_not_an_identifier:{k}:{str(a[k])[:40]}")
    map_table = str(a["map_table"]).strip().lower()
    if not _TABLE_RE.fullmatch(map_table):
        raise ValueError(f"panel_leg_map_table_not_a_qualified_name:{map_table[:60]}")
    families = [str(f) for f in a["families"]]
    bad = [f for f in families if not re.fullmatch(r"[a-z0-9_]+", f)]
    if not families or bad:
        raise ValueError(f"panel_leg_family_not_an_identifier:{(bad or families)[:4]}")
    period = str(a.get("period") or "1d")
    if not re.fullmatch(r"[0-9]+[a-z]{1,3}", period):
        raise ValueError(f"panel_leg_period_not_a_value:{period[:20]}")
    df = load_sector_family_panel(
        {
            "table": table,
            "map_table": map_table,
            "families": families,
            "period": period,
            "close_col": str(a["close_col"]),
            "amount_col": str(a["amount_col"]),
        }
    )
    ev = {
        "name": name,
        "table": table,
        "loader": "sector_family_panel",
        "grain": "day_x_sector",
        "columns": [str(c) for c in df.columns],
        "rows": int(len(df)),
        "days": int(df["d"].nunique()) if len(df) else 0,
        "codes": int(df["code"].nunique()) if len(df) else 0,
        "keys": [str(k) for k in (leg.get("keys") or [])],
        "family": families,
        "period": period,
        "map_table": map_table,
        "close_col": str(a["close_col"]),
        "dedup": "在册模板 (日,板块) anyLast 去版本行（禁把多版本行当多行样本）",
        "grain_evidence": face["grain_evidence"],
    }
    return df, ev


def _load_composite_leg(leg: dict) -> tuple[pd.Series | pd.DataFrame, dict]:
    """一腿一次在册装载口调用（批-A 两支形见 `_COMPOSITE_LOADERS`；表未进配方册即拒=R3）。"""
    from fexam.ch_data import ch_query_df

    name = str(leg.get("name") or "").strip()
    table = str(leg.get("table") or "").strip().lower()
    loader = str(leg.get("loader") or "")
    if not name:
        raise ValueError("composite_leg_unnamed")
    if loader not in _COMPOSITE_LOADERS:
        raise ValueError(f"composite_loader_not_registered:{loader}")
    face = _REGISTERED_TABLES.get(table)
    if face is None:
        raise ValueError(f"leg_table_not_in_recipe_book:{table}")
    if loader == "sector_family_panel":
        return _load_panel_leg(leg, table, face, name)
    col = str(leg.get("column") or "").strip()
    if not re.fullmatch(r"[a-z_][a-z0-9_]{1,40}", col):
        raise ValueError(f"leg_column_not_an_identifier:{col[:40]}")
    cast = str(leg.get("cast") or "float")
    if cast not in ("float", "text"):
        raise ValueError(f"leg_cast_unknown:{cast}")
    sql = SQL_FACE_DAILY.format(date_col=face["date_col"], col=col, tbl=table, where=face["where"])
    df = ch_query_df(sql)
    ser = _norm(df, 0, 1) if cast == "float" else _norm_text(df, 0, 1)
    ev = {
        "name": name,
        "table": table,
        "column": col,
        "cast": cast,
        "keys": [str(k) for k in (leg.get("keys") or [])],
        "rows": int(len(ser)),
        "grain_evidence": face["grain_evidence"],
    }
    return ser, ev


def assemble_composite_legs(card: dict, legs: list[dict], align: str = "inner_on_keys") -> tuple[dict, dict]:
    """多腿装载＋按冻结共键对齐，交付 {腿名: Series|DataFrame} 与凭据面。出口仍是日频序列面（判官零改动）。

    R1 腿集合：册内腿的表必须都在卡面 signal_table 申报过（禁多绑/偷绑）；
    R2 键面：见 `_check_legs_keys_on_card_face`；
    R5 对齐可见：inner join 后各腿丢了多少行**逐腿入凭据**，禁静默吞行，也禁前向填充
       （卡面 alignment 原文"1:1 行对齐；不做前向填充"）。
    """
    if not legs:
        raise ValueError("composite_entry_has_no_legs")
    if align not in _COMBINE_ALIGNS:
        raise ValueError(f"composite_align_not_registered:{align}")
    declared = set(tables_of(str((card.get("data_binding") or {}).get("signal_table") or "")))
    wanted = {str(l.get("table") or "").strip().lower() for l in legs}
    if not wanted <= declared:
        raise ValueError(f"composite_legs_not_declared_on_card:{sorted(wanted - declared)}")
    _check_legs_keys_on_card_face(card, legs)
    series: dict[str, pd.Series] = {}
    panels: dict[str, pd.DataFrame] = {}
    per_leg: list[dict] = []
    for leg in legs:
        obj, ev = _load_composite_leg(leg)
        if len(obj) == 0:
            raise ValueError(f"composite_leg_empty:{ev['name']}")
        ev.setdefault("grain", "day_x_sector" if isinstance(obj, pd.DataFrame) else "day")
        if isinstance(obj, pd.DataFrame):
            panels[ev["name"]] = obj
        else:
            series[ev["name"]] = obj
        per_leg.append(ev)
    if not panels:
        frame = pd.concat(series, axis=1, join="inner")
        rows_after = int(len(frame))
        for ev in per_leg:
            ev["rows_dropped_by_alignment"] = int(ev["rows"] - rows_after)
        aligned = {name: frame[name] for name in series}
        return aligned, {
            "align": align,
            "aligned_rows": rows_after,
            "legs": per_leg,
            "fill_policy": "none（禁 ffill/禁补零，缺日如实少行）",
        }

    def _day_axis(obj) -> pd.DatetimeIndex:
        idx = obj["d"] if isinstance(obj, pd.DataFrame) else obj.index
        return pd.DatetimeIndex(pd.to_datetime(idx.unique() if isinstance(obj, pd.DataFrame) else idx))

    # 混合粒度下 `inner_on_keys` 的定义＝各腿"日轴键集"的交集（长帧取 d 列唯一值、序列取 index）；
    # 交集之外如实少行，禁把长帧折成日频标量冒充对齐（那是折算捷径＝丢掉正是要判的信息）。
    common: pd.DatetimeIndex | None = None
    for obj in list(series.values()) + list(panels.values()):
        days = _day_axis(obj)
        common = days if common is None else common.intersection(days)
    if common is None or len(common) == 0:
        raise ValueError("composite_legs_no_common_days（腿之间没有任何共享日＝拒，不静默出空面）")
    aligned_mixed: dict[str, pd.Series | pd.DataFrame] = {}
    for name, s in series.items():
        aligned_mixed[name] = s.reindex(common)
    for name, p in panels.items():
        aligned_mixed[name] = p[p["d"].isin(common)].sort_values(["d", "code"]).reset_index(drop=True)
    rows_after = int(len(common))
    for ev in per_leg:
        if ev["grain"] == "day_x_sector":
            kept_rows = int(len(aligned_mixed[ev["name"]]))
            ev["days_dropped_by_alignment"] = int(ev["days"] - rows_after)
            ev["rows_dropped_by_alignment"] = int(ev["rows"] - kept_rows)
            ev["rows_kept"] = kept_rows
        else:
            ev["rows_dropped_by_alignment"] = int(ev["rows"] - rows_after)
    return aligned_mixed, {
        "align": align,
        "aligned_rows": rows_after,
        "aligned_days": rows_after,
        "mixed_grain": "inner_on_keys 在混合粒度上＝日轴键集交集（序列 reindex 到该日集、长帧按该日集过滤）",
        "legs": per_leg,
        "fill_policy": "none（禁 ffill/禁补零，缺日如实少行）",
    }


def op_agg4_state_ordinal_series(card: dict, args: dict) -> tuple[pd.Series, dict]:
    """L1-AGG/02：dominant 四档态名 → 先验冻结档序数值序列（r3/r2/r1/r4 → 1/2/3/4）。

    R6：档值**不在本函数里定义**——`ordinal_map` 必须由绑定册 args 整表传入（内容逐字抄自卡面
    signal_derivation 的"档序映射 …（先验冻结）"）； observed 态名不在表内即红（禁悄悄丢行、
    禁把 CH 的空串 NULL 面当某一档）。本卡不重算阈值：0.30/0.60/0.80 属实现件 anchored_state_machine。
    """
    legs = args.get("legs") or {}
    om_raw = args.get("ordinal_map")
    if not isinstance(om_raw, dict) or not om_raw:
        raise ValueError("agg4_ordinal_map_unfrozen_in_book")
    om = {str(k): v for k, v in om_raw.items()}
    for k, v in om.items():
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ValueError(f"agg4_ordinal_map_value_not_numeric:{k}")
    state_name = str(args.get("state_leg") or "state")
    if state_name not in legs:
        raise ValueError(f"agg4_state_leg_missing:{state_name}")
    state = legs[state_name]
    observed = sorted({str(v) for v in state.dropna().unique()})
    unknown = [v for v in observed if v not in om]
    if unknown:
        raise ValueError(f"agg4_state_out_of_declared_vocab:{unknown[:6]}")
    out = state.map(lambda v: float(om[str(v)])).dropna()
    return out, {
        "op": "agg4_state_ordinal_series",
        "state_leg": state_name,
        "state_observed": observed,
        "ordinal_map_size": len(om),
        "n_rows": int(len(out)),
    }


def op_rrg_quadrant_series(card: dict, args: dict) -> tuple[pd.Series, dict]:
    """L2-02-1/02b：在册 10/26 双 EMA 式逐板块算 RRG 象限，再出日截面"leading 占比 − lagging 占比"。

    零自拟四条钉死（本函数里不出现任何公式系数、带宽或阈值）：
    ①构造式=`sector_rrg.compute_rrg_series`（参数取该件 DEFAULT_SHORT_PERIOD/DEFAULT_LONG_PERIOD
      的缺省值，本函数不传数字，也不复制该式）；
    ②象限四分=该件 `classify_quadrant` 的 100 中枢规则，快慢序由函数签名固定
      （§33.10 第三分叉"坐标快慢序未指明"在甲路下由被承接的装置自身解决）；
    ③band 不存在＝该件四分规则没有带宽项，母卡的"±带宽 5"随锚点废止，本班不补回；
    ④采信=raw（"连续 2-3 日确认值不值"是 03b 卡的考题，本卡不预设；confirm_quadrant_series
      的复用位留给 03b 的臂面，本函数不调它）。
    62 日最小数据量由 `compute_rrg_series` 自身 raise 守⇒不足的历史整段不参与，逐数披露，
    禁在绑定腿里预削窗口（那会把节点 fallback 悄悄改成装载口策略）。
    """
    from zephyr.signal_ashare.sector.sector_rrg import (
        DEFAULT_LONG_PERIOD,
        DEFAULT_SHORT_PERIOD,
        compute_rrg_series,
    )

    legs = args.get("legs") or {}
    panel_name = str(args.get("panel_leg") or "panel")
    bench_name = str(args.get("bench_leg") or "bench")
    if panel_name not in legs or bench_name not in legs:
        raise ValueError(f"rrg_legs_missing:{sorted(legs)}（须含 {panel_name}/{bench_name} 两条腿）")
    panel, bench = legs[panel_name], legs[bench_name]
    if not isinstance(panel, pd.DataFrame) or not {"d", "code", "close"} <= set(panel.columns):
        raise ValueError(f"rrg_panel_leg_shape_unexpected:{list(getattr(panel, 'columns', []))[:6]}")
    if not isinstance(bench, pd.Series):
        raise ValueError(f"rrg_bench_leg_must_be_series:{type(bench).__name__}")
    bench = bench.sort_index()
    bench_pos = bench.dropna()
    if len(bench_pos) == 0:
        raise ValueError("rrg_bench_leg_all_nan（基准面无任何读数＝拒，禁拿板块均值冒充基准）")
    bad_bench = int((bench_pos <= 0).sum())
    if bad_bench:
        raise ValueError(
            f"rrg_bench_nonpositive_close_days:{bad_bench}（卡面硬约束"
            "『基准价须 >0』由装置自身守，本班不剔日、不替换基准）"
        )
    min_len = DEFAULT_LONG_PERIOD * 2 + DEFAULT_SHORT_PERIOD
    quads: dict[str, pd.Series] = {}
    skipped_short: list[str] = []
    for code, g in panel.groupby("code"):
        gg = g.sort_values("d").set_index("d")
        both = pd.concat([gg["close"].rename("s"), bench_pos.rename("b")], axis=1, join="inner").dropna()
        if len(both) < min_len:
            skipped_short.append(str(code))
            continue
        pts = compute_rrg_series(list(both["s"]), list(both["b"]))
        quads[str(code)] = pd.Series([p.quadrant.value for p in pts], index=both.index)
    if not quads:
        raise ValueError(f"rrg_no_sector_leg_passed_min_length:{min_len}（{len(skipped_short)} codes 全不足）")
    wide = pd.DataFrame(quads)
    denom = wide.notna().sum(axis=1)
    ser = ((wide.eq("LEADING").sum(axis=1) - wide.eq("LAGGING").sum(axis=1)) / denom.where(denom > 0)).dropna()
    dist = {str(k): int((wide == k).sum().sum()) for k in ("LEADING", "IMPROVING", "WEAKENING", "LAGGING")}
    ev = {
        "op": "rrg_quadrant_series",
        "construction": "sector_rrg.compute_rrg_series（RS=100×P_sector/P_bench；RS-Ratio=EMA(RS,10)/EMA(RS,26)×100；"
        "RS-Momentum=EMA(RS-Ratio,10)/EMA(RS-Ratio,26)×100；象限=classify_quadrant 100 中枢四分）",
        "short": DEFAULT_SHORT_PERIOD,
        "long": DEFAULT_LONG_PERIOD,
        "min_len": min_len,
        "admitted_caliber": "raw（连续确认腿由 03b 卡判）",
        "denominator_rule": "按日截面分母＝当日在数 code 数（族口径固定，防宇宙扩张冒充信号改善）",
        "codes_in_panel_leg": int(panel["code"].nunique()),
        "codes_computed": len(quads),
        "codes_skipped_below_min_len": len(skipped_short),
        "skipped_examples": skipped_short[:8],
        "quadrant_cell_counts": dist,
        "rows": int(len(ser)),
        "span": [str(ser.index.min().date()), str(ser.index.max().date())] if len(ser) else [],
    }
    return ser, ev


#: 算子册（每格都逐字引用卡面 signal_derivation 原文，禁自创口径；新增算子须同步测试）
OPS: dict[str, dict] = {
    "event_flag_rolling_pctile": {
        "fn": op_event_flag_rolling_pctile,
        "quote_key": "滚动分位",
    },
    "limit_up_premium_close_mean": {
        "fn": op_limit_up_premium_close_mean,
        "quote_key": "全部比值在后复权空间内计算",
    },
    "promotion_rate_from_limit_panel": {
        "fn": op_promotion_rate,
        "quote_key": "分母 <20 置 NaN",
    },
    "macro_scissors_monthly_lag_ffill": {
        "fn": op_macro_scissors,
        "quote_key": "剪刀差",
    },
    "margin_balance_5d_change_rate": {
        "fn": op_margin_balance_5d,
        "quote_key": "5 日环比",
    },
    "index_amount_sum_rolling_pctile": {
        "fn": op_index_amount_sum_pctile,
        "quote_key": "滚动分位",
    },
    "downside_deviation_250_pctile": {
        "fn": op_downside_dev_pctile,
        "quote_key": "下行半偏差",
    },
    "daily_agg_series": {
        "fn": op_daily_agg,
        "quote_key": "聚合",
    },
    "sector_top_n_amount_share": {
        "fn": op_sector_top_n_amount_share,
        "quote_key": "之和 / 全族 amount 之和",
    },
    "sector_adjustment_progress_mean": {
        "fn": op_sector_adjustment_progress,
        "quote_key": "时间维=min(1, 距 60 日高点交易日数 / 8)",
    },
    "sector_relay_retreat_net_ratio": {
        "fn": op_sector_relay_retreat_ratio,
        "quote_key": "series 面=当日(接棒板块数−撤离板块数)/板块总数",
    },
    "agg4_state_ordinal_series": {
        "fn": op_agg4_state_ordinal_series,
        "quote_key": "本卡不重算阈值",
    },
    "rrg_quadrant_series": {
        "fn": op_rrg_quadrant_series,
        "quote_key": "series=当日 leading 占比 − lagging 占比",
    },
}


def run_binding_book(card: dict, entry: dict) -> tuple[pd.Series, dict]:
    """绑定册驱动取数：算子存在性+卡面引句双校验（引句不在卡内=拒绑，防我给自己发假绿）。"""
    op = entry.get("op")
    spec = OPS.get(op)
    if spec is None:
        raise ValueError(f"op_not_in_ops_book:{op}")
    q = str(entry.get("prose_quote") or spec["quote_key"])
    blob = _card_text(card)
    if q.replace(" ", "") not in blob.replace(" ", ""):
        raise ValueError(f"prose_quote_not_found_on_card:{op}:{q[:24]}")
    args = dict(entry.get("args") or {})
    composite_ev: dict | None = None
    if entry.get("legs"):
        # 复合族入口（批-A）：先按卡面冻结的共键装配多腿，再把腿面交给算子；判据值一律来自册 args。
        legs, composite_ev = assemble_composite_legs(
            card,
            entry["legs"],
            align=str((entry.get("combine") or {}).get("align") or "inner_on_keys"),
        )
        args["legs"] = legs
    ser, ev = spec["fn"](card, args)
    ev.update(op=op, prose_quote=q, reviewed_by=entry.get("reviewed_by"), review_note=entry.get("review_note"))
    if composite_ev is not None:
        ev.update(source="composite_legs", composite=composite_ev, combine=entry.get("combine") or {})
    return ser, ev


def _arm_protocol_module():
    """单点解析臂协议真源件模块：两条导入路径按同一次序试，皆败即 raise（禁静默降级成单臂）。

    次序有讲究：先仓根包名（测试与仓内调用方走这条），失败再退 fexam.*（跑批侧 sys.path 只挂
    scripts/backtest 时走这条）。反序或各走各的会让同一模块被两个名字各导一次＝同一类成为两个
    对象：抛出的 ArmFaceMismatch 与调用方 pytest.raises 里的类不同一（17:4x 落地面实测到），
    以及 isinstance(base, ArmBase) 判不出底座（21:5x 合成装配预证实测到：ArmBase * float 崩）。
    **装配函数与底座来源构造 ArmBase 必须走这一个解析器**，否则两端口径不同一。
    """
    import importlib

    for mod in ("scripts.backtest.fexam.arm_protocol_binding", "fexam.arm_protocol_binding"):
        try:
            return importlib.import_module(mod)
        except ImportError:
            continue
    raise ImportError("arm_protocol_binding 两条导入路径皆不可达＝双臂装配无法校验 e/r 位面，拒装配")


def _arm_pair_builder():
    return _arm_protocol_module().build_arm_pair


# ──────────────────────────────────────────────────────────────────────────────
# 级别序列回放适配器（WO-A1 最后一道缝：MOD-RK-049 在册件的日频腿）
#
# 卡面 02/06/07 一致声明"级别判定与迟滞解除按在册件回放，禁在考卷里重写判定逻辑"，
# 而在册件是**事件步进式类**（逐日 evaluate 才有迟滞/持续窗/min_hold 可言），
# 装置交出的是一条日频净值——两者之间缺的就是本函数。它只做三件事：
# 算回撤（卡面口径 净值/历史峰值-1）、逐日 evaluate、读 current；
# 零阈值定义、零状态迁移表、零降级规则——要改那些须改在册件本身。
#
# L4 不可解除近似随件：KILL 的唯一出口 request_manual_reset 需三项人工确认，回测面不存在，
# 故级别序列一旦进 KILL 即整窗驻留。该后果不靠注释自觉，由凭据面 kill_stuck_days 量化。
# ──────────────────────────────────────────────────────────────────────────────

#: 双臂档位名（绑定册 arms.params_* 里写 levels: "series:<档名>" 即按名注入底座交付的 series 槽）


def _cap_maps_identical(a: dict, b: dict) -> bool:
    """两张级别→仓位乘子表是否逐字同值（档位名与数值全对上才算同一张）。"""
    try:
        return {str(k): float(v) for k, v in a.items()} == {str(k): float(v) for k, v in b.items()}
    except (TypeError, ValueError):
        return False


DRAWDOWN_LEVEL_TIERS = {
    "levels_hysteresis": {"hysteresis": True, "reset": False},
    "levels_no_hysteresis": {"hysteresis": False, "reset": False},
    "levels_with_reset": {"hysteresis": True, "reset": True},
    "levels_no_hysteresis_with_reset": {"hysteresis": False, "reset": True},
}

_RECOVERY_RUNG_MAX_STEP = 2  # 阶梯 0→1→2→NORMAL，毕业即回 NORMAL（在册件 :516-517）

_RECOVERY_RUNG_CARD_KEYS = tuple(f"step_{i}" for i in range(_RECOVERY_RUNG_MAX_STEP + 1))

_RECOVERY_RUNG_LABELS = tuple(f"RECOVERY@{i}" for i in range(_RECOVERY_RUNG_MAX_STEP + 1))


def _card_ladder_triples(card: dict) -> dict[tuple[float, ...], str]:
    """卡面各处声明过的 RECOVERY 三档 cap（三元组→出处名），返回空表示卡面没冻结过阶梯面。

    为什么按"三元组集合"收：07b 卡面里阶梯出现在三处——`recovery_ladder`（在册 position_cap 的
    0.25/0.50/0.75）、带阶梯的五态表、以及**关臂**的"复位即一次买回"表（三档全 1.0，那是它的角色
    而不是缺陷）。臂表必须等于其中一条，等不上就是在册外面拍数。
    """
    tables = (card.get("data_binding") or {}).get("level_to_cap_map") or {}
    out: dict[tuple[float, ...], str] = {}
    for tname, tmap in tables.items() if isinstance(tables, dict) else []:
        if not isinstance(tmap, dict):
            continue
        rows = {str(k): v for k, v in tmap.items()}
        if all(k in rows for k in _RECOVERY_RUNG_CARD_KEYS):  # recovery_ladder 本身用步号做键
            out[tuple(_rung_cap(rows[k], f"{tname}:{k}") for k in _RECOVERY_RUNG_CARD_KEYS)] = f"{tname}(step_k 形)"
            continue
        if all(lbl in rows for lbl in _RECOVERY_RUNG_LABELS):
            out[tuple(_rung_cap(rows[lbl], f"{tname}:{lbl}") for lbl in _RECOVERY_RUNG_LABELS)] = str(tname)
    return out


def _ladder_label(state: str, step: int, *, is_reset_tier: bool, arm_cfg: str) -> str:
    """RECOVERY 态 → 带步号的档名；步号越界即红（阶梯表装不下时禁取模、禁就地扩表）。"""
    if state != "RECOVERY" or not is_reset_tier:
        return state  # 非复位档出现 RECOVERY 时原样交回，由调用处的词表闸判红——不在这里收
    if step > _RECOVERY_RUNG_MAX_STEP:
        raise RuntimeError(
            f"recovery_step_out_of_ladder:{step}@{arm_cfg}（在册阶梯 0->1->2->NORMAL，毕业即回 NORMAL；"
            "出现第 3 档＝档名表装不下，须先呈批补表，禁取模冒充）"
        )
    return f"RECOVERY@{step}"


def _level_tier_flags(arm_cfg: str) -> dict[str, bool]:
    """按档名取档位属性；未登档名即红（"未知档按无迟滞处理"那种静默降级就是不报错的错分）。"""
    flags = DRAWDOWN_LEVEL_TIERS.get(arm_cfg)
    if flags is None:
        raise RuntimeError(f"drawdown_level_arm_cfg_unknown:{arm_cfg}（合法档名={list(DRAWDOWN_LEVEL_SERIES_NAMES)}）")
    return flags


def _named_series_tiers(entry: dict) -> list[str]:
    """从册格两臂 params 里取被点名的档位名（值形如 "series:<档名>"）；一个都没有即红。"""
    arms = entry.get("arms") or {}
    names: list[str] = []
    for side in ("open", "base"):
        ref = (arms.get(f"params_{side}") or {}).get("levels")
        if isinstance(ref, str) and ref.startswith("series:"):
            names.append(ref[len("series:") :])
    if not names:
        raise RuntimeError(
            "arms_levels_not_named_by_book（两臂都没按 series:<档名> 点名级别序列来源，禁在底座来源里替册格选档）"
        )
    bad = sorted({n for n in names if n not in DRAWDOWN_LEVEL_TIERS})
    if bad:
        raise RuntimeError(
            f"series_tier_unknown:{bad}（在册档位={list(DRAWDOWN_LEVEL_SERIES_NAMES)}；"
            "新档须先登 DRAWDOWN_LEVEL_TIERS 并补卡面映射，禁册格先点名后补实现）"
        )
    return names


def _peak_trough_pairs(nav: pd.Series) -> list[tuple[float, float]]:
    """逐日 (历史峰值, 自该峰以来的谷值)——逐字镜像在册件 drawdown_tracker.py:276-287 的更新次序。

    只镜像"峰/谷怎么更新"这一件事实，本函数零阈值、零判据；等值性由
    tests/backtest/test_card_binding.py 拿真 `DrawdownTracker` 逐日对拍钉住（不靠注释自觉）。
    """
    pairs: list[tuple[float, float]] = []
    peak = trough = float(nav.iloc[0])
    for v in nav.tolist():
        if v > peak:
            peak, trough = v, v  # 新峰值 → 谷值随峰重置（在册 :280）
        if v < trough:
            trough = v
        pairs.append((peak, trough))
    return pairs


def _recovered_pct_values(nav: pd.Series, pairs: list[tuple[float, float]]) -> list[float]:
    """逐日回补比例＝**直调**在册公式件 `RiskLayerOrchestrator._recovered_pct`（:884-888）。

    直调而不在此重写：复位入口档（07b 括号 A=0.50／B=0.75）判的正是这条比值，本地另写一份
    就等于给判官喂第二个真源，生产面与考卷面从此可以各漂各的。
    """
    from zephyr.ex_core.risk_layer_orchestrator import RiskLayerOrchestrator  # noqa: PLC0415

    calc = RiskLayerOrchestrator._recovered_pct
    out: list[float] = []
    for v, (peak, trough) in zip(nav.tolist(), pairs, strict=True):
        dd = (v - peak) / peak if peak > 0 else 0.0  # 在册 tracker 的回撤口径（:287）
        out.append(float(calc(dd, v, peak, trough)))
    return out


def _replay_confirmation(sm: Any, arm_cfg: str, ts: pd.Timestamp):
    """复位申请的三项确认＝07b 卡面 `three_confirmation_faces_in_replay` 的逐件对应物。

    holdings_verified_zero 不靠自觉：读在册件自家的 `position_cap`（KILL 档=0.0，:323-324），
    它非 0 就说明当日并非"敞口实测为零"，那一次复位就不该发生（在册件会拒，这里不替它放行）。
    orders_cancelled_verified=日频装置无在途挂单概念，按卡面声明的"日频无在途"近似置真并随件披露；
    new_open_locked_verified=复位日起新仓受 RECOVERY 阶梯 cap 约束（由阶梯本身实现）。
    """
    from zephyr.risk.core.drawdown_state_machine import ResetConfirmation  # noqa: PLC0415

    return ResetConfirmation(
        confirmed_by=f"replay:{arm_cfg}@{ts.date().isoformat()}",
        override_reason="07b 日频净值回放面的复位申请（三项确认按卡面 three_confirmation_faces_in_replay 逐件对应）",
        holdings_verified_zero=float(sm.position_cap) == 0.0,
        orders_cancelled_verified=True,
        new_open_locked_verified=True,
    )


def _reset_entry_param(entry: dict, tiers: list[str]) -> float | None:
    """复位入口参数＝绑定册逐跑交（07b implementation_gap ③：两括号参数禁硬编）。

    四种组合只放行两种：无复位档且无参数（07 现面，逐字不变）、有复位档且有参数（07b）。
    "有复位档却无参数"＝括号没冻结；"没复位档却给了参数"＝两跑之间动了别的东西——两者都红。
    """
    arms = entry.get("arms") or {}
    raw = arms.get("reset_trigger_recovered_pct")
    needs = [t for t in tiers if DRAWDOWN_LEVEL_TIERS[t]["reset"]]
    if needs and raw is None:
        raise RuntimeError(
            f"reset_bracket_not_injected:{needs}（复位档缺绑定册的 reset_trigger_recovered_pct＝括号未冻结，不开考）"
        )
    if not needs and raw is not None:
        raise RuntimeError(
            f"reset_bracket_unused:{raw}（本跑没点复位档却收到复位参数＝跑与跑之间动了别的参数，裁定甲③禁的事）"
        )
    return None if raw is None else float(raw)


def _rung_cap(value: Any, where: str) -> float:
    """阶梯档值必须是数——`float(None)` 抛 TypeError 会把"卡面没给数值"洗成"调用面写错了"。

    红蓝对抗实测（2026-10-13）撞出来的同族错：pack 参数那一侧已修过一次，这里是第二遍。
    带引号的 "0.25" 也不放行：档位数值写成文字＝没冻结，禁 coerce 着继续跑。
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuntimeError(
            f"recovery_rung_cap_not_numeric:{where}（实得={value!r}＝档位数值缺失或写成文字，禁按 0/1 蒙一个继续跑）"
        )
    return float(value)


def _try_in_register_reset(sm: Any, ts: pd.Timestamp, recovered: float, trigger: float, arm_cfg: str) -> str:
    """KILL 且回补比例达入口档 → 经在册件唯一出口申请复位。

    返回 `"not_attempted"`（本日不该复位）／`"granted"`（在册件放行）／其余＝在册件给的拒因原文。
    守卫（冷却/窗内上限/永久锁定）**一律由在册件自己判**（:575-597），本函数一条都不复制；
    被拒不放行、不重试、不改参数——只把拒因计数进凭据面。复位史在 store=None 的纯内存面里
    由在册件自家 `_mem_reset_history`（:694-704）累积，故守卫在回放面同样真的生效、不是空转。
    """
    if not sm.kill_switch_closed or recovered < trigger:
        return "not_attempted"
    from zephyr.risk.core.drawdown_state_machine import RefuseResetError  # noqa: PLC0415

    try:
        sm.request_manual_reset(_replay_confirmation(sm, arm_cfg, ts), trade_date=ts.date())
    except RefuseResetError as exc:
        return f"{type(exc).__name__}: {str(exc)[:160]}"
    return "granted"


def _validate_recovery_ladder(card: dict, side: str, cap_map: dict, flags: dict) -> dict:
    """复位档乘子表的阶梯面校验＝07b 文字柱 `reset_not_full_reentry` 的机判面。

    数值一律不在这里定：册格给的三档 cap 必须**等于卡面某处冻结过的三元组**（见
    `_card_ladder_triples`），否则就是在本层替卡面拍数。在此之上对**开臂**加卡面自报的形状约束
    （严格递增、首档 <1.0）——这一柱管的就是"开臂复位后不许直接回满"，回满会让两臂在解除形状上
    同构、本卡只剩回撤阈值一条腿；关臂的 1.0/1.0/1.0 是它的声明角色，不受该形状约束。
    查不过即抛＝如实报错不出分，禁降级成"观测一行照样给分"。
    """
    if not flags["reset"]:
        return {}
    want_map = _card_ladder_triples(card)
    if not want_map:
        raise RuntimeError(
            f"recovery_ladder_face_missing:{card.get('card_id')}（复位档卡面必须冻结 RECOVERY 阶梯表，缺表即不开考）"
        )
    absent = sorted(lbl for lbl in _RECOVERY_RUNG_LABELS if str(lbl) not in {str(k) for k in cap_map})
    if absent:
        raise RuntimeError(
            f"recovery_rung_cap_unfrozen:{side}:{absent}（复位档乘子表须整表覆盖三档阶梯，禁跑到位次再替卡面拍值）"
        )
    triple = tuple(_rung_cap(cap_map[lbl], f"{side}:{lbl}") for lbl in _RECOVERY_RUNG_LABELS)
    if triple not in want_map:
        raise RuntimeError(
            f"recovery_rung_cap_off_card_face:{side}（册格={triple} 卡面只冻结过 "
            f"{ {v: k for k, v in want_map.items()} }，两表不同源即红）"
        )
    if side != "open":
        return {"rung_caps": list(triple), "declined_from": want_map[triple]}
    increasing = all(triple[i] < triple[i + 1] for i in range(len(triple) - 1))
    if not increasing or triple[0] >= 1.0:
        raise RuntimeError(
            f"reset_not_full_reentry_violated:open（卡面声明开臂阶梯须严格递增且首档<1.0，实得={triple}＝"
            "复位即回满与关臂同形，本卡从此只剩回撤阈值一条腿可判）"
        )
    return {"rung_caps": list(triple), "strictly_increasing": True, "first_rung_below_full": True}


DRAWDOWN_LEVEL_SERIES_NAMES = tuple(DRAWDOWN_LEVEL_TIERS)
#: 适配器允许的级别词表＝在册件 position_cap 的五态；出现表外态（含 RECOVERY）即红，禁静默扩档
_DRAWDOWN_STATE_VOCAB = ("NORMAL", "WARN", "DANGER", "CRISIS", "KILL")


def _drawdown_replay_config(arm_cfg: str, reset_recovered_pct: float | None):
    """按臂档给在册 config 类的字段值——**只赋值，不定义**：阈值一律沿在册默认。

    levels_no_hysteresis 的构造性取值须如实记账两处：hysteresis_ratio 的在册校验是开区间
    (0,1)，1.0 会被 InvalidDrawdownStateError 拒，故取 1-1e-9（半阈值≈触发阈值）；
    而"解除即回满"仍做不到——在册件的降级路径是逐级边（_DEESCALATION_PATH 无跳级边），
    这一条属卡面近似披露，不在本函数里绕。

    复位档另加一件：`graduation_face="absent"`（统筹 2026-10-13 路径 1，署名批准＋Owner 否决窗）。
    毕业准则腿要的是逐笔交易面，日频回放装置交不出；沿用缺省 `required` 档时本班实测阶梯永久停在
    0 档不动——那不是判据而是死锁。跳过必计数、必打点，凭据面可复核。
    """
    from zephyr.risk.core.drawdown_state_machine import DrawdownStateMachineConfig  # noqa: PLC0415

    flags = _level_tier_flags(arm_cfg)
    if flags["reset"] and reset_recovered_pct is None:
        raise RuntimeError(
            f"reset_tier_entry_param_missing:{arm_cfg}（复位档的入口 recovered_pct 须由绑定册逐跑注入，禁硬编也禁缺省）"
        )
    if not flags["reset"] and reset_recovered_pct is not None:
        raise RuntimeError(
            f"reset_param_on_non_reset_tier:{arm_cfg}（该档不复位却收到复位参数＝跑与跑之间动了别的参数，裁定甲③禁的事）"
        )
    kwargs: dict[str, Any] = {}
    if flags["reset"]:
        if not 0.0 < float(reset_recovered_pct) <= 1.0:
            raise RuntimeError(
                f"reset_trigger_recovered_pct_out_of_range:{reset_recovered_pct}"
                "（须∈(0,1]——在册 recovered_pct 的定义域见 :720，越界即无从比）"
            )
        kwargs["graduation_face"] = "absent"
    if not flags["hysteresis"]:
        kwargs.update(
            hysteresis_ratio=1.0 - 1e-9,
            sustained_warn=1,
            sustained_danger=1,
            sustained_crisis=1,
            min_hold_warn=1,
            min_hold_danger=1,
            min_hold_crisis=1,
        )
    return DrawdownStateMachineConfig(**kwargs)


def replay_drawdown_levels(
    nav: pd.Series,
    *,
    arm_cfg: str = "levels_hysteresis",
    reset_recovered_pct: float | None = None,
) -> tuple[pd.Series, dict]:
    """基线日净值 → 日频级别序列（在册态名；复位档带阶梯步号）＋可复核凭据。

    判定全在在册件本体里发生：升级、迟滞解除、阶梯晋升/回退、复位守卫都是 `DrawdownStateMachine`
    自家的方法。本函数只做三件事——算输入（回撤、回补比例）、喂 `evaluate`、读输出
    （`current`/`recovery_step`），零阈值定义、零状态迁移表、零复位分支。
    """
    from zephyr.risk.core.drawdown_state_machine import DrawdownStateMachine  # noqa: PLC0415

    s = pd.Series(nav).astype("float64").sort_index()
    if len(s) == 0:
        raise RuntimeError("drawdown_level_replay_empty_nav（无净值即无级别，禁以空序列冒充全程 NORMAL）")
    s.index = pd.DatetimeIndex(pd.to_datetime(s.index))
    n_nan = int(s.isna().sum())
    if n_nan:
        # NaN 会被下游读成"当日无回撤"＝把缺失伪装成最轻档，这里先红
        raise RuntimeError(f"drawdown_level_nav_has_nan:days={n_nan}")
    if bool((s <= 0).any()):
        raise RuntimeError("drawdown_level_nav_nonpositive（净值/峰值比值失去意义，禁继续回放级别）")

    flags = _level_tier_flags(arm_cfg)
    is_reset = bool(flags["reset"])
    cfg = _drawdown_replay_config(arm_cfg, reset_recovered_pct)
    sm = DrawdownStateMachine(None, cfg)  # store=None＝纯内存，零落盘零副作用
    dd = (s / s.cummax()) - 1.0
    recovered = _recovered_pct_values(s, _peak_trough_pairs(s))
    allowed = _DRAWDOWN_STATE_VOCAB + (_RECOVERY_RUNG_LABELS if is_reset else ())
    labels: list[str] = []
    n_transitions = 0
    first_kill: str | None = None
    resets_granted = 0
    refusals: list[dict[str, str]] = []
    ladder = {"promotions": 0, "retreats": 0, "graduated_to_normal": 0}
    for (ts, d), r in zip(dd.items(), recovered, strict=True):
        if is_reset:
            outcome = _try_in_register_reset(sm, ts, float(r), float(reset_recovered_pct), arm_cfg)
            if outcome == "granted":
                resets_granted += 1
            elif outcome != "not_attempted":
                refusals.append({"date": ts.date().isoformat(), "reason": outcome})
        # 只喂 drawdown_pct（＋在册口径的 recovered_pct）：统筹批复 A1 裁乙——var/cvar 两槽不喂
        # （全仓唯一日频真实调用点 sim_daily_runner.py:1410 同形），卡面"日亏 2%/4%/6%"系叙事改写非参数。
        # 想在此处补 var 的，须先改卡面 axis_feeding 并重新呈批，禁在适配器里静默改口径。
        transition = sm.evaluate(trade_date=ts.date(), drawdown_pct=float(d), recovered_pct=float(r))
        if transition is not None:
            n_transitions += 1
            reason = str(transition.reason)
            if reason.startswith("recovery_step_up_"):
                ladder["promotions"] += 1
            elif reason.startswith("recovery_retreat_"):
                ladder["retreats"] += 1
            elif reason == "recovery_graduated_new_high":
                ladder["graduated_to_normal"] += 1
        label = _ladder_label(sm.current.value, int(sm.recovery_step), is_reset_tier=is_reset, arm_cfg=arm_cfg)
        if label not in allowed:
            raise RuntimeError(
                f"drawdown_level_state_out_of_vocab:{label}@{ts.date()}（卡面五态映射表装不下该态＝"
                "须先补卡面映射并呈批，禁在适配器里静默扩档给数）"
            )
        if label == "KILL" and first_kill is None:
            first_kill = ts.date().isoformat()
        labels.append(label)

    levels = pd.Series(labels, index=s.index, name=arm_cfg)
    # L4 近似的量化：已进 KILL 且当日回撤其实已回到触发阈值以内的那些日＝人工复位本可放行的日子
    kill_stuck = 0
    if first_kill is not None:
        kill_stuck = int((levels.eq("KILL") & (dd.abs() <= cfg.kill_dd)).sum())
    state_days = {str(k): int(v) for k, v in levels.value_counts().sort_index().items()}
    creds: dict[str, Any] = {
        "arm_cfg": arm_cfg,
        "tier_flags": dict(flags),
        "n_days": int(len(levels)),
        "state_days": state_days,
        "transitions": n_transitions,
        "first_kill_date": first_kill,
        "kill_stuck_days": kill_stuck,
        "vocab": list(allowed),
        "recovered_pct_source": "峰/谷＝在册 drawdown_tracker.py:276-287 语义镜像；比值＝直调在册 risk_layer_orchestrator.py:884-888",
    }
    if is_reset:
        creds.update(
            {
                "reset_trigger_recovered_pct": float(reset_recovered_pct),
                "resets_granted": resets_granted,
                "resets_refused": len(refusals),
                "refusals_first8": refusals[:8],
                "ladder_promotions": ladder["promotions"],
                "ladder_retreats": ladder["retreats"],
                "graduated_to_normal": ladder["graduated_to_normal"],
                "recovery_rung_days": {k: v for k, v in state_days.items() if str(k).startswith("RECOVERY@")},
                "graduation_face": cfg.graduation_face,
                "graduation_face_skips": int(getattr(sm, "graduation_face_skips", -1)),
            }
        )
    return levels, creds


def drawdown_level_series_pack(
    nav: pd.Series,
    *,
    tier_names: list[str],
    reset_recovered_pct: float | None = None,
) -> tuple[dict[str, pd.Series], dict]:
    """一次净值输入 → 按绑定册点名的档位产级别序列＋逐档凭据，供底座来源填进 ArmBase.series。

    档位必须逐档点名、无"默认全集"：默认全产会让新档位悄悄进每一跑，07 的既有读数面从此不可比，
    而 07b 的复位入口参数又必须逐跑不同（括号 A/B）——两件事都指向"由册格说要哪几档"。
    """
    names = list(dict.fromkeys(tier_names))
    # 两道 pack 级红先过（"全都不复位却收到参数"与"有复位档却没参数"），
    # 再逐档分发：混合 pack（一臂复位、一臂不复位）里非复位档必须收 None，
    # 把参数原样递给每一档会被 replay 的 `reset_param_on_non_reset_tier` 当场弹（2026-10-13 零 CH 预演实测）
    needs = [n for n in names if _level_tier_flags(n)["reset"]]
    if needs and reset_recovered_pct is None:
        raise RuntimeError(
            f"reset_tier_entry_param_missing:{needs}（复位档的入口 recovered_pct 须由绑定册逐跑注入，禁硬编也禁缺省）"
        )
    if not needs and reset_recovered_pct is not None:
        raise RuntimeError(
            f"reset_param_on_non_reset_tier:{names}（本 pack 没有复位档却收到复位参数＝跑与跑之间动了别的参数）"
        )
    series: dict[str, pd.Series] = {}
    creds: dict[str, dict] = {}
    for name in names:
        # 参数只发给复位档；非复位档拿 None＝07 现面逐字不变
        series[name], creds[name] = replay_drawdown_levels(
            nav,
            arm_cfg=name,
            reset_recovered_pct=reset_recovered_pct if _level_tier_flags(name)["reset"] else None,
        )
    return series, creds


#: 双臂底座来源册（WO-A1 绑定侧半件）：名→可调用（按臂参数产日频敞口序列）。
#: 空册是**有意**的：底座只能由在册重放装置产出，禁在绑定层现编近似序列冒充分母
#: （arm_protocol_binding.ArmBaseMissing 同一纪律）。每接一个来源，须同批改
#: tests/backtest/test_card_binding.py 的接线用例与册格 arm_base_source 字段。


def _exit_sim_baseline(card: dict, entry: dict) -> Any:
    """底座来源＝在册离场仿真装置（06 卡 piece_1/2/3/4 的符号引用链落地处）。

    只搬运在册装置的输入与输出，零新撮合、零自拟参数：列提取仍受 prereg 冻结清单自校
    （run_all 同款断言），敞口与净值直接取 simulate 交出的 st["exposure_daily"] 与 nav。
    series 面（按册格点名的档位序列）由 `drawdown_level_series_pack(nav, tier_names=…)` 产出——那是**在册判定件**
    src/zephyr/risk/core/drawdown_state_machine.py 的日频回放适配器（WO-A1 三颗红证在册），
    本函数零判定/零迟滞/零复位分支逻辑；判定件若拒（空净值/NaN/词表外状态/复位守卫拒绝）异常照原样上抛，
    册格引用未交付的 "series:<名>" 仍在 _resolve_named_series 处抛 ArmParamUnfrozen（＝不开考，不是出错分）。
    """
    ArmBase = _arm_protocol_module().ArmBase  # 与装配侧同一模块对象，防类身份跨包名分裂
    from fexam.exit_sim.exit_simulator import (  # noqa: PLC0415
        atr14_wilder,
        build_signals,
        load_indicator,
        load_kline,
        load_pass_columns,
        simulate,
    )

    cols = load_pass_columns()
    if not cols:
        raise RuntimeError("exit_sim_baseline: 在册指标列提取为空（装置无输入，拒装配）")
    kline_open = load_kline("open")
    kline_high = load_kline("high")
    kline_low = load_kline("low")
    kline_close = load_kline("close")
    atr = atr14_wilder(kline_close, kline_high, kline_low)
    ind_panels = {k: v for k, v in ((k, load_indicator(k)) for k, _ in cols) if not v.empty}
    signals, close_run, reb_rows = build_signals(ind_panels, kline_close, atr)
    nav, st = simulate(
        kline_open.reindex(close_run.index),
        close_run,
        atr.reindex(close_run.index),
        signals,
        reb_rows,
        stop_enabled=True,
    )
    exposure = st.get("exposure_daily")
    if exposure is None:
        raise RuntimeError("exit_sim_baseline: 装置未交付 exposure_daily 返回面（返回面扩展未落地？）")
    daily_return = nav.astype("float64").pct_change().dropna()
    # 档位由册格点名（07＝两档迟滞对照，07b＝含复位档四跑各取所需），复位入口参数同样逐跑由册给
    tiers = _named_series_tiers(entry)
    levels, level_creds = drawdown_level_series_pack(
        nav, tier_names=tiers, reset_recovered_pct=_reset_entry_param(entry, tiers)
    )
    base = ArmBase(
        exposure=pd.Series(exposure).reindex(pd.DatetimeIndex(nav.index)),
        daily_return=daily_return,
        series=levels,
        face_id="exit_sim_baseline_nav",
    )
    # 级别回放凭据随底座走（两档各自的状态驻留日数/转换数/KILL 首现日与驻留日数），
    # 由 arms_from_binding_book 并进出分凭据——凭据可复核，判定零自造
    base.level_creds = level_creds
    return base


#: 双臂底座来源册（WO-A1 绑定侧半件）：名→可调用（按臂参数产日频敞口序列）。
#: 纪律演进（0081 原注"空册是有意，注册留给下一袋"——本袋即那一袋）：
#:   册内只准**在册已签认**的来源（统筹批复乙案批 06 卡＋甲链签认；装置返回面由救援袋落地），
#:   未列名一律 fail-closed（run_one 走 arm_base_source_unwired 如实报错，禁静默降级单臂、
#:   禁现编近似序列冒充分母）——与 ArmBaseMissing/ArmFaceMismatch 同一哲学。
ARM_BASE_SOURCES: dict[str, Any] = {"exit_sim_baseline": _exit_sim_baseline}


def arms_from_binding_book(
    card: dict, entry: dict, *, base: pd.Series, target: pd.Series
) -> tuple[pd.Series, pd.Series, pd.Series, dict]:
    """双臂卡三面装配：e 位＝逐臂敞口、e 位配对基臂、r 位＝底座日收益（WO-A1 适配器绑定侧）。

    语义校验（敞口 0..1、日收益量纲帽、e/r 引句必须各落在该卡面对应文本域）**全在真源件
    arm_protocol_binding 里做**，本函数一行判据都不重复实现（宪法 §4.2 同真源可派生→必并）；
    这里只干两件事：把调用方注入的底座/目标交过去，再把凭据并上绑定册的算子与引句。
    """
    arms_entry = entry.get("arms") or {}
    if not arms_entry:
        raise ValueError(f"arms_face_missing:{entry.get('card_id')}（册格未声明 arms 面，禁按单臂路径冒充双臂）")
    open_arm, base_arm, tgt, ev = _arm_pair_builder()(card, arms_entry, base=base, target=target)
    ev.update(
        arm_op_open=ev["op"]["open"],
        arm_op_base=ev["op"]["base"],
        reviewed_by=entry.get("reviewed_by"),
        review_note=entry.get("review_note"),
        arm_target_len=int(len(tgt)),
        arms_variant=entry.get("arms_variant_applied"),
        arm_level_creds=getattr(base, "level_creds", None),
    )
    return open_arm, base_arm, tgt, ev


def arm_context_for_judge(card: dict, entry: dict, base: Any) -> dict | None:
    """双臂判官三柱的**读数上下文**（统筹裁定③ 2026-10-12：三柱机器面立项，归本班域）。

    三柱（`maxdd_improvement_vs_no_hysteresis_min_pp`／`whipsaw_roundtrip_ratio_max`／
    `missed_crisis_trigger_max`）判的是**级别序列的时序形状**与"该臂用的是哪一档级别序列"，
    这些量只存在于底座交付面 `ArmBase.series`（由在册判定件 MOD-RK-049 回放产出）与绑定册
    逐臂点名的 `params_*.levels`／`level_map` 里。本函数**只搬运不重算**：按册格点名的档名
    从底座取序列，判官侧绝不按名再取一次底座（那是第二真源，违宪法 §4.2）。
    任一件缺位即返回 None——判官对 None 记显式败（禁静默跳），与 arm_base_source_unwired 同一哲学。

    07b 追加两件（implementation_gap ②③）：档位属性**申报**进上下文（判官禁按档名猜），
    复位档的阶梯乘子表逐字对卡面校验（不符即抛，不给分）。
    """
    arms = entry.get("arms") or {}
    pool = getattr(base, "series", None)
    if not isinstance(pool, dict):
        return None
    ctx: dict[str, Any] = {"levels": {}, "cap_map": {}, "level_source": {}, "tier_flags": {}, "recovery_ladder": {}}
    for side in ("open", "base"):
        params = arms.get(f"params_{side}") or {}
        raw = params.get("levels")
        # 只认字面量档名："series:<名>"。裸 Series/None/数字一律拒（禁在此处既收名字又收序列——
        # 收了序列就等于允许调用方自带一份级别真源，判官读数不再是"在册回放件的输出"）
        ref = raw if isinstance(raw, str) else ""
        if not ref.startswith("series:"):
            return None
        name = ref[len("series:") :]
        if name not in pool:
            return None
        cmap = params.get("level_map")
        if not isinstance(cmap, dict) or not cmap:
            return None
        flags = _level_tier_flags(name)
        ctx["levels"][side] = pool[name]
        ctx["cap_map"][side] = cmap
        ctx["level_source"][side] = name
        ctx["tier_flags"][side] = dict(flags)
        ctx["recovery_ladder"][side] = _validate_recovery_ladder(card, side, cmap, flags)
    # `base_arm_cfg` 的契约＝**迟滞族档名**（判官按它认"基臂是不是无迟滞对照腿"），不是册内序列名：
    # 复位档的真实册名是 `levels_no_hysteresis_with_reset`，把册名直接交给只认
    # `== "levels_no_hysteresis"` 的落地面判官，会让 07b 的 off 与 mid 两跑都把柱一/柱二推给对方
    # ⇒ 两跑互让＝零判（假绿面，非报错面）。真实册名不丢：见 ctx["level_source"]。
    # 显式布尔 `base_is_no_hysteresis` 留给扩面判官（待投腿）读，两者在 07 面逐字等价。
    ctx["base_arm_cfg"] = "levels_no_hysteresis" if not ctx["tier_flags"]["base"]["hysteresis"] else "levels_hysteresis"
    ctx["base_arm_cfg_tier"] = ctx["level_source"]["base"]
    ctx["level_source_open"] = ctx["level_source"]["open"]
    # 迟滞/复位属性由档位册显式申报，判官禁按档名字符串猜：`levels_no_hysteresis_with_reset`
    # 拿 == "levels_no_hysteresis" 去匹配会读成"不是无迟滞档"⇒ 三柱静默不判＝假绿面，必须堵住
    ctx["base_is_no_hysteresis"] = not ctx["tier_flags"]["base"]["hysteresis"]
    ctx["open_is_no_hysteresis"] = not ctx["tier_flags"]["open"]["hysteresis"]
    ctx["reset_trigger_recovered_pct"] = arms.get("reset_trigger_recovered_pct")
    # 同一条级别序列不天然非法：07/07b 卡面都声明"臂间差异只允许出现在级别→cap 乘子表"，
    # off 配对正是同一序列×两张不同乘子表。真非法的是两面——见下面两条各自的解释。
    if ctx["level_source"]["open"] == ctx["level_source"]["base"]:
        if _cap_maps_identical(ctx["cap_map"]["open"], ctx["cap_map"]["base"]):
            raise ValueError(
                f"arms_identical_source_and_map:{ctx['level_source']['open']}（两臂连档位与乘子表都逐字相同＝"
                "单臂卡冒充双臂，判官拿到的差恒为 0）"
            )
        if not ctx["tier_flags"]["base"]["hysteresis"]:
            raise ValueError(
                f"arm_levels_same_source:{ctx['level_source']['open']}（迟滞对照跑的两臂引用同一条级别序列＝"
                "常数 0 差会被读成「迟滞带无增益」，该配对必须由两档分别回放）"
            )
    ctx["creds"] = getattr(base, "level_creds", None)
    ctx["arms_variant"] = entry.get("arms_variant_applied")
    return ctx


def load_binding_book(path: Path, arms_variant: str | None = None) -> dict[str, dict]:
    """绑定册读取＋按跑配对选择器（统筹裁定 2026-10-12 甲案③：跑与跑之间禁动其他参数）。

    变体词表是**按卡冻结**的：07 只有 off/mid，07b 有 off_A/off_B/mid_A/mid_B，两卡共用一本册。
    选择器判据因此是"全局有没有这一档"而不是"每一张双臂卡都得有这一档"——
    ①`arms_variant` 为 None 却有任一变体格 → 拒（禁默认取第一档）；
    ②`arms_variant` 在全册任何一格都找不到 → 拒（这是打字错，比静默少跑一张卡危险）；
    ③`arms_variant` 存在但某张卡的词表不含它 → **跳过该卡**（本跑就是不含它，不是错），
      含它的卡正常装配。跳过绝不降级成单臂：调用方拿到"册里没这张"会走 classify，
      而双臂卡 classify 不出双臂面，出不了分（fail-closed，与 arm_base_source_unwired 同哲学）。
    """
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = [e for e in (data.get("entries") or []) if isinstance(e, dict) and e.get("card_id")]
    variant_entries = [e for e in entries if e.get("arms_variants") is not None]
    if variant_entries and arms_variant is None:
        named = sorted({str(e.get("card_id")) for e in variant_entries})
        raise ValueError(f"arms_variant_required:{named}（这些格配对按跑显式化，须 --arms-variant 指名，禁默认第一档）")
    all_variants = {v for e in variant_entries for v in (e.get("arms_variants") or {})}
    if arms_variant is not None and variant_entries and arms_variant not in all_variants:
        raise ValueError(
            f"arms_variant_typo:{arms_variant}（全册在册档名并集={sorted(all_variants)}；"
            "一根都没命中＝打字错，禁当成'本跑不含双臂卡'静默少跑一张）"
        )
    book = {}
    for e in entries:
        if e.get("status") != "approved":
            continue
        variants = e.get("arms_variants")
        if variants is not None:
            if e.get("arms"):
                raise ValueError(
                    f"arms_pairing_ambiguous:{e.get('card_id')}（同格并存 arms 与 arms_variants＝"
                    "哪一跑在跑说不清，禁隐式取舍）"
                )
            chosen = (variants or {}).get(arms_variant)
            if not chosen:  # 该卡词表没这一档＝本跑不装它（按卡冻结，非错误）
                continue
            e = {**e, "arms": chosen, "arms_variant_applied": arms_variant}
        book[str(e["card_id"])] = e
    return book


def _judgment_snapshot(card: dict) -> dict:
    return {k: card.get(k) for k in JUDGMENT_KEYS}


def run_one(
    card_path: Path,
    approve: set[str],
    scores_path: Path,
    run_tag: str,
    dry: bool,
    book: dict[str, dict] | None = None,
    force: bool = False,
    recorded_by: str = "",
) -> dict:
    card = yaml.safe_load(card_path.read_text(encoding="utf-8"))
    cid = str(card.get("card_id"))
    if cid not in approve:
        return {"card_id": cid, "skipped": "not_in_approve_list"}
    if card.get("status") == "examined" and not force:
        # 在册坑（夜矿交接卡 §三.3：冒烟未隔离会翻卡状态而分数册无行＝账面不一致）⇒
        # 已考卡必须显式 --force 才允许重跑；分数册 only-add 旧行保留、新行追加、试次照计
        return {"card_id": cid, "skipped": "already_examined_needs_force"}
    entry = (book or {}).get(cid)
    if entry is not None:
        cls = {
            "cls": "BOOK",
            "reason": None,
            "recipe": f"binding_book:{entry.get('op')}",
            "op": entry.get("op"),
            "tables": tables_of(str((card.get("data_binding") or {}).get("signal_table", ""))),
        }
    else:
        cls = classify_card(card)
        if cls["cls"] not in _BINDABLE_CLASSES:
            return {"card_id": cid, "skipped": f"class_{cls['cls']}", "reason": cls["reason"]}
    if dry:
        return {"card_id": cid, "dry_run": True, "class": cls["cls"], "recipe": cls["recipe"], "op": cls["op"]}
    before = _judgment_snapshot(card)
    sig_b: pd.Series | None = None
    arm_ctx: dict | None = None
    tgt: pd.Series | None = None  # 双臂通道在 try 里就交回底座日收益；其余通道走下面的指数面
    try:
        if entry is not None and entry.get("arms"):
            # 双臂通道（WO-A1）：底座敞口序列须由在册重放装置按臂参数产出后注入；
            # 来源未接线时**如实报错不出分**——静默降级成单臂就是给判官喂错面
            src = str(entry.get("arm_base_source") or "")
            if src not in ARM_BASE_SOURCES:
                return {
                    "card_id": cid,
                    "error": f"arm_base_source_unwired:{src or '(empty)'}（双臂卡须声明底座来源且该来源已在 ARM_BASE_SOURCES 接线）",
                }
            src_obj = ARM_BASE_SOURCES[src](card, entry)
            # r 位（甲案第 5 步）：新来源自报底座日收益＝与 e 位同一次装置调用产出，
            # 不再硬编外部指数；旧形状（裸 Series）来源仍走旧通道，由身份断言闸只管新面。
            tgt_arm = getattr(src_obj, "daily_return", None)
            if tgt_arm is None:
                tgt_arm = index_next_day_return()
            sig, sig_b, tgt, ev = arms_from_binding_book(card, entry, base=src_obj, target=tgt_arm)
            # 三柱读数上下文（裁定③）：起始面自证注入了什么（档名/变体/序列长度），不落 Series 本体进 yaml
            arm_ctx = arm_context_for_judge(card, entry, src_obj)
            ev["arm_context_injected"] = {
                "present": arm_ctx is not None,
                "base_arm_cfg": (arm_ctx or {}).get("base_arm_cfg"),
                "arms_variant": (arm_ctx or {}).get("arms_variant"),
                "level_source": (arm_ctx or {}).get("level_source"),
                # 跑次判别面（07b 四跑＝2 复位括号 × 2 配对档）：括号入口值与档位属性必须逐跑显形，
                # 否则四行分数长得一样、事后无从分辨哪一跑用的哪一档入口（裁定甲③的可核账要求）
                "tier_flags": (arm_ctx or {}).get("tier_flags"),
                "base_is_no_hysteresis": (arm_ctx or {}).get("base_is_no_hysteresis"),
                "reset_trigger_recovered_pct": (arm_ctx or {}).get("reset_trigger_recovered_pct"),
                "recovery_ladder": (arm_ctx or {}).get("recovery_ladder"),
                "levels_len": {
                    k: int(len(v)) for k, v in ((arm_ctx or {}).get("levels") or {}).items() if v is not None
                },
            }
        elif entry is not None:
            sig, ev = run_binding_book(card, entry)
        else:
            sig, ev = build_signal(card, cls)
    except Exception as exc:  # noqa: BLE001
        return {"card_id": cid, "error": f"bind:{type(exc).__name__}:{str(exc)[:180]}"}
    if sig is None or len(sig) == 0:
        return {"card_id": cid, "error": "binding_rejected_empty_signal", **ev}
    nan_ratio = float(pd.Series(sig).isna().mean())
    if nan_ratio > 0.5:
        return {"card_id": cid, "error": f"binding_rejected_quality:nan_ratio={nan_ratio:.3f}", **ev}
    if tgt is None:
        # 单臂/册格通道的 r 位＝外部指数次日收益（那些卡面就是这么声明的）。
        # 双臂通道**绝不能**走到这里：它的 r 位已由 `arms_from_binding_book` 交出底座日收益
        # （卡面"三臂共用同一基线净值路径"），覆盖成指数面就把风控实验量成了择时面——
        # 2026-10-13 零 CH 预演实测这行曾无条件执行（红证见 tests ::test_arms_path_target_is_base_daily_return_not_index）
        tgt = index_next_day_return()
    from fexam.calibration_exam import run_card

    row = run_card(
        card_path,
        signal=sig,
        signal_b=sig_b,
        target=tgt,
        run_id=f"mineloop-{run_tag}-{cid.split('/')[-1][:20]}",
        recorded_by=recorded_by or "card_binding_unattributed",
        scores_path=scores_path,
        force=force,
        arm_context=arm_ctx,
    )
    after = _judgment_snapshot(yaml.safe_load(card_path.read_text(encoding="utf-8")))
    if json.dumps(before, sort_keys=True, default=str) != json.dumps(after, sort_keys=True, default=str):
        raise BindingIntegrityError(f"出分后卡面判据集被改：{cid}（分数册只增不改，本卡中止须人工复核）")
    return {
        "card_id": cid,
        "verdict": row.get("verdict"),
        "binding": ev,
        "metrics": {k: row.get("metrics", {}).get(k) for k in ("ic_mean", "mono_spearman", "n", "oos_ic", "regime_ic")},
    }


def _in_ch_yield_window(now: datetime) -> str | None:
    if now.hour == 21 or (now.hour == 22 and now.minute < 30):
        return "21:00-22:30 W1 v2 提前窗让路（真源=examcard_campaign/00_campaign_ledger.md 20:55 段）"
    if 1 <= now.hour < 4:
        return "01:00-04:00 夜跑让路窗（矿考循环班令 §三 红线）"
    return None


def build_vocab_census(cards_dir: Path) -> dict:
    """门柱词表普查（WO-V 词表立法的机生底座；宪法 §9.5=条目清单必须生成器产出，禁手抄）。

    只普查三件事：①每张卡的判官路由（直调 calibration_exam.pillars_route，禁抄第二份分派式）；
    ②卡面 pillars_numeric 的**键名**在该路由词表的哪一侧；③文字门柱 pillars 的键名与条数。
    硬约束：零写阈值（键值属卡面冻结面，改值=新版本卡走 G4-5）、零改判据、零 CH、零分数册与卡件写。"""
    from collections import Counter

    from fexam.calibration_exam import _CALIBRATION_JUDGED_KEYS, _EVENT_KNOWN_KEYS, _UNION_PILLAR_KEYS, pillars_route

    vocab = {
        "series": set(_CALIBRATION_JUDGED_KEYS),
        "dual_arm": set(_UNION_PILLAR_KEYS),
        "event": set(_EVENT_KNOWN_KEYS),
    }
    rows: list[dict] = []
    unk_keys: Counter = Counter()
    tally = {"route": Counter(), "family": Counter(), "status": Counter()}
    n_card = n_empty = 0
    for p in sorted(Path(cards_dir).rglob("*.yaml")):
        try:
            c = yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 — 非卡件（frontmatter 册/不可解析）跳过
            continue
        if not isinstance(c, dict) or not c.get("card_id"):
            continue
        n_card += 1
        pn = c.get("pillars_numeric") or {}
        route = pillars_route(c)
        tally["route"][route] += 1
        tally["family"][str(c.get("family"))] += 1
        tally["status"][str(c.get("status"))] += 1
        if not pn:
            n_empty += 1
            continue
        unknown = sorted(set(pn) - vocab[route])
        if unknown:
            unk_keys.update(unknown)
            prose = c.get("pillars")
            rows.append(
                {
                    "card_id": c["card_id"],
                    "family": c.get("family"),
                    "signal_kind": c.get("signal_kind"),
                    "status": c.get("status"),
                    "route": route,
                    "keys_outside_route_vocab": unknown,
                    "numeric_key_count": len(pn),
                    "prose_pillar_keys": sorted(prose) if isinstance(prose, dict) else [],
                }
            )
    rows.sort(key=lambda r: (-len(r["keys_outside_route_vocab"]), str(r["card_id"])))
    return {
        "schema_version": "mineloop-pillar-vocab/v1",
        "generated_by": "python scripts/backtest/fexam/card_binding.py --mode vocab-census --cards-dir <exam_cards> --out <本件>",
        "generated_at": datetime.now().isoformat(timespec="minutes"),
        "vocab_sources": {
            "series": sorted(vocab["series"]),
            "dual_arm": sorted(vocab["dual_arm"]),
            "note": "三侧词表直读执行核常量 _CALIBRATION_JUDGED_KEYS（校准判官）/_UNION_PILLAR_KEYS（双臂判官，03:3x 裁定①并为并集），本件不复制定义",
        },
        "card_total": n_card,
        "cards_without_numeric_face": n_empty,
        "cards_with_keys_outside_route_vocab": len(rows),
        "unique_keys_outside_vocab": len(unk_keys),
        "tally_route": dict(tally["route"]),
        "tally_family": dict(tally["family"]),
        "tally_status": dict(tally["status"]),
        "unknown_key_census": [
            {"key": k, "cards": v} for k, v in sorted(unk_keys.items(), key=lambda kv: (-kv[1], kv[0]))
        ],
        "rows": rows,
        "discipline": {
            "threshold_values_written": 0,
            "cards_modified": 0,
            "ch_queries": 0,
            "route_expression_copies": "1（pillars_route 单一真源，普查与判决同式）",
            "purpose": "词表立法工单（WO-V）的输入面：哪些卡面冻结键名当前无任何机判面覆盖——立法=补面与命名对齐，禁改键值",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mode", choices=("classify", "run", "vocab-census"), required=True)
    ap.add_argument("--cards-dir", default=str(CARDS_DIR))
    ap.add_argument("--out", required=True, help="普查/凭据输出 yaml（禁 .json，docs/_working 纪律）")
    ap.add_argument("--approve-list", help="run 面：点名卡清单（每行一个 card_id）")
    ap.add_argument("--binding-book", help="run 面：绑定册 yaml（entries[].op+args+prose_quote+status=approved）")
    ap.add_argument(
        "--arms-variant",
        default="",
        help="run 面：一卡多对臂对照时指名本跑的配对档（绑定册 arms_variants 的键）；"
        "未指名即拒装配件，禁默认取第一档（统筹裁定 2026-10-12 甲案③）",
    )
    ap.add_argument("--scores", help="run 面：分数册路径（显式必填，禁默认主区面）")
    ap.add_argument("--tag", default=datetime.now().strftime("%H%M"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--override-ch-window-with-reason", default="")
    ap.add_argument("--force", action="store_true", help="已考卡重跑：分数册 only-add 追加新行，禁改旧行")
    ap.add_argument(
        "--recorded-by",
        default="",
        help="run 面：试次台账的归属会话 sid（显式必填）。旧版把该字段写死成上一班 sid＝台账面归属"
        "篡改（在册缺陷登记＝mineloop2_campaign 班账 §33.9 尾段），修法＝参数化且不猜默认值。",
    )
    args = ap.parse_args()

    cards_dir = Path(args.cards_dir)
    if args.mode == "vocab-census":
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        out = build_vocab_census(cards_dir)
        Path(args.out).write_text(
            yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=140), encoding="utf-8", newline="\n"
        )
        print(json.dumps({"cards": out["card_total"], "out": args.out}, ensure_ascii=False))
        return 0
    rows = []
    for p in sorted(cards_dir.rglob("*.yaml")):
        try:
            c = yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        allowed = ("preregistered", "examined") if args.force else ("preregistered",)
        if not isinstance(c, dict) or c.get("status") not in allowed:
            continue
        cls = classify_card(c)
        rows.append(
            {"card_id": c.get("card_id"), "family": c.get("family"), "path": str(p.relative_to(RUN_ROOT)), **cls}
        )
    tally = {k: sum(1 for r in rows if r["cls"] == k) for k in _CENSUS_CLASSES}

    if args.mode == "classify":
        out = {
            "schema_version": "mineloop-binding-census/v1",
            "built_by": "scripts/backtest/fexam/card_binding.py",
            "card_total_preregistered": len(rows),
            "tally": tally,
            "rows": rows,
        }
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(
            yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=140), encoding="utf-8", newline="\n"
        )
        print(json.dumps({"tally": tally, "out": args.out}, ensure_ascii=False))
        return 0

    win = _in_ch_yield_window(datetime.now())
    if win and not args.override_ch_window_with_reason:
        print(json.dumps({"refused": win}, ensure_ascii=False))
        return 3
    if not args.scores:
        print(json.dumps({"error": "run 面必须显式 --scores（禁默认主区 SCORES_PATH）"}, ensure_ascii=False))
        return 2
    if not args.recorded_by and not args.dry_run:
        print(
            json.dumps(
                {
                    "error": "recorded_by_required：run 面必须显式 --recorded-by <本班 sid>"
                    "（试次台账归属字段禁写死、禁猜默认）"
                },
                ensure_ascii=False,
            )
        )
        return 2
    approve = {l.strip() for l in Path(args.approve_list).read_text(encoding="utf-8").splitlines() if l.strip()}
    book = (
        load_binding_book(Path(args.binding_book), arms_variant=(args.arms_variant or None))
        if args.binding_book
        else {}
    )
    results = []
    seen = {r["card_id"] for r in rows}
    for cid in sorted(approve - seen):
        results.append({"card_id": cid, "skipped": "not_enumerated_not_preregistered_or_absent"})
    for r in rows:
        res = run_one(
            Path(RUN_ROOT) / r["path"],
            approve,
            Path(args.scores),
            args.tag,
            args.dry_run,
            book,
            args.force,
            args.recorded_by,
        )
        results.append(res)
        print(json.dumps(res, ensure_ascii=False, default=str)[:400], flush=True)
    out = {
        "schema_version": "mineloop-binding-run/v1",
        "ch_window_override": args.override_ch_window_with_reason,
        "requested": sorted(approve),
        "results": results,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(
        yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=140), encoding="utf-8", newline="\n"
    )
    scored = sum(1 for r in results if "verdict" in r)
    print(json.dumps({"scored": scored, "out": args.out}, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  人工CLI驱动器（按需触发开考），非常驻自动系统
    sys.exit(main())
