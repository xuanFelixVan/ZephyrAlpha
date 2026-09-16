# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md | §consensus
# [MODULE] zephyr.data.implementations.consensus_daily_repaired_compute
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.provider_base; zephyr.data.table_registry;
#                zephyr.data.implementations.consensus_daily_compute;
#                schemas.categories.fundamental.consensus_daily_repaired
# [CONSUMERS] scripts/ch/build_consensus_daily_repaired.py（重建/回补/--check CLI）;
#             zephyr.data.implementations.internal_compute_provider（集成器按需重建路由分支）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 聚合口径真源不在此——复用 consensus_daily_compute.build_consensus_rows 纯函数核
#              （90 自然日窗/PIT publish_date<=trade_date/评级 7-5-3-2-1/日历年锚定/无覆盖不成行），
#              本模块只做"证据源适配器"：把 C4 PDF 提取行合成回研报行形态喂进该核，故 DS-229 与本表
#              的窗口/评级/覆盖统计逐列同义，差异只在 EPS 值来自发布时点原件；
#              守卫参数为预注册域内判据（禁按结果调参）：G1 eps∈(0,50]（2017-2021 全 A 股实际最高
#              EPS=茅台 2021 年 41.8 元，>50 段目视 14/14 均为营业收入/净利润行串列，无未来函数）；
#              G2 槽位选取规则 S1=先取 forecast_year>=发布年升序、不足 3 个再补发布年-1 降序，
#              截断至 3（对齐研报 fy0/fy1/fy2 三槽；94.2% 研报恰有 3 个年度故无歧义）；
#              mid/low 置信行不入聚合（铁律，留档于源表）；
#              segment B（analyst_forecast）是官方聚合快照，不经窗口聚合，window_days 记 1，
#              n_orgs 结构性不可得记 0、eps_std 恒 0、eps_min=eps_max=eps_consensus（分歧类因子不可用）；
#              2022-01-01~2026-07-21 为数据空洞（PDF 被 EO_Bot 挡，方案 §1 出界），禁前向填充故不补
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 源表不可达/空->RuntimeError（拒绝产出空派生层）；写入失败由调用方转译退出码
# [TESTS] tests/scripts/test_build_consensus_daily_repaired.py（槽位守卫+合成核纯函数，零 IO）
#         + build_consensus_daily_repaired.py --check（实库三重对照）
# [TTL] permanent
"""consensus_daily_repaired 计算核——PDF 发布时点证据 → 一致预期每日快照（C4 历史修复双轨重建）。

不重复实现聚合逻辑：窗口/PIT/评级/统计全部委托生产核
`consensus_daily_compute.build_consensus_rows`（DS-229 同源），本模块只负责把
`c3_fundamental.pdf_forecast_extracted`（C4 从研报 PDF 原文提取的发布时点预测）
合成回该核期望的"研报行"形态，从而让 DS-229 与 repaired 表的差异**只剩 EPS 值的来源**——
这是双轨对照可解释性的前提（对照验收若不同口径，秩相关就没有意义）。

两段数据源（见 schema 模块覆盖边界声明）：
    segment A  2017-01-02~2021-12-31  pdf_forecast_extracted(high) + research_report(评级/计数干净列)
    segment B  2026-07-22~最新        analyst_forecast（同花顺官方一致预期日度快照，§9.2 认定干净源）
"""

from __future__ import annotations

import logging
from collections.abc import Iterator

from zephyr.data.implementations.consensus_daily_compute import (
    build_consensus_rows,
    rating_score,
)
from zephyr.data.provider_base import FetchResult
from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 预注册守卫参数（方案 §6/§9.3 铁律的机读形态；改这些值=挪判据，须裁定）
# ---------------------------------------------------------------------------
GUARD_CONFIDENCE = "high"          # 铁律：high-only 入聚合，mid 留档待复核升级、low 排除
GUARD_EPS_GT = 0.0                 # G1 下界：非正 EPS 不入（提取无负值行，防御性）
GUARD_EPS_LE = 50.0                # G1 上界：域内不可能值（见 INVARIANTS 依据）
SLOT_MAX = 3                       # G2：研报槽位数上限（对齐 fy0/fy1/fy2）

