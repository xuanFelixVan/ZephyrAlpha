# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.backfill_auction_snapshot_history
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.implementations.ch_auction_derive
# [CONSUMERS] 运维一次性（2026-09-17 收盘后窗口施工单 §6，挖矿文档 §8.4 裁决点⑥ 档1）
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] 只灌空窗日（day_has_auction_rows 闸，已有行=跳过，禁覆盖 miniqmt 原产精确值）；
#              INSERT-only 零 DELETE（ReplacingMergeTree 幂等）；源=tick_data 1 档（2026-06 起有
#              竞价窗口，market_type 滤股防指数混线）；密集日阈值默认 1 万行（低于此=当日链路
#              迟启/残缺，回补价值低且可能只含半窗口，宁缺毋滥）；本脚本落库即台账（--dry-run
#              先行，实弹输出直接粘贴迁移台账 §2.2-B 勾选项证据）
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单日失败继续下一日，末尾汇总失败清单非零退出码
# [TESTS] 手动运维脚本（--dry-run 验证）；核心派生逻辑测试在 tests/zephyr/data/test_ch_auction_derive.py
# [TTL] task_bound
"""竞价快照历史回补（tick_data → auction_snapshot 空窗日，INSERT-only）。

背景（docs/_working/auction_bridge_switch_mining_2026_09_17.md §8.1/§8.4）：
auction_snapshot 原 miniqmt 通道 2026-08-12 起才有数据；自有 tick 库 2026-06 起
的"采集链 09:15 前活着"密集日含完整竞价窗口（9:15-9:25，终态撮合价/量/额），
可派生回灌空窗日。9/15 及 7/8 月缺采日永久缺失（任何渠道不可回），不在此列。

用法：
  python scripts/backfill_auction_snapshot_history.py --dry-run
  python scripts/backfill_auction_snapshot_history.py            # 实弹
  python scripts/backfill_auction_snapshot_history.py --start 2026-06-01 --end 2026-09-17 --min-rows 10000
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from zephyr.data.ch_writer import get_client  # noqa: E402
from zephyr.data.implementations.ch_auction_derive import (  # noqa: E402
    day_has_auction_rows,
    derive_auction_snapshot,
)
from zephyr.data.table_registry import get_registry  # noqa: E402

_TBL_SNAPSHOT = get_registry().table("market_auction_snapshot")
_SRC_TICK = get_registry().table("market_tick")

# 与 ch_auction_derive 同窗口口径
_W_START, _W_END = "09:15:00", "09:26:00"
_STOCK_TYPES = ("stock", "stock_bj")


# 密集日枚举（count 走常量，NO-BARE-SQL 同口径；窗口口径与 ch_auction_derive 一致）
SQL_DENSE_DAYS = (
    "SELECT trade_date, count() FROM {src} "
    "WHERE trade_date BETWEEN '{start}' AND '{end}' "
    "AND market_type IN ('stock', 'stock_bj') "
    "AND toHour(timestamp) = 9 AND toMinute(timestamp) BETWEEN 15 AND 25 "
    "GROUP BY trade_date ORDER BY trade_date"
)


def dense_days(client, start: str, end: str, min_rows: int) -> list[tuple[str, int]]:
    """枚举 [start,end] 内竞价窗口密集日（tick_data 全表窗口扫，一次性成本）。"""
    rows = client.execute(SQL_DENSE_DAYS.format(src=_SRC_TICK, start=start, end=end))
    out = []
    for d, n in rows:
        if int(n) >= min_rows:
            out.append((d.isoformat() if hasattr(d, "isoformat") else str(d), int(n)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="竞价快照历史回补（空窗日 INSERT-only）")
    ap.add_argument("--start", default="2026-06-01")
    ap.add_argument("--end", default="2026-09-17")
    ap.add_argument("--min-rows", type=int, default=10000)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    client = get_client()
    candidates = dense_days(client, args.start, args.end, args.min_rows)
    print(f"候选密集日（窗口行数>={args.min_rows}）: {len(candidates)} 天")

    done, skipped_existing, skipped_empty_src, failures = [], [], [], []
    for d, src_rows in candidates:
        if day_has_auction_rows(client, _TBL_SNAPSHOT, d):
            skipped_existing.append((d, src_rows))
            continue
        if args.dry_run:
            done.append((d, src_rows, "(dry-run)"))
            continue
        try:
            n = derive_auction_snapshot(d, client=client, src_table=_SRC_TICK)
            done.append((d, src_rows, n))
            print(f"  [OK] {d} src={src_rows} -> snapshot={n}")
        except Exception as e:  # noqa: BLE001 — 单日失败不阻塞批次
            failures.append((d, str(e)[:120]))
            print(f"  [FAIL] {d}: {e}")

    print("\n===== 回补汇总（粘贴台账证据） =====")
    print(f"窗口: [{args.start} ~ {args.end}] min_rows={args.min_rows} dry_run={args.dry_run}")
    print(f"回补成功: {len(done)} 天")
    for d, s, n in done:
        print(f"  {d}  src_rows={s}  snapshot_rows={n}")
    print(f"跳过（已有数据，防覆盖原产）: {len(skipped_existing)} 天 -> {[d for d, _ in skipped_existing]}")
    print(f"失败: {len(failures)} -> {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
