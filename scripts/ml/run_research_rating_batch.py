#!/usr/bin/env python
# [BLUEPRINT] MOD-NLP-PIPELINE | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md | §Phase 7
# [MODULE] scripts.ml.run_research_rating_batch
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.nlp.research_rating; zephyr.data.ch_reader（运行态，lazy）
# [CONSUMERS] (CLI 批量脚本，无模块消费者；产物供回测/机构行为分析消费)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 断点续作（news_id 去重）；按年分块查询防大结果集爆内存；零 GPU 纯规则；产物含日级评级指标（评级分布/变动计数/目标价统计）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ClickHouse 不可达→exit 1；单行解析失败跳过不阻断
# [TESTS] tests/scripts/test_ml_run_research_rating_batch.py
# [TTL] permanent
"""run_research_rating_batch.py — CAND-NLP-006：研报结构化评级批量提取 + 日级指标。

news_data(category=research_report) → research_rating.analyze_report 逐行提取
→ research_rating.jsonl（逐篇）+ daily_research_rating.jsonl（日级评级指标：
评级分布/首次覆盖与上调下调计数/目标价统计）。零 GPU 纯规则。

产物（--out-dir 下）:
  - research_rating.jsonl        逐篇（news_id/date/org/industry/rating/score/revision/target_price）
  - daily_research_rating.jsonl  日级指标（n_reports/mean_score/n_initiation/n_upgrade/n_downgrade/rating_dist/target_price 统计）

用法:
    python scripts/ml/run_research_rating_batch.py                # 全量（按年分块）
    python scripts/ml/run_research_rating_batch.py --limit 5000   # 试跑

依据: CAND-NLP-006（candidate_module_registry.yaml）
"""

from __future__ import annotations

import argparse
import collections
import json
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from zephyr.nlp.research_rating import analyze_report  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

DEFAULT_OUT_DIR = ROOT / "data" / "research_rating"
RATING_FILENAME = "research_rating.jsonl"
DAILY_FILENAME = "daily_research_rating.jsonl"

_QUERY_COLS = "news_id, publish_time, title, summary, source"
_YEAR_START = 2010
_YEAR_END = 2026


def iter_year_reports(year: int) -> list[dict]:
    """按年分块查询研报行（防大结果集爆内存）。"""
    from zephyr.data import ch_reader  # noqa: PLC0415 — lazy：运行态才触达 CH
    from zephyr.regime.features.regime_data_loader import parse_tsv  # noqa: PLC0415

    tsv = ch_reader.query(
        f"SELECT {_QUERY_COLS} FROM c3_fundamental.news_data "
        f"WHERE category = 'research_report' AND region = 'CN' AND language = 'zh' "
        f"AND publish_time >= toDateTime('{year}-01-01 00:00:00') "
        f"AND publish_time <= toDateTime('{year}-12-31 23:59:59') ORDER BY publish_time"
    )
    if not tsv or not tsv.strip():
        return []
    rows = parse_tsv(tsv, ncols=5)
    return [
        {"news_id": r[0], "publish_time": r[1], "title": r[2], "summary": r[3], "source": r[4]} for r in rows if r[2]
    ]


def load_done_ids(path: Path) -> set[str]:
    """断点续作：已提取的 news_id 集合。"""
    if not path.exists():
        return set()
    done: set[str] = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                done.add(json.loads(line)["news_id"])
            except (json.JSONDecodeError, KeyError):
                continue
    return done


def extract_rows(reports: list[dict]) -> list[dict]:
    """逐篇结构化提取（analyze_report 组合）。"""
    out: list[dict] = []
    for rep in reports:
        try:
            r = analyze_report(rep["title"], rep["summary"])
        except Exception:  # noqa: BLE001 — 单行失败跳过不阻断
            continue
        out.append(
            {
                "news_id": str(rep["news_id"]),
                "publish_date": str(rep["publish_time"])[:10],
                "org": r.org,
                "industry": r.industry,
                "rating": r.rating,
                "score": r.score,
                "revision": r.revision,
                "target_price": r.target_price,
                "title": rep["title"],
            }
        )
    return out


def aggregate_daily(rows: list[dict]) -> list[dict]:
    """日级评级指标：评级分布/变动计数/立场均分/目标价统计。"""
    by_day: dict[str, list[dict]] = {}
    for r in rows:
        by_day.setdefault(r["publish_date"], []).append(r)
    daily: list[dict] = []
    for day in sorted(by_day):
        g = by_day[day]
        scores = [r["score"] for r in g if r["score"] is not None]
        tps = [r["target_price"] for r in g if r["target_price"] is not None]
        dist = collections.Counter(r["rating"] for r in g if r["rating"])
        rev = collections.Counter(r["revision"] for r in g)
        daily.append(
            {
                "day": day,
                "n_reports": len(g),
                "mean_score": (sum(scores) / len(scores)) if scores else None,
                "rating_dist": dict(dist.most_common()),
                "n_initiation": rev.get("initiation", 0),
                "n_upgrade": rev.get("upgrade", 0),
                "n_downgrade": rev.get("downgrade", 0),
                "n_maintain": rev.get("maintain", 0),
                "n_with_target_price": len(tps),
                "mean_target_price": (sum(tps) / len(tps)) if tps else None,
            }
        )
    return daily


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="研报结构化评级批量提取（CAND-NLP-006）")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--limit", type=int, default=0, help="限制提取行数（0=全部）")
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rating_path = args.out_dir / RATING_FILENAME

    done = load_done_ids(rating_path) if args.resume else set()
    if done:
        log.info("断点续作：跳过已提取 %d 条", len(done))

    seen = set(done)  # 全局去重：news_data 保留多版本行（同 news_id ≈3.5x 冗余，2026-08-26 实证）
    t0 = time.time()
    total_new = 0
    stopped = False
    with open(rating_path, "a" if args.resume else "w", encoding="utf-8") as f:
        for year in range(_YEAR_START, _YEAR_END + 1):
            if stopped:
                break
            try:
                reports = iter_year_reports(year)
            except Exception as exc:  # noqa: BLE001 — CH 不可达 fail-closed
                log.error("ClickHouse 查询失败（%d 年）: %s", year, exc)
                sys.exit(1)
            if not reports:
                continue
            todo = [r for r in reports if str(r["news_id"]) not in seen]
            if not todo:
                continue
            log.info("%d 年：%d 行待提取（跳过 %d）", year, len(todo), len(reports) - len(todo))
            rows = extract_rows(todo)
            for r in rows:
                if r["news_id"] in seen:
                    continue
                seen.add(r["news_id"])
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                total_new += 1
                if args.limit > 0 and total_new >= args.limit:
                    stopped = True
                    break
            f.flush()

    # 日级聚合（从产物全量聚合，news_id 去重取首条防版本冗余）
    all_rows: list[dict] = []
    seen_agg: set[str] = set()
    if rating_path.exists():
        with open(rating_path, encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                nid = str(obj.get("news_id", ""))
                if nid in seen_agg:
                    continue
                seen_agg.add(nid)
                all_rows.append(obj)
    daily = aggregate_daily(all_rows)
    daily_path = args.out_dir / DAILY_FILENAME
    with open(daily_path, "w", encoding="utf-8") as f:
        for d in daily:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    log.info(
        "完成：新提取 %d 行（总 %d 行）→ %s；日级指标 %d 天 → %s（耗时 %.0f 秒）",
        total_new,
        len(all_rows),
        rating_path,
        len(daily),
        daily_path,
        time.time() - t0,
    )


if __name__ == "__main__":
    main()