# 重建批次标识（写入 build_batch 列；守卫参数与源行数写台账，不塞进数据列）
BUILD_BATCH = "c4-repair-20260916"

# segment A/B 边界（实测源表极值，禁手工漂移：由 probe_boundaries() 复核）
SEGMENT_A_START = "2017-01-02"
SEGMENT_A_END = "2021-12-31"
SEGMENT_B_START = "2026-07-22"

# 聚合窗口口径（与 DS-229 构建器同款默认值，双轨对照必须同窗）
WINDOW_DAYS = 90

# 表名走 TableRegistry 真源（#ARCH-CH-024：已注册表名禁硬编码字面量）
_TBL_RESEARCH_REPORT = get_registry().table("fund_research_report")
_TBL_ANALYST_FORECAST = get_registry().table("fund_analyst_forecast")

# SQL 集中化（§5.160.2：应用代码禁裸 SQL 字面量；参数只经 .format 注入自家常量/推断值，
# 无外部输入拼接面）。pdf_forecast_extracted 属 C4 域、尚未登记品类，故仍是字面量。
_SQL_REPORT_ROWS = (
    "SELECT report_id, symbol, publish_date, org_name, rating "
    "FROM {tbl} FINAL "
    "WHERE publish_date >= toDate('{lo}') AND publish_date <= toDate('{hi}')"
)
_SQL_PDF_EPS = (
    "SELECT report_id, forecast_year, eps "
    "FROM c3_fundamental.pdf_forecast_extracted FINAL "
    "WHERE confidence = '{confidence}'"
)
_SQL_ANALYST_ROWS = (
    "SELECT toString(report_date), symbol, forecast_year, forecast_eps, forecast_pe, rating, "
    "analyst_count FROM {tbl} FINAL "
    "WHERE report_date >= toDate('{lo}') AND report_date <= toDate('{hi}')"
)
_SQL_ANALYST_MAX_DATE = "SELECT max(report_date) FROM {tbl} FINAL"


# ---------------------------------------------------------------------------
# segment A 证据适配（PDF 提取行 → build_consensus_rows 的研报行形态）
# ---------------------------------------------------------------------------

def pick_slots(years_eps: list[tuple[int, float]], publish_year: int) -> list[tuple[int, float]]:
    """G2 槽位选取规则 S1：从一份研报的 (forecast_year, eps) 集合里选出至多 SLOT_MAX 个年度。

    先取 forecast_year >= publish_year 的（真·前瞻预测），按年升序；不足再补
    forecast_year == publish_year-1 的（年初研报预测上年度合法，抽核首批 #7 大族激光案实证），
    按年降序（即离发布年最近的优先）。

    纯函数、零 IO，供单测直测。
    """
    forward = sorted((y, e) for y, e in years_eps if y >= publish_year)
    backward = sorted(((y, e) for y, e in years_eps if y < publish_year), key=lambda t: -t[0])
    return (forward + backward)[:SLOT_MAX]


def guard_pass(eps: float | None) -> bool:
    """G1 量纲守卫：eps 必须落在 (GUARD_EPS_GT, GUARD_EPS_LE]。None/NaN 一律拒绝。"""
    if eps is None:
        return False
    if eps != eps:  # NaN
        return False
    return GUARD_EPS_GT < eps <= GUARD_EPS_LE


