#!/usr/bin/env python
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §4
# [MODULE] scripts.ch.backfill_research_report_2025
# [DOMAIN] D_DATA
# [DEPENDENCIES] akshare(lazy); zephyr.data.ch_writer; zephyr.data.news_dedup; zephyr.data.provider_base
# [CONSUMERS] (一次性补采 CLI，无模块消费者；产物=c3_fundamental.news_data 2025 年研报行)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 断点续作（进度文件记已完成 symbol，重启跳过）；单股失败跳过不阻断；限速 sleep 可配默认 0.4s；category 显式写 research_report（CAND-DAT-024 四分治理）；news_id=MD5(source+title+publish_time) 天然幂等，重复跑不产生重复行
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] akshare 导入失败/标的列表为空→exit 1；单股失败 continue；ClickHouse 写入失败→exit 2
# [TESTS] tests/scripts/test_ch_backfill_research_report_2025.py
# [TTL] permanent
"""backfill_research_report_2025.py — CAND-DAT-023：2025 年东财研报专项补采器。

背景：2025 年新闻语料塌陷（全年仅 3.7 万条，采集缺口）。实测东财研报接口
``ak.stock_research_report_em(symbol)`` 可回溯 2025 全年（茅台 771 条至 2017-08）。
本脚本全 A 逐只拉取、过滤 2025 年报告、按 news_data 标准行写入
（``category='research_report'``，配合 CAND-DAT-024 公告/研报/宏观数据/新闻四分治理）。

用法:
    python scripts/ch/backfill_research_report_2025.py                # 全量（~5000 只，约 1-2 小时）
    python scripts/ch/backfill_research_report_2025.py --limit 20     # 试跑 20 只
    python scripts/ch/backfill_research_report_2025.py --no-resume    # 不清进度从头跑

依据: CAND-DAT-023（candidate_module_registry.yaml v1.1.3）
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from zephyr.data import ch_writer  # noqa: E402
from zephyr.data.news_dedup import NEWS_DATA_COLUMNS, build_news_row  # noqa: E402
from zephyr.data.provider_base import FetchResult  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

_TBL_NEWS = "c3_fundamental.news_data"
# 写入列 = 标准 10 列 + category（CAND-DAT-024：研报显式打标，不动 build_news_row 契约）
_WRITE_COLUMNS: list[str] = NEWS_DATA_COLUMNS + ["category"]
_CATEGORY = "research_report"

_YEAR_START = "2025-01-01"
_YEAR_END = "2025-12-31"

PROGRESS_FILE = ROOT / ".runtime" / "backfill_rr2025_done.txt"


def progress_file_for(year_start: str, year_end: str) -> Path:
    """断点文件按区间分名（2025 单年保持原名复用已完成进度）。"""
    if (year_start, year_end) == (_YEAR_START, _YEAR_END):
        return PROGRESS_FILE
    return ROOT / ".runtime" / f"backfill_rr_{year_start[:4]}_{year_end[:4]}_done.txt"


def get_all_a_symbols() -> list[str]:
    """全 A 股 6 位代码列表（优先 CH c1_market.stock_list 本地源，兜底 akshare 现货快照）。"""
    codes = _symbols_from_ch()
    if not codes:
        codes = _symbols_from_akshare()
    log.info("全 A 标的 %d 只", len(codes))
    return codes


def _symbols_from_ch() -> list[str]:
    """c1_market.stock_list 取上市 A 股（本地源优先——东财快照接口有反爬断连风险，2026-08-26 实证）。"""
    from zephyr.data import ch_reader  # noqa: PLC0415 — lazy

    tsv = ch_reader.query(
        "SELECT DISTINCT symbol FROM c1_market.stock_list WHERE market = 'A股' AND list_status = '上市'"
    )
    if not tsv or not tsv.strip():
        log.warning("CH stock_list 为空或不可达，回退 akshare 快照")
        return []
    codes = sorted({line.strip() for line in tsv.strip().split("\n") if line.strip().isdigit()})
    log.info("标的来源: CH c1_market.stock_list（%d 只）", len(codes))
    return codes


def _symbols_from_akshare() -> list[str]:
    """akshare 现货快照兜底。"""
    import akshare as ak  # noqa: PLC0415 — lazy：仅本函数触达

    spot = ak.stock_zh_a_spot_em()
    codes = sorted({str(raw)[-6:] for raw in spot["代码"] if str(raw)[-6:].isdigit()})
    log.info("标的来源: akshare stock_zh_a_spot_em（%d 只）", len(codes))
    return codes


def load_done_symbols(progress_file: Path | None = None) -> set[str]:
    """断点续作：已完成 symbol 集合。"""
    pf = progress_file or PROGRESS_FILE
    if not pf.exists():
        return set()
    return {line.strip() for line in pf.read_text(encoding="utf-8").splitlines() if line.strip()}


def load_existing_news_ids(year_start: str = _YEAR_START, year_end: str = _YEAR_END) -> set[str]:
    """库内指定区间研报已有 news_id 集合（写入侧预检——news_data 保留多版本行，
    不预检会把已有报告再插一份（2026-08-26 实证 2025 年 2.10x 冗余）。

    CAND-DAT-025：实现沉淀为 news_dedup.existing_news_ids 公共助手。"""
    from zephyr.data.news_dedup import existing_news_ids  # noqa: PLC0415 — lazy：运行态才触达 CH

    ids = existing_news_ids(
        "source = 'akshare_research_report' "
        f"AND publish_time >= toDateTime('{year_start} 00:00:00') "
        f"AND publish_time <= toDateTime('{year_end} 23:59:59')"
    )
    log.info("库内已有 %s~%s 研报 id %d 个（写入预检跳过）", year_start[:4], year_end[:4], len(ids))
    return ids


def fetch_2025_rows(
    code: str,
    df,
    existing_ids: frozenset[str] | set[str] = frozenset(),
    year_start: str = _YEAR_START,
    year_end: str = _YEAR_END,
) -> list[tuple]:
    """从单只股票的研报 DataFrame 过滤年份区间并构造写入行（11 元组含 category）。

    existing_ids：库内已有 news_id 预检集——命中直接跳过（写侧防多版本冗余）。
    """
    rows: list[tuple] = []
    for _, r in df.iterrows():
        title = str(r.get("报告名称") or "")
        if not title:
            continue
        pub = str(r.get("日期") or "")[:10]
        if not (year_start <= pub <= year_end):
            continue
        org = str(r.get("机构") or "").strip()
        rating = str(r.get("东财评级") or "").strip()
        industry = str(r.get("行业") or "").strip()
        parts = [f"机构:{org}"] if org else []
        if rating:
            parts.append(f"评级:{rating}")
        if industry:
            parts.append(f"行业:{industry}")
        base = build_news_row(
            pub,
            title,
            str(r.get("报告PDF链接") or ""),
            " | ".join(parts),
            "akshare_research_report",
            "akshare",
        )
        if base[0] in existing_ids:  # news_id 是元组首列
            continue
        rows.append(tuple(base) + (_CATEGORY,))
    return rows


def flush(rows: list[tuple]) -> None:
    """批量写入 ClickHouse（write_result；失败抛异常由调用方exit 2）。"""
    if not rows:
        return
    result = FetchResult(
        table=_TBL_NEWS,
        columns=_WRITE_COLUMNS,
        rows=rows,
        last_key=_YEAR_END,
        elapsed_sec=0.0,
    )
    ok = ch_writer.write_result(result)
    if not ok:
        raise RuntimeError(f"ClickHouse 写入失败（{len(rows)} 行）")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="东财研报专项补采（CAND-DAT-023；年份区间可配，默认 2025）")
    parser.add_argument("--limit", type=int, default=0, help="只跑前 N 只（0=全部）")
    parser.add_argument("--sleep", type=float, default=0.4, help="每股间隔秒数（反爬限速）")
    parser.add_argument("--batch-size", type=int, default=200, help="多少只 flush 一次")
    parser.add_argument("--year-from", default=_YEAR_START, help="区间起（YYYY-MM-DD，默认 2025-01-01）")
    parser.add_argument("--year-to", default=_YEAR_END, help="区间止（YYYY-MM-DD，默认 2025-12-31）")
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    year_start, year_end = args.year_from, args.year_to
    progress_file = progress_file_for(year_start, year_end)
    try:
        symbols = get_all_a_symbols()
    except Exception as exc:  # noqa: BLE001 — akshare 不可达 fail-closed
        log.error("标的列表获取失败（akshare 不可达？）: %s", exc)
        sys.exit(1)
    if args.limit > 0:
        symbols = symbols[: args.limit]

    done = load_done_symbols(progress_file) if args.resume else set()
    todo = [s for s in symbols if s not in done]
    log.info("待采 %d 只（跳过已完成 %d 只；区间 %s~%s）", len(todo), len(symbols) - len(todo), year_start, year_end)
    if not todo:
        log.info("无待采标的，退出")
        return

    try:
        existing_ids = load_existing_news_ids(year_start, year_end)
    except Exception as exc:  # noqa: BLE001 — 预检失败 fail-closed（防冗余写入）
        log.error("库内已有 id 预检失败: %s", exc)
        sys.exit(1)

    import akshare as ak  # noqa: PLC0415 — lazy：标的后触达

    progress_file.parent.mkdir(parents=True, exist_ok=True)
    total_rows = 0
    batch: list[tuple] = []
    t0 = time.time()
    with open(progress_file, "a", encoding="utf-8") as pf:
        for idx, code in enumerate(todo, 1):
            try:
                df = ak.stock_research_report_em(symbol=code)
            except Exception as exc:  # noqa: BLE001 — 单股失败不阻断
                log.debug("stock_research_report_em(%s) 失败: %s", code, exc)
                df = None
            if df is not None and len(df) > 0:
                batch.extend(fetch_2025_rows(code, df, existing_ids, year_start, year_end))
            pf.write(code + "\n")
            pf.flush()
            if idx % args.batch_size == 0 or idx == len(todo):
                try:
                    flush(batch)
                except RuntimeError as exc:
                    log.error("%s", exc)
                    sys.exit(2)
                total_rows += len(batch)
                rate = idx / (time.time() - t0)
                log.info(
                    "进度 %d/%d 只（%.1f 只/秒），本批写入 %d 行，累计 %d 行",
                    idx,
                    len(todo),
                    rate,
                    len(batch),
                    total_rows,
                )
                batch = []
            time.sleep(args.sleep)
    log.info("完成：%d 只 → %d 行（耗时 %.0f 秒）", len(todo), total_rows, time.time() - t0)


if __name__ == "__main__":
    main()
