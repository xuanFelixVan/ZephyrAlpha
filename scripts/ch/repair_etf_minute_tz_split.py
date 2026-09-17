# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.ch.repair_etf_minute_tz_split
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; clickhouse-driver(pip)
# [CONSUMERS] data_ops_sop 修复链（工单=docs/_working/flash_biz/biz5_etf15min_tz_defect.md）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 修复判据（2026-09-18 三步验证实证，st-flashbiz-20260918）：ETF 分钟族五表
#   （1/5/15/30/60min）trade_date<=2026-06-30 的行 trade_time 为 UTC 墙钟误标进
#   DateTime64(3,'Asia/Shanghai') 列（~4.12 亿行，95%+），2026-07-01 起为北京墙钟；
#   两纪元边界零违例、修复落点零碰撞、trade_date 本身已是北京日零错日（只有 trade_time 需 +8h）；
#   trade_time 在 ORDER BY 键内 → ALTER UPDATE 禁改 → 影子表重建+EXCHANGE 换名路径；
#   旧表整体改名为 *_tz_bak_20260918 保留（可逆性=改回换名即退）；默认 dry-run 零写入，
#   --execute 为 Owner 门位批准后的破坏性通道（RULE-DATA-OPS 三步验证已过，放行权在 Owner）。
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 前置核验不过->退出码2拒绝执行；CH 不可达->退出码3；修复后 hour<=7 未清零->退出码4
# [TESTS] python scripts/ch/repair_etf_minute_tz_split.py --dry-run（默认；零写入）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 一次性修复脚本（apply_timezone_migration 同族先例），Owner 门位批准后手动执行一次即归档，非永久自动系统
"""ETF 分钟族 trade_time 时区劈叉修复（kimi-audit T lane 发现，2026-09-18 Flash 包5 就绪件）。

缺陷（真实性已实证）：c1_market 五张 ETF 分钟表（kline_etf_1min/5min/15min/30min/60min）
2026-06-30 及以前的行，trade_time 以 UTC 墙钟写入（日内小时∈[1,7]），列类型却是
Asia/Shanghai——全表约 4.12 亿行受累；2026-07-01 起写入侧已是北京墙钟（∈[9,15]）。
两区间完全不重叠，日期边界零违例，+8h 平移后与现存北京段零碰撞（落点唯一）。

修复：逐表影子表重建（INSERT SELECT 带条件 +8h）→ 校验行数/量和对账 → EXCHANGE 换名
→ 旧表保留为 <表>_tz_bak_20260918（可逆=反向换名即退，物理删除另行 Owner 门位）。

用法：
    python scripts/ch/repair_etf_minute_tz_split.py             # dry-run（默认）：核数+计划，零写入
    python scripts/ch/repair_etf_minute_tz_split.py --execute   # Owner 批准后真修（破坏性）
    python scripts/ch/repair_etf_minute_tz_split.py --verify    # 修复后核验（hour<=7 应清零）
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone

TABLES = [
    "c1_market.kline_etf_1min",
    "c1_market.kline_etf_5min",
    "c1_market.kline_etf_15min",
    "c1_market.kline_etf_30min",
    "c1_market.kline_etf_60min",
]
CUTOFF = "2026-06-30"          # UTC 纪元止日（含）——07-01 起北京墙钟
BAK_SUFFIX = "_tz_bak_20260918"


def log(msg: str) -> None:
    print(f"[{datetime.now(tz=timezone.utc).isoformat(timespec='seconds')}] {msg}", flush=True)


def get_cli():
    from zephyr.data.ch_writer import get_client_strict

    return get_client_strict()


def _name(tbl: str) -> str:
    return tbl.split(".", 1)[1]


def precheck(cli, tbl: str) -> dict:
    """三步验证之真实性+可逆性前置：边界零违例/零碰撞/trade_date 不受累。"""
    q = lambda s: cli.execute(s)[0][0]  # noqa: E731
    total = q(f"SELECT count() FROM {tbl}")
    utc_rows = q(f"SELECT count() FROM {tbl} WHERE toHour(trade_time) <= 7")
    v_bound = q(f"SELECT count() FROM {tbl} WHERE toHour(trade_time) <= 7 AND toDate(trade_time) > '{CUTOFF}'") \
        + q(f"SELECT count() FROM {tbl} WHERE toHour(trade_time) BETWEEN 9 AND 15 AND toDate(trade_time) <= '{CUTOFF}'")
    v_date = q(f"SELECT count() FROM {tbl} WHERE toHour(trade_time) <= 7 AND trade_date != toDate(trade_time + INTERVAL 8 HOUR)")
    coll = q(f"""
      SELECT count() FROM (
        SELECT symbol, trade_time + INTERVAL 8 HOUR AS nt FROM {tbl} WHERE toHour(trade_time) <= 7
      ) t SEMI LEFT JOIN (
        SELECT symbol, trade_time FROM {tbl} WHERE toHour(trade_time) > 7
      ) e ON t.symbol = e.symbol AND t.nt = e.trade_time""")
    return {
        "table": tbl, "total": total, "utc_rows": utc_rows,
        "boundary_violations": v_bound, "trade_date_mismatch": v_date, "collisions_after_shift": coll,
        "ok": v_bound == 0 and v_date == 0 and coll == 0,
    }


def verify(cli, tbl: str) -> dict:
    q = lambda s: cli.execute(s)[0][0]  # noqa: E731
    return {"table": tbl, "remaining_utc_rows": q(f"SELECT count() FROM {tbl} WHERE toHour(trade_time) <= 7"),
            "beijing_rows": q(f"SELECT count() FROM {tbl} WHERE toHour(trade_time) BETWEEN 9 AND 15"),
            "total": q(f"SELECT count() FROM {tbl}")}


def repair_table(cli, tbl: str, dry_run: bool) -> dict:
    """影子表重建+EXCHANGE 换名（trade_time 在 ORDER BY 键，ALTER UPDATE 禁改）。"""
    name = _name(tbl)
    shadow = f"c1_market.{name}_tzfix"
    bak = f"c1_market.{name}{BAK_SUFFIX}"
    q = lambda s: cli.execute(s)  # noqa: E731
    ddl = q(f"SHOW CREATE TABLE {tbl}")[0][0]
    engine_clause = ddl[ddl.find("ENGINE"):]
    before_rows = q(f"SELECT count() FROM {tbl}")[0][0]
    before_vol = q(f"SELECT sum(volume) FROM {tbl}")[0][0]
    plan = {"table": tbl, "before_rows": before_rows, "shadow": shadow, "bak": bak}
    if dry_run:
        plan["action"] = "dry-run（零写入）"
        return plan
    t0 = time.time()
    q(f"DROP TABLE IF EXISTS {shadow}")
    # AS {tbl} 治本（2026-09-18 st-tdchain 实测 Code 80：本版 CH 要求列清单/AS 子句，
    # 纯 ENGINE 子句建表被拒）；非复制引擎无zk路径冲突，AS 复制列定义最稳。
    q(f"CREATE TABLE {shadow} AS {tbl} {engine_clause}")
    q(f"""
      INSERT INTO {shadow} SELECT * REPLACE (
        if(trade_date <= '{CUTOFF}', trade_time + INTERVAL 8 HOUR, trade_time) AS trade_time
      ) FROM {tbl}
    """)
    after_rows = q(f"SELECT count() FROM {shadow}")[0][0]
    # 抗折叠对账（2026-09-18 st-tdchain 实测治本）：ReplacingMergeTree 后台合并会折叠
    # 重复键行，绝对 count()/sum(volume) 在建表窗口内自然下漂（首轮五表全误报 ABORT，
    # Δ 与表大小成比例）；uniqExact 复合键聚合态又超服务器 6.9GiB 限额（二轮 Code 241）。
    # 终版=单查询同快照流式指纹：sum(cityHash64(全载荷)) O(1) 内存（UInt64 环绕对两侧
    # 同为确定性）+分桶计数平移守恒：影子 hour<=7 == 原表北京行数、影子 date<=CUTOFF
    # 且 hour∈[9,15] == 原表 UTC 误标行数。
    _FP_COLS = ("symbol, trade_time, trade_date, open, close, high, low, volume, amount, "
                "pct_change, amplitude, exchange, symbol_canonical")
    inv = q(f"""
      SELECT
        (SELECT sum(cityHash64({_FP_COLS})) FROM {shadow}),
        (SELECT sum(cityHash64({_FP_COLS})) FROM {tbl}),
        (SELECT count() FROM {shadow} WHERE toHour(trade_time) <= 7),
        (SELECT count() FROM {tbl} WHERE toHour(trade_time) > 7),
        (SELECT count() FROM {shadow} WHERE toHour(trade_time) BETWEEN 9 AND 15 AND toDate(trade_time) <= '{CUTOFF}'),
        (SELECT count() FROM {tbl} WHERE toHour(trade_time) <= 7)
    """)[0]
    sh_fp, src_fp, sh_low, src_gt7, sh_shifted, src_low = [int(x) for x in inv]
    if sh_fp != src_fp or sh_low != src_gt7 or sh_shifted != src_low:
        plan.update({"action": "ABORTED（折叠不变量对账不平，影子表保留待查）",
                     "after_rows": after_rows,
                     "sh_fp": str(sh_fp), "src_fp": str(src_fp),
                     "sh_low": sh_low, "src_gt7": src_gt7,
                     "sh_shifted": sh_shifted, "src_low": src_low})
        return plan
    q(f"DROP TABLE IF EXISTS {bak}")
    q(f"RENAME TABLE {tbl} TO {bak}, {shadow} TO {tbl}")  # 顺序换名（同库原子段小窗）
    post = verify(cli, tbl)
    plan.update({"action": "done", "after_rows": after_rows,
                 "remaining_utc_rows": post["remaining_utc_rows"],
                 "elapsed_s": round(time.time() - t0, 1)})
    return plan


def main() -> int:
    ap = argparse.ArgumentParser(description="ETF 分钟族 trade_time 时区劈叉修复（默认 dry-run）")
    ap.add_argument("--execute", action="store_true", help="Owner 批准后真修（破坏性；旧表保留 *_tz_bak_20260918）")
    ap.add_argument("--verify", action="store_true", help="修复后核验：hour<=7 应清零")
    ap.add_argument("--tables", nargs="*", default=TABLES, help="默认五张 ETF 分钟表")
    args = ap.parse_args()

    cli = get_cli()
    report = {"mode": "verify" if args.verify else ("execute" if args.execute else "dry-run"),
              "cutoff": CUTOFF, "bak_suffix": BAK_SUFFIX, "tables": []}
    if args.verify:
        for tbl in args.tables:
            r = verify(cli, tbl)
            report["tables"].append(r)
            log(f"{tbl}: remaining_utc={r['remaining_utc_rows']} beijing={r['beijing_rows']} total={r['total']}")
            if r["remaining_utc_rows"] != 0:
                report["ok"] = False
        report["ok"] = report.get("ok", True)
        print(json.dumps(report, ensure_ascii=False, indent=1))
        return 0 if report["ok"] else 4

    for tbl in args.tables:
        pc = precheck(cli, tbl)
        report["tables"].append(pc)
        log(f"precheck {tbl}: total={pc['total']} utc={pc['utc_rows']} "
            f"边界违例={pc['boundary_violations']} 错日={pc['trade_date_mismatch']} 碰撞={pc['collisions_after_shift']}")
        if not pc["ok"]:
            report["ok"] = False
            log(f"REFUSED {tbl}: 前置核验不过——修复判据不成立，拒绝执行")
            continue
        if args.execute:
            r = repair_table(cli, tbl, dry_run=False)
            report["tables"].append(r)
            log(f"repair {tbl}: {r.get('action')} rows={r.get('after_rows')} remaining_utc={r.get('remaining_utc_rows')}")
            if r.get("action") != "done" or r.get("remaining_utc_rows") != 0:
                report["ok"] = False
        else:
            log(f"{tbl}: dry-run 计划=影子表重建+EXCHANGE 换名（零写入）")
    print(json.dumps(report, ensure_ascii=False, indent=1, default=str))
    if report.get("ok") is False:
        return 2
    if not args.execute:
        log("dry-run 完成：零写入。--execute 需 Owner 门位批准（RULE-DATA-OPS 破坏性操作）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