def to_report_row(
    symbol: str,
    publish_date: str,
    org_name: str,
    rating: str,
    slots: list[tuple[int, float]],
) -> dict:
    """把一份研报合成 build_consensus_rows 期望的行 dict（fy0/fy1/fy2 三槽 + 干净计数列）。

    槽位不足三位时对应 fy{i}_year=0 且 eps=None（该核按 year<=0 或 eps None 丢弃该槽）。
    PE 恒 None：C4 提取表 pe 列实测 0/192302 有值，故 repaired 的 pe_consensus 对 segment A 恒 NULL。
    """
    picked = pick_slots(slots, int(publish_date[:4]))
    row: dict = {
        "symbol": symbol,
        "publish_date": publish_date[:10],
        "org_name": org_name,
        "rating": rating,
    }
    for i in range(SLOT_MAX):
        if i < len(picked):
            row[f"fy{i}_year"] = picked[i][0]
            row[f"eps_fy{i}"] = picked[i][1]
        else:
            row[f"fy{i}_year"] = 0
            row[f"eps_fy{i}"] = None
        row[f"pe_fy{i}"] = None
    return row


def _pdf_slots_by_report(pdf_tsv: str) -> tuple[dict[str, list[tuple[int, float]]], int]:
    """解析 high 置信 EPS 提取行 → {report_id: [(forecast_year, eps)]}，并计数守卫剔除。

    列不足=静默跳过（非数据行）；EPS/年份不可解析或守卫不过=计入 n_guard_drop（出证口径）。
    """
    slots_by_report: dict[str, list[tuple[int, float]]] = {}
    n_guard_drop = 0
    for line in pdf_tsv.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        try:
            eps = float(parts[2])
        except ValueError:
            n_guard_drop += 1
            continue
        if not guard_pass(eps):
            n_guard_drop += 1
            continue
        try:
            year = int(float(parts[1]))
        except ValueError:
            n_guard_drop += 1
            continue
        slots_by_report.setdefault(parts[0], []).append((year, eps))
    return slots_by_report, n_guard_drop


def load_pdf_evidence() -> tuple[list[dict], dict[str, list[tuple[int, float]]], dict]:
    """读 segment A 两份证据：research_report 干净行 + pdf_forecast_extracted 守卫通过行。

    research_report 提供 symbol/publish_date/org_name/rating（§9.2 定性：这些列不受值污染，
    publish_date 与提取表逐行一致，实测 13268/13268 零漂移），决定窗口内的评级/覆盖统计集合；
    pdf_forecast_extracted 只提供 EPS 值，按 report_id 挂回研报行。

    Returns:
        (report_rows, slot_stats) —— report_rows 为喂给 build_consensus_rows 的 dict 列表
        （含"无 EPS 证据"的研报，它们只贡献评级/覆盖统计，与该核的 n_unrated 语义一致）；
        slot_stats 为守卫计数留痕 dict。

    Raises:
        RuntimeError: 任一证据源为空。
    """
    from zephyr.data import ch_reader

    rr_tsv = ch_reader.query(
        _SQL_REPORT_ROWS.format(tbl=_TBL_RESEARCH_REPORT, lo=SEGMENT_A_START, hi=SEGMENT_A_END)
    )
    if not (rr_tsv or "").strip():
        raise RuntimeError("research_report segment A 区间为空（源表不可达），拒绝产出空派生层")

    pdf_tsv = ch_reader.query(_SQL_PDF_EPS.format(confidence=GUARD_CONFIDENCE))
    if not (pdf_tsv or "").strip():
        raise RuntimeError("pdf_forecast_extracted high 置信行为空，拒绝产出空派生层")

    slots_by_report, n_guard_drop = _pdf_slots_by_report(pdf_tsv)

    n_slot_trim = 0
    for rid, lst in slots_by_report.items():
        if len(lst) > SLOT_MAX:
            n_slot_trim += len(lst) - SLOT_MAX

    report_rows: list[dict] = []
    for line in rr_tsv.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        rid = parts[0]
        report_rows.append(
            to_report_row(
                symbol=parts[1],
                publish_date=parts[2],
                org_name=parts[3] if len(parts) > 3 else "",
                rating=parts[4] if len(parts) > 4 else "",
                slots=slots_by_report.get(rid, []),
            )
        )
    stats = {
        "reports_in_window": len(report_rows),
        "reports_with_eps": len(slots_by_report),
        "eps_rows_kept": sum(len(v) for v in slots_by_report.values()),
        "eps_rows_dropped_by_guard": n_guard_drop,
        "slot_rows_trimmed": n_slot_trim,
    }
    log.info(
        "segment A 证据：%d 研报行（其中 %d 携带 EPS），EPS 行 %d，守卫剔除 %d，槽位截断 %d",
        stats["reports_in_window"], stats["reports_with_eps"], stats["eps_rows_kept"],
        stats["eps_rows_dropped_by_guard"], stats["slot_rows_trimmed"],
    )
    return report_rows, stats


