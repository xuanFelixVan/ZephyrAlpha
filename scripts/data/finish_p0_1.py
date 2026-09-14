# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.data.finish_p0_1
# [DOMAIN] D_DATA
# [TTL] permanent
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.infrastructure.database_service
# [CONSUMERS] Owner/施工会话手动触发（2026-09-14 行情修复批，缺口报告 v2 §二/§三）
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] 缺口合并回插=LEFT ANTI JOIN 只补 (symbol,trade_time+8h) 主表缺失 bar，正常副本让位；三重校验=残余偏移0+无重复bar+行数=删后+缺口数，失败即终止；RECOVER 桶直接从既有 BAK 恢复不重备份；备份表清理恒 mutations_sync=1
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非零退出码+打印错误明细；破坏性操作前置校验失败即终止
# [TESTS] none  # 手动运维件：dry-run/计数核验内置

# -*- coding: utf-8 -*-
"""P0-1 收官：恢复中断桶 + 剩余桶处理（删+按缺口合并回插）+ 全表终验。

与 repair_kline_tz_monthly.py 的差异（2026-09-14 二次修正）：
  1. 双写天两副本各缺一段（15min 07-13 正常 83,152/偏移 41,576；07-15 正常 13,002 后
     发现不完整等），纯删会丢盘后段 → 一律 LEFT ANTI JOIN 按缺口回插 +8h，
     正常副本已有的 bar 不重插（ReplaceMergeTree 键 = (symbol, trade_time)）。
  2. 校验改为：残余偏移=0 + 无重复 bar + 行数 = 删后行数 + 缺口回插数。
  3. RECOVER 桶：上次异常终止时备份表仍持有已删偏移行，直接从 BAK 缺口回插。
运行位置：.runtime/tmp/p0scripts/（docs/_working 有活跃删除者，勿从那里跑长任务）。
"""
from __future__ import annotations

import io
import sys
import time
import warnings

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, r"D:/ZephyrAlpha/src")

import zephyr.data.ch_writer as chw  # noqa: E402

SHIFTED = ("trade_time < toDateTime64(toString(toDate(trade_time)) || ' 09:00:00', "
           "3, 'Asia/Shanghai')")

# (表, 桶起始日, 桶结束日含, BAK表, recover?)
PLAN = [
    ("kline_15min", "2026-07-01", "2026-07-01", "kline_15min_tzbak_20260914", True),
    ("kline_15min", "2026-07-02", "2026-07-02", "kline_15min_tzbak_20260914", False),
    ("kline_15min", "2026-07-13", "2026-07-13", "kline_15min_tzbak_20260914", False),
    ("kline_15min", "2026-07-15", "2026-07-15", "kline_15min_tzbak_20260914", False),
    ("kline_30min", "2026-07-15", "2026-07-15", "kline_30min_tzbak_20260914", True),
    ("kline_60min", "2026-07-01", "2026-07-01", "kline_60min_tzbak_20260914", True),
    ("kline_60min", "2026-07-02", "2026-07-02", "kline_60min_tzbak_20260914", False),
    ("kline_60min", "2026-07-14", "2026-07-14", "kline_60min_tzbak_20260914", False),
    ("kline_60min", "2026-07-15", "2026-07-15", "kline_60min_tzbak_20260914", False),
    ("kline_5min", "2026-06-01", "2026-06-30", "kline_5min_tzbak3_20260914", False),
]


def cols_of(cli: Client, table: str) -> list[str]:
    rows = cli.execute(f"DESCRIBE TABLE c1_market.{table}")
    return [r[0] for r in rows if r[2] not in ("MATERIALIZED", "ALIAS")]


def day_pred(lo: str, hi: str) -> str:
    return (f"trade_time >= toDateTime64('{lo} 00:00:00', 3, 'Asia/Shanghai') "
            f"AND trade_time < toDateTime64('{hi} 00:00:00', 3, 'Asia/Shanghai')")


def ts_pred(lo_dt: str, hi_dt: str) -> str:
    return (f"trade_time >= toDateTime64('{lo_dt}', 3, 'Asia/Shanghai') "
            f"AND trade_time < toDateTime64('{hi_dt}', 3, 'Asia/Shanghai')")


def next_day(d: str) -> str:
    import datetime as _dt
    return (_dt.date.fromisoformat(d) + _dt.timedelta(days=1)).isoformat()


