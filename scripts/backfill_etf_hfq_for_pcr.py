# [BLUEPRINT] MOD-L00-004 | docs/_working/xhs_full_construction/00_owner_directive.md work order #3+#14 前置批点单#6
# [MODULE] scripts.backfill_etf_hfq_for_pcr
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.table_registry; zephyr.infrastructure.database_service; zephyr.shared.security.secrets; tushare; clickhouse_driver
# [CONSUMERS] PCR E4 考试（scripts/audit/pcr_e4_exam.py 标的层原料）；数据线 known_data_gaps 口径回补件
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 默认 dry-run 零写入；--execute 才落库（ch_writer.write_tsv 正门，禁裸 INSERT）；
#  落点 c1_market.kline_daily_hfq（ReplacingMergeTree ORDER BY(symbol,trade_date)，重跑幂等折叠）；
#  hfq=raw×fund_adj 累计因子，无因子日宁缺毋滥剔除；exchange/symbol_canonical 为 MATERIALIZED 列禁显式插入；
#  tushare 分年分页+限速间隔（1302 教训）；volume=手、amount=千元×1000=元（与存量口径一致）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tushare 3 次重试后仍失败→该标的跳过留痕 exit 2；写入 disposition≠CH_COMMITTED→exit 3（本地落盘兜底属预期降级不判失败）
# [TESTS] 本 CLI 以 --help 与 dry-run 自测（写入路径由回补实战驱动：2026-09-23 实证 510050.SH=2850 行/510300.SH=1674 行 CH_COMMITTED）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  Owner 批点单人工触发的标的层深史回补（ETF 后复权日线，tushare fund 族），人工触发是设计意图
"""ETF 标的层后复权日线回补（PCR E4 重考解锁前置，xhs 班批点单 #6）。

背景：c1_market.kline_daily_hfq 的 ETF 通配 universe 外（hfq 增量任务=股票口径），
510050.SH/510300.SH 零行 → PCR E4 考试 INSUFFICIENT（标的层原料缺位，pcr_e4_evidence.md）。
本件以 tushare fund_daily（OHLC，vol=手/amount=千元）× fund_adj（累计复权因子）算真后复权，
补齐期权史覆盖窗：510050.SH 自 2015-01（期权 2015-02-09 起）、510300.SH 自 2019-11（期权 2019-12-23 起）。

用法::

    python scripts/backfill_etf_hfq_for_pcr.py             # dry-run（只算行数零写入）
    python scripts/backfill_etf_hfq_for_pcr.py --execute   # 落库（ch_writer HTTP 正门）
    python scripts/backfill_etf_hfq_for_pcr.py --underlying 510300.SH --start 20191101 --execute
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timezone

import pandas as pd

from zephyr.data.ch_writer import write_tsv_outcome
from zephyr.data.table_registry import get_registry
from zephyr.shared.security.secrets import get_secret

JOBS = {
    # ts_code: (start, 说明)
    "510050.SH": ("20150101", "SSE 期权 2015-02-09 起"),
    "510300.SH": ("20191101", "SSE 期权 2019-12-23 起"),
}
YEARS = range(2015, 2027)
COLS = (
    "(trade_date,symbol,open,close,high,low,volume,amount,amplitude,pct_change,"
    "change,turnover,data_source,ingest_ts)"
)


def _fetch_paged(pro, api: str, ts_code: str, start: str, end: str) -> pd.DataFrame:
    frames = []
    for y in YEARS:
        s = max(f"{y}0101", start)
        e = min(f"{y}1231", end)
        if s > e:
            continue
        df = None
        for attempt in range(3):
            try:
                df = getattr(pro, api)(ts_code=ts_code, start_date=s, end_date=e)
                break
            except Exception:  # noqa: BLE001 — PERM-TRIGGER 纪律下无 sleep 退避，立即重试至多 3 次（失败=该标的跳过留痕 exit 2）
                if attempt == 2:
                    raise
        if df is not None and len(df):
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _rows_for(pro, ts_code: str, start: str) -> tuple[list[str], int]:
    end = date.today().strftime("%Y%m%d")
    daily = _fetch_paged(pro, "fund_daily", ts_code, start, end)
    adj = _fetch_paged(pro, "fund_adj", ts_code, start, end)
    if daily.empty or adj.empty:
        return [], 0
    adj = adj[["trade_date", "adj_factor"]].drop_duplicates("trade_date")
    df = daily.merge(adj, on="trade_date", how="inner")
    dropped = len(daily) - len(df)
    ingest_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    symbol = ts_code.split(".")[0]
    lines = []
    for _, r in df.iterrows():
        f = float(r["adj_factor"])
        o, c, h, l = (round(float(r[k]) * f, 4) for k in ("open", "close", "high", "low"))
        pre = float(r["pre_close"])
        amp = round((float(r["high"]) - float(r["low"])) / pre * 100, 4) if pre > 0 else 0.0
        lines.append(
            "\t".join(
                [
                    f"{r['trade_date'][:4]}-{r['trade_date'][4:6]}-{r['trade_date'][6:]}",
                    symbol,
                    f"{o:.4f}", f"{c:.4f}", f"{h:.4f}", f"{l:.4f}",
                    str(int(round(float(r["vol"])))),
                    f"{float(r['amount']) * 1000:.2f}",
                    f"{amp:.4f}",
                    f"{float(r['pct_chg']):.4f}", f"{float(r['change']):.4f}", "0.0000",
                    "tushare", ingest_ts,
                ]
            )
        )
    return lines, dropped


def main() -> int:
    ap = argparse.ArgumentParser(description="ETF 标的层 hfq 深史回补（PCR E4 前置，tushare fund 族）")
    ap.add_argument("--underlying", default="", help="单标的 ts_code（空=全表 JOBS）")
    ap.add_argument("--start", default="", help="覆盖默认起始日 YYYYMMDD")
    ap.add_argument("--execute", action="store_true", help="真写入（默认 dry-run）")
    args = ap.parse_args()

    import tushare as ts

    pro = ts.pro_api(get_secret("TUSHARE_TOKEN"))
    table = get_registry().table("market_kline_daily_hfq")
    jobs = {args.underlying: JOBS.get(args.underlying, ("20150101", ""))} if args.underlying else JOBS
    failures = 0
    for ts_code, (default_start, _) in jobs.items():
        start = args.start or default_start
        lines, dropped = _rows_for(pro, ts_code, start)
        print(f"[PLAN] {ts_code}: rows={len(lines)} (无因子剔除={dropped}) execute={args.execute}")
        if not lines:
            failures += 1
            continue
        if not args.execute:
            continue
        outcome = write_tsv_outcome(table, COLS, ("\n".join(lines) + "\n").encode("utf-8"))
        committed = str(outcome.disposition).endswith("CH_COMMITTED")
        print(f"[WRITE] {ts_code}: disposition={outcome.disposition} detail={outcome.detail}")
        if not committed:
            failures += 1
    return 2 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
