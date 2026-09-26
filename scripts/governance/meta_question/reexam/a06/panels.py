# [BLUEPRINT] MOD-METAQ-REEXAM-A06 | docs/_working/meta_question_answers/gaps/A06_MONEYFLOW_BACKFILL_workbook.md §3
# [MODULE] scripts.governance.meta_question.reexam.a06.panels
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pandas; numpy; zephyr.infrastructure.database_service (CH reader 只读)
# [CONSUMERS] scripts.governance.meta_question.reexam.a06.exam_a06（A06 族 6 问复考器）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] PIT 硬约束：所有取数 SQL 的 trade_date 上界恒等于闭卷切点（默认 2025-09-09），
#              且 load_panels 装载后对面板真实端点二次断言（越界即 AssertionError，禁"事后清洗"）；
#              money_flow 是 ReplacingMergeTree → 查询一律 FINAL；
#              价格真源=c1_market.kline_daily(不复权 close) × c1_market.adj_factor（后复权自算），
#              money_flow.close/pct_change 恒 0 绝不作价格用（tushare moneyflow 接口不提供）；
#              信号口径=表内 main_net_inflow_pct（主力=大单+超大单净买 ÷ 主力档毛成交×100，
#              与 tushare_provider._fetch_money_flow 及 backfill_money_flow_history 同式）；
#              前瞻收益=wide.shift(-n)/wide-1（交易日历对齐；停牌端点无行→NaN→该名该日剔除，
#              禁把停牌期算进收益窗）；
#              全 SQL 文本随 A06Panels.sqls 导出（重放核对），取数顺序恒 ORDER BY trade_date,symbol；
#              池口径主判=全 A 现价池（题面"全 A 池"，同 PQ-0110 先例无 ST/退市过滤），
#              ST/次新/涨跌停/流动性过滤仅作稳健性变体 pool_variant_st_cn（不改主判据）
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 切点违规/空结果→raise（复考须 fail-visible，禁静默降级为空面板）；
#                  掩码表缺失→该掩码退化为不过滤并写 meta.warnings 记账
# [TESTS] python scripts/governance/meta_question/reexam/a06/exam_a06.py --selftest
# [A_module] module_id=MOD-METAQ-REEXAM-A06 | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""A06 复考面板装载：主力净流入信号 + 后复权价 + 前瞻收益 + 覆盖率/口径版本存证。

接口（六问共用一次装载，保证同输入同输出）：
    from panels import load_panels, PIT_CUTOFF_DEFAULT
    p = load_panels(conn, start="2021-01-04", cutoff=PIT_CUTOFF_DEFAULT, horizons=(1, 5, 20))
    p.signal / p.inflow        # 日期×symbol 宽表：主力净流入占比(%) / 净流入额(万元)
    p.adj_close / p.close_raw / p.amount
    p.fwd(n)                   # n 交易日前瞻收益（端点停牌→NaN）
    p.pool("main"|"variant")   # 池掩码（主判=全 A 现价池；变体=ST/次新/涨跌停/流动性过滤）
    p.coverage                 # 逐日样本量与信号分布存证
    p.version_census           # data_source 版本标记实测 + ingest 批次 + PIT 探针
    p.sqls                     # 全部取数 SQL 文本
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Sequence
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from zephyr.data.table_registry import TableRegistry  # noqa: E402

PIT_CUTOFF_DEFAULT = "2025-09-09"
MIN_NAMES_DEFAULT = 300
# 稳健性变体参数（不进主判据）
MIN_LISTED_DAYS = 120  # 次新剔除：上市满 120 个日历日（≈100 交易日）
MIN_DAILY_AMOUNT = 1e7  # 成交额 ≥1000 万（zephyr.factor.analysis.multifactor_tradability_mask 同源阈值）

