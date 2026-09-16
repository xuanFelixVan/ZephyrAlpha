# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §4
# [MODULE] scripts.ch.build_consensus_daily_repaired
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.data.buffered_writer; zephyr.data.implementations.consensus_daily_repaired_compute;
#                zephyr.data.table_registry
# [CONSUMERS] (C4 历史修复重建/回补/验收 CLI；值类因子复评 EXP-01/02/03/05 的数据源生产者)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 聚合口径委托 consensus_daily_repaired_compute（其再委托生产核 consensus_daily_compute，
#              PIT/窗口/评级语义与 DS-229 逐列同义）；写入经 BufferedWriter 攒批层（裁定 #ARCH-CH-003，
#              循环内禁直调 write_result=CH-BATCH-SIZE 硬拦），INSERT 次数=flush 次数=data parts 数；
#              ReplacingMergeTree(ingest_ts) 同键重建幂等；
#              只写 consensus_daily_repaired，永不写 DS-229 consensus_daily（双轨物理隔离，方案 §L48）；
#              --check 三重对照判据为方案 §6 预注册值，禁挪
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 源表不可达/区间无交易日->exit 1；ClickHouse 写入失败->exit 2；
#                  --check 对照判据不过->exit 1（并把各项数值打印到 stdout 供台账回填）
# [TESTS] tests/scripts/test_build_consensus_daily_repaired.py（守卫+槽位纯函数）+ 本脚本 --check（实库三重对照）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 手动重建/回补/验收 CLI（A 类一次性运维；
#                                   repaired 表未进 tasks.yaml 夜间管线，Owner 验收切换前不自动跑）
"""build_consensus_daily_repaired.py — C4 历史修复双轨重建器（2026-09-16）。

从 `c3_fundamental.pdf_forecast_extracted`（研报 PDF 原文提取的发布时点预测）按 DS-229 同口径
重聚合出 `c3_fundamental.consensus_daily_repaired`，与污染的 consensus_daily 物理隔离双轨并存，
验收后交 Owner 切换——值类因子（EXP-01/02/03/05）历史解锁的第一步。

施工依据：docs/_working/2026-09-14-c4-history-repair-plan.md §2-L4/§6；
污染定性：policies/expectation_consumption_design_policy.md §9；裁定 #253。

用法::

    python scripts/ch/apply_consensus_daily_repaired_ddl.py          # 先建表
    python scripts/ch/build_consensus_daily_repaired.py              # 全量重建（A 段 + B 段）
    python scripts/ch/build_consensus_daily_repaired.py --stats      # 只出守卫/证据计数，不写库
    python scripts/ch/build_consensus_daily_repaired.py --symbols 600519 --start 2019-01-01
    python scripts/ch/build_consensus_daily_repaired.py --check      # 三重对照验收（方案 §6 判据）
"""

from __future__ import annotations

import argparse
import logging
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))  # schemas.categories.* 在项目根

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# 纯函数核转出（tests/scripts/test_build_consensus_daily_repaired.py 经本壳按名导入）
# build_consensus_rows 来自生产核 consensus_daily_compute——适配层复用同一聚合真源，不克隆
from zephyr.data.implementations.consensus_daily_compute import build_consensus_rows  # noqa: E402
from schemas.categories.fundamental.consensus_daily_repaired import (  # noqa: E402
    EPS_SOURCE_PDF_HIGH,
)
from zephyr.data.implementations.consensus_daily_repaired_compute import (  # noqa: E402
    BUILD_BATCH,
    GUARD_CONFIDENCE,
    GUARD_EPS_LE,
    SEGMENT_A_END,
    SEGMENT_A_START,
    SLOT_MAX,
    WINDOW_DAYS,
    guard_pass,
    load_pdf_evidence,
    pick_slots,
    run_compute_repaired,
    to_report_row,
)
from zephyr.data.table_registry import get_registry  # noqa: E402

