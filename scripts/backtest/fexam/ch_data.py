# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | CH只读数据装载层
# [MODULE] scripts.backtest.fexam.ch_data
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; 标准库 urllib
# [CONSUMERS] ic_exam.py; strategy_exam.py; allocator_shadow.py
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 只读 SELECT（宪法§9.8 CH只读口径）；禁任何 DDL/INSERT；查询失败=抛错上抛（fail-closed，禁伪造空数据冒充分数）；Nullable(Float64) 空值保 NaN
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 不可达/超时 → CHAccessError；空结果返回空 DataFrame 不报错
# [TESTS] tests/backtest/fexam/test_ic_exam.py（经上层间接）
# [MODIFY-GUARD] docs/_working/matrix_campaign/90_execution_log.md（CH只读契约，禁加写路径）
# [TTL] permanent
# create-guard-not-dup: fexam专用CH只读装载层（表名经TableRegistry，与dataflow/northbound等命中无功能交集）
"""ch_data — ClickHouse 只读装载：面板/前向收益/regime 态。

考试纪律（fexam prereg v1）：
- HOLDOUT 考试窗=2025-10-09..2026-09-30（近12月干净窗）
- IS_REF 衰减参照窗=2024-10-08..2025-09-30（与 HOLDOUT 严格不交）
- 窗口定义随分数册头部落盘，禁止事后修改（exam_policy §1 挪门柱=作废）
"""

from __future__ import annotations

import io
import sys
from pathlib import Path
from urllib import request

import pandas as pd

RUN_ROOT = Path(__file__).resolve().parents[3]
_SRC = RUN_ROOT / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

CH_BASE = "http://172.24.30.100:8123/"

#: 表名真源=TableRegistry（NO-BARE-SQL 同款集中化；fail-closed 查无即抛）
from zephyr.data.table_registry import get_registry  # noqa: E402

_REG = get_registry()
T_TECHNICAL_INDICATOR = _REG.table("market_technical_indicator")
T_STOCK_INDICATOR = _REG.table("market_stock_indicator")
T_DAILY_VALUATION = _REG.table("market_daily_valuation")
T_FINANCIAL_INDICATOR = _REG.table("fund_financial_indicator")
T_KLINE_DAILY_HFQ = _REG.table("market_kline_daily_hfq")

#: 候选列真源表（因子/指标 outputs 列 → CH 表映射；顺序=优先级）
CANDIDATE_TABLES: tuple[str, ...] = (
    T_TECHNICAL_INDICATOR,
    T_STOCK_INDICATOR,
    T_DAILY_VALUATION,
    T_FINANCIAL_INDICATOR,
    T_KLINE_DAILY_HFQ,
)

#: prereg v1 冻结窗口（写进一切分数册头；改窗=重考）
WINDOW_HOLDOUT = ("2025-10-09", "2026-09-30")
WINDOW_IS_REF = ("2024-10-08", "2025-09-30")
WINDOW_UNION = ("2024-10-08", "2026-09-30")

_REGIME_LABELS = {
    "p_r1": "ranging_low_vol",
    "p_r2": "ranging_mid_vol",
    "p_r3": "trend_up",
    "p_r4": "trend_down",
}


class CHAccessError(RuntimeError):
    """CH 查询失败（网络/超时/语法）。fail-closed，上层禁吞。"""


#: 直连 opener：Windows 系统代理（127.0.0.1:10808）会劫持 urllib 对内网 CH 的 POST=404，强制绕过
_OPENER = request.build_opener(request.ProxyHandler({}))

#: SQL 集中化（NO-BARE-SQL 正道：全模块查询模板唯一定义点；只读，禁拼接 DDL/INSERT）
SQL_SYSTEM_COLUMNS = "SELECT name FROM system.columns WHERE database='{db}' AND table='{tbl}' FORMAT TSV"
SQL_PANEL = "SELECT trade_date, symbol, {column} AS v FROM {table} WHERE {conds} ORDER BY trade_date, symbol FORMAT TSV"
SQL_REGIME = (
    "SELECT trade_date, p_r1, p_r2, p_r3, p_r4 FROM c1_backtest.regime_snapshot_history "
    "WHERE trade_date >= '{start}' AND trade_date <= '{end}' ORDER BY trade_date FORMAT TSV"
)


