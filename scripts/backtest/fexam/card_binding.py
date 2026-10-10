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

import pandas as pd
import yaml

from zephyr.data.table_registry import get_registry

HERE = Path(__file__).resolve().parent
RUN_ROOT = HERE.parents[2]
if str(RUN_ROOT / "scripts" / "backtest") not in sys.path:
    sys.path.insert(0, str(RUN_ROOT / "scripts" / "backtest"))

CARDS_DIR = RUN_ROOT / "docs" / "03_modules" / "_domain_backtest" / "exam_cards"
SERIES_DIR = RUN_ROOT / "docs" / "_working" / "nightmine_campaign" / "series"

#: 表名面唯一真源=TableRegistry（品类 id 派生全限定名；业务代码禁字面量表名——TABLE-NAME-REGISTRY 门约束）
_TBL = {
    c: get_registry().table(c)
    for c in ("market_index_kline", "market_index_valuation_daily", "market_news_sentiment_window")
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
}
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
    horizon = _HORIZON_RE.search(str((card.get("target") or {}).get("primary") or ""))
    if not _INDEX_TARGET_RE.search(tgt) and not _INDEX_TARGET_RE.search(
        str((card.get("target") or {}).get("primary") or "")
    ):
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
        if col_raw == hint or declared == hint or col_raw.startswith(hint + "_derived"):
            if (SERIES_DIR / fname).exists():
                return {"cls": "D", "reason": None, "recipe": "local_series_csv", "op": f"file={fname}", "tables": tl}
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
}


def build_signal(card: dict, cls: dict) -> tuple[pd.Series | None, dict]:
    """按分类结果取数（run 面专用；返回 series + 凭据）。"""
    from fexam.ch_data import ch_query_df

    b = card["data_binding"]
    ev: dict = {"recipe": cls["recipe"], "op": cls["op"], "tables": cls["tables"]}
    if cls["recipe"] == "local_series_csv":
        fname = cls["op"].split("=", 1)[1]
        ev.update(source="local_csv", file=str(SERIES_DIR / fname))
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


#: 算子册（每格都逐字引用卡面 signal_derivation 原文，禁自创口径；新增算子须同步测试）
OPS: dict[str, dict] = {
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
    ser, ev = spec["fn"](card, entry.get("args") or {})
    ev.update(op=op, prose_quote=q, reviewed_by=entry.get("reviewed_by"), review_note=entry.get("review_note"))
    return ser, ev


def load_binding_book(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    book = {}
    for e in data.get("entries") or []:
        if not isinstance(e, dict) or not e.get("card_id"):
            continue
        if e.get("status") != "approved":
            continue
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
    try:
        if entry is not None:
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
    tgt = index_next_day_return()
    from fexam.calibration_exam import run_card

    row = run_card(
        card_path,
        signal=sig,
        target=tgt,
        run_id=f"mineloop-{run_tag}-{cid.split('/')[-1][:20]}",
        recorded_by="st-mineloop-20261010",
        scores_path=scores_path,
        force=force,
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mode", choices=("classify", "run"), required=True)
    ap.add_argument("--cards-dir", default=str(CARDS_DIR))
    ap.add_argument("--out", required=True, help="普查/凭据输出 yaml（禁 .json，docs/_working 纪律）")
    ap.add_argument("--approve-list", help="run 面：点名卡清单（每行一个 card_id）")
    ap.add_argument("--binding-book", help="run 面：绑定册 yaml（entries[].op+args+prose_quote+status=approved）")
    ap.add_argument("--scores", help="run 面：分数册路径（显式必填，禁默认主区面）")
    ap.add_argument("--tag", default=datetime.now().strftime("%H%M"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--override-ch-window-with-reason", default="")
    ap.add_argument("--force", action="store_true", help="已考卡重跑：分数册 only-add 追加新行，禁改旧行")
    args = ap.parse_args()

    cards_dir = Path(args.cards_dir)
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
    approve = {l.strip() for l in Path(args.approve_list).read_text(encoding="utf-8").splitlines() if l.strip()}
    book = load_binding_book(Path(args.binding_book)) if args.binding_book else {}
    results = []
    seen = {r["card_id"] for r in rows}
    for cid in sorted(approve - seen):
        results.append({"card_id": cid, "skipped": "not_enumerated_not_preregistered_or_absent"})
    for r in rows:
        res = run_one(Path(RUN_ROOT) / r["path"], approve, Path(args.scores), args.tag, args.dry_run, book, args.force)
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
