# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md
# [MODULE] zephyr.data.implementations.consensus_daily_compute
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.provider_base; schemas.categories.fundamental.consensus_daily
# [CONSUMERS] scripts/ch/build_consensus_daily.py（CLI 回补/重建/--check）;
#             zephyr.data.implementations.internal_compute_provider（fund_consensus_daily capability 夜间派生，C1.5）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] PIT铁律=只聚合 publish_date<=trade_date 的研报（发布即得零 embargo）；无覆盖不成行禁前向填充；
#              forecast_year 锚定日历年（研报槽位 fy0/fy1/fy2 展开为槽位年）；
#              评级分映射 买入7/增持5/中性持有3/减持卖出回避2-1（空值不计入均值，计入 n_unrated）；
#              ReplacingMergeTree(ingest_ts) 同键重建幂等；
#              纯函数核 build_consensus_rows 无 IO 可测；
#              调度增量起点=表内最新快照日-重叠窗（吸收迟到入库的同日研报，重建幂等）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] research_report/交易日历不可达->RuntimeError; 写入失败由调用方转译退出码（CLI exit 2）
# [TESTS] tests/scripts/test_build_consensus_daily.py（纯函数核，经薄壳 CLI 转出）+ build_consensus_daily.py --check（实库 PIT 交叉验证）
# [TTL] permanent
"""consensus_daily 计算核——研报事件流 → 一致预期每日快照矩阵（消费端 C1/C1.5）。

把 c3_fundamental.research_report（研报事件流）聚合为 c3_fundamental.consensus_daily
（每股每日×预测目标日历年的一致预期矩阵）——华泰金工一致预期因子族（EXP-01~06）的标准输入。
设计真源：docs/01_policies_and_standards/policies/expectation_consumption_design_policy.md §M1。

PIT 语义（本模块的灵魂）：
    只聚合 publish_date <= trade_date 的研报（publish_date 即可得=零 embargo），
    窗口=[trade_date-窗宽自然日, trade_date]；窗口内无研报→不成行（NULL 不前向填充）。

调度增量语义（C1.5，internal provider 夜间档）：
    起点不取任务 last_key 而按表内实况推断（infer_incremental_start）：
    最新快照日回退重叠窗重算——迟到入库的同日研报被吸收，重建幂等（ReplacingMergeTree）。
"""

from __future__ import annotations

import logging
import statistics
import time
from collections.abc import Iterator

from zephyr.data.provider_base import FetchResult

log = logging.getLogger(__name__)

# 表名/列序惰性初始化（schemas.* 在项目根，顶层导入重演 financial_derived_compute 懒加载口径）
_TBL: str | None = None
_COLUMNS_LIST: list[str] | None = None


def _schema() -> tuple[str, list[str]]:
    """(表全名, INSERT 列序)——首次调用时从 schema 模块加载。"""
    global _TBL, _COLUMNS_LIST
    if _COLUMNS_LIST is None or _TBL is None:
        from schemas.categories.fundamental.consensus_daily import (
            INSERT_COLUMNS,
            TABLE_NAME,
        )

        _TBL = f"c3_fundamental.{TABLE_NAME}"
        _COLUMNS_LIST = [c.strip() for c in INSERT_COLUMNS.strip("()").split(",")]
    return _TBL, _COLUMNS_LIST

# 评级分映射（华泰基本面量化之二口径：买入7/增持5/中性3/减持2/卖出1；持有≈中性、回避≈减持）
RATING_SCORE_MAP: dict[str, int] = {
    "买入": 7,
    "增持": 5,
    "中性": 3,
    "持有": 3,
    "减持": 2,
    "卖出": 1,
    "回避": 2,
}

# 调度增量重叠窗（自然日）：吸收"研报发布日在窗内但入库晚于上次构建"的迟到行
_INCREMENTAL_OVERLAP_DAYS = 3


# ============================================================================
# 纯函数核（无 IO，tests/scripts/test_build_consensus_daily.py 直测）
# ============================================================================

def rating_score(rating: str) -> int | None:
    """评级文本→分数；空/未知评级返回 None（不计入均值，计入 n_unrated）。"""
    return RATING_SCORE_MAP.get((rating or "").strip())