def build_segment_a(
    trade_dates: list,
    start: str | None,
    end: str | None,
    window_days: int,
    symbols: list[str] | None,
) -> tuple[list[tuple], dict]:
    """segment A 产出：DS-229 二十列（改 data_source 为提取表名）+ provenance 两列。"""
    from schemas.categories.fundamental.consensus_daily_repaired import EPS_SOURCE_PDF_HIGH

    report_rows, stats = load_pdf_evidence()
    if symbols:
        keep = set(symbols)
        report_rows = [r for r in report_rows if r["symbol"] in keep]
    base = build_consensus_rows(
        report_rows, trade_dates, window_days=window_days, start=start, end=end
    )
    # 现核第 20 列硬编码 'research_report'（=DS-229 口径），双轨表须如实标 EPS 证据源
    out = [
        r[:19] + ("pdf_forecast_extracted", EPS_SOURCE_PDF_HIGH, BUILD_BATCH)
        for r in base
    ]
    return out, stats


# ---------------------------------------------------------------------------
# segment B（官方一致预期快照，非窗口聚合）
# ---------------------------------------------------------------------------

def _rating_counts(sc: float | None) -> tuple[int, int, int, int, int]:
    """评级分档：买入≥7 / 增持 5-6 / 中性·持有 3-4 / 消极 <3 / 未评（sc 为 None）。"""
    return (
        1 if sc is not None and sc >= 7 else 0,
        1 if sc is not None and 5 <= sc < 7 else 0,
        1 if sc is not None and 3 <= sc < 5 else 0,
        1 if sc is not None and sc < 3 else 0,
        1 if sc is None else 0,
    )


def _segment_b_row(parts: list[str], eps_source: str) -> tuple | None:
    """单条 analyst_forecast 快照 → 与 segment A 同构的 22 列行；EPS 不可用则返回 None。

    该源是聚合值不经窗口：window_days 记 1、n_orgs 结构性不可得记 0、eps_std 恒 0、
    eps_min=eps_max=eps_consensus。
    """
    import datetime as dt

    d, symbol, fy, eps_s, pe_s, rating, ac_s = parts[:7]
    d = d[:10]
    try:
        eps = float(eps_s)
    except ValueError:
        return None
    if eps != eps or eps <= 0:
        return None
    try:
        pe: float | None = float(pe_s)
    except ValueError:
        pe = None
    if pe is not None and pe != pe:
        pe = None
    try:
        n_analysts = int(float(ac_s))
    except ValueError:
        n_analysts = 0
    sc = rating_score(rating)
    n_buy, n_add, n_neu, n_neg, n_unrated = _rating_counts(sc)
    return (
        d, symbol, int(float(fy)), round(eps, 6), round(eps, 6), 0.0, round(eps, 6), round(eps, 6),
        pe, n_analysts, 0, float(sc) if sc is not None else None,
        n_buy, n_add, n_neu, n_neg, n_unrated,
        dt.date.fromisoformat(d).isoformat(), 1,
        "analyst_forecast", eps_source, BUILD_BATCH,
    )