_SIG_COLS = ["trade_date", "symbol", "main_net_inflow", "main_net_inflow_pct"]
_PX_COLS = ["trade_date", "symbol", "close_raw", "adj_close", "amount"]
_LIM_COLS = ["trade_date", "symbol", "limit_up", "limit_down", "st_flag"]


# 表名唯一真源 = TableRegistry 品类册（#ARCH-CH-024 Phase 5：禁硬编码全限定表名）
_T_MONEY_FLOW = TableRegistry().table("market_money_flow")
_T_KLINE_DAILY = TableRegistry().table("market_kline_daily")
_T_ADJ_FACTOR = TableRegistry().table("market_adj_factor")
_T_STK_LIMIT = TableRegistry().table("market_stk_limit")
_T_STOCK_LIST = TableRegistry().table("market_stock_list")

# NO-BARE-SQL：面板取数 SQL 骨架集中于此（§5.160.2）；builder 只负责填参。
# {start}/{cutoff} 一律先经 _chk_date 校验为 ISO 日期再代入（禁裸串拼进 SQL）；
# {tbl_kline}/{tbl_adj}/{tbl} 由上方品类册常量代入（表名不落字面量）；
# 后复权价恒等式 adj_close = close × adj_factor 与 WO-004 真源口径一致。
_SQL_PRICE = (
    "SELECT k.trade_date AS trade_date, k.symbol AS symbol, toFloat64(k.close) AS close_raw, "
    "toFloat64(k.close) * toFloat64(a.adj_factor) AS adj_close, toFloat64(k.amount) AS amount "
    "FROM (SELECT trade_date, symbol, close, amount FROM {tbl_kline} FINAL "
    "      WHERE trade_date >= '{start}' AND trade_date <= '{cutoff}' "
    "        AND market_type = 'A_share' AND close > 0) AS k "
    "INNER JOIN (SELECT trade_date, symbol, argMax(adj_factor, ingest_ts) AS adj_factor "
    "            FROM {tbl_adj} "
    "            WHERE trade_date >= '{start}' AND trade_date <= '{cutoff}' "
    "            GROUP BY trade_date, symbol) AS a "
    "ON k.symbol = a.symbol AND k.trade_date = a.trade_date "
    "ORDER BY trade_date, symbol"
)
_SQL_LIMITS = (
    "SELECT trade_date, symbol, toFloat64(max(limit_up)) AS limit_up, "
    "toFloat64(max(limit_down)) AS limit_down, max(st_flag) AS st_flag FROM ("
    "  SELECT trade_date, symbol, limit_up, limit_down, st_flag FROM {tbl} FINAL "
    "  WHERE trade_date >= '{start}' AND trade_date <= '{cutoff}') "
    "GROUP BY trade_date, symbol ORDER BY trade_date, symbol"
)
_SQL_LISTED = (
    f"SELECT symbol, min(list_date) AS listed_on FROM {_T_STOCK_LIST} FINAL "
    "WHERE list_date IS NOT NULL GROUP BY symbol ORDER BY symbol"
)
_SQL_TABLE_SPAN = "SELECT min(trade_date), max(trade_date), count() FROM {tbl}"


def _chk_date(d: str) -> str:
    return dt.date.fromisoformat(d).isoformat()