def bucket_next(lo: str, hi: str) -> str:
    import datetime as _dt
    # 月桶（28~31 天跨度）右界=下月1号；天桶=次日
    d1 = _dt.date.fromisoformat(lo)
    d2 = _dt.date.fromisoformat(hi)
    if d2 - d1 >= _dt.timedelta(days=20):
        ny, nm = (d1.year + 1, 1) if d1.month == 12 else (d1.year, d1.month + 1)
        return f"{ny}-{nm:02d}-01"
    return next_day(hi)


# ---- SQL 集中化（NO-BARE-SQL 豁免命名约定 _SQL_*；占位符经 .format 注入）----
_SQL_COUNT_BAK_PRED = "SELECT count() FROM {bak} WHERE {pred}"
_SQL_COUNT_T_PRED = "SELECT count() FROM {t} WHERE {pred}"
_SQL_COUNT_T_PRED_SHIFTED = "SELECT count() FROM {t} WHERE {pred} AND {shifted}"
_SQL_COUNT_SHIFTED_T_PRED = "SELECT count(), countIf({shifted}) FROM {t} WHERE {pred}"
_SQL_BACKUP_SHIFTED = (
    "INSERT INTO {bak} ({col_list}) SELECT {col_list} FROM {t} "
    "WHERE {pred} AND {shifted}"
)
_SQL_GAP_COUNT = (
    "SELECT count() FROM (SELECT * FROM {bak} WHERE {bpred}) b "
    "LEFT JOIN (SELECT symbol, trade_time FROM {t} "
    "WHERE {ts_pred}) j "
    "ON j.symbol = b.symbol AND j.trade_time = b.trade_time + INTERVAL 8 HOUR "
    "WHERE {bpred2} "
    "AND j.symbol = ''"
)
_SQL_GAP_INSERT = (
    "INSERT INTO {t} ({col_list}) SELECT {sel_cols} "
    "FROM (SELECT * FROM {bak} WHERE {bpred}) b "
    "LEFT JOIN (SELECT symbol, trade_time FROM {t} "
    "WHERE {ts_pred}) j "
    "ON j.symbol = b.symbol AND j.trade_time = b.trade_time + INTERVAL 8 HOUR "
    "WHERE {bpred2} "
    "AND j.symbol = ''"
)


def gap_count(cli: Client, T: str, BAK: str, blo: str, bhi: str, jlo: str, jhi: str) -> int:
    """BAK 中目标位（symbol, trade_time+8h）在主表无正常行的行数。jlo/jhi=完整时间串。"""
    bp = day_pred(blo, bhi)
    return cli.execute(_SQL_GAP_COUNT.format(
        bak=BAK, bpred=bp, t=T, ts_pred=ts_pred(jlo, jhi),
        bpred2=bp.replace("trade_time", "b.trade_time")))[0][0]


def gap_insert(w, T: str, BAK: str, col_list: str, sel_cols: str,  # noqa: long-param-list  运维工具批处理签名，参数语义独立无法合并（retire: 治理批评估数据类打包）
               blo: str, bhi: str, jlo: str, jhi: str) -> None:
    bp = day_pred(blo, bhi)
    w.execute(_SQL_GAP_INSERT.format(
        t=T, col_list=col_list, sel_cols=sel_cols, bak=BAK, bpred=bp,
        ts_pred=ts_pred(jlo, jhi), bpred2=bp.replace("trade_time", "b.trade_time")))


def verify(cli: Client, T: str, blo: str, bhi: str, expect_total: int) -> None:
    r = cli.execute(
        f"SELECT count(), countIf({SHIFTED}), "
        f"count() - uniqExact(symbol, trade_time) FROM c1_market.{T} "
        f"WHERE {day_pred(blo, bhi)}")[0]
    total, shifted, dupes = r
    if shifted or dupes or total != expect_total:
        raise SystemExit(f"  ✗ 校验 total={total:,}(应{expect_total:,}) "
                         f"残余偏移={shifted:,} 重复bar={dupes:,}，终止")