def build_segment_b(trade_dates: list, end: str | None) -> list[tuple]:
    """把 analyst_forecast 日度快照直接映射为同构行（不经 build_consensus_rows）。

    该源本身即聚合值：forecast_eps/forecast_pe/analyst_count/rating 每股每日一行（实测
    rows==uniqExact(symbol) per report_date），故无窗口可算——window_days 记 1，
    n_orgs 结构性不可得记 0，eps_std 恒 0，eps_min=eps_max=eps_consensus。
    非交易日的 report_date 丢弃（禁前向填充）。
    """
    from zephyr.data import ch_reader
    from schemas.categories.fundamental.consensus_daily_repaired import (
        EPS_SOURCE_ANALYST_FORECAST,
    )

    trade_set = {d if isinstance(d, str) else d.isoformat() for d in trade_dates}
    hi = end or max(trade_set)
    tsv = ch_reader.query(
        _SQL_ANALYST_ROWS.format(tbl=_TBL_ANALYST_FORECAST, lo=SEGMENT_B_START, hi=hi)
    )
    rows: list[tuple] = []
    n_offcal = 0
    for line in (tsv or "").strip().split("\n"):
        parts = line.split("\t")
        if len(parts) < 7:
            continue
        if parts[0][:10] not in trade_set:
            n_offcal += 1
            continue
        row = _segment_b_row(parts, EPS_SOURCE_ANALYST_FORECAST)
        if row is not None:
            rows.append(row)
    if n_offcal:
        log.info("segment B 丢弃非交易日快照 %d 行（禁前向填充）", n_offcal)
    log.info("segment B 产出 %d 行", len(rows))
    return rows


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def run_compute_repaired(
    symbols: list[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    window_days: int = WINDOW_DAYS,
    batch_size: int = 100_000,
    skip_segment_b: bool = False,
) -> Iterator[FetchResult]:
    """两段产出合流为 FetchResult 批（供 CLI/scheduler 消费）。

    start/end 只约束 segment A 的快照日区间；segment B 恒从 SEGMENT_B_START 起（不受 start 下界
    影响，因为 B 段是独立证据链，与 A 段无连续性关系）。

    Raises:
        RuntimeError: 源表不可达或区间无交易日。
    """
    from zephyr.data.implementations.consensus_daily_compute import load_trade_dates
    from schemas.categories.fundamental.consensus_daily_repaired import (
        INSERT_COLUMNS,
        TABLE_NAME,
    )

    lo = start or SEGMENT_A_START
    hi = end or SEGMENT_A_END
    trade_dates = load_trade_dates(lo, hi)
    if not trade_dates:
        raise RuntimeError(f"区间 {lo}~{hi} 无交易日，拒绝产出")

    rows_a, stats = build_segment_a(trade_dates, lo, hi, window_days, symbols)
    all_rows = list(rows_a)
    if not skip_segment_b:
        b_end = _segment_b_end()
        b_dates = load_trade_dates(SEGMENT_B_START, b_end)
        if b_dates:
            all_rows.extend(build_segment_b(b_dates, b_end))
    if not all_rows:
        raise RuntimeError("两段均 0 行产出（源表可达但无匹配），拒绝写入空派生层")

    all_rows.sort(key=lambda r: (r[1], r[0], r[2]))
    columns = [c.strip() for c in INSERT_COLUMNS.strip("()").split(",")]
    tbl = f"c3_fundamental.{TABLE_NAME}"
    log.info("合计产出 %d 行（A=%d, B=%d）", len(all_rows), len(rows_a), len(all_rows) - len(rows_a))
    for i in range(0, len(all_rows), batch_size):
        yield FetchResult(
            table=tbl, columns=columns, rows=all_rows[i : i + batch_size],
            last_key="", elapsed_sec=0.0,
        )


def segment_stats() -> dict:
    """守卫/证据计数留痕（CLI 出证与台账用，不落数据列）。"""
    _, stats = load_pdf_evidence()
    return stats


def _segment_b_end() -> str:
    """segment B 终点=analyst_forecast 表内最新快照日（按表实况推断，禁 datetime.now()）。"""
    from zephyr.data import ch_reader

    tsv = ch_reader.query(_SQL_ANALYST_MAX_DATE.format(tbl=_TBL_ANALYST_FORECAST))
    line = (tsv or "").strip().split("\n")[0].strip() if (tsv or "").strip() else ""
    if not line or line.startswith("\\N"):
        raise RuntimeError("analyst_forecast 表为空，无法推断 segment B 终点")
    return line[:10]
