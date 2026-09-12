#!/usr/bin/env python
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §4
# [MODULE] scripts.ch.build_consensus_daily
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.ch_writer; schemas.categories.fundamental.consensus_daily; schemas.categories.fundamental.fundamental_research_report
# [CONSUMERS] (回补/重建 CLI；C2 起消费方=factor/expectations 预期因子族；夜间重建调度接线为 C1.5 项)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 纯函数核 build_consensus_rows 无 IO 可测；PIT 铁律=只聚合 publish_date<=trade_date（发布即得零 embargo）；无覆盖不成行禁前向填充；forecast_year 锚定日历年（报告槽位 fy0/fy1/fy2 展开为槽位年）；评级分映射 买入7/增持5/中性持有3/减持卖出回避2-1 空值不计入均值；ReplacingMergeTree(ingest_ts) 同键重建幂等
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] research_report/交易日历不可达→exit 1；ClickHouse 写入失败→exit 2；--check 交叉验证不一致→exit 1
# [TESTS] tests/scripts/test_build_consensus_daily.py（纯函数核）+ 本脚本 --check（实库 PIT 交叉验证）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 手动构建/重建 CLI（A 类一次性运维，幂等重建按需手动执行；夜间调度接线=C1.5 待办）
"""build_consensus_daily.py — 一致预期每日快照构建器（消费端 C1，2026-09-12）。

把 c3_fundamental.research_report（研报事件流，146,633 行）聚合为
c3_fundamental.consensus_daily（每股每日×预测目标日历年的一致预期矩阵）——
华泰金工一致预期因子族（EXP-01~06）的标准输入。
设计真源：docs/_working/2026-09-12-expectation-consumption-design.md §M1。

用法::

    python scripts/ch/build_consensus_daily.py                    # 全量（2017-01-01~今天）
    python scripts/ch/build_consensus_daily.py --start 2026-08-01 # 区间重建
    python scripts/ch/build_consensus_daily.py --check            # 实库 PIT 交叉验证（SQL 重算 vs 表内值）
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import statistics
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))  # schemas.categories.* 在项目根

from schemas.categories.fundamental.consensus_daily import (  # noqa: E402
    INSERT_COLUMNS,
    TABLE_NAME,
)
from zephyr.data import ch_writer  # noqa: E402
from zephyr.data.provider_base import FetchResult  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

_TBL = f"c3_fundamental.{TABLE_NAME}"
_COLUMNS_LIST: list[str] = [c.strip() for c in INSERT_COLUMNS.strip("()").split(",")]

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

_DEFAULT_START = "2017-01-01"


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
# IO 边缘（读取/写入/校验）
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


def flush(rows: list[tuple]) -> None:
    if not rows:
        return
    result = FetchResult(table=_TBL, columns=_COLUMNS_LIST, rows=rows, last_key="", elapsed_sec=0.0)
    if not ch_writer.write_result(result):
        raise RuntimeError(f"ClickHouse 写入失败（{len(rows)} 行）")


def run_build(args: argparse.Namespace) -> int:
    try:
        reports = load_reports(args.symbols.split(",") if args.symbols else None)
    except Exception as exc:  # noqa: BLE001
        log.error("research_report 读取失败: %s", exc)
        return 1
    if not reports:
        log.error("研报明细为空，退出")
        return 1
    start = args.start or min(r["publish_date"] for r in reports)
    end = args.end or time.strftime("%Y-%m-%d")
    try:
        trade_dates = load_trade_dates(start, end)
    except Exception as exc:  # noqa: BLE001
        log.error("交易日历读取失败: %s", exc)
        return 1
    if not trade_dates:
        log.error("交易日历为空，退出")
        return 1

    t0 = time.time()
    rows = build_consensus_rows(reports, trade_dates, window_days=args.window, start=start, end=end)
    log.info("聚合完成：%d 行（耗时 %.1f 秒）", len(rows), time.time() - t0)
    try:
        for i in range(0, len(rows), args.batch_size):
            flush(rows[i : i + args.batch_size])
        log.info("写入完成：%d 行 → %s", len(rows), _TBL)
    except RuntimeError as exc:
        log.error("%s", exc)
        return 2
    return 0


def run_check() -> int:
    """实库 PIT 交叉验证：SQL 现算 vs 表内值（茅台最新快照日，逐年比对 eps_consensus/n_reports）。"""
    from zephyr.data import ch_reader

    tsv = ch_reader.query(
        f"SELECT max(trade_date), uniqExact(symbol), count() FROM {_TBL} FINAL"
    )
    if not tsv or not tsv.strip():
        log.error("CHECK FAIL: %s 无数据", _TBL)
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
    sql_stats = {}
    for line in (t2 or "").strip().split("\n"):
        if not line:
            continue
        y, avg_e, cnt = line.split("\t")
        sql_stats[int(float(y))] = (float(avg_e), int(float(cnt)))

    t3 = ch_reader.query(
        f"SELECT forecast_year, eps_consensus, n_reports FROM {_TBL} FINAL "
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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="一致预期每日快照构建（c3_fundamental.consensus_daily）")
    parser.add_argument("--start", default=None, help="快照区间起（默认=研报最早 publish_date）")
    parser.add_argument("--end", default=None, help="快照区间止（默认=今天）")
    parser.add_argument("--window", type=int, default=90, help="窗宽自然日（默认 90）")
    parser.add_argument("--symbols", default=None, help="逗号分隔标的子集（调试用）")
    parser.add_argument("--batch-size", type=int, default=100000)
    parser.add_argument("--check", action="store_true", help="验收模式：行数+PIT 交叉验证")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    try:
        sys.exit(run_check() if args.check else run_build(args))
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 — 致命错误落盘（无头运行 stdout 可能不可见）
        err_file = ROOT / ".runtime" / "tmp" / "build_consensus_daily_error.txt"
        err_file.parent.mkdir(parents=True, exist_ok=True)
        err_file.write_text(traceback.format_exc(), encoding="utf-8")
        log.error("未处理异常，详情见 %s", err_file)
        sys.exit(1)


if __name__ == "__main__":
    main()