def ch_query(sql: str, *, timeout: int = 180) -> str:
    """执行只读 SELECT，返回 TSV 文本。非 2xx 或异常一律 CHAccessError。"""
    lowered = sql.lstrip().lower()
    if not lowered.startswith(("select", "with", "describe", "exists")):
        raise CHAccessError(f"拒绝非只读查询: {sql[:80]}")
    try:
        req = request.Request(CH_BASE, data=sql.encode("utf-8"), method="POST")
        with _OPENER.open(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001 — 统一转 CHAccessError（fail-closed 契约）
        raise CHAccessError(f"CH 查询失败: {exc}: {sql[:120]}") from exc


def ch_query_df(sql: str, *, timeout: int = 180) -> pd.DataFrame:
    """TSV→DataFrame。FORMAT TSV 无表头：列宽按首行动态确定，列名 c1..cN（位置协议）。"""
    text = ch_query(sql, timeout=timeout)
    if not text.strip():
        return pd.DataFrame()
    if text.lstrip().startswith("Code:"):  # CH 异常体（部分网关以 200/404 携带错误文本）
        raise CHAccessError(f"CH 错误体: {text[:200]}")
    width = len(text.split("\n", 1)[0].split("\t"))
    names = [f"c{i}" for i in range(1, width + 1)]
    return pd.read_csv(
        io.StringIO(text),
        sep="\t",
        dtype=str,
        keep_default_na=False,
        header=None,
        names=names,
    )


def table_columns(table: str, *, cache: dict[str, set[str]] | None = None) -> set[str]:
    """表全部列名（含系统列之外的业务列）。cache 跨调用复用。"""
    store = cache if cache is not None else {}
    if table not in store:
        db, tbl = table.split(".", 1)
        df = ch_query_df(SQL_SYSTEM_COLUMNS.format(db=db, tbl=tbl))
        store[table] = set(df.iloc[:, 0].tolist())
    return store[table]


def resolve_output_columns(outputs: list[str], *, cache: dict[str, set[str]] | None = None) -> list[tuple[str, str]]:
    """把注册册 outputs 列名解析到 (table, column)。多表命中取 CANDIDATE_TABLES 优先序第一个。"""
    found: list[tuple[str, str]] = []
    seen: set[str] = set()
    for table in CANDIDATE_TABLES:
        cols = table_columns(table, cache=cache)
        for out in outputs or []:
            key = str(out).strip()
            if key and key in cols and key not in seen:
                found.append((table, key))
                seen.add(key)
    return found


def load_panel(
    table: str,
    column: str,
    start: str,
    end: str,
    *,
    period: str = "daily",
    _col_cache: dict[str, set[str]] | None = None,
) -> pd.DataFrame:
    """单列宽面板：index=date(DatetimeIndex), columns=symbol, float32。空数据=空DataFrame。

    period 过滤仅对含 period 列的表生效（kline 族无 period 列）。
    """
    conds = [f"trade_date >= '{start}'", f"trade_date <= '{end}'", f"{column} IS NOT NULL"]
    if "period" in table_columns(table, cache=_col_cache):
        conds.insert(0, f"period='{period}'")
    sql = SQL_PANEL.format(column=column, table=table, conds=" AND ".join(conds))
    df = ch_query_df(sql)
    if df.empty:
        return pd.DataFrame()
    df.columns = ["trade_date", "symbol", "v"]
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    wide = df.pivot_table(index="trade_date", columns="symbol", values="v", aggfunc="last")
    return wide.astype("float32")


def load_close(start: str, end: str) -> pd.DataFrame:
    """后复权收盘价面板（date×symbol）。"""
    return load_panel(T_KLINE_DAILY_HFQ, "close", start, end, period="daily")


def forward_returns(close: pd.DataFrame, horizons: tuple[int, ...]) -> dict[int, pd.DataFrame]:
    """前向收益面板（PIT：t 日因子对 t→t+h 收益，实现收益不含未来信息泄露）。"""
    return {h: close.shift(-h) / close - 1.0 for h in horizons}


def load_regime_states(start: str, end: str) -> pd.Series:
    """HMM 四态概率 argmax → 稳定标签。index=date。缺失日期由上层 fallback 补。"""
    sql = SQL_REGIME.format(start=start, end=end)
    df = ch_query_df(sql)
    if df.empty:
        return pd.Series(dtype="object")
    df.columns = ["trade_date", "p_r1", "p_r2", "p_r3", "p_r4"]
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    prob_cols = list(_REGIME_LABELS)
    for c in prob_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    df = df.drop_duplicates(subset="trade_date", keep="last")  # 同日多快照取末笔（PIT：最新检测态）
    states = df[prob_cols].idxmax(axis=1).map(_REGIME_LABELS)
    return pd.Series(states.values, index=df["trade_date"], name="regime")


def sma_regime_fallback(dates: pd.DatetimeIndex, window: int = 200) -> pd.Series:
    """regime 表未覆盖期（<2019-04）的确定性 fallback：代理指数 200 日 SMA 上/下。

    代理=后复权全市场等权均值（不引入额外数据源，确定性可复算）。
    regime 表覆盖期不得用本 fallback（优先真源）。
    """
    proxy = load_close("1990-01-01", dates.max().strftime("%Y-%m-%d")).mean(axis=1).dropna()
    if proxy.empty:
        return pd.Series(dtype="object")
    sma = proxy.rolling(window, min_periods=window).mean()
    state = (proxy > sma).map({True: "trend_up", False: "trend_down"})
    state = state.reindex(pd.DatetimeIndex(dates)).ffill().bfill()
    return state.rename("regime")


def regime_series(start: str, end: str) -> tuple[pd.Series, str]:
    """regime 态序列+来源标注（regime_table / sma_fallback / mixed）。

    真源优先：regime_snapshot_history 覆盖的日期用 HMM 态；
    未覆盖日期（<2019-04）用确定性 SMA fallback 补，来源如实标注。
    """
    hmm = load_regime_states(start, end)
    dates = pd.date_range(start, end, freq="D")
    if hmm.empty:
        return sma_regime_fallback(dates), "sma_fallback"
    merged = sma_regime_fallback(dates)
    if merged.empty:
        merged = hmm.copy()
    else:
        common = merged.index.intersection(hmm.index)
        merged.loc[common] = hmm.reindex(common)
    source = "regime_table+sma_fallback"
    if pd.Timestamp(start) >= hmm.index.min():
        source = "regime_table"
    return merged.dropna(), source
