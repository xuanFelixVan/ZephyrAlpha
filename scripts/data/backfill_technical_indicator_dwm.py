# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/blueprint.md
# [MODULE] scripts.data.backfill_technical_indicator_dwm
# [DOMAIN] D_DATA
# [A_module] module_id=scripts-data-ti-dwm-backfill | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [DEPENDENCIES] zephyr.data.buffered_writer; zephyr.data.implementations.internal_compute_provider; zephyr.data.provider_base
# [CONSUMERS] tilib_indicator_backfill_nightly（02:30 经 backfill_night.ps1→tilib_dwm_shard_runner 分片调用）；Owner/施工会话手动补数
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] 单进程串行分片（并发=内存总闸 Code 241）；ReplacingMergeTree 同键 (symbol,period,trade_time) 覆盖幂等可重跑；BufferedWriter 批量写（max_seconds=30）；dry-run 不落库
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FetchResult.error 或 BufferedWriter.add/flush 失败即 RuntimeError 非零退出；单片失败不污染其他分片（子进程隔离）
# [TESTS] 本 CLI 以 --help 与 --dry-run 自测；指标正确性由 tests/zephyr/factor/technical_indicators/ 全套件守卫
# noqa: m11-perm-manual-legitimate  tilib_indicator_backfill_nightly 02:30 夜跑分片子进程自动调用（backfill_night.ps1→runner 链），兼手动补数运维件，人工触发是设计意图非缺陷
"""日/周/月技术指标历史回填器（16 号设计文档 §7⑥，2026-09-14 探针发现）。

背景：
    c1_market.technical_indicator 的 daily/weekly/monthly 数据起点=2026-08（调度闭环日），
    仅 ~1 个月历史；而 30/60/120min 有 5 年。根因=scheduler._compute_start_date 对
    incremental=False 任务返回"当月 1 号"——technical_indicator_full_refresh 实为月初校准，
    无历史回填能力。本脚本走生产 provider→BufferedWriter 同链路补齐。

范围裁定（本脚本默认值）：
    daily   2021-01-01 起（表合同 valid_since=2021-09-01，预留 MA60/bias_24 等预热跑道）
    weekly  2019-01-01 起（kline_weekly 源下界）
    monthly 2019-01-01 起（kline_monthly 源下界）

幂等性：ReplacingMergeTree 同键 (symbol, period, trade_time) 覆盖式更新，可安全重跑。

用法：
    python scripts/data/backfill_technical_indicator_dwm.py                # 三周期默认范围
    python scripts/data/backfill_technical_indicator_dwm.py --periods daily --dry-run
    python scripts/data/backfill_technical_indicator_dwm.py --start-daily 2020-01-01

运维红线：
    长批任务先登记 data/runtime/process_reaper_keep.txt（子串 backfill_technical_indicator_dwm）。
"""

from __future__ import annotations

import argparse
import datetime
import logging
import sys
import time
from pathlib import Path

# provider 懒加载 schemas.categories.*（DDL-as-Code 真源），需 repo root 在 sys.path
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from zephyr.data.buffered_writer import BufferedWriter
from zephyr.data.implementations.internal_compute_provider import InternalComputeProvider
from zephyr.data.provider_base import FetchPayload

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ti-dwm-backfill")

from zephyr.data.table_registry import get_registry

TABLE = get_registry().table("market_technical_indicator")
_DEFAULT_STARTS = {
    "daily": "2021-01-01",
    "weekly": "2019-01-01",
    "monthly": "2019-01-01",
}


