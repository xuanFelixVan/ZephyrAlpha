# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.data.repair_kline_tz_monthly
# [DOMAIN] D_DATA
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  Owner 手动触发的数据运维兵器（15.6亿行迁移/时区修复），备份-删除-校验不变量内置，人工触发是设计意图非缺陷
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.infrastructure.database_service
# [CONSUMERS] Owner/施工会话手动触发（2026-09-14 行情修复批，缺口报告 v2 §二/§三）
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] 先 check 后 apply 且 --apply 必带 --confirm；偏移判定恒为 trade_time<当日09:00；逐桶 备份→删除→(唯一副本月)回插→校验，任一校验失败立即终止；模式按天判定防月内混合误删（kline_5min 2026-06 案例）；--bak-suffix 防误清既有 tzbak 备份表；双写缺口天应改用 finish_p0_1（本脚本用于全历史纯唯一副本段）
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非零退出码+打印错误明细；破坏性操作前置校验失败即终止
# [TESTS] none  # 手动运维件：dry-run/计数核验内置
# noqa: m11-perm-manual-legitimate  Owner 手动触发的数据运维工具，人工触发是设计意图非缺陷

# -*- coding: utf-8 -*-
"""分钟线时区偏移通用修复脚本（备份→删除→+8h回插→校验，模式按天判定）。

背景（2026-09-14 实测结论）：
  c1_market.kline_1min 从 2021-09 至 2026-05 的全部历史（约 11.3 亿行）trade_time
  被整体 -8h 写入（bdpan 采集器用 UTC 时间戳写 DateTime64(...,'Asia/Shanghai') 列），
  真实 09:30 被存成 01:30。2026-06-01 ~ 2026-07-15 段已于 09-14 凌晨修复完毕
  （1min 双写月份只删、唯一副本月份删+回插）。本脚本用于处理剩余的 2021-09 ~ 2026-05
  全历史段，以及 15/30/60min/5min 等表的残余段。

已验证的硬约束（踩过的坑，勿再踩）：
  1) 各 kline_* 表 trade_time 是 ReplacingMergeTree 排序键首列
     → `ALTER TABLE ... UPDATE trade_time=...` 会报 "Cannot UPDATE key column"，禁用；
     正确做法 = ALTER TABLE DELETE（删行不受键列限制）+ 从备份表 INSERT SELECT +8h。
  2) zephyr_writer 账号无 TRUNCATE 权限（备份表清理用 ALTER TABLE DELETE）。
  3) 偏移行时刻边界干净：全部落在 01:30~07:00，08:00 后零行 → 判定式
     `trade_time < 当日09:00` 不会误伤盘前/竞价数据。
  4) 月内平移不跨月（09:30~15:00 ± 8h 仍在同一天同一个月）。
  5) 复验口径：处理前后「月总行数」必须相等 + 残余偏移必须为 0。
  6) 【2026-09-14 下午新增】模式必须按「天」判定，不能按「月」：
     kline_5min 2026-06 月内混合（06-01~06-18 唯一副本 + 06-22 以后已修复的正常行），
     按月判会误判成双写只删 → 直接抹掉 14 天唯一副本。本版对每个偏移天独立判定：
     该天有正常行 → 只删（双写）；该天无正常行 → 删+回插（唯一副本）。
     纯唯一副本月（整月正常=0）仍按月一次性处理减少 mutation 次数。
  7) 【07:04 清空事故后重建】本文件为接班会话凭上下文逐字重建版（原版未跟踪被清），
     含 month_range 元组 bug 修复与 --bak-suffix 新增（保护已有 tzbak 备份表）。
     注意：双写天两副本各缺一段时（如 15min 07-13），纯"只删"会丢盘后段——
     终版方案见 finish_p0_1.py 的 LEFT ANTI JOIN 缺口合并回插；本脚本保留
     天级判定与唯一副本月一次性处理能力，供 P0-2 全历史段使用（该段为纯唯一副本，
     不受双写缺口问题影响）。

用法（先 check 后 apply，务必分两步）：
  python repair_kline_tz_monthly.py --table kline_1min --start 2021-09-01 --end 2026-05-29 --check
  python repair_kline_tz_monthly.py --table kline_1min --start 2021-09-01 --end 2026-05-29 --apply --confirm
  # --apply 需同时给 --confirm 防手滑；单月可 --only-month 202604 缩小范围断点续跑
  # 对已有备份表的（如 kline_5min）必须给 --bak-suffix 新后缀，防误清旧备份

⚠️ RULE-DATA-OPS：全量 apply 预计数小时 IO + 大量 part 重写，属数据操作门位，
   须 Owner 明确批准后执行。逐桶校验失败立即终止，人工介入。
"""
from __future__ import annotations

