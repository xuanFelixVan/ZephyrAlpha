# [BLUEPRINT] MOD-TDMVAL-001 | docs/03_modules/_domain_trading/validation/blueprint.md
# [MODULE] zephyr.trading.validation.decay_watch
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.data.ch_writer
# [CONSUMERS] 面板 /api/tdm/validation（decaying 行=预警通道）; P2-1 调度挂载（DataScheduler，待接线）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只对有 valid 首验的节点判衰减; 衰减>=50% 判 decaying; 台账只追加不删改
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValidationError
# [TESTS] tests/trading/test_validation_runner.py::TestDecayWatch
# [TTL] permanent
"""衰减自动巡检（PB-14，Owner 裁定"替代固定复审：报警才触发复审，事件驱动"）。

原理：台账（c1_backtest.node_verdict）是唯一真源——同一节点首验（最早 verdict=valid 行）
vs 最新一行（最近一次验证窗口）的命中指标比对，衰减>=50%（PB-13 土规 2 同源）即追加
verdict=decaying 行；面板「验证档案」区渲染该行为"衰减中"徽章=预警通道本身
（真源 §7.1：台账标噪音/衰减即完成，前端可见+AI 优化优先级输入，不做治理流程）。

调度挂载（P2-1 遗留接线项，晨报登记）：run_decay_check() 为无状态批函数，
挂 DataScheduler 日频作业或 backtest 完成事件由 Owner 择一（trigger_router 新增触发器属
Human-Gated 不可自改）；接线前由验证 runner 批次末尾顺带调用（同进程低成本）。
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Callable

from zephyr.data import ch_writer
from zephyr.trading.validation.runner import (
    _VERDICT_COLUMNS,
    _VERDICT_TABLE,
    ValidationError,
)

logger = logging.getLogger(__name__)

_LEDGER_QUERY = (
    "SELECT node_id, verdict, toString(window_end), run_id, toString(verdict_at), hit_ratio,"
    " validation_method FROM c1_backtest.node_verdict ORDER BY node_id, verdict_at, window_end"
)


def _parse_ledger_tsv(tsv: str) -> list[dict[str, Any]]:
    """ch_writer.query 的 TSV 输出 → 行字典（空串=NULL）。"""
    rows: list[dict[str, Any]] = []
    for line in tsv.strip().split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) != 7:
            continue
        node_id, verdict, window_end, run_id, verdict_at, hit_ratio, method = parts
        rows.append({
            "node_id": node_id,
            "verdict": verdict,
            "window_end": window_end,
            "run_id": run_id,
            "verdict_at": verdict_at,
            "hit_ratio": float(hit_ratio) if hit_ratio not in ("", "\\N", "None") else None,
            "validation_method": method,
        })
    return rows


def detect_decays(
    rows: list[dict[str, Any]], decay_threshold: float = 0.50
) -> list[dict[str, Any]]:
    """纯函数：台账历史 → 待追加的 decaying 行。

    判定：节点存在 verdict=valid 的首验行（基线 hit_ratio），且最新行 hit_ratio
    <= 基线×(1-decay_threshold) → 判衰减。基线/最新缺值（NULL）不判（宁漏勿误）。
    """
    by_node: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        by_node.setdefault(r["node_id"], []).append(r)
    out: list[dict[str, Any]] = []
    for node_id, hist in by_node.items():
        valid_rows = [r for r in hist if r["verdict"] == "valid" and r["hit_ratio"] is not None]
        if not valid_rows:
            continue
        baseline = valid_rows[0]
        latest = hist[-1]
        if latest is baseline or latest["hit_ratio"] is None:
            continue
        if baseline["hit_ratio"] <= 0:
            continue
        decay = (baseline["hit_ratio"] - latest["hit_ratio"]) / baseline["hit_ratio"]
        if decay >= decay_threshold:
            out.append({
                "node_id": node_id,
                "baseline_hit": baseline["hit_ratio"],
                "latest_hit": latest["hit_ratio"],
                "decay": round(decay, 4),
                "window_end": latest["window_end"],
                "run_id": latest["run_id"],
                "validation_method": latest.get("validation_method"),
            })
    return out


def run_decay_check(
    decay_threshold: float = 0.50,
    dry_run: bool = False,
    writer: Callable[[str, str, bytes], bool] | None = None,
    ledger_tsv: str | None = None,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """衰减巡检批：读台账 → detect_decays → 追加 decaying 行。

    writer/ledger_tsv 供测试注入；dry_run 只报不写。
    """
    writer = writer or (lambda t, c, b: ch_writer.write_tsv(t, c, b))
    if ledger_tsv is None:
        ledger_tsv = ch_writer.query(_LEDGER_QUERY)
    if not ledger_tsv:
        return {"checked": 0, "decayed": 0, "written": False, "rows": []}
    rows = _parse_ledger_tsv(ledger_tsv)
    decays = detect_decays(rows, decay_threshold)
    if not decays:
        return {"checked": len(rows), "decayed": 0, "written": False, "rows": []}

    now = (as_of or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    run_id = f"DECAY-{(as_of or datetime.now()).strftime('%Y%m%d-%H%M%S')}"
    out_rows = []
    for d in decays:
        out_rows.append({
            "run_id": run_id,
            "snapshot_commit": "",
            "window_start": d["window_end"],
            "window_end": d["window_end"],
            "node_id": d["node_id"],
            "validation_method": d.get("validation_method") or "agg_discrimination",
            "triggers": 0,
            "hit_ratio": d["latest_hit"],
            "significance": "oos_decay_suspect",
            "verdict": "decaying",
            "verdict_at": now,
            "notes": (
                f"衰减巡检：首验命中 {d['baseline_hit']:.0%} → 最新 {d['latest_hit']:.0%}"
                f"（衰减 {d['decay']:.0%}>=50% 土规线）——报警触发复审（PB-14）"
            ),
        })
    tsv = ("\n".join(
        "\t".join("" if r[c] is None else str(r[c]).replace("\t", " ") for c in (
            "run_id", "snapshot_commit", "window_start", "window_end", "node_id", "validation_method",
            "triggers", "hit_ratio", "significance", "verdict", "verdict_at", "notes"))
        for r in out_rows
    ) + "\n").encode("utf-8")
    written = False
    if not dry_run:
        written = writer(_VERDICT_TABLE, _VERDICT_COLUMNS, tsv)
        if not written:
            logger.error("decaying 行写入未确认（run_id=%s）", run_id)
    return {"checked": len(rows), "decayed": len(out_rows), "written": written, "rows": out_rows}


__all__ = ["detect_decays", "run_decay_check", "ValidationError"]
