#!/usr/bin/env python
# [BLUEPRINT] MOD-REGIME-001
# [MODULE] scripts.ch.build_anchored_state_history
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.buffered_writer; zephyr.regime.core.anchored_state_machine
# [CONSUMERS] (历史构建/验收 CLI；产物=c1_backtest.regime_state_anchored，validate_p0_discrimination --prob-table 消费)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 纯函数核委托 anchored_state_machine（锚定语义见其 INVARIANTS）；
#              写入走 BufferedWriter（CH-BATCH-SIZE）；写入后 SELECT 计数复核
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 行情不可达->exit 1；写入失败->exit 2；--check 抽查不一致->exit 1
# [TESTS] tests/zephyr/regime/test_anchored_state_machine.py（纯函数核）+ 本脚本 --check
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 历史构建/验收 CLI（A 类一次性运维；态判定为纯规则无拟合，
#                                   结构变化=全量重算幂等，常态无需排班
"""build_anchored_state_history.py — 锚定态历史构建器（P0-002 重印批，裁定#229）。

把 000300 收盘价经特征锚定四态状态机（零拟合）重建为
c1_backtest.regime_state_anchored，供 validate_p0_discrimination.py
--prob-table 冻结验收消费。

用法::

    python scripts/ch/build_anchored_state_history.py            # 全量重算（幂等）
    python scripts/ch/build_anchored_state_history.py --check    # 占用+抽查交叉验证
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def run_build() -> int:
    from zephyr.data import ch_reader
    from zephyr.data.buffered_writer import BufferedWriter
    from zephyr.regime.core.anchored_state_machine import run_compute

    t0 = time.time()
    writer = BufferedWriter("c1_backtest.regime_state_anchored")
    n_written = 0
    try:
        for result in run_compute():
            if not writer.add(result):
                raise RuntimeError(f"BufferedWriter 写入失败（批 {len(result.rows)} 行）")
            n_written += len(result.rows)
        if not writer.flush():
            raise RuntimeError("BufferedWriter 末批 flush 失败")
    except RuntimeError as exc:
        log.error("%s", exc)
        return 2 if "写入失败" in str(exc) else 1
    n_written = writer.total_flushed

    tsv = ch_reader.query("SELECT count() FROM c1_backtest.regime_state_anchored FINAL")
    n_table = int(tsv.strip()) if tsv and tsv.strip() else 0
    log.info("表内计数复核：%d 行（本批写入 %d，耗时 %.1f 秒）", n_table, n_written, time.time() - t0)
    if n_table < n_written:
        log.error("表内计数 < 写入计数——写入链路异常，人工核查")
        return 2
    # 幂等重建后合并历史版本（ReplacingMergeTree 后台 merge 时机不定，判定器查询
    # 无 FINAL 会读到新旧两版态——主动收敛；base 账号直连同 apply 脚本先例）
    try:
        from clickhouse_driver import Client

        from zephyr.data.ch_config import load_ch_config

        cfg = load_ch_config()
        c = Client(host=cfg["host"], port=int(cfg.get("port", 9000)), user=cfg["user"],
                   password=cfg.get("password", ""), connect_timeout=5)
        c.execute("OPTIMIZE TABLE c1_backtest.regime_state_anchored FINAL")
        log.info("OPTIMIZE FINAL 完成（历史版本收敛）")
    except Exception as exc:  # noqa: BLE001 — 合并失败不阻断（consumer 侧 FINAL 兜底）
        log.warning("OPTIMIZE FINAL 失败（consumer 侧 FINAL 兜底）: %s", exc)
    return 0


def run_check() -> int:
    """验收：四态占用健康（无死态）+ 随机抽 3 日用表内特征重算态交叉验证。"""
    from zephyr.data import ch_reader
    from zephyr.regime.core.anchored_state_machine import classify_state

    tsv = ch_reader.query(
        "SELECT dominant, count() FROM c1_backtest.regime_state_anchored FINAL "
        "GROUP BY dominant ORDER BY dominant FORMAT TSV"
    )
    if not tsv or not tsv.strip():
        log.error("CHECK FAIL: regime_state_anchored 无数据")
        return 1
    occupancy = {line.split("\t")[0]: int(line.split("\t")[1]) for line in tsv.strip().split("\n")}
    total = sum(occupancy.values())
    log.info("态占用：%s（总 %d 日）", occupancy, total)
    dead = [k for k, v in occupancy.items() if v < total * 0.01]
    if dead:
        log.error("CHECK FAIL: 死态回潮（占用<1%%）: %s——违反裁定#229 约束②", dead)
        return 1

    import random

    all_dates = ch_reader.query(
        "SELECT trade_date, dominant, vol_pct, close, ma20, ma60, ma120 "
        "FROM c1_backtest.regime_state_anchored FINAL ORDER BY rand() LIMIT 3 FORMAT TSV"
    )
    mismatches = 0
    for line in (all_dates or "").strip().split("\n"):
        td, dom, vol, c, m20, m60, m120 = line.split("\t")
        recomputed = classify_state(float(vol))
        tag = "OK" if recomputed == dom else "MISMATCH"
        if recomputed != dom:
            mismatches += 1
        log.info("抽查 %s: 表内=%s 重算=%s [%s]", td, dom, recomputed, tag)
    if mismatches:
        log.error("CHECK FAIL: %d 日抽查不一致", mismatches)
        return 1
    log.info("CHECK OK: 四态无死态，抽查 %d 日全部一致", 3)
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="锚定态历史构建（c1_backtest.regime_state_anchored）")
    parser.add_argument("--check", action="store_true", help="验收模式：占用健康+抽查交叉验证")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    try:
        sys.exit(run_check() if args.check else run_build())
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001
        err_file = ROOT / ".runtime" / "tmp" / "build_anchored_state_error.txt"
        err_file.parent.mkdir(parents=True, exist_ok=True)
        err_file.write_text(traceback.format_exc(), encoding="utf-8")
        log.error("未处理异常，详情见 %s", err_file)
        sys.exit(1)


if __name__ == "__main__":
    main()