def expand_report_slots(rep: dict) -> list[tuple[int, float, float | None]]:
    """把一份研报展开为至多 3 个 (forecast_year, eps, pe) 槽位（fy0/fy1/fy2）。

    槽位年份<=0 或 EPS 为 None/NaN 的槽位丢弃（NaN 判定 val!=val）。
    """
    out: list[tuple[int, float, float | None]] = []
    for i in range(3):
        year = rep.get(f"fy{i}_year") or 0
        eps = rep.get(f"eps_fy{i}")
        pe = rep.get(f"pe_fy{i}")
        if not year or eps is None or eps != eps:
            continue
        if pe is not None and pe != pe:
            pe = None
        out.append((int(year), float(eps), float(pe) if pe is not None else None))
    return out


def _stats(values: list[float]) -> tuple[float, float, float, float, float]:
    """(mean, median, pstdev, min, max)；pstdev 在 n=1 时为 0。"""
    mean = sum(values) / len(values)
    med = statistics.median(values)
    std = statistics.pstdev(values) if len(values) > 1 else 0.0
    return mean, med, std, min(values), max(values)


def build_consensus_rows(
    reports: list[dict],
    trade_dates: list,
    window_days: int = 90,
    start: str | None = None,
    end: str | None = None,
) -> list[tuple]:
    """纯函数核：研报事件流 → consensus_daily 行元组（INSERT_COLUMNS 序）。

    Args:
        reports: dict 列表，键=symbol/publish_date(iso str)/fy{0,1,2}_year/eps_fy{0,1,2}/
                 pe_fy{0,1,2}/org_name/rating
        trade_dates: 交易日 date 对象升序列表（真源=c1_market.trade_calendar）
        window_days: 窗宽（自然日）
        start/end: 只输出 [start, end] 区间内的 trade_date 行（iso str，None=不限）

    Returns:
        行元组列表（20 元组，与 INSERT_COLUMNS 对齐），按 (symbol, trade_date, forecast_year) 排序。

    实现：bisect 二分定位 [trade_date-90d, trade_date] 窗口，逐日重算窗口聚合
    （窗口内容即输出规模，复杂度与产出成正比）。
    """
    import bisect
    import datetime as dt

    by_symbol: dict[str, list[dict]] = {}
    for rep in reports:
        by_symbol.setdefault(rep["symbol"], []).append(rep)

    dates_sorted = sorted(trade_dates)
    lo_iso = start or ""
    hi_iso = end or ""
    rows: list[tuple] = []

    for symbol, reps in by_symbol.items():
        reps = sorted(reps, key=lambda r: r["publish_date"])
        pub_dates = [r["publish_date"] for r in reps]
        for td in dates_sorted:
            td_iso = td.isoformat()
            if hi_iso and td_iso > hi_iso:
                break
            if lo_iso and td_iso < lo_iso:
                continue
            window_lo = (td - dt.timedelta(days=window_days)).isoformat()
            lo_idx = bisect.bisect_left(pub_dates, window_lo)
            hi_idx = bisect.bisect_right(pub_dates, td_iso)
            active = reps[lo_idx:hi_idx]
            if not active:
                continue
            per_year: dict[int, list[tuple[float, float | None]]] = {}
            for rep in active:
                for year, eps, pe in expand_report_slots(rep):
                    per_year.setdefault(year, []).append((eps, pe))
            if not per_year:
                continue
            cur_orgs = {(r.get("org_name") or "").strip() for r in active if (r.get("org_name") or "").strip()}
            cur_scores = [s for s in (rating_score(r.get("rating") or "") for r in active) if s is not None]
            n_buy = n_add = n_neu = n_neg = n_unr = 0
            for r in active:
                sc = rating_score(r.get("rating") or "")
                if sc is None:
                    n_unr += 1
                elif sc >= 7:
                    n_buy += 1
                elif sc >= 5:
                    n_add += 1
                elif sc >= 3:
                    n_neu += 1
                else:
                    n_neg += 1
            rating_mean = (sum(cur_scores) / len(cur_scores)) if cur_scores else None
            last_rep = max(r["publish_date"] for r in active)
            for year, eps_pe in sorted(per_year.items()):
                eps_vals = [e for e, _p in eps_pe]
                pe_vals = [p for _e, p in eps_pe if p is not None]
                mean, med, std, lo_v, hi_v = _stats(eps_vals)
                rows.append((
                    td_iso,
                    symbol,
                    year,
                    round(mean, 6),
                    round(med, 6),
                    round(std, 6),
                    round(lo_v, 6),
                    round(hi_v, 6),
                    round(sum(pe_vals) / len(pe_vals), 6) if pe_vals else None,
                    len(eps_vals),
                    len(cur_orgs),
                    round(rating_mean, 6) if rating_mean is not None else None,
                    n_buy,
                    n_add,
                    n_neu,
                    n_neg,
                    n_unr,
                    last_rep,
                    window_days,
                    "research_report",
                ))
    rows.sort(key=lambda r: (r[1], r[0], r[2]))
    return rows