@dataclass
class A06Panels:
    """复考面板包。"""

    start: str
    cutoff: str
    signal: pd.DataFrame
    inflow: pd.DataFrame
    adj_close: pd.DataFrame
    close_raw: pd.DataFrame
    amount: pd.DataFrame
    coverage: pd.DataFrame
    version_census: dict
    horizons: tuple[int, ...]
    sqls: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    limit_up: pd.DataFrame | None = None
    limit_down: pd.DataFrame | None = None
    st_flag: pd.DataFrame | None = None
    listed_on: pd.Series | None = None

    # ---- 派生量 ----
    def fwd(self, n: int) -> pd.DataFrame:
        """n 交易日前瞻收益（T→T+n 后复权收盘比）。"""
        if int(n) not in self.horizons:
            raise ValueError(f"horizon {n} 未装载（已装 {self.horizons}）")
        px = self.adj_close
        return px.shift(-int(n)) / px - 1.0

    def signal_amount_ratio(self) -> pd.DataFrame:
        """题面字面口径稳健性：主力净流入占**当日成交额**比（%，inflow 万元→元）。

        表内 main_net_inflow_pct 的分母是主力档（大单+超大单）毛成交；本方法把分母换成
        全市场成交额，用于核对结论是否随分母口径翻转（仅披露用）。
        """
        amt = self.amount.where(self.amount > 0)
        return 100.0 * (self.inflow * 1e4) / amt

    def pool(self, kind: str = "main") -> pd.DataFrame:
        """池掩码：main=全 A 现价池（信号与价格同时在市）；variant=加 ST/次新/涨跌停/流动性过滤。"""
        m = self.signal.notna() & self.adj_close.notna()
        if kind == "main":
            return m
        if kind != "variant":
            raise ValueError(f"未知池口径 {kind}")
        if self.st_flag is not None:
            st = self.st_flag.reindex(index=m.index, columns=m.columns)
            m = m & ~(st == True)  # noqa: E712 — NaN 与 False 同判"非 ST"，禁 fillna 降级告警
        if self.limit_up is not None and self.limit_down is not None:
            lu = self.limit_up.reindex(index=m.index, columns=m.columns)
            ld = self.limit_down.reindex(index=m.index, columns=m.columns)
            cl = self.close_raw.reindex(index=m.index, columns=m.columns)
            locked = (cl >= lu - 1e-9) & lu.notna() | (cl <= ld + 1e-9) & ld.notna()
            m = m & ~locked
        m = m & (self.amount.reindex(index=m.index, columns=m.columns) >= MIN_DAILY_AMOUNT)
        if self.listed_on is not None:
            lo = self.listed_on.reindex(self.signal.columns)
            ok = pd.DataFrame(True, index=self.signal.index, columns=self.signal.columns)
            for s in self.signal.columns:
                d0 = lo.get(s, pd.NaT)
                if pd.isna(d0):
                    continue
                ok.loc[:, s] = self.signal.index >= (d0 + pd.Timedelta(days=MIN_LISTED_DAYS))
            m = m & ok
        return m

    @property
    def trade_dates(self) -> pd.DatetimeIndex:
        return self.signal.index


