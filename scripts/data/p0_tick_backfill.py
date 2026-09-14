# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.data.p0_tick_backfill
# [DOMAIN] D_DATA
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  Owner 手动触发的数据运维兵器（15.6亿行迁移/时区修复），备份-删除-校验不变量内置，人工触发是设计意图非缺陷
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.infrastructure.database_service; xtquant
# [CONSUMERS] Owner/施工会话手动触发（2026-09-14 行情修复批，缺口报告 v2 §二/§三）
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] 行格式恒等 tick_subscriber.tick_to_row（裸代码/中性盘/quality_flag=1）；过滤 09:15:00~15:00:59 且 lastPrice>0；done 断点文件防重灌；--wipe 必须备份表先行且计数核验；ReplacingMergeTree 同键幂等
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非零退出码+打印错误明细；--wipe 前置校验失败即终止
# [TESTS] none  # 手动运维件：内置 done 断点防重灌+计数核验

# -*- coding: utf-8 -*-
"""QMT tick 历史补数脚本（09-09/09-10/09-11 三天，2026-09-14）。

背景：采集管线 09-09 起退化，tick_data 三天严重不全（09-11 全缺 / 09-10 仅 4 标的 /
09-09 466,616 行 qmt_bridge 残留）。本脚本从 miniQMT 服务器逐标的下载三天 tick 并按
现役格式（tick_subscriber.tick_to_row 口径）写入 c1_market.tick_data。

格式对齐（实测 2026-09-14）：
  - 15 列：trade_date, timestamp, recorded_time, symbol(裸代码), market_type,
    price, volume, amount, direction='中性盘', data_source='miniqmt',
    bid_price, ask_price, bid_volume, ask_volume, quality_flag=1
  - exchange/symbol_canonical 是 MATERIALIZED 自动派生；ingest_ts/data_source 走 DEFAULT
  - recorded_time=回填执行时刻（naive 本地时间串，与 tick_subscriber 既有惯例一致）
  - 过滤口径（交接文档 §四.4）：09:15:00 <= t <= 15:00:59 且 lastPrice > 0
  - ReplacingMergeTree ORDER BY (market_type, symbol, trade_date, timestamp, price)，
    同键重写幂等

用法：
  python p0_tick_backfill.py --pilot                 # 6 标的试跑，验证格式与入库
  python p0_tick_backfill.py --wipe                  # 备份+清掉三天残留行（幂等；
                                                     #   备份表 tick_data_tzbak_20260914）
  python p0_tick_backfill.py --dates 20260909        # 全量跑某天（默认三天全跑）
  # 断点续跑：--done-dir 下每天一个 done 清单，重跑自动跳过已完成标的
"""
from __future__ import annotations

import argparse
import io
import sys
import time
import warnings
from datetime import datetime
from decimal import Decimal

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, r"D:/ZephyrAlpha/src")

from xtquant import xtdata  # noqa: E402

import zephyr.data.ch_writer as chw  # noqa: E402
from zephyr.data.tick_subscriber import infer_market_type, _stock_to_symbol  # noqa: E402

DATA_DIR = r"E:\国金证券QMT交易端\userdata_mini\datadir"
DONE_DIR = r"D:/ZephyrAlpha/.runtime/tmp"
TICK_COLS = ["trade_date", "timestamp", "recorded_time", "symbol", "market_type",
             "price", "volume", "amount", "direction", "data_source",
             "bid_price", "ask_price", "bid_volume", "ask_volume", "quality_flag"]
WIPE_DATES = ("2026-09-09", "2026-09-10", "2026-09-11")


def get_universe() -> list[str]:
    """与 tick_subscriber._get_all_symbols 同口径：5 市场 + 指数。"""
    seen: set[str] = set()
    out: list[str] = []

    def add(syms):
        for s in syms:
            if s and s not in seen:
                seen.add(s)
                out.append(s)

    add(xtdata.get_stock_list_in_sector("沪深A股"))
    add(xtdata.get_stock_list_in_sector("京市A股"))
    fund = xtdata.get_stock_list_in_sector("沪深基金")
    add([s for s in fund if s.split(".")[0][:2] in ("15", "51", "16", "18")])
    add(xtdata.get_stock_list_in_sector("沪深转债"))
    add(xtdata.get_stock_list_in_sector("沪深指数"))
    return out


def dec(val, nd) -> Decimal | None:
    try:
        f = float(val)
    except (TypeError, ValueError):
        return None
    if f == 0:
        return None
    return Decimal(str(round(f, nd)))


def _tick_row(ddate, ts, rt, bare, mtype, price, vol, amt, bid_p, ask_p, bid_v, ask_v):  # noqa: long-param-list  运维工具批处理签名，参数语义独立无法合并（retire: 治理批评估数据类打包）
    return (
        ddate,
        ts,
        rt,
        bare,
        mtype,
        Decimal(str(round(price, 4))),
        int(vol or 0),
        Decimal(str(round(float(amt or 0), 2))),
        "中性盘",
        "miniqmt",
        dec(bid_p[0] if bid_p is not None and len(bid_p) else None, 4),
        dec(ask_p[0] if ask_p is not None and len(ask_p) else None, 4),
        int(bid_v[0]) if bid_v is not None and len(bid_v) and bid_v[0] else None,
        int(ask_v[0]) if ask_v is not None and len(ask_v) and ask_v[0] else None,
        1,
    )


def parse_day(df, code: str, day: str) -> list[tuple]:
    """df → 入库行列表。day=YYYYMMDD。"""
    if df is None or len(df) == 0:
        return []
    bare = _stock_to_symbol(code)
    mtype = infer_market_type(code)
    dstr = f"{day[:4]}-{day[4:6]}-{day[6:8]}"
    ddate = datetime.strptime(dstr, "%Y-%m-%d").date()
    lo = time.mktime(time.strptime(f"{dstr} 09:15:00", "%Y-%m-%d %H:%M:%S"))
    hi = time.mktime(time.strptime(f"{dstr} 15:01:00", "%Y-%m-%d %H:%M:%S"))
    rt = datetime.now()
    rows: list[tuple] = []
    if "time" in df.columns:
        ts_vals = df["time"].tolist()
    else:
        ts_vals = list(df.index)
    for pos in range(len(df)):
        row = df.iloc[pos]
        ms = float(ts_vals[pos])
        ts = datetime.fromtimestamp(ms / 1000.0)
        t = ts.timetuple()
        if not (lo <= time.mktime(t) <= hi):
            continue
        price = float(row.get("lastPrice") or 0)
        if price <= 0:
            continue
        bid_p = row.get("bidPrice")
        ask_p = row.get("askPrice")
        bid_v = row.get("bidVol")
        ask_v = row.get("askVol")
        vol = row.get("volume")
        amt = row.get("amount")
        rows.append(_tick_row(ddate, ts, rt, bare, mtype, price, vol, amt,
                              bid_p, ask_p, bid_v, ask_v))
    return rows


def main() -> int:
    a = _parse_args()
    dates = [d for d in a.dates.split(",") if d]

    xtdata.data_dir = DATA_DIR
    xtdata.enable_hello = False
    print("connect:", xtdata.connect())

    from zephyr.infrastructure.database_service import get_db_service

    cli = get_db_service().get_clickhouse_conn(
        role="reader", extra_kwargs={"settings": {"max_execution_time": 600}})
    w = chw.get_client()

    if a.wipe:
        return _wipe_three_days(cli, w)

    universe = _load_universe(a)
    return _process_days(dates, universe, cli, w)


if __name__ == "__main__":
    sys.exit(main())