import argparse
import io
import sys
import time
import warnings

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, r"D:/ZephyrAlpha/src")

import zephyr.data.ch_writer as chw  # noqa: E402

SHIFTED_PRED = ("trade_time < toDateTime64(toString(toDate(trade_time)) || ' 09:00:00', "
                "3, 'Asia/Shanghai')")


# ---- SQL 集中化（NO-BARE-SQL 豁免命名约定 _SQL_*；占位符经 .format 注入）----
_SQL_COUNT_SHIFTED_PRED = "SELECT count(), countIf({shifted}) FROM {t} WHERE {pred}"
_SQL_COUNTIF_SHIFTED_PRED = "SELECT countIf({shifted}) FROM {t} WHERE {pred}"
_SQL_COUNT_MIXED = (
    "SELECT count() FROM {t} WHERE {pred} AND toDate(trade_time) IN "
    "(SELECT DISTINCT toDate(trade_time) FROM {t} WHERE {spred}) "
    "AND NOT ({shifted})"
)
_SQL_DISTINCT_DAYS = "SELECT DISTINCT toString(toDate(trade_time)) FROM {t} WHERE {mpred} AND {spred} ORDER BY 1"
_SQL_BACKUP_SPRED = "INSERT INTO {bak} ({col_list}) SELECT {col_list} FROM {t} WHERE {spred}"
_SQL_COUNT_BAK = "SELECT count() FROM {bak}"
_SQL_COUNT_T_SPRED = "SELECT count() FROM {t} WHERE {spred}"
_SQL_REINSERT = "INSERT INTO {t} ({col_list}) SELECT {sel_cols} FROM {bak} WHERE {bpred}"


def month_range(a: tuple[int, int], b: tuple[int, int]):
    y, m = a
    while (y, m) <= (b[0], b[1]):
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def next_month(y: int, m: int):
    return (y + 1, 1) if m == 12 else (y, m + 1)


def non_materialized_cols(cli: Client, table: str) -> list[str]:
    rows = cli.execute(f"DESCRIBE TABLE c1_market.{table}")
    return [r[0] for r in rows if r[2] not in ("MATERIALIZED", "ALIAS")]


def shifted_days_in_month(cli: Client, T: str, mpred: str, spred: str) -> list[str]:
    rows = cli.execute(_SQL_DISTINCT_DAYS.format(t=T, mpred=mpred, spred=spred))
    return [r[0] for r in rows]