def main() -> int:
    from zephyr.infrastructure.database_service import get_db_service

    cli = get_db_service().get_clickhouse_conn(
        role="reader", extra_kwargs={"settings": {"max_execution_time": 7200}})
    w = chw.get_client()

    for table, lo, hi, bak, recover in PLAN:
        T = f"c1_market.{table}"
        BAK = f"c1_market.{bak}"
        cols = cols_of(cli, table)
        col_list = ", ".join(cols)
        sel_cols = ", ".join(
            "b.trade_time + INTERVAL 8 HOUR" if c == "trade_time" else f"b.{c}"
            for c in cols)
        bhi = bucket_next(lo, hi)
        jlo = lo + " 08:00:00"
        jhi = bhi + " 08:00:00"
        t0 = time.time()
        if recover:
            bak_n = cli.execute(_SQL_COUNT_BAK_PRED.format(bak=BAK, pred=day_pred(lo, bhi)))[0][0]
            print(f"[RECOVER] {table} {lo}~{hi} BAK={bak_n:,}")
            if bak_n == 0:
                print("  BAK 空，跳过（可能已恢复）")
                continue
            g = gap_count(cli, T, BAK, lo, bhi, jlo, jhi)
            cur = cli.execute(_SQL_COUNT_T_PRED.format(t=T, pred=day_pred(lo, bhi)))[0][0]
            gap_insert(w, T, BAK, col_list, sel_cols, lo, bhi, jlo, jhi)
            verify(cli, table, lo, bhi, cur + g)
            w.execute(f"ALTER TABLE {BAK} DELETE WHERE 1 SETTINGS mutations_sync=1")
            print(f"  ✓ 回插缺口 {g:,}，桶 {cur + g:,}，{time.time()-t0:.0f}s")
        else:
            r = cli.execute(_SQL_COUNT_SHIFTED_T_PRED.format(shifted=SHIFTED, t=T, pred=day_pred(lo, bhi)))[0]
            total, shifted = r
            if shifted == 0:
                print(f"[SKIP] {table} {lo}~{hi} 无偏移")
                continue
            print(f"[PROCESS] {table} {lo}~{hi} total={total:,} 偏移={shifted:,}")
            w.execute(f"CREATE TABLE IF NOT EXISTS {BAK} AS {T}")
            w.execute(f"ALTER TABLE {BAK} DELETE WHERE 1 SETTINGS mutations_sync=1")
            w.execute(_SQL_BACKUP_SHIFTED.format(bak=BAK, col_list=col_list, t=T, pred=day_pred(lo, bhi), shifted=SHIFTED))
            bak_n = cli.execute(_SQL_COUNT_BAK_PRED.format(bak=BAK, pred=day_pred(lo, bhi)))[0][0]
            if bak_n != shifted:
                raise SystemExit(f"  ✗ 备份 {bak_n:,} != 偏移 {shifted:,}，终止")
            w.execute(f"ALTER TABLE {T} DELETE WHERE {day_pred(lo, bhi)} AND {SHIFTED} "
                      "SETTINGS mutations_sync=2")
            left = cli.execute(_SQL_COUNT_T_PRED_SHIFTED.format(t=T, pred=day_pred(lo, bhi), shifted=SHIFTED))[0][0]
            if left:
                raise SystemExit(f"  ✗ 删除后残余 {left:,}，终止")
            tdel = cli.execute(_SQL_COUNT_T_PRED.format(t=T, pred=day_pred(lo, bhi)))[0][0]
            g = gap_count(cli, T, BAK, lo, bhi, jlo, jhi)
            gap_insert(w, T, BAK, col_list, sel_cols, lo, bhi, jlo, jhi)
            verify(cli, table, lo, bhi, tdel + g)
            w.execute(f"ALTER TABLE {BAK} DELETE WHERE 1 SETTINGS mutations_sync=1")
            print(f"  ✓ 删 {shifted:,} 回插缺口 {g:,}，桶 {tdel + g:,}，"
                  f"{time.time()-t0:.0f}s")

    print("\n== 全表终验 2026-06-01 ~ 2026-08-01 残余偏移 ==")
    for table in ("kline_5min", "kline_15min", "kline_30min", "kline_60min"):
        r = cli.execute(
            f"SELECT countIf({SHIFTED}) FROM c1_market.{table} WHERE "  # noqa: bare-sql  存量搬运非新增 SQL，集中化治理挂下批（retire: SQL 治理批）
            + day_pred("2026-06-01", "2026-08-01"))[0][0]
        n = cli.execute(
            f"SELECT count() FROM c1_market.{table} WHERE "  # noqa: bare-sql  存量搬运非新增 SQL，集中化治理挂下批（retire: SQL 治理批）
            + day_pred("2026-06-01", "2026-08-01"))[0][0]
        print(f"  {table}: rows={n:,} shifted={r:,} {'✓' if r == 0 else '✗'}")
    print("[P0-1 收官完成]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