# 方案 §6 预注册验收判据（禁挪；数值改动=挪判据，须裁定）
ACCEPTANCE_OVERLAP_RANK_IC = 0.9      # ① B 段与 DS-229 重叠期秩相关下限
# ② 锚点股历史曲线：覆盖条件检验（"多源却恒等"=DS-229 定义性症状）
ACCEPTANCE_ANCHOR_MULTI_SOURCE_N = 2  # 窗口内曾出现 ≥2 份研报即视为多源序列
ACCEPTANCE_ANCHOR_MIN_REVISIONS = 2   # 多源序列的 eps_consensus 去重值数下限
# ③ 窗口重算对照的抽样规模下限（本次重建自拟实现口径，方案 §6 未预注册数值）
ACCEPTANCE_RECOMPUTE_MIN_ROWS = 100   # 累计比对行数下限（不足即判 FAIL，防抽样过窄假 PASS）
ANCHOR_SYMBOLS = ("600519", "000858", "601318", "000651", "600036")

# 表名走 TableRegistry 真源（#ARCH-CH-024：本门查 added 行字符串常量，scripts/ch/ 不豁免）
_TBL_REPAIRED = get_registry().table("fund_consensus_daily_repaired")
_TBL_POLLUTED = get_registry().table("fund_consensus_daily")
_TBL_RESEARCH_REPORT = get_registry().table("fund_research_report")
_TBL_PDF_EVIDENCE = get_registry().table("pdf_forecast_extracted")


def run_build(args: argparse.Namespace) -> int:
    from zephyr.data.buffered_writer import BufferedWriter
    from schemas.categories.fundamental.consensus_daily_repaired import TABLE_NAME

    phase = "read"
    try:
        result_iter = run_compute_repaired(
            symbols=args.symbols.split(",") if args.symbols else None,
            start=args.start,
            end=args.end,
            window_days=args.window,
            batch_size=args.batch_size,
            skip_segment_b=args.skip_segment_b,
        )
        # 裁定 #ARCH-CH-003：写入必经 BufferedWriter 攒批层（循环内禁直调 write_result，
        # CH-BATCH-SIZE 门禁硬拦）；max_rows 与产出行分批同宽，data parts 数=flush 次数。
        writer = BufferedWriter(f"c3_fundamental.{TABLE_NAME}", max_rows=args.batch_size)
        for fr in result_iter:
            phase = "write"
            if not writer.add(fr):
                log.error("ClickHouse 写入失败（%d 行）", len(fr.rows))
                return 2
            phase = "read"
        if not writer.flush():
            log.error("ClickHouse 末批 flush 失败（缓冲区残留 %d 行）", writer.pending_rows)
            return 2
        n_written = writer.total_flushed
        if n_written == 0:
            log.warning("0 行写入（区间无快照或无交易日）")
            return 1
        log.info(
            "写入完成：%d 行 / %d 次 INSERT（build_batch=%s）",
            n_written, writer.flush_count, BUILD_BATCH,
        )
    except RuntimeError as exc:
        log.error("%s", exc)
        return 1
    except Exception as exc:  # noqa: BLE001
        log.error("%s 阶段异常: %s", phase, exc)
        return 1 if phase == "read" else 2
    return 0


def run_stats() -> int:
    """只出守卫/证据计数（重建前置出证，不写库）。"""
    _, stats = load_pdf_evidence()
    for k, v in stats.items():
        print(f"{k}={v}")
    print(f"guard=eps_in({GUARD_CONFIDENCE}_confidence,{0}<{GUARD_EPS_LE:.0f}] slots<={SLOT_MAX}")
    return 0


# ---------------------------------------------------------------------------
# 三重对照验收（方案 §6）
# ---------------------------------------------------------------------------