def process_bucket(w, cli: Client, T: str, BAK: str, col_list: str, sel_cols: str,  # noqa: long-param-list  运维工具批处理签名，参数语义独立无法合并（retire: 治理批评估数据类打包）
                   bpred: str, spred: str, label: str, t0: float) -> None:
    """对单个桶（一个月或一天）执行 备份→删除→(唯一副本)回插→校验。"""
    total, shifted = cli.execute(_SQL_COUNT_SHIFTED_PRED.format(shifted=SHIFTED_PRED, t=T, pred=bpred))[0]
    normal = total - shifted
    # 桶内正常行数按「偏移天内」口径重算（月桶可能混有已修复日的正常行）
    if normal:
        normal = cli.execute(_SQL_COUNT_MIXED.format(
            t=T, pred=bpred, spred=spred, shifted=SHIFTED_PRED))[0][0]
    if shifted == 0:
        print(f"  {label} 无偏移，跳过")
        return
    mode = "唯一副本→删+回插" if normal == 0 else f"双写→只删(偏移天正常行={normal:,})"
    print(f"  {label} total={total:,} 偏移={shifted:,} {mode} ...")

    # 1) 备份偏移行（清掉旧备份内容，防上次残留）
    w.execute(f"ALTER TABLE {BAK} DELETE WHERE 1 SETTINGS mutations_sync=1")
    w.execute(_SQL_BACKUP_SPRED.format(bak=BAK, col_list=col_list, t=T, spred=spred))
    bak_n = cli.execute(_SQL_COUNT_BAK.format(bak=BAK))[0][0]
    if bak_n != shifted:
        raise SystemExit(f"  ✗ 备份行数 {bak_n:,} != 偏移行数 {shifted:,}，终止")
    # 2) 删除偏移行
    w.execute(f"ALTER TABLE {T} DELETE WHERE {spred} SETTINGS mutations_sync=2")
    left = cli.execute(_SQL_COUNT_T_SPRED.format(t=T, spred=spred))[0][0]
    if left:
        raise SystemExit(f"  ✗ 删除后残余 {left:,}，终止")
    # 3) 唯一副本桶才回插 +8h（双写桶正常行已覆盖，无需回插）
    if normal == 0:
        w.execute(_SQL_REINSERT.format(t=T, col_list=col_list, sel_cols=sel_cols, bak=BAK, bpred=bpred))
    # 4) 校验：桶总行数不变 + 残余偏移=0
    t2, s2 = cli.execute(_SQL_COUNT_SHIFTED_PRED.format(shifted=SHIFTED_PRED, t=T, pred=bpred))[0]
    if s2 != 0 or t2 != total:
        raise SystemExit(f"  ✗ 校验失败 total={t2:,}(应{total:,}) 残余偏移={s2:,}，终止")
    w.execute(f"ALTER TABLE {BAK} DELETE WHERE 1 SETTINGS mutations_sync=1")
    print(f"     ✓ 完成 {time.time()-t0:.0f}s")


def _parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=True, help="如 kline_1min / kline_5min")
    ap.add_argument("--start", required=True, help="含，YYYY-MM-DD")
    ap.add_argument("--end", required=True, help="含，YYYY-MM-DD")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--only-month", default=None, help="只处理某月 YYYYMM（断点续跑）")
    ap.add_argument("--bak-suffix", default="tzbak_20260914",
                    help="备份表后缀；对已有备份的表（如 kline_5min）用新后缀防误清旧备份")
    ap.add_argument("--by-day", action="store_true",
                    help="强制按天分桶（防大月单块 INSERT 撞 CH 内存上限，"
                         "2026-09-14 1min 2022-03 25M 行实测 Code 241）")
    a = ap.parse_args()
    if not (a.check or a.apply):
        ap.error("需指定 --check 或 --apply")
    if a.apply and not a.confirm:
        ap.error("--apply 必须同时给 --confirm（Owner 已批准的显式确认）")
    return a


def _run_check(a, cli, T, col_list, sel_cols, ya, ma, yb, mb) -> int:  # noqa: long-param-list  运维工具批处理签名，参数语义独立无法合并（retire: 治理批评估数据类打包）
    print(f"{'桶':12s} {'总行数':>14s} {'偏移':>14s} 处置")
    tot_shift = 0
    for (y, m) in month_range((ya, ma), (yb, mb)):
        if a.only_month and f"{y}{m:02d}" != a.only_month:
            continue
        ny, nm = next_month(y, m)
        MPRED = (f"trade_time >= toDateTime64('{y}-{m:02d}-01', 3, 'Asia/Shanghai') "
                 f"AND trade_time < toDateTime64('{ny}-{nm:02d}-01', 3, 'Asia/Shanghai')")
        SPRED = f"{MPRED} AND {SHIFTED_PRED}"
        total, shifted = cli.execute(_SQL_COUNT_SHIFTED_PRED.format(shifted=SHIFTED_PRED, t=T, pred=MPRED))[0]
        if shifted == 0:
            continue
        tot_shift += shifted
        # 混合月检测：偏移天内是否存在正常行
        mixed = cli.execute(_SQL_COUNT_MIXED.format(
            t=T, pred=MPRED, spred=SPRED, shifted=SHIFTED_PRED))[0][0]
        if mixed:
            days = shifted_days_in_month(cli, T, MPRED, SPRED)
            print(f"  {y}-{m:02d}(混合月, 按天)  {total:>14,} {shifted:>14,} "
                  f"偏移天={len(days)}: {','.join(days)}")
        else:
            print(f"  {y}-{m:02d}          {total:>14,} {shifted:>14,} 唯一副本→删+回插")
    print(f"[合计待修复偏移行] {tot_shift:,}")
    return 0