def _wide(df: pd.DataFrame, value: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(dtype="float64")
    out = df.copy()
    out["trade_date"] = pd.to_datetime(out["trade_date"])
    out["symbol"] = out["symbol"].astype("category")
    out = out.drop_duplicates(subset=["trade_date", "symbol"], keep="last")
    w = out.pivot(index="trade_date", columns="symbol", values=value).sort_index()
    if w.index.duplicated().any() or w.columns.duplicated().any():
        raise AssertionError("面板键重复——去重步骤失效")
    return w


def _sql_signal(start: str, cutoff: str) -> str:
    return (
        "SELECT trade_date, symbol, toFloat64(main_net_inflow) AS main_net_inflow, "
        "toFloat64(main_net_inflow_pct) AS main_net_inflow_pct "
        f"FROM {_T_MONEY_FLOW} FINAL "
        f"WHERE trade_date >= '{start}' AND trade_date <= '{cutoff}' "
        "ORDER BY trade_date, symbol"
    )


def _sql_price(start: str, cutoff: str) -> str:
    return _SQL_PRICE.format(
        start=_chk_date(start), cutoff=_chk_date(cutoff), tbl_kline=_T_KLINE_DAILY, tbl_adj=_T_ADJ_FACTOR
    )


def _sql_limits(start: str, cutoff: str) -> str:
    return _SQL_LIMITS.format(start=_chk_date(start), cutoff=_chk_date(cutoff), tbl=_T_STK_LIMIT)


def _sql_listed() -> str:
    return _SQL_LISTED


def _sql_version_census(start: str, cutoff: str) -> str:
    return (
        "SELECT data_source, count() AS rows, uniqExact(symbol) AS symbols, "
        "min(trade_date) AS min_td, max(trade_date) AS max_td, "
        "min(toDate(ingest_ts)) AS min_ing, max(toDate(ingest_ts)) AS max_ing, "
        "uniqExact(toDate(ingest_ts)) AS ingest_days "
        f"FROM {_T_MONEY_FLOW} FINAL "
        f"WHERE trade_date >= '{start}' AND trade_date <= '{cutoff}' "
        "GROUP BY data_source ORDER BY data_source"
    )


def _sql_ingest_batches(start: str, cutoff: str) -> str:
    return (
        "SELECT toDate(ingest_ts) AS ingest_day, count() AS rows, "
        "min(trade_date) AS min_td, max(trade_date) AS max_td, uniqExact(symbol) AS symbols "
        f"FROM {_T_MONEY_FLOW} FINAL "
        f"WHERE trade_date >= '{start}' AND trade_date <= '{cutoff}' "
        "GROUP BY ingest_day ORDER BY ingest_day"
    )


def _pit_probe(conn, cutoff: str, start: str) -> dict:
    """PIT 实证：表级与窗级端点必须 ≤ 切点（用了切点后数据=换卷作弊，直接阻断）。"""
    probes: dict = {}
    for tbl in (_T_MONEY_FLOW, _T_KLINE_DAILY):
        r = conn.execute(_SQL_TABLE_SPAN.format(tbl=tbl))[0]
        probes[tbl.split(".")[-1] + "_table_level"] = {"min": str(r[0]), "max": str(r[1]), "rows": int(r[2])}
    w = conn.execute(
        "SELECT min(trade_date), max(trade_date), count(), uniqExact(trade_date), uniqExact(symbol) "
        f"FROM {_T_MONEY_FLOW} FINAL WHERE trade_date >= '{start}' AND trade_date <= '{cutoff}'"
    )[0]
    probes["signal_window"] = {
        "min": str(w[0]),
        "max": str(w[1]),
        "rows": int(w[2]),
        "days": int(w[3]),
        "symbols": int(w[4]),
    }
    if w[1] is None or str(w[1]) > cutoff:
        raise AssertionError(f"PIT 越界：money_flow 窗内 max(trade_date)={w[1]} > 切点 {cutoff}")
    return probes


def _validate_window(start: str, cutoff: str, horizons: Sequence[int]) -> tuple[str, str]:
    """入参校验（fail-visible）：ISO 化 + 切点不可后移 + 窗序合法 + horizon 下界；返回 (start, cutoff)。"""
    start, cutoff = _chk_date(start), _chk_date(cutoff)
    if cutoff > PIT_CUTOFF_DEFAULT:
        raise AssertionError(
            f"PIT 闭卷切点不可后移：请求 cutoff={cutoff} > 战役切点 {PIT_CUTOFF_DEFAULT}（用切点后数据=换卷作弊）"
        )
    if start > cutoff:
        raise AssertionError(f"start {start} 晚于切点 {cutoff}")
    for h in horizons:
        if int(h) < 1:
            raise ValueError(f"horizon 必须 ≥1 交易日，得 {h}")
    return start, cutoff


def _fetch_core_frames(conn, sqls: dict, start: str, cutoff: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """信号窗两路核心取数；任一零行即 raise（复考须 fail-visible，禁静默降级为空面板）。"""
    sig_df = pd.DataFrame(conn.execute(sqls["signal"]), columns=_SIG_COLS)
    if sig_df.empty:
        raise AssertionError(f"money_flow 在 [{start},{cutoff}] 零行——复考前置未落地")
    px_df = pd.DataFrame(conn.execute(sqls["price"]), columns=_PX_COLS)
    if px_df.empty:
        raise AssertionError(f"kline_daily×adj_factor 在 [{start},{cutoff}] 零行")
    return sig_df, px_df


def _collect_nonfinite_warnings(sig_df: pd.DataFrame, px_df: pd.DataFrame) -> list[str]:
    """源侧非有限值探查（宽表空格子不计），逐面板记账为 warning。"""
    warns: list[str] = []
    for name, long_df, col in (
        ("signal", sig_df, "main_net_inflow_pct"),
        ("inflow", sig_df, "main_net_inflow"),
        ("adj_close", px_df, "adj_close"),
        ("close_raw", px_df, "close_raw"),
    ):
        v = pd.to_numeric(long_df[col], errors="coerce")
        rep = int((~np.isfinite(v)).sum())
        if rep:
            warns.append(f"{name} 源侧非有限值 {rep} 行置 NaN（宽表空格子不计）")
    return warns


def _version_census_block(conn, sqls: dict, start: str, cutoff: str, pit: dict) -> dict:
    """data_source 版本标记实测 + ingest 批次 + PIT 探针 + 唯一标记完整性判定。"""
    census = conn.execute(sqls["version_census"])
    batches = conn.execute(sqls["ingest_batches"])
    version_census = {
        "window": [start, cutoff],
        "by_data_source": [
            {
                "data_source": str(r[0]),
                "rows": int(r[1]),
                "symbols": int(r[2]),
                "min_td": str(r[3]),
                "max_td": str(r[4]),
                "min_ingest": str(r[5]),
                "max_ingest": str(r[6]),
                "ingest_days": int(r[7]),
            }
            for r in census
        ],
        "ingest_batches": [
            {"ingest_day": str(r[0]), "rows": int(r[1]), "min_td": str(r[2]), "max_td": str(r[3]), "symbols": int(r[4])}
            for r in batches
        ],
        "distinct_markers": sorted({str(r[0]) for r in census}),
        "empty_marker_rows": int(sum(int(r[1]) for r in census if not str(r[0]).strip())),
        "pit_probe": pit,
    }
    version_census["marker_single_and_complete"] = bool(
        len(version_census["distinct_markers"]) == 1
        and "" not in version_census["distinct_markers"]
        and version_census["empty_marker_rows"] == 0
    )
    return version_census


def _variant_masks(conn, sqls: dict, start: str, cutoff: str, cal, signal: pd.DataFrame, warns: list[str]) -> tuple:
    """稳健性变体掩码装载（涨跌停/ST/次新）；空表退化为不过滤并写 warnings 记账。

    Returns:
        (limit_up, limit_down, st_flag, listed_on)
    """
    limit_up = limit_down = st_flag = None
    listed_on: pd.Series | None = None
    sqls["limits"] = _sql_limits(start, cutoff)
    sqls["listed"] = _sql_listed()
    lim = pd.DataFrame(conn.execute(sqls["limits"]), columns=_LIM_COLS)
    if lim.empty:
        warns.append("stk_limit 窗内零行——涨跌停/ST 变体掩码退化为不过滤")
    else:
        limit_up = _wide(lim, "limit_up").astype("float64").reindex(index=cal).loc[:, signal.columns]
        limit_down = _wide(lim, "limit_down").astype("float64").reindex(index=cal).loc[:, signal.columns]
        st_flag = _wide(lim, "st_flag").astype("float64").reindex(index=cal).loc[:, signal.columns] > 0.5
    ld = pd.DataFrame(conn.execute(sqls["listed"]), columns=["symbol", "listed_on"])
    if ld.empty:
        warns.append("stock_list 无上市日期——次新过滤变体退化为不过滤")
    else:
        s = ld.drop_duplicates("symbol").set_index("symbol")["listed_on"]
        listed_on = pd.Series(pd.to_datetime(s.astype(str)), index=s.index)
    return limit_up, limit_down, st_flag, listed_on


def load_panels(
    conn,
    start: str = "2021-01-04",
    cutoff: str = PIT_CUTOFF_DEFAULT,
    horizons: Sequence[int] = (1, 5, 20),
    with_variant_masks: bool = True,
) -> A06Panels:
    """装载复考面板（一次装载六问共用）。

    Args:
        conn: ClickHouse reader（DatabaseService().get_clickhouse_conn(role='reader')）
        start: 信号窗起点（含）
        cutoff: PIT 闭卷切点（含）——一切取数与前瞻端点的硬上界
        horizons: 前瞻收益窗（交易日）
        with_variant_masks: 是否装载稳健性变体掩码（ST/次新/涨跌停/流动性）

    Returns:
        A06Panels（面板端点二次断言 ≤ cutoff；SQL 文本全量导出）
    """
    start, cutoff = _validate_window(start, cutoff, horizons)

    pit = _pit_probe(conn, cutoff, start)
    sqls = {
        "signal": _sql_signal(start, cutoff),
        "price": _sql_price(start, cutoff),
        "version_census": _sql_version_census(start, cutoff),
        "ingest_batches": _sql_ingest_batches(start, cutoff),
    }
    warns: list[str] = []

    sig_df, px_df = _fetch_core_frames(conn, sqls, start, cutoff)

    signal = _wide(sig_df, "main_net_inflow_pct").astype("float64")
    inflow = _wide(sig_df, "main_net_inflow").astype("float64")
    adj_close = _wide(px_df, "adj_close").astype("float64")
    close_raw = _wide(px_df, "close_raw").astype("float64")
    amount = _wide(px_df, "amount").astype("float64")

    warns.extend(_collect_nonfinite_warnings(sig_df, px_df))
    signal = signal.where(np.isfinite(signal))
    inflow = inflow.where(np.isfinite(inflow))
    adj_close = adj_close.where(np.isfinite(adj_close) & (adj_close > 0))
    close_raw = close_raw.where(np.isfinite(close_raw) & (close_raw > 0))

    cal = adj_close.index.intersection(signal.index)
    signal, inflow = signal.loc[cal], inflow.loc[cal]
    adj_close, close_raw, amount = adj_close.loc[cal], close_raw.loc[cal], amount.loc[cal]
    if len(cal) == 0 or str(cal[-1].date()) > cutoff:
        raise AssertionError(f"面板日历越界：末交易日 {cal[-1] if len(cal) else None} > {cutoff}")

    coverage = pd.DataFrame(
        {
            "n_signal": signal.notna().sum(axis=1),
            "n_price": adj_close.notna().sum(axis=1),
            "n_join": (signal.notna() & adj_close.notna()).sum(axis=1),
            "n_signal_pos": (signal > 0).sum(axis=1),
            "mean_signal": signal.mean(axis=1),
            "median_signal": signal.median(axis=1),
            "std_signal": signal.std(axis=1),
            "q05_signal": signal.quantile(0.05, axis=1),
            "q95_signal": signal.quantile(0.95, axis=1),
            "mean_inflow": inflow.mean(axis=1),
        }
    )
    coverage.insert(0, "day_rank", range(1, len(coverage) + 1))

    version_census = _version_census_block(conn, sqls, start, cutoff, pit)

    limit_up = limit_down = st_flag = None
    listed_on: pd.Series | None = None
    if with_variant_masks:
        limit_up, limit_down, st_flag, listed_on = _variant_masks(conn, sqls, start, cutoff, cal, signal, warns)

    return A06Panels(
        start=start,
        cutoff=cutoff,
        signal=signal,
        inflow=inflow,
        adj_close=adj_close,
        close_raw=close_raw,
        amount=amount,
        coverage=coverage,
        version_census=version_census,
        horizons=tuple(int(h) for h in horizons),
        sqls=sqls,
        warnings=warns,
        limit_up=limit_up,
        limit_down=limit_down,
        st_flag=st_flag,
        listed_on=listed_on,
    )