def _check_overlap_rank() -> tuple[bool, str]:
    """① B 段（analyst_forecast 证据链）与 DS-229 在同期的横截面秩相关。

    B 段与 DS-229 在 2026-07-22~最新 都覆盖同一 forecast_year——DS-229 该段来自前向积累的
    研报快照（§9.2 认定近端不受污染），故两条独立证据链在此应当高度一致；不一致说明
    repaired 的口径适配（而非源）出了问题。判据=逐快照日 Spearman 均值 ≥ 0.9。
    """
    from zephyr.data import ch_reader

    tsv = ch_reader.query(
        "SELECT r.trade_date, corr(rRank, cRank) FROM ("
        "  SELECT trade_date, symbol, forecast_year, rank() OVER (PARTITION BY trade_date, forecast_year "
        f"         ORDER BY eps_consensus) rRank, eps_consensus FROM {_TBL_REPAIRED} FINAL"
        "  WHERE eps_source='analyst_forecast_snapshot'"
        ") r INNER JOIN ("
        "  SELECT trade_date, symbol, forecast_year, rank() OVER (PARTITION BY trade_date, forecast_year "
        f"         ORDER BY eps_consensus) cRank, eps_consensus FROM {_TBL_POLLUTED} FINAL"
        "  WHERE trade_date >= toDate('2026-07-22')"
        ") c ON r.trade_date=c.trade_date AND r.symbol=c.symbol AND r.forecast_year=c.forecast_year "
        "GROUP BY r.trade_date HAVING count() >= 30 ORDER BY r.trade_date"
    )
    if not (tsv or "").strip():
        return False, "① B 段与 DS-229 无可比重叠快照日（B 段未构建或 forecast_year 不对齐）"
    ics = [float(ln.split("\t")[1]) for ln in tsv.strip().split("\n") if ln.strip()]
    mean_ic = sum(ics) / len(ics)
    ok = mean_ic >= ACCEPTANCE_OVERLAP_RANK_IC
    return ok, (
        f"① 重叠秩相关 均值={mean_ic:.4f} 快照日数={len(ics)} "
        f"min={min(ics):.4f} max={max(ics):.4f} 判据≥{ACCEPTANCE_OVERLAP_RANK_IC} -> {'PASS' if ok else 'FAIL'}"
    )


def _check_anchor_curves() -> tuple[bool, str]:
    """② 锚点股历史曲线：多源即须有修正（DS-229 的定义性症状是"多源却恒等"）。

    判据 (a) 覆盖条件检验——任一锚点序列若其窗口内曾出现 ≥2 份不同研报
    （max(n_reports)≥ACCEPTANCE_ANCHOR_MULTI_SOURCE_N），则 eps_consensus 去重值必须
    ≥ACCEPTANCE_ANCHOR_MIN_REVISIONS；一条不满足即 FAIL。比"绝对去重数阈值"更严且对症：
    单份研报覆盖的稀疏年份天然恒定（无可修正源），不因此判死；而"两份以上研报却值不动"
    正是回放污染的症状，必须为零。
    判据 (b) 反面证据——同窗 DS-229 每个 forecast_year 的 uniq 与快照日数一并量出。
    注意 DS-229 在 2017-2021 窗口内的 forecast_year 全当下年份（2026-2028，回放使然），
    不可按 2017-2021 过滤，否则查不到行。

    本项判据为本次重建自拟实现（方案 §6 只预注册锚点准确率≥90%/抽核≤5%/秩相关≥0.9），
    口径变更留痕于 docs/_working/reports/ 台账。
    """
    from zephyr.data import ch_reader

    sym_list = ",".join(f"'{s}'" for s in ANCHOR_SYMBOLS)
    tsv = ch_reader.query(
        "SELECT symbol, forecast_year, uniqExact(eps_consensus) u, count() n, max(n_reports) max_n "
        f"FROM {_TBL_REPAIRED} FINAL "
        f"WHERE symbol IN ({sym_list}) AND eps_source='pdf_forecast_high' "
        "GROUP BY symbol, forecast_year ORDER BY symbol, forecast_year"
    )
    polluted = ch_reader.query(
        "SELECT forecast_year, uniqExact(eps_consensus) u, count(distinct trade_date) d "
        f"FROM {_TBL_POLLUTED} FINAL "
        f"WHERE symbol='600519' AND trade_date BETWEEN toDate('{SEGMENT_A_START}') "
        f"AND toDate('{SEGMENT_A_END}') GROUP BY forecast_year ORDER BY forecast_year"
    )
    lines = [ln.split("\t") for ln in (tsv or "").strip().split("\n") if ln.strip()]
    if not lines:
        return False, "② repaired 锚点股 A 段无行（未构建？）"

    offenders = [
        f"{x[0]}/{x[1]}:u={x[2]},max_n={x[4]}"
        for x in lines
        if int(float(x[4])) >= ACCEPTANCE_ANCHOR_MULTI_SOURCE_N
        and int(float(x[2])) < ACCEPTANCE_ANCHOR_MIN_REVISIONS
    ]
    multi_source = sum(1 for x in lines if int(float(x[4])) >= ACCEPTANCE_ANCHOR_MULTI_SOURCE_N)
    pol_bits = "; ".join(f"DS229 y={y}:uniq={u}/{d}日" for y, u, d in
                         ((ln.split("\t") + ["", "", ""])[:3] for ln in (polluted or "").strip().split("\n") if ln.strip()))
    live = [int(float(x[2])) for x in lines]
    ok = not offenders
    return ok, (
        f"② 锚点曲线 repaired 序列={len(lines)}（其中多源序列={multi_source}）"
        f" 去重值 min={min(live)} max={max(live)} | 反面证据 {pol_bits} | "
        f"违反'多源须有修正'的序列={len(offenders)}{'：' + ', '.join(offenders[:5]) if offenders else ''} "
        f"-> {'PASS' if ok else 'FAIL'}"
    )


