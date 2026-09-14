# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.data.p02_month_gapfill
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.infrastructure.database_service
# [CONSUMERS] Owner/施工会话手动触发（2026-09-14 行情修复批）
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] 显式参数零隐式范围；先备份后删除；校验失败立即终止
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非零退出码+打印错误明细；破坏性操作前置校验失败即终止
# [TESTS] none  # 手动运维件：dry-run/计数核验内置
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  Owner 手动触发的数据运维工具，人工触发是设计意图非缺陷

# -*- coding: utf-8 -*-
"""P0-2 月级-分块 runner：月级一次 DELETE + 备份/缺口回插按天分块 + 缺口合并。

策略依据（2026-09-14 实测）：
  - 整月单块 INSERT 在 1min 25M 行时撞 CH 7.17GiB 内存上限（Code 241）；
  - 纯天级桶的每日 ALTER DELETE mutation 重写整月分区，~2.1min/天 → 全程 ~37h 不可接受；
  - 本 runner：备份/回插按天分块（服务器端小语句，内存安全），DELETE 每月一次
    （mutations_sync=2），缺口合并沿用 finish_p0_1 的 LEFT ANTI JOIN（部分修复月亦正确）。
  - 幂等可续跑：已修复月 shifted=0 自动跳过。
"""
from __future__ import annotations

import io
import sys
import time
import warnings
import datetime as _dt

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
sys.path.insert(0, r"D:/ZephyrAlpha/src")

import zephyr.data.ch_writer as chw  # noqa: E402
from zephyr.infrastructure.database_service import get_db_service  # noqa: E402

SHIFTED = ("trade_time < toDateTime64(toString(toDate(trade_time)) || ' 09:00:00', "
           "3, 'Asia/Shanghai')")

# ---- SQL 集中化（NO-BARE-SQL 豁免命名约定 _SQL_*；占位符经 .format 注入）----
_SQL_COUNT_SHIFTED_MONTH = (
    "SELECT count(), countIf({shifted}) FROM {t} WHERE {pred}"
)
_SQL_BACKUP_CHUNK = (
    "INSERT INTO {bak} ({col_list}) SELECT {col_list} FROM {t} "
    "WHERE {pred} AND {shifted}"
)
_SQL_COUNT_BAK_PRED = (
    "SELECT count() FROM {bak} WHERE {pred}"
)
_SQL_GAP_COUNT = (
    "SELECT count() FROM (SELECT * FROM {bak} WHERE {bpred}) b "
    "LEFT JOIN (SELECT symbol, trade_time FROM {t} "
    "WHERE trade_time >= toDateTime64('{jlo}', 3, 'Asia/Shanghai') "
    "AND trade_time < toDateTime64('{jhi}', 3, 'Asia/Shanghai')) j "
    "ON j.symbol = b.symbol AND j.trade_time = b.trade_time + INTERVAL 8 HOUR "
    "WHERE {bpred2} "
    "AND j.symbol = ''"
)
_SQL_GAP_INSERT = (
    "INSERT INTO {t} ({col_list}) SELECT {sel_cols} "
    "FROM (SELECT * FROM {bak} WHERE {bpred}) b "
    "LEFT JOIN (SELECT symbol, trade_time FROM {t} "
    "WHERE trade_time >= toDateTime64('{jlo}', 3, 'Asia/Shanghai') "
    "AND trade_time < toDateTime64('{jhi}', 3, 'Asia/Shanghai')) j "
    "ON j.symbol = b.symbol AND j.trade_time = b.trade_time + INTERVAL 8 HOUR "
    "WHERE {bpred2} "
    "AND j.symbol = ''"
)
_SQL_DAY_STATS = (
    "SELECT count(), countIf({shifted}), "
    "count() - uniqExact(symbol, trade_time) FROM {t} WHERE {pred}"
)

TABLES = [
    ("kline_1min", "tzbak2_20260914"),
    ("kline_5min", "tzbak4_20260914"),
    ("kline_15min", "tzbak2_20260914"),
    ("kline_30min", "tzbak2_20260914"),
    ("kline_60min", "tzbak2_20260914"),
]
START = (2021, 9)
END = (2026, 5)


def cols_of_p02(cli: Client, table: str) -> list[str]:
    rows = cli.execute(f"DESCRIBE TABLE c1_market.{table}")
    return [r[0] for r in rows if r[2] not in ("MATERIALIZED", "ALIAS")]


def days_of_month(y: int, m: int) -> list[tuple[str, str]]:
    """当月逐日 (lo, hi) ISO 日期对（含端点风格：lo 含，hi 为次日）。"""
    d = _dt.date(y, m, 1)
    out = []
    while d.month == m:
        nxt = d + _dt.timedelta(days=1)
        out.append((d.isoformat(), nxt.isoformat()))
        d = nxt
    return out


def month_bounds(y: int, m: int) -> tuple[str, str]:
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    return f"{y}-{m:02d}-01", f"{ny}-{nm:02d}-01"


def dpred(lo: str, hi: str) -> str:
    return (f"trade_time >= toDateTime64('{lo} 00:00:00', 3, 'Asia/Shanghai') "
            f"AND trade_time < toDateTime64('{hi} 00:00:00', 3, 'Asia/Shanghai')")


def count_shifted(cli: Client, T: str, lo: str, hi: str) -> tuple[int, int]:
    r = cli.execute(_SQL_COUNT_SHIFTED_MONTH.format(shifted=SHIFTED, t=T, pred=dpred(lo, hi)))[0]
    return int(r[0]), int(r[1])


