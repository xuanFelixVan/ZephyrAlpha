# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md
# [MODULE] zephyr.data.implementations.financial_derived_compute
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.provider_base; schemas.categories.fundamental.financial_derived
# [CONSUMERS] scripts/ch/build_financial_derived.py（CLI 回补/重建/--check）;
#             zephyr.data.implementations.internal_compute_provider（financial_derived capability 夜间派生）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] PIT铁律=只消费 announce_date>1970-01-02 行（哨兵守卫,D1 裁定与 pit_query 同构）+历史期取值
#              一律取衍生公告日时点可见最新版本（修正公告前视免疫）; 衍生行公告日=三方公告日最大值
#              （三方齐公告才成行）; 单季=本期累计−同年上期累计（Q1=累计本身,非季末→NULL）;
#              TTM=上年FY+本期累计−去年同季累计（FY期=累计本身）; 增长率=(cur-base)/|base|（基期空/零→NULL）;
#              ReplacingMergeTree(ingest_ts) 同键重建幂等; 纯函数核 build_symbol_rows 无 IO 可测
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 源表不可达->RuntimeError; 写入失败由调用方转译退出码（CLI exit 2）
# [TESTS] tests/zephyr/data/test_financial_derived_compute.py（纯函数核）+ scripts/ch/build_financial_derived.py --check（实库交叉验证）
# [TTL] permanent
"""financial_derived 计算核——三大报表 → statement 粒度派生宽表（消费端 F1-M1，DS-230）。

把 c3_fundamental 三大报表（income/balance/cashflow，累计口径+多版本）对齐派生为
c3_fundamental.financial_derived 宽表：跨表对齐 + 单季拆分 + TTM + 派生比率。
设计真源：docs/_working/2026-09-12-fundamental-consumption-design.md §M1
（D2 裁定：statement 粒度，不做每日物化——每日可见性展开是 pit_query as_of 的职责）。

PIT 语义（本模块的灵魂，全部实现为纯函数便于单测）：
    1. 加载层哨兵守卫：announce_date <= 1970-01-02 的行一律不可见（D1 裁定，宁缺毋错）。
    2. 版本 store：每 (symbol, statement, report_period) 保留全部有效版本 (announce_date, 值)。
    3. 对齐事件：任一侧出现新公告版本即新事件（事件集=三方公告日并集）；仅当该时点
       三方均有可见版本才成行——原公告事件与修正公告事件各自成行（与源表同构）。
    4. as-of 取数：单季/TTM/YoY 引用的任意历史期数值 = 该事件时点可见最新版本
       （max announce_date <= 事件时点）——期后修正公告不会污染已公告时点的派生值。

用法（经 CLI / scheduler）：
    python scripts/ch/build_financial_derived.py --full      # 历史全量回补（幂等）
    python scripts/ch/build_financial_derived.py --check     # 实库 PIT 交叉验证
    scheduler → InternalComputeProvider → run_compute()     # 夜间派生（nightly_financial 后）
"""

from __future__ import annotations

import calendar
import datetime as dt
import logging
from collections.abc import Iterator

from zephyr.data.provider_base import FetchResult

log = logging.getLogger(__name__)

# 哨兵截断（D1 裁定 2026-09-12：公告时间未知=PIT 不可见；与 pit_query.py 模板字面一致）
SENTINEL_CUTOFF = "1970-01-02"

DATA_SOURCE = "financial_derived_builder"
_BATCH_SIZE = 100_000

# 各语句加载列（键 3 列 + 派生所需字段；列名经 system.columns 核实 2026-09-13）
_LOAD_COLS: dict[str, list[str]] = {
    "income_statement": [
        "symbol", "report_period", "announce_date",
        "operating_revenue", "operating_cost", "operating_profit", "total_profit",
        "income_tax", "net_profit_incl_minority", "net_profit_excl_minority",
        "eps_basic", "rd_expense",
    ],
    "balance_sheet": [
        "symbol", "report_period", "announce_date",
        "total_assets", "total_liabilities", "total_current_assets",
        "total_current_liabilities", "accounts_receivable", "inventory", "goodwill",
        "equity_incl_minority", "retained_earnings", "short_term_loan", "long_term_loan",
    ],
    "cashflow_statement": [
        "symbol", "report_period", "announce_date",
        "ocf_net", "icf_net", "fcff",
    ],
}

