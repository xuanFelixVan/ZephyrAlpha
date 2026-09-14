#!/usr/bin/env python
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §4
# [MODULE] scripts.ch.build_consensus_daily
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.implementations.consensus_daily_compute
# [CONSUMERS] (回补/重建 CLI；C2 起消费方=factor/expectations 预期因子族)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 纯函数核委托 consensus_daily_compute（PIT 语义见该模块 INVARIANTS）；
#              写入经 ch_writer.write_result（FetchResult 批）；
#              ReplacingMergeTree(ingest_ts) 同键重建幂等
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] research_report/交易日历不可达→exit 1；ClickHouse 写入失败→exit 2；--check 交叉验证不一致→exit 1
# [TESTS] tests/scripts/test_build_consensus_daily.py（纯函数核，经本壳转出）+ 本脚本 --check（实库 PIT 交叉验证）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 手动构建/重建/验收 CLI（A 类一次性运维；
#                                   常态夜间重建走 internal provider（tasks.yaml consensus_daily_build），不经本 CLI
"""build_consensus_daily.py — 一致预期每日快照构建器（消费端 C1，2026-09-12）。

把 c3_fundamental.research_report（研报事件流，14.6 万行）聚合为
c3_fundamental.consensus_daily（每股每日×预测目标日历年的一致预期矩阵）——
华泰金工一致预期因子族（EXP-01~06）的标准输入。
计算核真源=zephyr.data.implementations.consensus_daily_compute（本壳仅 CLI 转发）。
设计真源：docs/01_policies_and_standards/policies/expectation_consumption_design_policy.md §M1。

用法::

    python scripts/ch/build_consensus_daily.py                    # 全量（研报最早 publish_date~今天）
    python scripts/ch/build_consensus_daily.py --start 2026-08-01 # 区间重建
    python scripts/ch/build_consensus_daily.py --check            # 实库 PIT 交叉验证（SQL 重算 vs 表内值）
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))  # schemas.categories.* 在项目根

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# 纯函数核转出（tests/scripts/test_build_consensus_daily.py 经本壳按名导入）
from zephyr.data.implementations.consensus_daily_compute import (  # noqa: E402
    build_consensus_rows,
    expand_report_slots,
    load_reports,
    load_trade_dates,
    rating_score,
    run_check,
    run_compute,
)


def run_build(args: argparse.Namespace) -> int:
    from zephyr.data import ch_writer

    phase = "read"
    try:
        result_iter = run_compute(
            symbols=args.symbols.split(",") if args.symbols else None,
            start=args.start,
            end=args.end,
            window_days=args.window,
            batch_size=args.batch_size,
        )
        n_written = 0
        t0 = time.time()
        for fr in result_iter:
            phase = "write"
            if not ch_writer.write_result(fr):
                log.error("ClickHouse 写入失败（%d 行）", len(fr.rows))
                return 2
            n_written += len(fr.rows)
            phase = "read"
        if n_written == 0:
            log.warning("0 行写入（区间无新快照或无交易日）")
        else:
            log.info("写入完成：%d 行（耗时 %.1f 秒）", n_written, time.time() - t0)
    except RuntimeError as exc:  # run_compute 源侧归一（研报/日历不可达、空库拒绝）
        log.error("%s", exc)
        return 1
    except Exception as exc:  # noqa: BLE001
        log.error("%s 阶段异常: %s", phase, exc)
        return 1 if phase == "read" else 2
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="一致预期每日快照构建（c3_fundamental.consensus_daily）")
    parser.add_argument("--start", default=None, help="快照区间起（默认=研报最早 publish_date，全量）")
    parser.add_argument("--end", default=None, help="快照区间止（默认=今天）")
    parser.add_argument("--window", type=int, default=90, help="窗宽自然日（默认 90）")
    parser.add_argument("--symbols", default=None, help="逗号分隔标的子集（调试用）")
    parser.add_argument("--batch-size", type=int, default=100000)
    parser.add_argument("--check", action="store_true", help="验收模式：行数+PIT 交叉验证")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    try:
        sys.exit(run_check() if args.check else run_build(args))
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 — 致命错误落盘（无头运行 stdout 可能不可见）
        err_file = ROOT / ".runtime" / "tmp" / "build_consensus_daily_error.txt"
        err_file.parent.mkdir(parents=True, exist_ok=True)
        err_file.write_text(traceback.format_exc(), encoding="utf-8")
        log.error("未处理异常，详情见 %s", err_file)
        sys.exit(1)


if __name__ == "__main__":
    main()
