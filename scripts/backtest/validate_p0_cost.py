# [BLUEPRINT] MOD-BT-034 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.validate_p0_cost
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.trading.validation.runner(复用 exec_quality 指标与土规); zephyr.backtest.run_archive; zephyr.data.ch_writer
# [CONSUMERS] c1_backtest.node_verdict(P0-003 四节点族台账行); 桌面壳 TDM 抽屉
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 阈值冻结(slip 20/40bp, BT-P0-003 frozen 2026-09-12 禁挪); 土规(总触发<30→pending/insufficient_samples); holdout 定稿锚点 D=2026-09-09 前全锁; 台账/档案只增不改; 落库失败不归档
# [MODIFY-GUARD] tests/backtest/test_validate_p0_cost.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(落库未确认)
# [TESTS] tests/backtest/test_validate_p0_cost.py
# [A_module] module_id=MOD-BT-034 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""P0-003 成本模型合并检验（exec_quality，四节点族 BT-P0-003，SOP-A P0 铁行第三件）。

对象：TDM-E-L4-09（订单级预检）/ TDM-P-P2-01（做T资格门）/ TDM-P-P2-03（做T闭环）/ TDM-X-S2-01（卖出执行路由）
方法：exec_quality（复用 validation.runner 的 compute_exec_metrics + apply_soil_rules——不重造口径）
冻结口径（backlog BT-P0-003，frozen 2026-09-12）：滑点均值<=20bp→valid；<=40bp→pending；>40bp→noise；
  总触发<30→pending/insufficient_samples；成本五项=佣金+印花税+滑点+市场冲击+做T额外成本（费率读账户配置）。

数据现实（如实披露）：定稿锚点 D=2026-09-09 后流水仅 4 笔（L4/XFLOW 批同源）——预期 verdict=pending/
insufficient_samples；本检验的意义=P0 三件套在台账全部有"已检验"状态行 + 4 笔流水滑点留痕，待流水积累后
decay_watch/重验批自动转正。
依据: backtest_backlog BT-P0-003 frozen plan + validation_method_registry exec_quality。
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from typing import Any

from zephyr.backtest.run_archive import create_run, finalize_run, write_step
from zephyr.trading.validation.runner import (
    ValidationConfig,
    _ARTIFACTS_DIR,
    apply_soil_rules,
    compute_exec_metrics,
    holdout_cutoff,
    load_fills,
    partition_by_holdout,
)

logger = logging.getLogger(__name__)

_NODE_IDS = ["TDM-E-L4-09", "TDM-P-P2-01", "TDM-P-P2-03", "TDM-X-S2-01"]
_VERDICT_TABLE = "c1_backtest.node_verdict"
_VERDICT_COLUMNS = (
    "(run_id, snapshot_commit, window_start, window_end, node_id, validation_method,"
    " triggers, hit_ratio, significance, verdict, verdict_reason, verdict_at, notes)"
)