# 源列 → 派生宽表列映射（一律显式列出，禁隐式通配）
_WIDE_FROM_INCOME = {
    "revenue_cum": "operating_revenue",
    "cost_cum": "operating_cost",
    "operating_profit_cum": "operating_profit",
    "total_profit_cum": "total_profit",
    "income_tax_cum": "income_tax",
    "np_cum": "net_profit_incl_minority",
    "np_excl_cum": "net_profit_excl_minority",
    "eps_basic": "eps_basic",
    "rd_expense_cum": "rd_expense",
}
_WIDE_FROM_CASHFLOW = {"ocf_cum": "ocf_net", "icf_cum": "icf_net", "fcff_cum": "fcff"}
_WIDE_FROM_BALANCE = {
    "total_assets": "total_assets",
    "total_liabilities": "total_liabilities",
    "total_current_assets": "total_current_assets",
    "total_current_liabilities": "total_current_liabilities",
    "accounts_receivable": "accounts_receivable",
    "inventory": "inventory",
    "goodwill": "goodwill",
    "equity_incl_minority": "equity_incl_minority",
    "retained_earnings": "retained_earnings",
    "short_term_loan": "short_term_loan",
    "long_term_loan": "long_term_loan",
}

# 版本 store：stmt -> symbol -> report_period -> [(announce_date, {col: raw_str})]
VersionStore = dict[str, dict[str, dict[dt.date, list[tuple[dt.date, dict]]]]]

_STMTS = ("income_statement", "balance_sheet", "cashflow_statement")


# ============================================================================
# 纯函数核（无 IO；tests/zephyr/data/test_financial_derived_compute.py 直测）
# ============================================================================

def parse_float(v) -> float | None:
    """TSV 值/原始值 → float；''/'\\N'/NaN/不可解析 → None。"""
    if v is None:
        return None
    s = str(v).strip()
    if not s or s == "\\N":
        return None
    try:
        x = float(s)
    except ValueError:
        return None
    return None if x != x else x


def shift_quarter(p: dt.date, n: int) -> dt.date:
    """报告期按季平移（n=-1 上季、-4 去年同季）。

    季末期保持季末日；非季末期（历史脏数据）按月平移、日钳位到目标月末——查
    store 自然 miss → 派生字段 NULL，不参与拆分。
    """
    total = p.year * 12 + (p.month - 1) + n * 3
    y, m0 = divmod(total, 12)
    m = m0 + 1
    day = {3: 31, 6: 30, 9: 30, 12: 31}.get(m) or min(p.day, calendar.monthrange(y, m)[1])
    return dt.date(y, m, day)


def fiscal_prev(p: dt.date) -> dt.date | None:
    """同年上一报告期；Q1 或非季末月 → None（Q1 单季=累计本身；非季末不拆分）。"""
    if p.month in (6, 9, 12):
        return shift_quarter(p, -1)
    return None


def growth(cur: float | None, base: float | None) -> float | None:
    """同比增长率=(cur-base)/|base|（|base| 防负值翻转）；基期缺失/为零/当期缺失 → NULL。"""
    if cur is None or base is None or base == 0:
        return None
    return (cur - base) / abs(base)


def safe_div(a: float | None, b: float | None) -> float | None:
    """安全除法；分母缺失/为零 → NULL。"""
    if a is None or b is None or b == 0:
        return None
    return a / b


def safe_sub(a: float | None, b: float | None) -> float | None:
    """安全减法（累计差分）；任一缺失 → NULL。"""
    if a is None or b is None:
        return None
    return a - b


