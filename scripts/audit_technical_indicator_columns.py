# [BLUEPRINT] MOD-L02-031 | docs/_working/data_fix_campaign §批10 验收台账
# [MODULE] data_fix_campaign.audit_technical_indicator_columns
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader
# [CONSUMERS] 总包甲·数据正确性线（210 列验收核销）；夜跑后人工核销
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] summary 模式=单次聚合扫描（一次全表读）；盘中禁跑 summary（153GiB 重读+内存总闸，仅限低峰窗且避开 02:30 夜跑带）；sample 模式轻查询盘中可用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 不可达→exit 2；列探针为空→exit 1
# [TESTS] 无（只读探针，验收人工核销）
# [A_module] module_id=MOD-L02-031 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""technical_indicator 全列非空审计台账（audit_all_cols.py 批10 复刻+台账化）。

用法：
  # 单列抽验（轻查询，盘中可用）：
  python scripts/data/audit_technical_indicator_columns.py --mode sample \\
      --columns chips_winner,scr,cyc_inf --symbols 000852,000001 --since 2026-08-05

  # 全 210 列台账（全表聚合扫描，重读——仅限收盘后低峰窗，避开 02:30 夜跑带，
  # 跑前把 "audit_technical_indicator_columns" 追加进 data/runtime/process_reaper_keep.txt）：
  python scripts/data/audit_technical_indicator_columns.py --mode summary --period daily \\
      --out .runtime/tmp/st-data-fix-20260921/audit_ledger_daily.tsv

台账列：column, non_null, total, null_pct（0 列=回填缺口，验收判据=210 列全>0，除 chips 族按 daily 覆盖口径）。
"""

from __future__ import annotations

import argparse
import csv
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, _REPO)
sys.path.insert(1, os.path.join(_REPO, "src"))

from zephyr.data import ch_reader  # noqa: E402
from zephyr.data.table_registry import get_registry  # noqa: E402

TABLE = get_registry().table("market_technical_indicator")

# SQL 集中化（§5.160.2）：模板为模块级常量，仅命名槽位运行时填充
_SQL_SUMMARY = "SELECT count() AS __total__, {metrics_expr} FROM {table} WHERE {where} FORMAT TSVWithNames"
_SQL_SAMPLE = (
    "SELECT symbol, trade_date, {cols} FROM {table} WHERE {where} ORDER BY symbol, trade_date FORMAT TSVWithNames"
)


# 210 列真源=schemas INSERT_COLUMNS（动态取，不手抄静态清单——静态清单禁手工维护铁律）
def indicator_columns() -> list[str]:
    from schemas.categories.market.market_technical_indicator import INSERT_COLUMNS

    return [c.strip() for c in INSERT_COLUMNS.strip("()").split(",") if c.strip()]


def mode_summary(args) -> int:
    cols = indicator_columns()
    metrics = []
    for c in cols:
        if c in ("trade_date", "trade_time", "symbol", "period", "data_source"):
            continue
        metrics.append(f"countIf({c} IS NOT NULL) AS `{c}`")
    where = f"period = '{args.period}'"
    if args.since:
        where += f" AND trade_date >= '{args.since}'"
    sql = _SQL_SUMMARY.format(metrics_expr=", ".join(metrics), table=TABLE, where=where)
    tsv = ch_reader.query(sql, timeout=args.timeout)
    lines = [ln for ln in (tsv or "").splitlines() if ln.strip()]
    if len(lines) < 2:
        print("探针为空（表空或查询失败）")
        return 1
    header = lines[0].split("\t")
    values = lines[1].split("\t")
    row = dict(zip(header, values, strict=False))
    total = int(row["__total__"])
    ledger = []
    zero_cols = []
    for c in cols:
        if c not in row:
            continue
        non_null = int(row[c])
        null_pct = 100.0 * (total - non_null) / total if total else 100.0
        ledger.append((c, non_null, total, round(null_pct, 4)))
        if non_null == 0:
            zero_cols.append(c)
    out = args.out or os.path.join(_REPO, ".runtime", "tmp", "audit_ledger.tsv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["column", "non_null", "total", "null_pct"])
        w.writerows(ledger)
    print(f"total rows={total}  columns={len(ledger)}  ledger={out}")
    print(f"zero (全空) 列 {len(zero_cols)} 个: {zero_cols if zero_cols else '无——验收判据达标'}")
    return 0 if not zero_cols else 1


def mode_sample(args) -> int:
    cols = [c.strip() for c in args.columns.split(",") if c.strip()]
    symbols = [s.strip() for s in (args.symbols or "").split(",") if s.strip()]
    where = [f"period = '{args.period}'"]
    if symbols:
        where.append("symbol IN (" + ",".join(f"'{s}'" for s in symbols) + ")")
    if args.since:
        where.append(f"trade_date >= '{args.since}'")
    sql = _SQL_SAMPLE.format(cols=", ".join(cols), table=TABLE, where=" AND ".join(where))
    print(ch_reader.query(sql))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="technical_indicator 全列非空审计台账")
    ap.add_argument("--mode", choices=["summary", "sample"], default="sample")
    ap.add_argument("--period", default="daily")
    ap.add_argument("--columns", default="chips_winner,scr,cyc_inf")
    ap.add_argument("--symbols", default="000852,000001")
    ap.add_argument("--since", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--timeout", type=int, default=1800, help="summary 全表扫描超时秒数")
    args = ap.parse_args()
    return mode_summary(args) if args.mode == "summary" else mode_sample(args)


if __name__ == "__main__":
    sys.exit(main())