# ============================================================================
# IO 边缘（读取/推断/产出）
# ============================================================================

def load_reports(symbols: list[str] | None = None) -> list[dict]:
    """读研报明细（FINAL 去重），展开前的原始行。"""
    from zephyr.data import ch_reader

    where = ""
    if symbols:
        sym_list = ",".join(f"'{s}'" for s in symbols)
        where = f"WHERE symbol IN ({sym_list})"
    tsv = ch_reader.query(
        "SELECT symbol, publish_date, fy0_year, eps_fy0, pe_fy0, fy1_year, eps_fy1, pe_fy1, "
        f"fy2_year, eps_fy2, pe_fy2, org_name, rating FROM c3_fundamental.research_report FINAL {where}"
    )
    reports: list[dict] = []
    for line in (tsv or "").strip().split("\n"):
        if not line:
            continue
        parts = line.split("\t")

        def _f(v: str) -> float | None:
            try:
                x = float(v)
                return None if x != x else x
            except (TypeError, ValueError):
                return None

        def _i(v: str) -> int:
            try:
                return int(float(v))
            except (TypeError, ValueError):
                return 0

        reports.append({
            "symbol": parts[0],
            "publish_date": parts[1][:10],
            "fy0_year": _i(parts[2]),
            "eps_fy0": _f(parts[3]),
            "pe_fy0": _f(parts[4]),
            "fy1_year": _i(parts[5]),
            "eps_fy1": _f(parts[6]),
            "pe_fy1": _f(parts[7]),
            "fy2_year": _i(parts[8]),
            "eps_fy2": _f(parts[9]),
            "pe_fy2": _f(parts[10]),
            "org_name": parts[11] if len(parts) > 11 else "",
            "rating": parts[12] if len(parts) > 12 else "",
        })
    log.info("研报明细 %d 行", len(reports))
    return reports


def load_trade_dates(start: str, end: str) -> list:
    """交易日历（c1_market.trade_calendar：exchange/cal_date/is_open），升序 date 列表。"""
    import datetime as dt

    from zephyr.data import ch_reader

    tsv = ch_reader.query(
        f"SELECT DISTINCT cal_date FROM c1_market.trade_calendar FINAL "
        f"WHERE exchange = 'SSE' AND is_open = 1 "
        f"AND cal_date >= toDate('{start}') AND cal_date <= toDate('{end}') ORDER BY cal_date"
    )
    days = [dt.date.fromisoformat(ln.strip()[:10]) for ln in (tsv or "").split("\n") if ln.strip()]
    log.info("交易日 %d 天（%s~%s）", len(days), start, end)
    return days


def infer_incremental_start(overlap_days: int = _INCREMENTAL_OVERLAP_DAYS) -> str | None:
    """调度增量起点推断：表内最新快照日-重叠窗；空表返回 None（=全量重建）。

    不取任务 last_key 而按表内实况推断——表状态是真源，且重叠窗吸收迟到研报。
    """
    import datetime as dt

    from zephyr.data import ch_reader

    tbl, _ = _schema()
    tsv = ch_reader.query(f"SELECT max(trade_date) FROM {tbl} FINAL")
    line = (tsv or "").strip().split("\n")[0].strip() if (tsv or "").strip() else ""
    if not line or line.startswith("\\N"):
        return None
    latest = dt.date.fromisoformat(line[:10])
    return (latest - dt.timedelta(days=overlap_days)).isoformat()