def visible(versions: list[tuple[dt.date, dict]] | None, at: dt.date) -> dict | None:
    """as-of 取数：announce_date <= at 的最新版本；无可见版本 → None（PIT 公理1）。"""
    if not versions:
        return None
    best: tuple[dt.date, dict] | None = None
    for ann, vals in versions:
        if ann <= at and (best is None or ann >= best[0]):
            best = (ann, vals)
    return best[1] if best else None


def _ttm3(fy_val, cur_val, ly_val) -> float | None:
    """TTM = 上年FY + 本期累计 − 去年同季累计；任一缺失 → NULL。"""
    fy, cur, ly = parse_float(fy_val), parse_float(cur_val), parse_float(ly_val)
    if fy is None or cur is None or ly is None:
        return None
    return fy + cur - ly


def build_symbol_rows(symbol: str, store: dict[str, dict[dt.date, list]]) -> list[dict]:
    """单标的派生核：三表版本 store → financial_derived 行 dict 列表（键=INSERT_COLUMNS 列名）。

    Args:
        symbol: 标的代码。
        store: 该标的 {statement: {report_period: [(announce_date, {col: raw})]}}，
               已由加载层完成哨兵过滤（announce_date > 1970-01-02）。

    Returns:
        行 dict 列表，按 report_period 升序。
    """
    inc = store.get("income_statement", {})
    bal = store.get("balance_sheet", {})
    cfs = store.get("cashflow_statement", {})
    periods = sorted(set(inc) & set(bal) & set(cfs))

    rows: list[dict] = []
    for p in periods:
        # 对齐事件集=三方公告日并集；每个时点独立成行（若该时点三方均已可见）
        events = sorted({ann for side in (inc[p], bal[p], cfs[p]) for ann, _ in side})
        for a in events:
            row = _build_event_row(symbol, p, a, inc, bal, cfs)
            if row is not None:
                rows.append(row)
    return rows