def backfill_period(
    provider: InternalComputeProvider,
    period: str,
    start: str,
    end: str,
    dry_run: bool,
    skip_batches: int = 0,
    symbols_file: str | None = None,
) -> int:
    """单周期回填：provider.fetch → BufferedWriter 批量写入。返回总行数。

    skip_batches: 跳过本周期前 N 批（断点续跑）。标的清单与 provider 同源
    （_get_symbols，ORDER BY symbol 序稳定），在生成器消费**前**切片——
    被跳过的标的完全不计算（旧版生成器消费后丢弃=白算 30 分钟实证）。
    ReplacingMergeTree 幂等，边界重叠无害。
    symbols_file: 显式标的清单文件（一行一个），优先级高于 skip_batches。
    """
    payload = FetchPayload(
        table=TABLE,
        symbols=None,  # None → provider 自查 kline_{period} DISTINCT 标的
        start=datetime.date.fromisoformat(start),
        end=datetime.date.fromisoformat(end),
        incremental=False,
        extra={"period": period, "capability": "technical_indicator"},
    )
    if symbols_file:
        payload.symbols = [
            s.strip()
            for s in Path(symbols_file).read_text(encoding="utf-8").splitlines()
            if s.strip()
        ]
        log.info("[%s] 使用标的清单 %d 个（%s）", period, len(payload.symbols), symbols_file)
    elif skip_batches > 0:
        all_symbols = provider._get_symbols(payload, period)
        cut = skip_batches * 100
        payload.symbols = list(all_symbols[cut:])
        log.info(
            "[%s] 断点续跑：跳过前 %d 批（%d 标的不计算），剩余 %d 个",
            period, skip_batches, min(cut, len(all_symbols)), len(payload.symbols),
        )
    writer = BufferedWriter(TABLE, max_seconds=30)
    total_rows = 0
    batch_idx = 0
    t0 = time.monotonic()
    log.info(
        "[%s] 回填开始 %s ~ %s（dry_run=%s，skip_batches=%d）",
        period, start, end, dry_run, skip_batches,
    )
    for result in provider.fetch(payload, None):
        if result.error:
            log.error("[%s] FetchResult.error: %s", period, result.error)
            raise RuntimeError(f"[{period}] {result.error}")
        batch_idx += 1
        if not result.rows:
            continue
        total_rows += len(result.rows)
        if not dry_run:
            if not writer.add(result):
                raise RuntimeError(f"[{period}] BufferedWriter.add 失败")
        if total_rows % 100_000 < len(result.rows):
            log.info("[%s] 累计 %d 行，耗时 %.0fs", period, total_rows, time.monotonic() - t0)
    if not dry_run:
        if not writer.flush():
            raise RuntimeError(f"[{period}] BufferedWriter.flush 失败")
    log.info("[%s] 回填完成：%d 行，耗时 %.0fs", period, total_rows, time.monotonic() - t0)
    return total_rows


def main() -> int:
    ap = argparse.ArgumentParser(description="日/周/月技术指标历史回填（16号 §7⑥）")
    ap.add_argument("--periods", default="daily,weekly,monthly", help="逗号分隔周期（默认三周期）")
    ap.add_argument("--start-daily", default=_DEFAULT_STARTS["daily"])
    ap.add_argument("--start-weekly", default=_DEFAULT_STARTS["weekly"])
    ap.add_argument("--start-monthly", default=_DEFAULT_STARTS["monthly"])
    ap.add_argument("--end", default=datetime.date.today().isoformat())
    ap.add_argument(
        "--skip-daily-batches",
        type=int,
        default=0,
        help="daily 周期跳过前 N 批（断点续跑；与 provider 同源标的清单切片，被跳标的完全不计算）",
    )
    ap.add_argument(
        "--symbols-file",
        default=None,
        help="显式标的清单文件（一行一个 symbol），优先级高于 --skip-daily-batches",
    )
    ap.add_argument("--dry-run", action="store_true", help="只计算不写库")
    args = ap.parse_args()

    starts = {
        "daily": args.start_daily,
        "weekly": args.start_weekly,
        "monthly": args.start_monthly,
    }
    periods = [p.strip() for p in args.periods.split(",") if p.strip()]
    for p in periods:
        if p not in starts:
            ap.error(f"不支持周期: {p}（仅 daily/weekly/monthly）")

    provider = InternalComputeProvider()
    grand = 0
    for p in periods:
        skip = args.skip_daily_batches if p == "daily" else 0
        grand += backfill_period(
            provider, p, starts[p], args.end, args.dry_run,
            skip_batches=skip, symbols_file=args.symbols_file,
        )
    log.info("全部完成：%d 周期共 %d 行（幂等可重跑）", len(periods), grand)
    return 0


if __name__ == "__main__":
    sys.exit(main())