def _accumulate_recompute(tsv: str, snap: str) -> tuple[int, int]:
    """比对单个快照日的重算结果行，返回 (比对行数, 不一致数)。

    表内值 vs 独立 SQL 重算值容差 0.05（表内存 round(6)）；n_reports 与重算
    count(DISTINCT report_id) 须相等（重算侧有行时）。sql 侧无匹配（\\N）=不参与比对。
    """
    checked = mismatch = 0
    for ln in (tsv or "").strip().split("\n"):
        parts = ln.split("\t")
        if len(parts) < 5 or not parts[3] or parts[3].startswith("\\N"):
            continue
        checked += 1
        table_avg, sql_avg = float(parts[2]), float(parts[3])
        table_n = int(float(parts[4]))
        sql_n = int(float(parts[5])) if len(parts) > 5 else -1
        if abs(table_avg - sql_avg) > 0.05 or (sql_n > 0 and table_n != sql_n):
            mismatch += 1
            log.warning("MISMATCH %s %s/%s 表=%.4f,n=%d vs SQL=%.4f,n=%d",
                        snap, parts[0], parts[1], table_avg, table_n, sql_avg, sql_n)
    return checked, mismatch


def _check_window_recompute() -> tuple[bool, str]:
    """③ 窗口聚合值 SQL 重算对照：表内 eps_consensus vs 源表现算（同源异路径交叉验证）。

    与 DS-229 的 --check 不同——那是对污染的源重算（同饮一池水，验不了语义，§9.1 方法论教训）；
    本项从 pdf_forecast_extracted 独立重算窗口均值，与表内值比对，验证的是"适配+聚合"链路。

    抽样=A 段每季度最后一个快照日全抽（锚点股×预测年为比对单元），避免只验单日导致
    156 万行重建覆盖面过薄。比对行数下限为本次重建自拟实现口径（方案 §6 未预注册此项数值）。
    """
    from zephyr.data import ch_reader

    sym_list = ",".join(f"'{s}'" for s in ANCHOR_SYMBOLS)
    days_tsv = ch_reader.query(
        f"SELECT toString(max(trade_date)) FROM {_TBL_REPAIRED} FINAL "
        "WHERE eps_source='pdf_forecast_high' AND symbol IN (" + sym_list + ") "
        "GROUP BY toStartOfQuarter(trade_date) ORDER BY toStartOfQuarter(trade_date)"
    )
    quarters = [ln.strip()[:10] for ln in (days_tsv or "").strip().split("\n") if ln.strip()[:10]]
    if not quarters:
        return False, "③ 锚点股 A 段无快照日可抽"

    checked = 0
    mismatch = 0
    for snap in quarters:
        t2 = ch_reader.query(
            "SELECT r.symbol, r.forecast_year, r.eps_consensus, sql_avg, r.n_reports, sql_n FROM ("
            "  SELECT symbol, forecast_year, eps_consensus, n_reports "
            f"  FROM {_TBL_REPAIRED} FINAL WHERE trade_date=toDate('{snap}') "
            f"  AND eps_source='pdf_forecast_high' AND symbol IN ({sym_list})"
            ") r LEFT JOIN ("
            "  SELECT rr.symbol AS s, p.forecast_year AS fy, avg(p.eps) sql_avg, "
            "count(DISTINCT p.report_id) sql_n "
            f"  FROM {_TBL_PDF_EVIDENCE} p FINAL "
            f"  INNER JOIN (SELECT DISTINCT report_id, symbol, publish_date FROM {_TBL_RESEARCH_REPORT} FINAL) rr "
            "    USING (report_id) "
            f"  WHERE p.confidence='{GUARD_CONFIDENCE}' AND p.eps>0 AND p.eps<={GUARD_EPS_LE} "
            f"    AND rr.publish_date <= toDate('{snap}') "
            f"    AND rr.publish_date >= toDate('{snap}') - INTERVAL {WINDOW_DAYS} DAY "
            "  GROUP BY s, fy"
            ") c ON r.symbol=c.s AND r.forecast_year=c.fy "
            "ORDER BY r.symbol, r.forecast_year"
        )
        checked_i, mismatch_i = _accumulate_recompute(t2, snap)
        checked += checked_i
        mismatch += mismatch_i
    ok = checked >= ACCEPTANCE_RECOMPUTE_MIN_ROWS and mismatch == 0
    return ok, (
        f"③ 窗口重算对照 A 段季末快照日全抽 {len(quarters)} 日 "
        f"比对行={checked}（下限 {ACCEPTANCE_RECOMPUTE_MIN_ROWS}）不一致={mismatch} "
        f"（容差 0.05，因表内存 round(6)） -> {'PASS' if ok else 'FAIL'}"
    )


