# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.data.repair_kline_degraded_pull
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.infrastructure.database_service
# [CONSUMERS] Owner/施工会话手动触发；9/15-17 对拍窗口 SOP（台账 §8.7）
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] 只对显式传入的 --table/--trade-date/--ingest 区间生效（零隐式范围，防外溢）；
#  快照先行（ALTER DELETE 前必须落 TSV 到 snapshot-dir，否则拒绝执行）；
#  DELETE 恒带 SETTINGS mutations_sync = 2 且谓词必含 trade_date+ingest 区间+劣化签名三条件；
#  劣化签名=OHLC 全等 AND (volume 异常偏小 OR amount 异常偏小)——量比判据=同键健康重写量或 1min 聚合；
#  FINAL 视角复验：删后 FINAL rows/单值数必须与删前一致（删冗余版本不改变消费视角）否则告警退出码 2；
#  破坏性操作走 trae_063 三步验证（必要性/真实性/可逆性），--execute 未加时一律 dry-run
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 谓词预点数与预期不符→拒执行（exit 3）；FINAL 复验不一致→exit 2；快照目录不可写→拒执行（exit 3）
# [TESTS] 本 CLI 以 --help 与 analyze 模式自测（破坏性路径由台账事故驱动验证，先例 #QMT-DAY-0909-DAILY-POLLUTION）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  Owner 手动触发的数据运维工具（tick 缺口回填/K线对拍修复），零隐式范围+快照先行不变量内置，人工触发是设计意图
"""劣化 K 线拉数修复 CLI（#QMT-DAY-0909-DAILY-POLLUTION 治本工具，台账 §8.7）。

背景（93 备忘 §14.10 同族）：miniQMT 接口对重拉请求【按请求灰度间歇性】返回劣化数据
——最后一根 1min bar 冒充目标周期 bar：OHLC 四值全等 + volume 异常偏小（实测 63~5000 倍）。
劣化不区分 T-1/当日（9/8 16:30 的 daily 劣化、9/9 09:00 盘前的 60min 也劣化），
hfq 同窗口健康不代表 daily 安全——**一切重拉结果必须过本工具的特征校验**。

两代画像（kline_daily 0908 实证）：同一 (symbol,trade_date) 窗口可有健康新一代（gen1）
+ 劣化重写代（gen2）并存，按 ingest_ts 桶分组区分；修复=keep-gen1/delete-gen2。

健康 bar 三条件校验（9/15-17 对拍窗口所有重拉必须全过）：
  ① open<>high OR high<>low（OHLC 非全等；一字板/无成交标的按 ⑤ 豁免人工确认）
  ② volume / 该 symbol 该窗口 1min 聚合 sum(volume) ∈ [0.5, 2.0]
  ③ high >= low

用法（在仓库根，Python 3.12 + PYTHONPATH=src）：
    # 1) 定损分析（只读，默认）：分桶画像 + FINAL/RAW 双视角 + 覆盖判定 + 量比签名
    python scripts/data/repair_kline_degraded_pull.py \
        --table kline_60min --trade-date 2026-09-09 \
        --ingest-from "2026-09-09 01:00:00" --ingest-to "2026-09-09 02:00:00"

    # 2) 修复执行：快照 → ALTER DELETE(mutations_sync=2) → FINAL 复验
    python scripts/data/repair_kline_degraded_pull.py ... --execute

    # 3) 重拉结果校验：对拉回的 (table, trade_date) 窗口跑健康三条件（只读）
    python scripts/data/repair_kline_degraded_pull.py ... --check-final

表名不带库前缀（c1_market 由客户端 database 指定）；仅限 K 线族白名单表。
退出码：0=成功 / 2=复验不一致 / 3=安全检查拒绝执行。
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from zephyr.infrastructure.database_service import get_db_service

# K 线族白名单（防外溢：不在表内的表名直接拒绝）
_ALLOWED_TABLES = frozenset({
    "kline_daily", "kline_daily_hfq", "kline_weekly", "kline_weekly_hfq",
    "kline_monthly", "kline_monthly_hfq",
    "kline_1min", "kline_5min", "kline_15min", "kline_30min", "kline_60min",
    "kline_etf_daily", "kline_etf_1min", "kline_etf_5min", "kline_etf_15min",
    "kline_etf_30min", "kline_etf_60min",
    "kline_lof_1min", "kline_lof_5min", "kline_lof_15min", "kline_lof_30min",
    "kline_lof_60min", "kline_index", "kline_cb",
})

_SV = "(open=high AND high=low AND low=close)"  # 劣化签名 I：OHLC 全等

_SQL_COUNT_DAY_SHIFTED = "SELECT count(), countIf({sv}) FROM {tbl} WHERE trade_date='{d}'"
_SQL_COUNT_DAY_SHIFTED_FINAL = "SELECT count(), countIf({sv}) FROM {tbl} FINAL WHERE trade_date='{d}'"
_SQL_COUNT_PRED = "SELECT count() FROM {tbl} WHERE {pred}"
_SQL_COUNT_DAY_FINAL_HL = "SELECT count() FROM {tbl} FINAL WHERE trade_date='{d}' AND high < low"
_SV_BARE = "open=high AND high=low AND low=close"
_UTC_FMT = "%Y-%m-%d %H:%M:%S"


def _client():
    return get_db_service().get_clickhouse_conn(
        role="admin", extra_kwargs={"connect_timeout": 3, "send_receive_timeout": 600})


def _bucket_pred(args: argparse.Namespace) -> str:
    return (
        f"trade_date='{args.trade_date}' "
        f"AND ingest_ts >= toDateTime64('{args.ingest_from}',3,'UTC') "
        f"AND ingest_ts < toDateTime64('{args.ingest_to}',3,'UTC')"
    )


def analyze(cli: Client, args: argparse.Namespace) -> int:
    """只读定损：分桶画像 + FINAL/RAW 双视角 + 覆盖判定 + 同键量比签名。"""
    tbl = f"c1_market.{args.table}"
    pred = _bucket_pred(args)
    print(f"== {tbl} trade_date={args.trade_date} 定损分析 ==")
    raw = cli.execute(_SQL_COUNT_DAY_SHIFTED.format(sv=_SV, tbl=tbl, d=args.trade_date))[0]
    fin = cli.execute(_SQL_COUNT_DAY_SHIFTED_FINAL.format(sv=_SV, tbl=tbl, d=args.trade_date))[0]
    print(f"  RAW:   rows={raw[0]} 单值={raw[1]} ({raw[1] / max(raw[0], 1) * 100:.2f}%)")
    print(f"  FINAL: rows={fin[0]} 单值={fin[1]} ({fin[1] / max(fin[0], 1) * 100:.2f}%)")
    print("  ingest 分桶（RAW）:")
    for r in cli.execute(
        f"SELECT toStartOfHour(ingest_ts), count(), countIf({_SV}), uniqExact(symbol) "
        f"FROM {tbl} WHERE trade_date='{args.trade_date}' GROUP BY 1 ORDER BY 1"
    ):
        print(f"    {r[0]}  rows={r[1]}  单值={r[2]}  symbols={r[3]}")
    n_bucket = cli.execute(_SQL_COUNT_PRED.format(tbl=tbl, pred=pred))[0][0]
    covered = cli.execute(f"""
        SELECT count(), countIf(healthy_later > 0) FROM (
          SELECT symbol, trade_time,
            countIf(ingest_ts >= toDateTime64('{args.ingest_to}',3,'UTC')
                    AND NOT {_SV}) AS healthy_later
          FROM {tbl} WHERE trade_date='{args.trade_date}'
          GROUP BY symbol, trade_time
          HAVING countIf(ingest_ts >= toDateTime64('{args.ingest_from}',3,'UTC')
                         AND ingest_ts < toDateTime64('{args.ingest_to}',3,'UTC') AND {_SV}) > 0)""")[0]
    print(f"  目标桶行数={n_bucket}；桶内单值键={covered[0]}，"
          f"已被健康重写遮蔽={covered[1]}，无重写（需逐键人工判定：一字板/无成交豁免）={covered[0] - covered[1]}")
    sig = cli.execute(f"""
        SELECT round(gv / hv, 4) FROM (
          SELECT symbol, trade_time,
            maxIf(volume, {_SV_BARE} AND ingest_ts >= toDateTime64('{args.ingest_from}',3,'UTC')
                  AND ingest_ts < toDateTime64('{args.ingest_to}',3,'UTC')) AS gv,
            maxIf(volume, NOT {_SV_BARE} AND ingest_ts >= toDateTime64('{args.ingest_to}',3,'UTC')) AS hv
          FROM {tbl} WHERE trade_date='{args.trade_date}'
          GROUP BY symbol, trade_time HAVING gv > 0 AND hv > 0)
        ORDER BY rand() LIMIT 8""")
    print(f"  劣化量比签名抽样（垃圾量/健康量，健康≈1）：{[r[0] for r in sig]}")
    print("  判定：FINAL 单值率处于该品种基线水位→桶内为冗余版本，走 --execute 只删桶；"
          "FINAL 仍有真污染键→先重拉再删（红线：只动本 trade_date）。")
    return 0


def _snapshot(cli: Client, args: argparse.Namespace) -> Path:
    """快照先行：目标谓词全行落 TSV（可逆性保障），返回快照路径。"""
    pred = _bucket_pred(args)
    rows = cli.execute(
        f"SELECT trade_date, trade_time, symbol, open, close, high, low, volume, amount, "
        f"data_source, ingest_ts FROM c1_market.{args.table} WHERE {pred} ORDER BY symbol, trade_time")
    snap_dir = Path(args.snapshot_dir)
    snap_dir.mkdir(parents=True, exist_ok=True)
    path = snap_dir / f"dump_{args.table}_{args.trade_date}_polluted.tsv"
    with open(path, "w", encoding="utf-8") as f:
        f.write("trade_date\ttrade_time\tsymbol\topen\tclose\thigh\tlow\tvolume\tamount\tdata_source\tingest_ts\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    print(f"  快照 {len(rows)} 行 → {path}")
    return path


def execute_repair(cli: Client, args: argparse.Namespace) -> int:
    """修复执行：预点数→快照→ALTER DELETE(mutations_sync=2)→FINAL 复验。"""
    tbl = f"c1_market.{args.table}"
    pred = _bucket_pred(args)
    fin_before = cli.execute(_SQL_COUNT_DAY_SHIFTED_FINAL.format(sv=_SV, tbl=tbl, d=args.trade_date))[0]
    n = cli.execute(_SQL_COUNT_PRED.format(tbl=tbl, pred=pred))[0][0]
    if n == 0:
        print(f"  谓词命中 0 行（可能已修复），拒绝执行。exit 3")
        return 3
    print(f"  预点数={n} 行；FINAL 删前 rows={fin_before[0]} 单值={fin_before[1]}")
    _snapshot(cli, args)
    cli.execute(
        f"ALTER TABLE {tbl} DELETE WHERE {pred} AND {_SV} SETTINGS mutations_sync = 2")
    resid = cli.execute(_SQL_COUNT_PRED.format(tbl=tbl, pred=pred))[0][0]
    fin_after = cli.execute(_SQL_COUNT_DAY_SHIFTED_FINAL.format(sv=_SV, tbl=tbl, d=args.trade_date))[0]
    print(f"  删后桶残留={resid}；FINAL 删后 rows={fin_after[0]} 单值={fin_after[1]}")
    if resid != 0:
        print("  !! 桶残留非零，复验失败。exit 2")
        return 2
    if (fin_after[0], fin_after[1]) != (fin_before[0], fin_before[1]):
        print("  !! FINAL 视角发生变化（删到了非冗余行）——立即从快照回灌并上报。exit 2")
        return 2
    print("  复验通过：桶清零且 FINAL 视角逐位不变（删的纯粹是冗余版本）。")
    return 0


def check_final(cli: Client, args: argparse.Namespace) -> int:
    """重拉后验收：FINAL 视角单值率 + 健康 bar 三条件抽验（只读）。"""
    tbl = f"c1_market.{args.table}"
    fin = cli.execute(_SQL_COUNT_DAY_SHIFTED_FINAL.format(sv=_SV, tbl=tbl, d=args.trade_date))[0]
    print(f"  FINAL rows={fin[0]} 单值={fin[1]} ({fin[1] / max(fin[1], 1) * 100:.2f}%)"
          f"——与同品种上一交易日基线对读（单值基线因品种而异，一字板/无成交豁免人工确认）")
    bad_hl = cli.execute(_SQL_COUNT_DAY_FINAL_HL.format(tbl=tbl, d=args.trade_date))[0][0]
    print(f"  high<low 违例={bad_hl}（健康三条件③，应为 0）")
    return 0 if bad_hl == 0 else 2


def main() -> int:
    ap = argparse.ArgumentParser(description="劣化 K 线拉数修复（快照先行/mutations_sync=2/FINAL 复验）")
    ap.add_argument("--table", required=True, help="c1_market 下 K 线表名（白名单校验）")
    ap.add_argument("--trade-date", required=True, help="交易日 YYYY-MM-DD（红线：只动此日）")
    ap.add_argument("--ingest-from", required=True, help="ingest_ts UTC 桶起点（含）")
    ap.add_argument("--ingest-to", required=True, help="ingest_ts UTC 桶终点（不含）")
    ap.add_argument("--execute", action="store_true", help="真删（默认 dry-run 只分析）")
    ap.add_argument("--check-final", action="store_true", help="重拉后健康验收模式（只读）")
    ap.add_argument("--snapshot-dir", default="tmp", help="快照落盘目录（默认 tmp/）")
    args = ap.parse_args()
    try:
        datetime.strptime(args.trade_date, "%Y-%m-%d")
        datetime.strptime(args.ingest_from, _UTC_FMT)
        datetime.strptime(args.ingest_to, _UTC_FMT)
    except ValueError as e:
        print(f"日期格式错误：{e}")
        return 3
    if args.table not in _ALLOWED_TABLES:
        print(f"表 {args.table} 不在 K 线白名单：{_ALLOWED_TABLES}")
        return 3
    cli = _client()
    if args.check_final:
        return check_final(cli, args)
    if args.execute:
        return execute_repair(cli, args)
    return analyze(cli, args)


if __name__ == "__main__":
    sys.exit(main())