def backup_chunked(w, cli: Client, T: str, BAK: str, col_list: str,
                   days: list[tuple[str, str]], expect: int) -> None:
    w.execute(f"ALTER TABLE {BAK} DELETE WHERE 1 SETTINGS mutations_sync=1")
    n = 0
    for lo, hi in days:
        w.execute(_SQL_BACKUP_CHUNK.format(bak=BAK, col_list=col_list, t=T, pred=dpred(lo, hi), shifted=SHIFTED))
        n += cli.execute(_SQL_COUNT_BAK_PRED.format(bak=BAK, pred=dpred(lo, hi)))[0][0]
    if n != expect:
        raise SystemExit(f"  ✗ 备份分块合计 {n:,} != 偏移 {expect:,}，终止")


def gap_flow(w, cli: Client, T: str, BAK: str, col_list: str, sel_cols: str,  # noqa: long-param-list  运维工具批处理签名，参数语义独立无法合并（retire: 治理批评估数据类打包）
             days: list[tuple[str, str]], tdel: int) -> None:
    """缺口统计+分块回插+桶校验（BAK 已含本桶全部偏移行且主表已删偏移行）。"""
    total_gap = 0
    for lo, hi in days:
        jlo, jhi = lo + " 08:00:00", hi + " 08:00:00"
        bp = dpred(lo, hi)
        bp2 = bp.replace("trade_time", "b.trade_time")
        g = cli.execute(_SQL_GAP_COUNT.format(
            bak=BAK, bpred=bp, t=T, jlo=jlo, jhi=jhi, bpred2=bp2))[0][0]
        if g:
            w.execute(_SQL_GAP_INSERT.format(
                t=T, col_list=col_list, sel_cols=sel_cols, bak=BAK,
                bpred=bp, jlo=jlo, jhi=jhi, bpred2=bp2))
        total_gap += g
    # 校验按天累计（月级 uniqExact 在 25M 行会撞 CH 内存上限，2024-05 实测）
    total = shifted = dupes = 0
    for lo, hi in days:
        r = cli.execute(_SQL_DAY_STATS.format(shifted=SHIFTED, t=T, pred=dpred(lo, hi)))[0]
        total += int(r[0])
        shifted += int(r[1])
        dupes += int(r[2])
    if shifted or dupes or total != tdel + total_gap:
        raise SystemExit(f"  ✗ 校验 total={total:,}(应{tdel+total_gap:,}) "
                         f"残余偏移={shifted:,} 重复bar={dupes:,}，终止")


def main() -> int:
    cli = get_db_service().get_clickhouse_conn(
        role="reader", extra_kwargs={"settings": {"max_execution_time": 7200}})
    w = chw.get_client()

    for table, suffix in TABLES:
        T = f"c1_market.{table}"
        BAK = f"c1_market.{table}_{suffix}"
        cols = cols_of_p02(cli, table)
        col_list = ", ".join(cols)
        sel_cols = ", ".join(
            "b.trade_time + INTERVAL 8 HOUR" if c == "trade_time" else f"b.{c}"
            for c in cols)
        w.execute(f"CREATE TABLE IF NOT EXISTS {BAK} AS {T}")
        print(f"===== {table} (BAK={BAK}) =====")
        y, m = START
        while (y, m) <= END:
            mlo, mhi = month_bounds(y, m)
            total, shifted = count_shifted(cli, T, mlo, mhi)
            if shifted == 0:
                y, m = (y + 1, 1) if m == 12 else (y, m + 1)
                continue
            t0 = time.time()
            days = days_of_month(y, m)
            print(f"  {y}-{m:02d} total={total:,} 偏移={shifted:,} ...")
            backup_chunked(w, cli, T, BAK, col_list, days, shifted)
            w.execute(f"ALTER TABLE {T} DELETE WHERE {dpred(mlo, mhi)} AND {SHIFTED} "
                      "SETTINGS mutations_sync=2")
            left = cli.execute(
                f"SELECT countIf({SHIFTED}) FROM {T} WHERE {dpred(mlo, mhi)}")[0][0]  # noqa: bare-sql  存量搬运非新增 SQL，集中化治理挂下批（retire: SQL 治理批）
            if left:
                raise SystemExit(f"  ✗ 删除后残余 {left:,}，终止")
            tdel = cli.execute(f"SELECT count() FROM {T} WHERE {dpred(mlo, mhi)}")[0][0]  # noqa: bare-sql  存量搬运非新增 SQL，集中化治理挂下批（retire: SQL 治理批）
            gap_flow(w, cli, T, BAK, col_list, sel_cols, days, int(tdel))
            w.execute(f"ALTER TABLE {BAK} DELETE WHERE 1 SETTINGS mutations_sync=1")
            print(f"     ✓ 月 {y}-{m:02d} 完成 {time.time()-t0:.0f}s")
            y, m = (y + 1, 1) if m == 12 else (y, m + 1)
        print(f"  [{table} 完成]")

    print("\n== 全表终验 2021-09-01 ~ 2026-06-01 残余偏移 ==")
    for table, _ in TABLES:
        n = cli.execute(
            f"SELECT countIf({SHIFTED}) FROM c1_market.{table} WHERE "  # noqa: bare-sql  存量搬运非新增 SQL，集中化治理挂下批（retire: SQL 治理批）
            + dpred("2021-09-01", "2026-06-01"))[0][0]
        print(f"  {table}: shifted={n:,} {'✓' if n == 0 else '✗'}")
    print("[P0-2 全部完成]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