def _build_event_row(symbol: str, p: dt.date, a: dt.date,
                     inc: dict, bal: dict, cfs: dict) -> dict | None:
    """单个对齐事件的派生行（as-of a 取三方可见版本；任一侧尚不可见→None 不成行）。"""
    i0 = visible(inc[p], a)
    b0 = visible(bal[p], a)
    c0 = visible(cfs[p], a)
    if i0 is None or b0 is None or c0 is None:
        return None  # 该时点宽表未齐（如 balance 尚未公告）——不成行

    def g(vals: dict | None, col: str) -> float | None:
        return parse_float(vals.get(col)) if vals else None

    # 单季 at 期（as-of a）：(rev_q, np_q, ocf_q)；上期缺失/非季末 → (None, None, None)
    def single_at(px: dt.date, at: dt.date) -> tuple[float | None, float | None, float | None]:
        ix = visible(inc.get(px), at)
        cx = visible(cfs.get(px), at)
        if ix is None:
            return None, None, None
        if px.month == 3:  # Q1：单季=累计本身
            return g(ix, "operating_revenue"), g(ix, "net_profit_incl_minority"), g(cx, "ocf_net")
        fpx = fiscal_prev(px)
        if fpx is None:
            return None, None, None
        i_fpx = visible(inc.get(fpx), at)
        c_fpx = visible(cfs.get(fpx), at)
        return (
            safe_sub(g(ix, "operating_revenue"), g(i_fpx, "operating_revenue")),
            safe_sub(g(ix, "net_profit_incl_minority"), g(i_fpx, "net_profit_incl_minority")),
            safe_sub(g(cx, "ocf_net"), g(c_fpx, "ocf_net")),
        )

    row: dict = {
        "symbol": symbol,
        "report_period": p.isoformat(),
        "announce_date": a.isoformat(),
    }
    for out_col, src_col in _WIDE_FROM_INCOME.items():
        row[out_col] = g(i0, src_col)
    for out_col, src_col in _WIDE_FROM_CASHFLOW.items():
        row[out_col] = g(c0, src_col)
    for out_col, src_col in _WIDE_FROM_BALANCE.items():
        row[out_col] = g(b0, src_col)

    # ---- 单季拆分（流量项；Q1=累计本身，非季末→NULL）----
    if p.month == 3:
        row["rev_q"], row["cost_q"] = row["revenue_cum"], row["cost_cum"]
        row["np_q"], row["ocf_q"] = row["np_cum"], row["ocf_cum"]
    else:
        fp = fiscal_prev(p)
        i_fp = visible(inc.get(fp), a) if fp else None
        c_fp = visible(cfs.get(fp), a) if fp else None
        row["rev_q"] = safe_sub(row["revenue_cum"], g(i_fp, "operating_revenue"))
        row["cost_q"] = safe_sub(row["cost_cum"], g(i_fp, "operating_cost"))
        row["np_q"] = safe_sub(row["np_cum"], g(i_fp, "net_profit_incl_minority"))
        row["ocf_q"] = safe_sub(row["ocf_cum"], g(c_fp, "ocf_net"))

    # ---- 单季同比/环比（基期单季同样走 as-of 累计差分）----
    ly_rev, ly_np, ly_ocf = single_at(shift_quarter(p, -4), a)
    row["rev_q_yoy"] = growth(row["rev_q"], ly_rev)
    row["np_q_yoy"] = growth(row["np_q"], ly_np)
    row["ocf_q_yoy"] = growth(row["ocf_q"], ly_ocf)
    lq_rev, lq_np, _ = single_at(shift_quarter(p, -1), a)
    row["rev_q_qoq"] = growth(row["rev_q"], lq_rev)
    row["np_q_qoq"] = growth(row["np_q"], lq_np)

    # ---- TTM（滚动四季；FY 期=累计本身）----
    if p.month == 12:
        row["rev_ttm"] = row["revenue_cum"]
        row["cost_ttm"] = row["cost_cum"]
        row["np_ttm"] = row["np_cum"]
        row["ocf_ttm"] = row["ocf_cum"]
        row["total_profit_ttm"] = row["total_profit_cum"]
        row["income_tax_ttm"] = row["income_tax_cum"]
    else:
        fy_i = visible(inc.get(dt.date(p.year - 1, 12, 31)), a)
        fy_c = visible(cfs.get(dt.date(p.year - 1, 12, 31)), a)
        ly_p = shift_quarter(p, -4)
        ly_i = visible(inc.get(ly_p), a)
        ly_c = visible(cfs.get(ly_p), a)
        row["rev_ttm"] = _ttm3(g(fy_i, "operating_revenue"), row["revenue_cum"], g(ly_i, "operating_revenue"))
        row["cost_ttm"] = _ttm3(g(fy_i, "operating_cost"), row["cost_cum"], g(ly_i, "operating_cost"))
        row["np_ttm"] = _ttm3(g(fy_i, "net_profit_incl_minority"), row["np_cum"], g(ly_i, "net_profit_incl_minority"))
        row["ocf_ttm"] = _ttm3(g(fy_c, "ocf_net"), row["ocf_cum"], g(ly_c, "ocf_net"))
        row["total_profit_ttm"] = _ttm3(g(fy_i, "total_profit"), row["total_profit_cum"], g(ly_i, "total_profit"))
        row["income_tax_ttm"] = _ttm3(g(fy_i, "income_tax"), row["income_tax_cum"], g(ly_i, "income_tax"))

    # ---- 派生比率（M2 因子族原料）----
    row["accrual_ttm"] = safe_div(safe_sub(row["np_ttm"], row["ocf_ttm"]), row["total_assets"])
    row["gpoa_ttm"] = safe_div(safe_sub(row["rev_ttm"], row["cost_ttm"]), row["total_assets"])
    row["gross_margin_q"] = safe_div(safe_sub(row["rev_q"], row["cost_q"]), row["rev_q"])
    row["eff_tax_rate_ttm"] = safe_div(row["income_tax_ttm"], row["total_profit_ttm"])
    row["debt_ratio"] = safe_div(row["total_liabilities"], row["total_assets"])
    return row
    return rows


