# [BLUEPRINT] MOD-CHAINPILE-METAQ | 工单 WO-B3 §簇3-3（历史回灌方案：存证字段建成、历史不可回补须如实登记）
# [MODULE] scripts.governance.meta_question.wo_b3_macro.register_macro_history_inventory
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.meta_question.wo_b3_macro.macro_vintage;
#                 zephyr.infrastructure.database_service (reader 取存量); zephyr.data.ch_writer (strict 写通道)
# [CONSUMERS] 手工运维一次性登记（幂等可重跑）；audit_macro_vintage.py 的 C3 零伪造判据依赖其产物
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 零伪造铁律：历史存量行一律 pub_ts=NULL + pub_ts_basis='backfill_final' + vintage=1，
#              pub_ref 记明"一次性回补终值，发布时戳不可回补"——绝不给回补值编造发布时戳；
#              纯增量幂等：NOT IN (vintage 表已有键) 过滤，重跑只补差、不造伪版次；
#              现值表 c1_market.macro_data 只读零触碰。
# [MODIFY-GUARD] none
# [STABILITY] new
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 词表缺 backfill_final->ValueError 拒跑；CH 写失败->记账非零退出；--dry-run 零写。
# [TESTS] python scripts/governance/meta_question/wo_b3_macro/register_macro_history_inventory.py --dry-run
# [A_module] module_id=MOD-CHAINPILE-METAQ | layer=script | stability=new | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""历史存量登记：把现值表已回补的宏观观测如实登记为 backfill_final（零伪造）。

用法::

    python .../register_macro_history_inventory.py --dry-run           # 只盘点不写
    python .../register_macro_history_inventory.py                   # 默认 fred,eia
    python .../register_macro_history_inventory.py --sources akshare,worldbank
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parents[3] / "src"))

import macro_vintage as mv  # noqa: E402

_BATCH = 5000

# NO-BARE-SQL：SQL 集中于此（§5.160.2）。mv.TABLE_VINTAGE 为模块常量、import 期解析，
# 落地 SQL 文本与原内联 f-string 逐字等值。
_SQL_TOTAL = f"SELECT count() FROM {mv.TABLE_VINTAGE}"
_SQL_BY_BASIS = (
    f"SELECT pub_ts_basis, count(), countIf(pub_ts IS NULL) FROM {mv.TABLE_VINTAGE} "
    "GROUP BY pub_ts_basis ORDER BY 2 DESC"
)


def _fetch(sql: str) -> list[tuple]:
    """只读取存量（经 DatabaseService reader，禁裸 duckdb/裸连接）。"""
    from zephyr.infrastructure.database_service import DatabaseService

    reader = DatabaseService().get_clickhouse_conn(role="reader")
    try:
        return list(reader.execute(sql))
    finally:
        reader.disconnect()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="宏观 vintage 历史存量登记（backfill_final）")
    parser.add_argument("--sources", default="fred,eia", help="按 data_source 选取存量（fred,eia,akshare,worldbank）")
    parser.add_argument("--dry-run", action="store_true", help="只统计不写入")
    args = parser.parse_args(argv)

    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    from zephyr.data import ch_writer
    from zephyr.shared.utils.time_utils import now_utc

    rows = mv.build_backfill_rows(_fetch(mv.inventory_sql(sources)), registered_at=now_utc())
    print(f"[inventory] 源={sources} 待登记={len(rows)} 行（其余为 vintage 表已有键，幂等跳过）")
    if args.dry_run or not rows:
        return 0
    written = mv.write_vintage_rows(rows)
    print(f"[write] 已写 {written}/{len(rows)} 行（批量上限 {_BATCH}）")

    reader = _reader_client()
    try:
        total = int(reader.execute(_SQL_TOTAL)[0][0])
        by_basis = reader.execute(_SQL_BY_BASIS)
    finally:
        reader.disconnect()
    print(f"[done] 写入 {written} 行；vintage 表现存 {total} 行；分档={by_basis}")
    problems = []
    for basis, cnt, null_cnt in by_basis:
        if basis == mv._BASIS_BACKFILL and null_cnt != cnt:  # noqa: SLF001 — 常量真源在 macro_vintage
            problems.append(f"backfill_final 档存在 {cnt - null_cnt} 行被赋 pub_ts（伪造历史）")
        if basis != mv._BASIS_BACKFILL and null_cnt:  # noqa: SLF001
            problems.append(f"{basis} 档存在 {null_cnt} 行缺 pub_ts")
    for msg in problems:
        print(f"[FAIL] {msg}")
    return 1 if problems else 0


def _reader_client():
    from zephyr.data import ch_writer

    return ch_writer.get_client_strict()


if __name__ == "__main__":
    raise SystemExit(main())