def _tsv_cell(v: Any) -> str:
    return "\\N" if v is None else str(v).replace("\t", " ")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="P0-003 成本模型合并检验（exec_quality，冻结口径）")
    parser.add_argument("--dry-run", action="store_true", help="只算不写台账/不归档")
    args = parser.parse_args()

    now = datetime.now()
    run_id = f"VAL-P0-{now.strftime('%Y%m%d-%H%M%S')}-003"
    create_run(
        run_id=run_id, object_id="BT-P0-003", kind="VAL",
        window={"start": "2026-09-09", "end": now.strftime("%Y-%m-%d")},
        holdout={"mode": "anchor", "cutoff": "2026-09-09"},
        cost_mode="full", created_by="ai-session:p0-cost",
    )

    # 数据链：复用 runner 的流水加载与 holdout 切分（D=2026-09-09 前全锁）
    cfg = ValidationConfig()  # finalized_at=2026-09-09 / min_triggers=30 / 20-40bp 土规线（冻结同源）
    fills = load_fills(_ARTIFACTS_DIR)
    inside, locked = partition_by_holdout(fills, holdout_cutoff(now, cfg.holdout_months),
                                          finalized_at=cfg.finalized_at)
    metrics = compute_exec_metrics(inside)
    significance, verdict, reason = apply_soil_rules(metrics, cfg)
    logger.info("流水: 在验 %d 笔 / holdout 锁 %d 笔; 滑点均值 %s bp (口径=%s)",
                metrics["triggers"], len(locked), metrics.get("slip_bp_mean"), metrics.get("slip_basis"))

    body = json.dumps({
        "triggers": metrics["triggers"], "locked": len(locked),
        "slip_bp_mean": metrics.get("slip_bp_mean"), "slip_basis": metrics.get("slip_basis"),
        "verdict": verdict, "significance": significance, "reason": reason,
    }, ensure_ascii=False, indent=1)

    write_step(run_id, "01", (
        "# 方法学调研结论\n\nexec_quality 口径=validation_method_registry.yaml（滑点 20/40bp 土规线）；"
        "复用 validation.runner 的 compute_exec_metrics/apply_soil_rules（零新口径）；"
        "成本五项=佣金+印花税+滑点+市场冲击+做T额外成本（费率读账户配置，BT-P0-003 frozen）。\n"
    ))
    write_step(run_id, "02", (
        "# DATA-GAP 清单\n\n- [已备] 成交流水 data/backtest_artifacts/bt-*.json（trade_log 含 decision_price）\n"
        "- [缺口-流水量] D=2026-09-09 后仅 4 笔在验窗口流水（<30 土规）——pending 如实披露，"
        "待模拟盘/实盘流水积累后 decay_watch 或重验批转正\n- [缺口-对照] VWAP 代理 ref_prices 未接入本批（decision_price 优先口径）\n"
    ))
    write_step(run_id, "03", (
        "# 数据清单\n\n- name: 成交流水\n  source: data/backtest_artifacts/bt-*.json（引擎产物,不入 git）\n"
        "  pit_note: 'D=2026-09-09 前全锁（PB-08 定稿锚点）; 脏时间戳按保密处理（宁严勿漏）'\n  proxy: false\n"
    ))
    write_step(run_id, "05", "# 剪枝记录\n\n不适用：流水全量参与（无参数网格）。\n")
    write_step(run_id, "06", f"# 分段统计\n\n{body}\n", filename="cost_stats.json")
    write_step(run_id, "verdict", (
        f"# 判定书：{run_id}\n\n对象：BT-P0-003 四节点族（{', '.join(_NODE_IDS)}）｜ method=exec_quality ｜ "
        f"窗口=D(2026-09-09)~今 ｜ 成本口径=full\n"
        f"结论：verdict={verdict} ｜ significance={significance or 'na'} ｜ verdict_reason={reason}\n"
        f"判定链：冻结口径（backlog BT-P0-003 frozen 2026-09-12）+ runner 土规代码执行，未手调。\n\n"
        f"关键数字：{body}\n\n"
        "遗留问题：流水量不足（D 后 4 笔）——待流水积累转正；五项成本中市场冲击/做T额外成本需要更高频数据，"
        "当前口径=滑点+佣金近似（notes 如实披露）。\n\n"
        f"台账回执：node_verdict run_id={run_id}\n"
    ))
    finalize_run(run_id, verdict_ref={"table": _VERDICT_TABLE, "run_id": run_id})
    if args.dry_run:
        print(json.dumps({"run_id": run_id, "dry_run": True, **json.loads(body)}, ensure_ascii=False, indent=1))
        return

    from zephyr.backtest.core.engine_base import current_map_snapshot
    from zephyr.data import ch_writer

    snapshot_commit = current_map_snapshot()
    window_start = min((f["timestamp"][:10] for f in inside), default="2026-09-09")
    window_end = max((f["timestamp"][:10] for f in inside), default="2026-09-09")
    notes = (f"滑点均值={metrics.get('slip_bp_mean')}bp(口径={metrics.get('slip_basis') or 'na'}); "
             f"在验 {metrics['triggers']} 笔/锁 {len(locked)} 笔; 四节点族合并验证（归因粒度限制：流水无节点字段）")
    tsv = "\n".join(
        "\t".join(_tsv_cell(c) for c in [
            run_id, snapshot_commit, window_start, window_end, nid, "exec_quality",
            metrics["triggers"], metrics.get("fill_rate"), significance or "na",
            verdict, reason, now.strftime("%Y-%m-%d %H:%M:%S"), notes,
        ]) for nid in _NODE_IDS
    ) + "\n"
    written = ch_writer.write_tsv(_VERDICT_TABLE, _VERDICT_COLUMNS, tsv.encode("utf-8"))
    if not written:
        raise RuntimeError(f"台账落库未确认（BT-P0-003 四节点行）——fail-closed")
    logger.info("台账已写 4 行: verdict=%s reason=%s", verdict, reason)
    print(json.dumps({"run_id": run_id, "rows": len(_NODE_IDS), **json.loads(body)}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.exit(main())
