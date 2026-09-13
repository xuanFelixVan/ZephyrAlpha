#!/usr/bin/env python
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §4
# [MODULE] scripts.ch.build_financial_derived
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.ch_writer; zephyr.data.implementations.financial_derived_compute
# [CONSUMERS] (回补/重建/验收 CLI；夜间调度=internal provider financial_derived capability，tasks.yaml financial_derived_build)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 纯函数核委托 financial_derived_compute.build_symbol_rows（PIT 语义见该模块 INVARIANTS）；
#              写入后必须 SELECT 计数复核（ch_writer 对 INSERT 返回空串≠失败）；
#              ReplacingMergeTree(ingest_ts) 同键重建幂等
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 三表不可达->exit 1；ClickHouse 写入失败->exit 2；--check 交叉验证不一致->exit 1
# [TESTS] tests/zephyr/data/test_financial_derived_compute.py（纯函数核）+ 本脚本 --check（实库交叉验证）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 历史回补/重建/验收 CLI（A 类一次性运维+手动验收；
#                                   常态夜间派生走 internal provider（tasks.yaml financial_derived_build），不经本 CLI
"""build_financial_derived.py — 财报派生层构建器（消费端 F1-M1，DS-230）。

把 c3_fundamental 三大报表对齐派生为 c3_fundamental.financial_derived
（跨表对齐+单季拆分+TTM+应计/GPOA 等比率，statement 粒度）。
设计真源：docs/_working/2026-09-12-fundamental-consumption-design.md §M1。

用法::

    python scripts/ch/build_financial_derived.py --full             # 历史全量回补（幂等）
    python scripts/ch/build_financial_derived.py --start 2026-08-01 # 按衍生公告日窗口重建
    python scripts/ch/build_financial_derived.py --symbols 600519,000001  # 子集调试
    python scripts/ch/build_financial_derived.py --check            # 实库 PIT 交叉验证
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))  # schemas.categories.* 在项目根

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def run_build(args: argparse.Namespace) -> int:
    from zephyr.data import ch_reader
    from zephyr.data.buffered_writer import BufferedWriter
    from zephyr.data.implementations.financial_derived_compute import run_compute

    from schemas.categories.fundamental.financial_derived import TABLE_NAME

    symbols = [s.strip() for s in args.symbols.split(",")] if args.symbols else None
    t0 = time.time()
    writer = BufferedWriter(f"c3_fundamental.{TABLE_NAME}")
    try:
        for result in run_compute(symbols=symbols, start=args.start, end=args.end):
            if not writer.add(result):
                raise RuntimeError(f"BufferedWriter 写入失败（批 {len(result.rows)} 行）")
        if not writer.flush():
            raise RuntimeError("BufferedWriter 末批 flush 失败")
        n_written = writer.total_flushed
    except RuntimeError as exc:
        log.error("%s", exc)
        return 2

    # ch_writer 对 INSERT 返回空串≠失败——写入后必须事后 SELECT 计数复核
    where = f" WHERE symbol IN ({','.join(chr(39) + s + chr(39) for s in symbols)})" if symbols else ""
    tsv = ch_reader.query(f"SELECT count() FROM c3_fundamental.{TABLE_NAME}{where}")
    n_table = int(tsv.strip()) if tsv and tsv.strip() else 0
    log.info("表内计数复核：%d 行（本批写入 %d，耗时 %.1f 秒）", n_table, n_written, time.time() - t0)
    if n_table < n_written:
        log.error("表内计数 < 写入计数——写入链路异常，人工核查")
        return 2
    return 0


def _prev_quarter_end(rp: str) -> str:
    """报告期 → 上季季末（06-30→03-31；跨年 03-31→上年 12-31 类推）。"""
    y, m = int(rp[:4]), int(rp[5:7])
    m2 = m - 3
    if m2 <= 0:
        m2 += 12
        y -= 1
    qday = {3: "31", 6: "30", 9: "30", 12: "31"}.get(m2, "30")
    return f"{y:04d}-{m2:02d}-{qday}"


def run_check() -> int:
    """实库 PIT 交叉验证：茅台最新派生行的单季营收 vs SQL 现算（H1累计−Q1累计，as-of 衍生公告日）。"""
    from zephyr.data import ch_reader

    from schemas.categories.fundamental.financial_derived import TABLE_NAME

    tsv = ch_reader.query(
        f"SELECT max(report_period), uniqExact(symbol), count() FROM c3_fundamental.{TABLE_NAME} FINAL"
    )
    if not tsv or not tsv.strip():
        log.error("CHECK FAIL: financial_derived 无数据")
        return 1
    latest, n_sym, n_rows = tsv.strip().split("\t")
    log.info("表内实况：rows=%s symbols=%s 最新报告期=%s", n_rows, n_sym, latest)

    # 校验标的取自身最新报告期（全市场公告进度不一，全局 max 期未必含校验标的）
    t2 = ch_reader.query(
        f"SELECT report_period, announce_date, rev_q, rev_ttm, accrual_ttm, debt_ratio "
        f"FROM c3_fundamental.{TABLE_NAME} FINAL "
        f"WHERE symbol = '600519' ORDER BY report_period DESC, announce_date DESC LIMIT 1 FORMAT TSV"
    )
    if not t2 or not t2.strip():
        log.error("CHECK FAIL: 600519 无派生行")
        return 1
    rp, ann, rev_q, rev_ttm, accrual, debt = t2.strip().split("\t")[:6]
    log.info("校验标的 600519 最新行：%s ann=%s rev_q=%s rev_ttm=%s accrual=%s debt=%s",
             rp, ann, rev_q, rev_ttm, accrual, debt)

    # SQL 现算：单季营收 = Q1→累计本身；Q2+→本期累计−上季累计（各取 ann 时点可见最新版本）。
    # 两次独立查询+Python 相减（子查询相减经 ch_reader 偶发返回 'None'，拆开稳定）。
    def _cum_rev(period: str) -> float | None:
        q = ("SELECT operating_revenue FROM c3_fundamental.income_statement FINAL "
             " WHERE symbol='600519' AND report_period = toDate('" + period + "') "
             " AND announce_date <= toDate('" + ann + "') AND announce_date > toDate('1970-01-02') "
             " ORDER BY announce_date DESC LIMIT 1 FORMAT TSV")
        v = (ch_reader.query(q) or "").strip()
        if not v or v == "\\N" or v == "None":
            return None
        try:
            return float(v)
        except ValueError:
            return None

    cur_val = _cum_rev(rp)
    base_val = cur_val if rp[5:7] == "03" else _cum_rev(_prev_quarter_end(rp))
    if cur_val is None or (rp[5:7] != "03" and base_val is None):
        log.error("CHECK FAIL: SQL 现算不可得（cur=%r base=%r）", cur_val, base_val)
        return 1
    sql_val = cur_val if rp[5:7] == "03" else cur_val - base_val
    if abs(float(rev_q) - sql_val) > max(1.0, abs(sql_val) * 1e-6):
        log.error("MISMATCH: 表内 rev_q=%s vs SQL 现算=%.4f", rev_q, sql_val)
        return 1
    log.info("PIT 交叉验证 OK: 600519 %s rev_q 表内=%.2f SQL=%.2f", rp, float(rev_q), sql_val)
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="财报派生层构建（c3_fundamental.financial_derived，DS-230）")
    parser.add_argument("--full", action="store_true", help="历史全量回补（幂等重建；默认行为）")
    parser.add_argument("--start", default=None, help="衍生公告日窗口起（含，iso）")
    parser.add_argument("--end", default=None, help="衍生公告日窗口止（含，iso）")
    parser.add_argument("--symbols", default=None, help="逗号分隔标的子集（调试用）")
    parser.add_argument("--check", action="store_true", help="验收模式：行数+单季 PIT 交叉验证")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    try:
        sys.exit(run_check() if args.check else run_build(args))
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 — 致命错误落盘（无头运行 stdout 可能不可见）
        err_file = ROOT / ".runtime" / "tmp" / "build_financial_derived_error.txt"
        err_file.parent.mkdir(parents=True, exist_ok=True)
        err_file.write_text(traceback.format_exc(), encoding="utf-8")
        log.error("未处理异常，详情见 %s", err_file)
        sys.exit(1)


if __name__ == "__main__":
    main()
