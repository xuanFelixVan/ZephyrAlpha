#!/usr/bin/env python
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §4
# [MODULE] scripts.ch.backfill_research_report_full
# [DOMAIN] D_DATA
# [DEPENDENCIES] akshare(lazy); zephyr.data.ch_writer; zephyr.data.ch_reader; schemas.categories.fundamental.fundamental_research_report
# [CONSUMERS] (一次性补采 CLI + --check 验收模式；产物=c3_fundamental.research_report 全字段研报明细)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 断点续作（进度文件记已完成 symbol，重启跳过）；单股失败跳过不阻断；限速 sleep 可配默认 0.4s；report_id=PDF链接 infoCode 提取（缺失 MD5(symbol+title+date) 兜底）幂等，重复跑写侧重检+ReplacingMergeTree(ingest_ts) 双保险；EPS 动态年份列按年份升序映射 fy0/fy1/fy2 并落年份值（防年份滚动漂移）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] akshare 导入失败/标的列表为空→exit 1；单股失败 continue；ClickHouse 写入失败→exit 2；--check 无数据→exit 1
# [TESTS] 本脚本 --limit 5 试跑 + --check 模式验收
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 一次性补采 CLI（A 类断点续作补采按需手动；日度增量走 tasks.yaml research_report_detail_incremental）
"""backfill_research_report_full.py — 东财研报全字段历史回补器（写入 c3_fundamental.research_report）。

背景（docs/_working/2026-09-12-research-report-data-plan.md）：现有 research_report_incremental
把研报塞 news_data 共表且丢失盈利预测数值/个股代码。本脚本按个股全量拉取
``ak.stock_research_report_em(symbol)``（茅台实证回溯至 2017-08；接口参数 beginTime=2000-01-01），
解析全字段（含每份研报的预测期 EPS/PE）写入独立明细表——该表即 PIT 正确一致预期的原料
（按 publish_date 聚合，对标朝阳永续原理，免付费数据商）。

用法::

    python scripts/ch/backfill_research_report_full.py --limit 5      # 试跑 5 只
    python scripts/ch/backfill_research_report_full.py                # 全市场（~5000 只，约 1-2 小时）
    python scripts/ch/backfill_research_report_full.py --check        # 验收：行数/日期范围/股数（exit 0=有数据）
    python scripts/ch/backfill_research_report_full.py --no-resume    # 不读进度从头跑

改造自 backfill_research_report_2025.py（断点续作/控频/单股失败跳过骨架一致）。
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import re
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))  # schemas.categories.* 在项目根（同 apply_research_report_ddl.py）

from schemas.categories.fundamental.fundamental_research_report import (  # noqa: E402
    INSERT_COLUMNS,
    TABLE_NAME,
)
from zephyr.data import ch_writer  # noqa: E402
from zephyr.data.provider_base import FetchResult  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

_TBL = f"c3_fundamental.{TABLE_NAME}"
# FetchResult.columns 契约=list[str]（provider_base.py），ch_writer 自动列过滤按 list 消费
_COLUMNS_LIST: list[str] = [c.strip() for c in INSERT_COLUMNS.strip("()").split(",")]

_DEFAULT_FROM = "2000-01-01"
PROGRESS_FILE = ROOT / ".runtime" / "backfill_rr_full_done.txt"

_INFOCODE_RE = re.compile(r"H3_([A-Za-z0-9]+)_1\.pdf")


def progress_file_for(date_from: str, date_to: str) -> Path:
    """断点文件按区间分名（默认全量区间保持原名复用已完成进度）。"""
    if date_from == _DEFAULT_FROM:
        return PROGRESS_FILE
    return ROOT / ".runtime" / f"backfill_rr_full_{date_from[:10].replace('-', '')}_{date_to[:10].replace('-', '')}_done.txt"


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


def load_done_symbols(progress_file: Path) -> set[str]:
    """断点续作：已完成 symbol 集合。"""
    if not progress_file.exists():
        return set()
    return {line.strip() for line in progress_file.read_text(encoding="utf-8").splitlines() if line.strip()}


def load_existing_report_ids() -> set[str]:
    """库内已有 report_id 集合（写入侧预检防冗余；新表阶段表小，全量拉取）。"""
    from zephyr.data import ch_reader  # noqa: PLC0415 — lazy

    tsv = ch_reader.query(f"SELECT DISTINCT report_id FROM {_TBL}")
    ids = {line.strip() for line in (tsv or "").strip().split("\n") if line.strip()}
    log.info("库内已有 report_id %d 个（写入预检跳过）", len(ids))
    return ids


def _forecast_columns(df) -> dict[str, dict[int, float]]:
    """从动态年份列提取预测值：{"eps": {year: val}, "pe": {year: val}}。

    akshare 列名形如 "2026-盈利预测-收益" / "2026-盈利预测-市盈率"（年份随接口滚动）。
    """
    out: dict[str, dict[int, float]] = {"eps": {}, "pe": {}}
    for col in df.columns:
        col = str(col)
        m = re.match(r"^(\d{4})-盈利预测-(收益|市盈率)$", col)
        if not m:
            continue
        year = int(m.group(1))
        kind = "eps" if m.group(2) == "收益" else "pe"
        series = df[col]
        for idx, raw in series.items():
            try:
                val = float(raw)
            except (TypeError, ValueError):
                continue
            if val != val:  # NaN 防穿透（接口空预测值常见）
                continue
            if year not in out[kind]:
                out[kind][year] = val
            else:
                # 同年多列（理论上不会）：保留非空
                out[kind][year] = out[kind][year] or val
    return out


def _extract_report_id(pdf_url: str, symbol: str, title: str, pub: str) -> str:
    """report_id=PDF链接 infoCode（H3_{code}_1.pdf）；缺失时 MD5(symbol+title+date) 兜底。"""
    m = _INFOCODE_RE.search(pdf_url or "")
    if m:
        return m.group(1)
    digest = hashlib.md5(f"{symbol}|{title}|{pub}".encode("utf-8")).hexdigest()
    return f"md5_{digest}"


def parse_rows(code: str, df, existing_ids: set[str], date_from: str, date_to: str) -> list[tuple]:
    """单股 DataFrame → INSERT_COLUMNS 序的全字段行元组列表（report_id 预检去重）。"""
    rows: list[tuple] = []
    fc = _forecast_columns(df)
    eps_years = sorted(fc["eps"].keys())
    # EPS 按年份升序映射 fy0/fy1/fy2（接口只给当前/次年/后年三期）
    fy = {pos: (eps_years[pos] if pos < len(eps_years) else 0) for pos in range(3)}

    for _, r in df.iterrows():
        title = str(r.get("报告名称") or "").strip()
        pub = str(r.get("日期") or "")[:10]
        if not title or not pub:
            continue
        if not (date_from[:10] <= pub <= date_to[:10]):
            continue
        pdf_url = str(r.get("报告PDF链接") or "")
        report_id = _extract_report_id(pdf_url, code, title, pub)
        if report_id in existing_ids:
            continue
        rows.append((
            report_id,
            code,
            title,
            str(r.get("机构") or "").strip(),
            str(r.get("东财评级") or "").strip(),
            str(r.get("评级变动") or "").strip(),
            str(r.get("行业") or "").strip(),
            str(r.get("研究员") or "").strip(),
            pub,
            fy[0], fc["eps"].get(fy[0]), fc["pe"].get(fy[0]),
            fy[1], fc["eps"].get(fy[1]), fc["pe"].get(fy[1]),
            fy[2], fc["eps"].get(fy[2]), fc["pe"].get(fy[2]),
            pdf_url,
            0, "", "akshare_research_report_em",
        ))
    return rows


def flush(rows: list[tuple]) -> None:
    """批量写入 ClickHouse（write_result；失败抛异常由调用方 exit 2）。"""
    if not rows:
        return
    result = FetchResult(
        table=_TBL,
        columns=_COLUMNS_LIST,
        rows=rows,
        last_key="",
        elapsed_sec=0.0,
    )
    ok = ch_writer.write_result(result)
    if not ok:
        raise RuntimeError(f"ClickHouse 写入失败（{len(rows)} 行）")


def run_backfill(args: argparse.Namespace) -> int:
    date_from, date_to = args.date_from, args.date_to
    progress_file = progress_file_for(date_from, date_to)
    try:
        symbols = get_all_a_symbols()
    except Exception as exc:  # noqa: BLE001 — akshare 不可达 fail-closed
        log.error("标的列表获取失败（akshare 不可达？）: %s", exc)
        return 1
    if not symbols:
        log.error("标的列表为空，退出")
        return 1
    if args.limit > 0:
        symbols = symbols[: args.limit]

    done = load_done_symbols(progress_file) if args.resume else set()
    todo = [s for s in symbols if s not in done]
    log.info("待采 %d 只（跳过已完成 %d 只；区间 %s~%s）", len(todo), len(symbols) - len(todo), date_from, date_to)
    if not todo:
        log.info("无待采标的，退出")
        return 0

    try:
        existing_ids = load_existing_report_ids()
    except Exception as exc:  # noqa: BLE001 — 预检失败 fail-closed（防冗余写入）
        log.error("库内已有 report_id 预检失败: %s", exc)
        return 1

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
                batch.extend(parse_rows(code, df, existing_ids, date_from, date_to))
            pf.write(code + "\n")
            pf.flush()
            if idx % args.batch_size == 0 or idx == len(todo):
                try:
                    flush(batch)
                except RuntimeError as exc:
                    log.error("%s", exc)
                    return 2
                total_rows += len(batch)
                rate = idx / (time.time() - t0)
                log.info(
                    "进度 %d/%d 只（%.1f 只/秒），本批写入 %d 行，累计 %d 行",
                    idx, len(todo), rate, len(batch), total_rows,
                )
                batch = []
            time.sleep(args.sleep)
    log.info("完成：%d 只 → %d 行（耗时 %.0f 秒）", len(todo), total_rows, time.time() - t0)
    return 0


def run_check() -> int:
    """验收模式：行数/日期范围/覆盖股数/EPS 非空率（本会话输出不可见，靠 exit code：0=有数据 1=空表）。"""
    from zephyr.data import ch_reader  # noqa: PLC0415 — lazy

    tsv = ch_reader.query(
        f"SELECT count(), min(publish_date), max(publish_date), uniqExact(symbol), "
        f"round(countIf(eps_fy0 IS NOT NULL) / max(count(), 1) * 100, 1) FROM {_TBL} FINAL"
    )
    line = (tsv or "").strip()
    if not line or line.split("\t")[0] == "0":
        log.error("CHECK FAIL: %s 无数据", _TBL)
        return 1
    log.info("CHECK OK: rows=%s date_range=%s~%s symbols=%s eps_fy0_nonnull_pct=%s", *line.split("\t"))
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="东财研报全字段历史回补（c3_fundamental.research_report）")
    parser.add_argument("--limit", type=int, default=0, help="只跑前 N 只（0=全部）")
    parser.add_argument("--sleep", type=float, default=0.4, help="每股间隔秒数（反爬限速）")
    parser.add_argument("--batch-size", type=int, default=200, help="多少只 flush 一次")
    parser.add_argument("--date-from", default=_DEFAULT_FROM, help="区间起（YYYY-MM-DD，默认 2000-01-01，实际深度以接口返回为准）")
    parser.add_argument("--date-to", default=time.strftime("%Y-%m-%d"), help="区间止（YYYY-MM-DD，默认今天）")
    parser.add_argument("--check", action="store_true", help="验收模式：只查库不采集")
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.set_defaults(resume=True)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.check:
        sys.exit(run_check())
    try:
        sys.exit(run_backfill(args))
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 — 致命错误落盘（无头运行环境 stdout 可能不可见）
        err_file = ROOT / ".runtime" / "tmp" / "backfill_research_report_full_error.txt"
        err_file.parent.mkdir(parents=True, exist_ok=True)
        err_file.write_text(traceback.format_exc(), encoding="utf-8")
        log.error("未处理异常，详情见 %s", err_file)
        sys.exit(1)


if __name__ == "__main__":
    main()
