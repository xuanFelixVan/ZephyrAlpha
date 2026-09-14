# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.ch.c4_extract_batch
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.c4_history_repair; zephyr.data.ch_reader
# [CONSUMERS] C4 历史修复②原型批/③全量批（Owner 立项 2026-09-14）；批次报告产出
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 断点=缓存目录+提取表既有 report_id（重跑自动跳过已完成）；
#              批次统计四指标=下载结局分布/表命中/LLM 兜底/空手率；
#              --hs300 限定沪深300 成分（index_constituent 历史成员并集）；
#              验收门禁=锚点集准确率>=90% 方可进全量（方案 §6）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] research_report 不可达->exit 1；单份失败不阻断（计入统计）
# [TESTS] 原型批报告即验收物
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: C4 历史修复批处理 CLI（A 类批次运维）
"""c4_extract_batch.py — C4 历史修复批处理（下载→三层提取→落表→批次报告）。

用法::

    python scripts/ch/c4_extract_batch.py --hs300 --limit 300          # 原型批
    python scripts/ch/c4_extract_batch.py --years 2017,2018,2019,2020,2021  # 全量批
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from zephyr.data.c4_history_repair import extract_report  # noqa: E402


def hs300_symbols() -> set[str]:
    """沪深300 历史成员并集（2017-2021 任一时段在册）。"""
    from zephyr.data import ch_reader

    out = ch_reader.query(
        "SELECT DISTINCT symbol FROM c1_market.index_constituent FINAL "
        "WHERE index_code = '000300.SH' "
        "AND valid_from <= toDate('2021-12-31') AND valid_to >= toDate('2017-01-01') FORMAT TSV")
    # 成分表 symbol=600519.SH 形态；research_report.symbol=裸码 → 剥后缀对齐
    return {ln.strip().split(".")[0] for ln in out.strip().split("\n") if ln.strip()}


def done_report_ids() -> set[str]:
    """已提取过的 report_id（断点续传）。"""
    from zephyr.data import ch_reader

    out = ch_reader.query(
        "SELECT DISTINCT report_id FROM c3_fundamental.pdf_forecast_extracted FINAL FORMAT TSV")
    return {ln.strip() for ln in out.strip().split("\n") if ln.strip()}


def main() -> None:
    ap = argparse.ArgumentParser(description="C4 历史修复批处理（下载→提取→落表）")
    ap.add_argument("--hs300", action="store_true", help="限定沪深300 历史成员")
    ap.add_argument("--years", default="2017,2018,2019,2020,2021", help="年份逗号分隔")
    ap.add_argument("--limit", type=int, default=0, help="最多处理份数（0=不限）")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default=None, help="批次报告 JSON 路径")
    args = ap.parse_args()

    from zephyr.data import ch_reader

    years = [y.strip() for y in args.years.split(",")]
    year_list = ",".join(y for y in years)
    symbols_clause = ""
    if args.hs300:
        syms = hs300_symbols()
        print(f"沪深300 历史成员并集: {len(syms)} 只", flush=True)
        # symbol 列带交易所后缀形态与 research_report 对齐（600519 → 600519.SH）
        sym_list = ",".join(f"'{s}'" for s in sorted(syms))
        symbols_clause = f" AND symbol IN ({sym_list})"
    sql = ("SELECT report_id, symbol, publish_date FROM c3_fundamental.research_report FINAL "
           f"WHERE toYear(publish_date) IN ({year_list}){symbols_clause} "
           "ORDER BY publish_date, symbol FORMAT TSV")
    rows = [ln.split("\t") for ln in ch_reader.query(sql).strip().split("\n") if ln and "\t" in ln]
    rows = [r for r in rows if len(r) == 3]
    done = done_report_ids()
    rows = [r for r in rows if r[0] not in done]
    if args.limit:
        rows = rows[:args.limit]
    print(f"待处理 {len(rows)} 份（已完成跳过 {len(done)} 个 report_id）", flush=True)

    stats: Counter = Counter()
    llm_used = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(extract_report, rid, sym, d): (rid, sym, d) for rid, sym, d in rows}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                r = fut.result()
            except Exception as exc:  # noqa: BLE001
                stats["error"] += 1
                continue
            stats[r.get("outcome", "unknown")] += 1
            if r.get("rows"):
                stats["has_rows"] += 1
            else:
                stats["empty_extract"] += 1
            if i % 50 == 0:
                el = time.time() - t0
                print(f"  进度 {i}/{len(rows)} 已用 {el:.0f}s", flush=True)

    print("\n===== 批次报告 =====")
    for k, v in stats.most_common():
        print(f"  {k}: {v}")
    print(f"总耗时 {time.time()-t0:.0f}s")
    if args.out:
        Path(args.out).write_text(json.dumps(
            {"args": vars(args), "stats": dict(stats)}, ensure_ascii=False, indent=1),
            encoding="utf-8")
        print(f"WROTE {args.out}")


if __name__ == "__main__":
    main()
