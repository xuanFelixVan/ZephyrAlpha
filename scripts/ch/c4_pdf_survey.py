#!/usr/bin/env python
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.ch.c4_pdf_survey
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; urllib(标准库)
# [CONSUMERS] C4 历史修复工程第一步（存活率普查，Owner 立项 2026-09-14）；后续批次决策点
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 抽样=按年分层随机（seed 固定可复测同批）；结局三分类=real_pdf（HTTP200+%PDF魔数+
#              体积>=10KB）/bot_page（HTTP200 但反爬 JS 页）/http_err（含超时）；并发=8 线程+
#              30s 超时（对免费公开渠道克制使用）；URL 形态=http://pdf.dfcfw.com/pdf/H3_{info}_1.pdf
#              （https 端点返回反爬质询页——2026-09-14 实测）；本脚本只测存活不留存内容（版权边界）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] research_report 不可达->exit 1
# [TESTS] 一次性普查 CLI（结果表即验收物）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: C4 历史修复侦察 CLI（A 类一次性运维）
"""c4_pdf_survey.py — C4 历史修复第一步：PDF 存活率普查（Owner 立项 2026-09-14）。

按年分层随机抽样（默认每年 100 份），并发实测东财 PDF 直链存活率。
结局三分类：real_pdf=可下载真 PDF；bot_page=命中反爬质询页；http_err=网络层失败。
产出按年存活率表（JSON+控制台），作为 C4 全量批的盘子决策依据。

用法::

    python scripts/ch/c4_pdf_survey.py --per-year 100 --out survey.json
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

_URL_TMPL = "http://pdf.dfcfw.com/pdf/H3_{rid}_1.pdf"
_UA = "Mozilla/5.0"
_MIN_PDF_BYTES = 10_000


def sample_reports(per_year: int, seed: int) -> list[dict]:
    """按年分层随机抽样（seed 固定 → 复测同批可复现）。"""
    from zephyr.data import ch_reader

    years = ch_reader.query(
        "SELECT toYYYYMM(publish_date) ym, count() FROM c3_fundamental.research_report FINAL "
        "GROUP BY ym ORDER BY ym FORMAT TSV").strip().split("\n")
    by_year: dict[str, int] = {}
    for ln in years:
        if ln and "\t" in ln:
            ym, n = ln.split("\t")
            by_year[ym[:4]] = by_year.get(ym[:4], 0) + int(n)
    rng = random.Random(seed)
    samples: list[dict] = []
    for year in sorted(by_year):
        n_total = by_year[year]
        n_take = min(per_year, n_total)
        sql = (f"SELECT publish_date, report_id FROM c3_fundamental.research_report FINAL "
               f"WHERE toYear(publish_date) = {year} FORMAT TSV")
        # 大年份直接 SQL 端随机取（CH rand() 不可种子化 → 客户端种子抽样保证可复测）
        if n_total <= 200_000:
            rows = [r for r in ch_reader.query(sql).strip().split("\n")
                    if r and "\t" in r and not r.startswith("publish_date")]
            n_take = min(n_take, len(rows))
            if n_take == 0:
                print(f"  警告: {year} 年 SQL 端返回空（count={n_total}），跳过", flush=True)
                continue
            picked = rng.sample(rows, n_take)
            for r in picked:
                d, rid = r.split("\t")
                samples.append({"year": year, "publish_date": d[:10], "report_id": rid})
        else:
            # 超大年分月抽样再合并
            for m in range(1, 13):
                ym = f"{year}{m:02d}"
                msql = (f"SELECT publish_date, report_id FROM c3_fundamental.research_report FINAL "
                        f"WHERE toYYYYMM(publish_date) = {ym} FORMAT TSV")
                mrows = [r for r in ch_reader.query(msql).strip().split("\n") if r and "\t" in r]
                if not mrows:
                    continue
                take = max(1, round(n_take * len(mrows) / n_total))
                for r in rng.sample(mrows, min(take, len(mrows))):
                    d, rid = r.split("\t")
                    samples.append({"year": year, "publish_date": d[:10], "report_id": rid})
    return samples


def probe_one(item: dict, timeout: int = 30) -> dict:
    """单份探测：返回结局分类。"""
    url = _URL_TMPL.format(rid=item["report_id"])
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            head = resp.read(_MIN_PDF_BYTES + 1)
        size_head = len(head)
        if head[:4] == b"%PDF" and size_head >= _MIN_PDF_BYTES:
            outcome = "real_pdf"
        elif head[:4] == b"%PDF":
            outcome = "tiny_pdf"
        else:
            outcome = "bot_page"
        return {**item, "outcome": outcome, "bytes": size_head, "sec": round(time.time() - t0, 1)}
    except Exception as exc:  # noqa: BLE001 — 普查统计一切失败形态
        return {**item, "outcome": "http_err", "bytes": 0,
                "sec": round(time.time() - t0, 1), "err": repr(exc)[:80]}


def main() -> None:
    ap = argparse.ArgumentParser(description="C4 PDF 存活率普查（按年分层随机抽样）")
    ap.add_argument("--per-year", type=int, default=100, help="每年抽样数（默认 100）")
    ap.add_argument("--seed", type=int, default=20260914, help="抽样种子（复测同批）")
    ap.add_argument("--workers", type=int, default=8, help="并发线程数")
    ap.add_argument("--out", default=None, help="结果 JSON 路径")
    args = ap.parse_args()

    samples = sample_reports(args.per_year, args.seed)
    print(f"抽样 {len(samples)} 份（每年<= {args.per_year}），开始并发探测…", flush=True)
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(probe_one, it) for it in samples]
        for i, fut in enumerate(as_completed(futs), 1):
            results.append(fut.result())
            if i % 100 == 0:
                print(f"  进度 {i}/{len(samples)}", flush=True)

    by_year: dict[str, Counter] = {}
    for r in results:
        by_year.setdefault(r["year"], Counter())[r["outcome"]] += 1
    print("\n年份    样本  real_pdf  bot_page  http_err  tiny_pdf  存活率")
    summary = {}
    for year in sorted(by_year):
        c = by_year[year]
        total = sum(c.values())
        alive = c.get("real_pdf", 0)
        rate = alive / total * 100 if total else 0.0
        print(f"{year}  {total:>5}  {alive:>7}  {c.get('bot_page',0):>8}  "
              f"{c.get('http_err',0):>8}  {c.get('tiny_pdf',0):>8}  {rate:5.1f}%")
        summary[year] = {"total": total, "real_pdf": alive,
                         "bot_page": c.get("bot_page", 0),
                         "http_err": c.get("http_err", 0),
                         "tiny_pdf": c.get("tiny_pdf", 0),
                         "alive_rate": round(rate, 1)}
    total_alive = sum(v["real_pdf"] for v in summary.values())
    total_n = sum(v["total"] for v in summary.values())
    print(f"\n合计存活率: {total_alive}/{total_n} = {total_alive/total_n*100:.1f}%")
    if args.out:
        Path(args.out).write_text(json.dumps(
            {"seed": args.seed, "per_year": args.per_year, "summary": summary,
             "detail": results}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"WROTE {args.out}")


if __name__ == "__main__":
    main()