def _run_apply(a, cli, w, T, BAK, col_list, sel_cols, ya, ma, yb, mb) -> int:  # noqa: long-param-list  运维工具批处理签名，参数语义独立无法合并（retire: 治理批评估数据类打包）
    # ---- apply：逐桶 备份→删除→(唯一副本)回插→校验 ----
    w.execute(f"CREATE TABLE IF NOT EXISTS {BAK} AS {T}")
    for (y, m) in month_range((ya, ma), (yb, mb)):
        if a.only_month and f"{y}{m:02d}" != a.only_month:
            continue
        ny, nm = next_month(y, m)
        MPRED = (f"trade_time >= toDateTime64('{y}-{m:02d}-01', 3, 'Asia/Shanghai') "
                 f"AND trade_time < toDateTime64('{ny}-{nm:02d}-01', 3, 'Asia/Shanghai')")
        SPRED = f"{MPRED} AND {SHIFTED_PRED}"
        shifted = cli.execute(_SQL_COUNTIF_SHIFTED_PRED.format(shifted=SHIFTED_PRED, t=T, pred=MPRED))[0][0]
        if shifted == 0:
            print(f"  {y}-{m:02d} 无偏移，跳过")
            continue
        mixed = cli.execute(_SQL_COUNT_MIXED.format(
            t=T, pred=MPRED, spred=SPRED, shifted=SHIFTED_PRED))[0][0]
        if not mixed and not a.by_day:
            # 整月唯一副本：一个月桶一次搞定
            process_bucket(w, cli, T, BAK, col_list, sel_cols, MPRED, SPRED,
                           f"{y}-{m:02d}", time.time())
        else:
            # 混合月或 --by-day：按天分桶
            for d in shifted_days_in_month(cli, T, MPRED, SPRED):
                DPRED = (f"toDate(trade_time) = toDate('{d}')")
                DSPRED = f"{DPRED} AND {SHIFTED_PRED}"
                process_bucket(w, cli, T, BAK, col_list, sel_cols, DPRED, DSPRED,
                               d, time.time())
        # 月级总校验
        t3, s3 = cli.execute(_SQL_COUNT_SHIFTED_PRED.format(shifted=SHIFTED_PRED, t=T, pred=MPRED))[0]
        if s3 != 0:
            raise SystemExit(f"  ✗ 月级复验 {y}-{m:02d} 残余偏移={s3:,}，终止")
        print(f"     月级复验 {y}-{m:02d} total={t3:,} 残余偏移=0 ✓")
    print("[全部完成]")
    return 0


def main() -> int:
    a = _parse_args()
    from zephyr.infrastructure.database_service import get_db_service

    cli = get_db_service().get_clickhouse_conn(
        role="reader", extra_kwargs={"settings": {"max_execution_time": 7200}})
    w = chw.get_client()
    T = f"c1_market.{a.table}"
    BAK = f"c1_market.{a.table}_{a.bak_suffix}"
    cols = non_materialized_cols(cli, a.table)
    col_list = ", ".join(cols)
    sel_cols = ", ".join(
        "trade_time + INTERVAL 8 HOUR" if c == "trade_time" else c for c in cols)
    print(f"[表] {T}  备份表 {BAK}")
    print(f"[写入列] {col_list}")

    ya, ma = int(a.start[:4]), int(a.start[5:7])
    yb, mb = int(a.end[:4]), int(a.end[5:7])

    if a.check:
        return _run_check(a, cli, T, col_list, sel_cols, ya, ma, yb, mb)
    return _run_apply(a, cli, w, T, BAK, col_list, sel_cols, ya, ma, yb, mb)


if __name__ == "__main__":
    sys.exit(main())