def run_check() -> int:
    """三重对照验收：三项全 PASS 才退 0（方案 §6 门禁；不过的错数据不得进入切换）。"""
    from zephyr.data import ch_reader

    head = ch_reader.query(
        "SELECT toString(count()), toString(uniqExact(symbol)), toString(min(trade_date)), "
        "toString(max(trade_date)), toString(uniqExact(eps_source)) "
        f"FROM {_TBL_REPAIRED} FINAL"
    ).strip()
    if not head or head.startswith("0\t"):
        print("CHECK FAIL: consensus_daily_repaired 无数据（先跑构建）")
        return 1
    rows, syms, dmin, dmax, nsrc = head.split("\t")
    print(f"表内实况：rows={rows} symbols={syms} span={dmin}~{dmax} eps_source 数={nsrc}")

    results = [_check_overlap_rank(), _check_anchor_curves(), _check_window_recompute()]
    codes = 0
    for ok, msg in results:
        print(msg)
        if not ok:
            codes += 1
    if codes:
        print(f"CHECK FAIL: {codes}/3 项未过门禁")
        return 1
    print("CHECK OK: 三重对照全过门禁（eps_source 分段与守卫参数见台账 "
          f"docs/_working/reports/，build_batch={BUILD_BATCH}）")
    return 0


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=f"C4 历史修复双轨重建（{_TBL_REPAIRED}）")
    p.add_argument("--start", default=None, help=f"A 段快照区间起（默认 {SEGMENT_A_START}）")
    p.add_argument("--end", default=None, help=f"A 段快照区间止（默认 {SEGMENT_A_END}）")
    p.add_argument("--window", type=int, default=WINDOW_DAYS, help=f"窗宽自然日（默认 {WINDOW_DAYS}，与 DS-229 同口径）")
    p.add_argument("--symbols", default=None, help="逗号分隔标的子集（调试/锚点复算用）")
    p.add_argument("--batch-size", type=int, default=100000)
    p.add_argument("--skip-segment-b", action="store_true", help="只重建 A 段（PDF 证据链）")
    p.add_argument("--stats", action="store_true", help="只出守卫/证据计数，不写库")
    p.add_argument("--check", action="store_true", help="三重对照验收（方案 §6 预注册判据）")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    try:
        if args.check:
            sys.exit(run_check())
        if args.stats:
            sys.exit(run_stats())
        sys.exit(run_build(args))
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 — 致命错误落盘（无头运行 stdout 可能不可见）
        err_file = ROOT / ".runtime" / "tmp" / "build_consensus_daily_repaired_error.txt"
        err_file.parent.mkdir(parents=True, exist_ok=True)
        err_file.write_text(traceback.format_exc(), encoding="utf-8")
        log.error("未处理异常，详情见 %s", err_file)
        sys.exit(1)


if __name__ == "__main__":
    main()
