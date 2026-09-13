# [BLUEPRINT] MOD-BT-080 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.data.backfill_stock_indicator_daily_basic
# [DOMAIN] D_DATA
# [DEPENDENCIES] tushare; zephyr.data.ch_writer; zephyr.data.ch_config
# [CONSUMERS] c1_market.stock_indicator（估值/财务类策略翻译管线的食材，解锁 112 条 fundamental_gate 挂起策略）
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] PIT（估值=当日收盘派生数据，as_of=trade_date，无公告哨兵需求）；幂等（已有日期跳过）；
#   只写不删改（台账式追加）；fail-closed（落库未确认即 raise）；数据源标记 tushare_daily_basic
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(落库未确认/token 缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py（冒烟级：单日 pilot 断言）
# [A_module] module_id=MOD-BT-080 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""stock_indicator 历史估值回补——tushare daily_basic 按交易日拉全市场。

设计真源：docs/_working/2026-09-13-c5-cluster-differentiation-report.md 附三。
映射：pe←pe_ttm、pb←pb、ps←ps_ttm、dividend_yield←dv_ttm、pcf 缺省 NULL（daily_basic 无此列）。
用法：python scripts/data/backfill_stock_indicator_daily_basic.py --start 2020-01-01 --end 2026-06-30
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)
_TABLE = "c1_market.stock_indicator"
_COLS = ("(trade_date, symbol, pe, pb, ps, pcf, dividend_yield, data_source, ingest_ts, total_mv, circ_mv)")  # exchange/symbol_canonical=MATERIALIZED 列禁插
_SRC = "tushare_daily_basic"


def _load_token() -> str:
    env = {}
    for p in (Path(".env"), Path(".env.local")):
        if p.exists():
            for ln in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                if "=" in ln and not ln.strip().startswith("#"):
                    k, _, v = ln.partition("=")
                    env[k.strip()] = v.strip()
    tok = env.get("TUSHARE_TOKEN", "")
    if not tok:
        raise RuntimeError("TUSHARE_TOKEN 缺失（.env）")
    return tok


def _trade_days(start: str, end: str, client) -> list[str]:
    rows = client.execute(
        f"SELECT DISTINCT trade_date FROM c1_market.stk_limit "
        f"WHERE trade_date >= '{start}' AND trade_date <= '{end}' ORDER BY trade_date")
    return [r[0].strftime("%Y%m%d") for r in rows]


def _existing_dates(client) -> set[str]:
    rows = client.execute(
        f"SELECT DISTINCT trade_date FROM {_TABLE} WHERE data_source = '{_SRC}'")
    return {r[0].strftime("%Y%m%d") for r in rows}


def _cell(v) -> str:
    if v is None:
        return chr(92) + "N"
    return str(v).replace(chr(9), " ").replace(chr(10), " ")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="stock_indicator 历史估值回补（tushare daily_basic）")
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--sleep", type=float, default=0.35, help="每次调用间隔秒（限速保护）")
    ap.add_argument("--pilot", type=int, default=0, help="只跑前 N 个未覆盖交易日（冒烟）")
    ap.add_argument("--refetch", action="store_true", help="忽略已回补集合全量重拉（ReplacingMergeTree 去重）")
    args = ap.parse_args()

    from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config

    ensure_ch_env_loaded()
    cfg = load_ch_reader_config()
    from clickhouse_driver import Client

    client = Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
                    user=cfg.get("user", "default"), password=cfg.get("password", ""), connect_timeout=5)
    days = _trade_days(args.start, args.end, client)
    done = _existing_dates(client)
    todo = list(days) if args.refetch else [d for d in days if d not in done]
    if args.pilot:
        todo = todo[: args.pilot]
    logger.info("窗口 %s..%s：交易日 %d，已回补 %d，待拉 %d", args.start, args.end, len(days), len(done), len(todo))
    if not todo:
        print(json_days(days, done))
        return

    import tushare as ts

    ts.set_token(_load_token())
    pro = ts.pro_api()
    from zephyr.data import ch_writer

    ingested = 0
    for i, d in enumerate(todo):
        df = None
        for attempt in range(3):  # 网络超时退避重试（2026-09-14 ReadTimeout 中断教训）
            try:
                df = pro.daily_basic(
                    trade_date=d,
                    fields="ts_code,trade_date,close,pe_ttm,pb,ps_ttm,dv_ttm,total_mv,circ_mv",
                )
                break
            except Exception as exc:  # noqa: BLE001 网络类异常退避后重试
                if attempt == 2:
                    raise
                logger.warning("%s 第%d次拉取失败退避: %s", d, attempt + 1, str(exc)[:80])
                time.sleep(5 * (attempt + 1))
        rows = []
        ing_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        for _, r in df.iterrows():
            sym = str(r["ts_code"])[:6]
            rows.append([
                f"{d[:4]}-{d[4:6]}-{d[6:]}", sym,
                None if pd_isna(r["pe_ttm"]) else round(float(r["pe_ttm"]), 6),
                None if pd_isna(r["pb"]) else round(float(r["pb"]), 6),
                None if pd_isna(r["ps_ttm"]) else round(float(r["ps_ttm"]), 6),
                None,  # pcf：daily_basic 无此列
                None if pd_isna(r["dv_ttm"]) else round(float(r["dv_ttm"]), 6),
                _SRC, ing_ts,
                None if pd_isna(r["total_mv"]) else round(float(r["total_mv"]), 2),
                None if pd_isna(r["circ_mv"]) else round(float(r["circ_mv"]), 2),
            ])
        if rows:
            tsv = "\n".join("\t".join(_cell(v) for v in row) for row in rows) + "\n"
            if not ch_writer.write_tsv(_TABLE, _COLS, tsv.encode("utf-8")):
                raise RuntimeError(f"落库未确认 {d}——fail-closed")
            ingested += len(rows)
        logger.info("[%d/%d] %s: %d 行", i + 1, len(todo), d, len(rows))
        time.sleep(args.sleep)
    print(f"{{\"done_days\": {len(todo)}, \"rows\": {ingested}}}")


def pd_isna(v) -> bool:
    return v is None or v != v


def json_days(days, done) -> str:
    import json

    return json.dumps({"already_done_days": len(done), "window_days": len(days)})


if __name__ == "__main__":
    sys.exit(main())