def run_compute(
    symbols: list[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    window_days: int = 90,
    batch_size: int = 100_000,
) -> Iterator[FetchResult]:
    """计算主流程：读研报明细+交易日历 → 窗口聚合 → FetchResult 批（供 CLI/scheduler 消费）。

    Args:
        symbols: 标的子集（None=全市场）。
        start/end: 快照区间（iso str，含）。start=None=研报最早 publish_date 起（全量）；
                   end=None=今天（本地日期）。
        window_days: 窗宽自然日（华泰口径 90）。
        batch_size: 单批 FetchResult 行数。

    Raises:
        RuntimeError: 研报明细为空（源表不可达或空库），拒绝产出空派生层。
    """
    reports = load_reports(symbols)
    if not reports:
        raise RuntimeError("research_report 明细为空（源表不可达或空库），拒绝产出空派生层")
    if start is None:
        start = min(r["publish_date"] for r in reports)
    if end is None:
        end = time.strftime("%Y-%m-%d")
    trade_dates = load_trade_dates(start, end)
    if not trade_dates:
        log.warning("区间 %s~%s 无交易日，0 行产出", start, end)
        return

    t0 = time.time()
    rows = build_consensus_rows(reports, trade_dates, window_days=window_days, start=start, end=end)
    log.info("聚合完成：%d 行（耗时 %.1f 秒）", len(rows), time.time() - t0)
    tbl, columns = _schema()
    for i in range(0, len(rows), batch_size):
        yield FetchResult(
            table=tbl,
            columns=columns,
            rows=rows[i : i + batch_size],
            last_key="",
            elapsed_sec=0.0,
        )


def run_check() -> int:
    """实库 PIT 交叉验证：SQL 现算 vs 表内值（茅台最新快照日，逐年比对 eps_consensus/n_reports）。

    Returns:
        0=全部一致；1=不一致或表空（调用方转译退出码）。
    """
    from zephyr.data import ch_reader

    tbl, _ = _schema()
    tsv = ch_reader.query(
        f"SELECT max(trade_date), uniqExact(symbol), count() FROM {tbl} FINAL"
    )
    if not tsv or not tsv.strip():
        log.error("CHECK FAIL: %s 无数据", tbl)
        return 1
    parts = tsv.strip().split("\t")
    latest, n_sym, n_rows = parts[0][:10], parts[1], parts[2]
    log.info("表内实况：rows=%s symbols=%s latest=%s", n_rows, n_sym, latest)

    t2 = ch_reader.query(
        "SELECT y, avg(e), count() FROM ("
        "SELECT years AS y, eps_vals AS e FROM c3_fundamental.research_report FINAL "
        "ARRAY JOIN [fy0_year, fy1_year, fy2_year] AS years, [eps_fy0, eps_fy1, eps_fy2] AS eps_vals "
        "WHERE symbol = '600519' AND publish_date <= toDate('" + latest + "') "
        "AND publish_date >= toDate('" + latest + "') - INTERVAL 90 DAY) "
        "WHERE y > 0 AND e IS NOT NULL AND e = e GROUP BY y ORDER BY y FORMAT TSV"
    )
    sql_stats: dict[int, tuple[float, int]] = {}
    for line in (t2 or "").strip().split("\n"):
        if not line:
            continue
        y, avg_e, cnt = line.split("\t")
        sql_stats[int(float(y))] = (float(avg_e), int(float(cnt)))

    t3 = ch_reader.query(
        f"SELECT forecast_year, eps_consensus, n_reports FROM {tbl} FINAL "
        f"WHERE symbol = '600519' AND trade_date = toDate('{latest}') ORDER BY forecast_year FORMAT TSV"
    )
    mismatches = 0
    for line in (t3 or "").strip().split("\n"):
        if not line:
            continue
        y, eps_c, n_rep = line.split("\t")
        y_i = int(float(y))
        if y_i not in sql_stats:
            log.error("MISMATCH: 表内有 y=%s 但 SQL 重算缺失", y_i)
            mismatches += 1
            continue
        sql_avg, sql_n = sql_stats[y_i]
        if abs(float(eps_c) - sql_avg) > 1e-4 or int(float(n_rep)) != sql_n:
            log.error("MISMATCH: y=%s 表内 eps=%s n=%s vs SQL eps=%.6f n=%s", y_i, eps_c, n_rep, sql_avg, sql_n)
            mismatches += 1
        else:
            log.info("PIT 交叉验证 OK: 600519 %s y=%s eps=%.4f n=%s", latest, y_i, sql_avg, sql_n)
    if mismatches:
        return 1
    log.info("CHECK OK: rows=%s symbols=%s latest=%s，交叉验证全部一致", n_rows, n_sym, latest)
    return 0