# ============================================================================
# IO 边缘（加载/写批）
# ============================================================================

def load_versions(symbols: list[str] | None = None) -> VersionStore:
    """读三大报表全部有效版本（哨兵过滤在 SQL 层完成）→ 版本 store。

    只读 announce_date > 1970-01-02 的行（D1 哨兵守卫——公告时间未知行一律
    不可见，宁缺毋错防前视）。
    """
    from zephyr.data import ch_reader

    where_sym = ""
    if symbols:
        quoted = ",".join("'" + s.replace("'", "") + "'" for s in symbols)
        where_sym = f" AND symbol IN ({quoted})"
    store: VersionStore = {stmt: {} for stmt in _STMTS}
    for stmt in _STMTS:
        cols = _LOAD_COLS[stmt]
        tsv = ch_reader.query(
            f"SELECT {', '.join(cols)} FROM c3_fundamental.{stmt} "
            f"WHERE announce_date > toDate('{SENTINEL_CUTOFF}'){where_sym}"
        )
        if tsv is None:
            raise RuntimeError(f"{stmt} 查询失败（ch_reader 返回 None）")
        n_rows = 0
        for line in tsv.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < len(cols):
                continue
            try:
                period = dt.date.fromisoformat(parts[1][:10])
                ann = dt.date.fromisoformat(parts[2][:10])
            except ValueError:
                continue
            vals = {c: parts[i] for i, c in enumerate(cols) if i >= 3}
            store[stmt].setdefault(parts[0], {}).setdefault(period, []).append((ann, vals))
            n_rows += 1
        log.info("%s 有效版本 %d 行（哨兵过滤后）", stmt, n_rows)
    return store


def columns_list() -> list[str]:
    """INSERT_COLUMNS → 列名 list（写入列序真源）。"""
    from schemas.categories.fundamental.financial_derived import INSERT_COLUMNS

    return [c.strip() for c in INSERT_COLUMNS.strip("()").split(",")]


def run_compute(
    symbols: list[str] | None = None,
    start: str | None = None,
    end: str | None = None,
) -> Iterator[FetchResult]:
    """计算主流程：加载三表版本 → 逐标的派生 → FetchResult 批（供 CLI/scheduler 消费）。

    Args:
        symbols: 标的子集（None=全市场）。
        start/end: 衍生公告日窗口（含，iso str）。None=不限（历史全量回补）。
    """
    store = load_versions(symbols)
    n_symbols = len(set().union(*(set(store[s]) for s in _STMTS))) if store else 0
    if n_symbols == 0:
        raise RuntimeError("三大报表版本 store 为空（源表不可达或全被哨兵过滤），拒绝产出空派生层")

    cols = columns_list()
    batch: list[tuple] = []
    n_rows = 0
    sym_set = sorted(set().union(*(set(store[s]) for s in _STMTS)))
    for sym in sym_set:
        per_stmt = {stmt: store.get(stmt, {}).get(sym, {}) for stmt in _STMTS}
        for row in build_symbol_rows(sym, per_stmt):
            if start and row["announce_date"] < start:
                continue
            if end and row["announce_date"] > end:
                continue
            batch.append(tuple(row.get(c) for c in cols))
            n_rows += 1
            if len(batch) >= _BATCH_SIZE:
                yield _make_result(cols, batch)
                batch = []
    if batch:
        yield _make_result(cols, batch)
    log.info("financial_derived 派生完成：%d 行（%d 标的）", n_rows, len(sym_set))


def _make_result(cols: list[str], rows: list[tuple]) -> FetchResult:
    from schemas.categories.fundamental.financial_derived import TABLE_NAME

    return FetchResult(
        table=f"c3_fundamental.{TABLE_NAME}",
        columns=cols,
        rows=rows,
        last_key="",
        elapsed_sec=0.0,
    )
