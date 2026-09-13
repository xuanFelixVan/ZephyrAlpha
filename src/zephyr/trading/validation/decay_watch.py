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

调度挂载（2026-09-10 裁定，已落地）：衰减判定依赖"新验证行落地"才有意义——
run_validation() 写台账成功后尾随调用本巡检（decay_check=True 默认开，失败不阻断验证批）。
不挂 DataScheduler cron（巡检无新数据时空转）、不动 trigger_router（Human-Gated）。
衰减判据本函数独立可手动触发（run_decay_check），调度解耦。

重要性分档联动（备忘 96 批 2，2026-09-14）：节点在地图里带 materiality 档 →
decay_scan_frequency（critical=monthly/high=quarterly/normal=semiannual）。
按档扫描=调 run_decay_check(scan_frequency="monthly") 时只看该档节点——
生死线节点月月查、边缘节点半年查一次，验证资源按影响面分配（SR 26-2）。
不传 scan_frequency=全节点扫描（旧行为，向后兼容）。
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from zephyr.data import ch_reader, ch_writer
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

# 地图真源（备忘 96 批 1 已回填 materiality/decay_scan_frequency）——本模块只读不写
_DEFAULT_MAP_PATH = Path(__file__).resolve().parents[4] / "config" / "trading_decision_map.yaml"

# materiality → 缺省扫描频率（decay_scan_frequency 显式写了就以显式为准）
_MATERIALITY_DEFAULT_FREQUENCY = {
    "critical": "monthly",
    "high": "quarterly",
    "normal": "semiannual",
}

_SCAN_FREQUENCIES = ("monthly", "quarterly", "semiannual")


def load_node_scan_tiers(map_path: Path | None = None) -> dict[str, str]:
    """地图真源 → {node_id: scan_frequency}（备忘 96 批 2 接线点）。

    优先级：节点显式 decay_scan_frequency > materiality 档推导 > 不纳入分档扫描。
    地图解析走 decision_map.load_decision_map（SSOT，禁手挑 YAML）。
    """
    from zephyr.trading.decision_map import load_decision_map  # 延迟导入避免循环依赖

    path = Path(map_path) if map_path is not None else _DEFAULT_MAP_PATH
    if not path.exists():
        raise ValidationError(f"地图真源不存在: {path}")
    dm = load_decision_map(path)
    tiers: dict[str, str] = {}
    for node in dm.nodes:
        freq = node.decay_scan_frequency
        if not freq and node.materiality:
            freq = _MATERIALITY_DEFAULT_FREQUENCY.get(str(node.materiality))
        if freq:
            tiers[node.node_id] = str(freq)
    return tiers


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
    rows: list[dict[str, Any]],
    decay_threshold: float = 0.50,
    scan_frequency: str | None = None,
    tiers: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """纯函数：台账历史 → 待追加的 decaying 行。

    判定：节点存在 verdict=valid 的首验行（基线 hit_ratio），且最新行 hit_ratio
    <= 基线×(1-decay_threshold) → 判衰减。基线/最新缺值（NULL）不判（宁漏勿误）。

    分档扫描（备忘 96 批 2）：传 scan_frequency 时只判该档节点——
    tiers 必须由 load_node_scan_tiers() 从地图真源取得；缺 tiers 一律报错 fail-closed
    （宁可响一声也不静默退化成全量扫描，否则档位形同虚设）。
    """
    if scan_frequency is not None:
        if scan_frequency not in _SCAN_FREQUENCIES:
            raise ValidationError(
                f"未知扫描频率 {scan_frequency!r}，须为 {_SCAN_FREQUENCIES}"
            )
        if tiers is None:
            raise ValidationError(
                "按档扫描必须提供 tiers（load_node_scan_tiers() 取自地图真源）"
            )
    by_node: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        by_node.setdefault(r["node_id"], []).append(r)
    out: list[dict[str, Any]] = []
    for node_id, hist in by_node.items():
        if scan_frequency is not None and tiers.get(node_id) != scan_frequency:
            continue
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
                "scan_frequency": (tiers or {}).get(node_id),
            })
    return out


def run_decay_check(
    decay_threshold: float = 0.50,
    dry_run: bool = False,
    writer: Callable[[str, str, bytes], bool] | None = None,
    ledger_tsv: str | None = None,
    as_of: datetime | None = None,
    scan_frequency: str | None = None,
    map_path: Path | None = None,
    tiers: dict[str, str] | None = None,
) -> dict[str, Any]:
    """衰减巡检批：读台账 → detect_decays → 追加 decaying 行。

    writer/ledger_tsv 供测试注入；dry_run 只报不写。

    分档扫描（备忘 96 批 2）：scan_frequency 给定时只扫该档节点，
    档位表默认从地图真源 load_node_scan_tiers() 取（tiers 可注入供测试）。
    """
    writer = writer or (lambda t, c, b: ch_writer.write_tsv(t, c, b))
    if scan_frequency is not None and tiers is None:
        tiers = load_node_scan_tiers(map_path)
    if ledger_tsv is None:
        # 读路径走 ch_reader（#ARCH-CH-007：SELECT 应自动注入 FINAL 的正道）
        ledger_tsv = ch_reader.query(_LEDGER_QUERY)
    if not ledger_tsv:
        return {"checked": 0, "decayed": 0, "written": False, "rows": [],
                "scan_frequency": scan_frequency, "scanned_nodes": 0}
    rows = _parse_ledger_tsv(ledger_tsv)
    decays = detect_decays(rows, decay_threshold, scan_frequency, tiers)
    scanned_nodes = (
        len({r["node_id"] for r in rows})
        if scan_frequency is None
        else sum(1 for nid in {r["node_id"] for r in rows} if tiers.get(nid) == scan_frequency)
    )
    if not decays:
        return {"checked": len(rows), "decayed": 0, "written": False, "rows": [],
                "scan_frequency": scan_frequency, "scanned_nodes": scanned_nodes}

    now = (as_of or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    run_id = f"DECAY-{(as_of or datetime.now()).strftime('%Y%m%d-%H%M%S')}"
    if scan_frequency:
        run_id = f"{run_id}-{scan_frequency.upper()}"
    out_rows = []
    for d in decays:
        tier_note = f"｜{scan_frequency} 档巡检" if d.get("scan_frequency") else ""
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
            "verdict_reason": "oos_decay_suspect",
            "verdict_at": now,
            "notes": (
                f"衰减巡检：首验命中 {d['baseline_hit']:.0%} → 最新 {d['latest_hit']:.0%}"
                f"（衰减 {d['decay']:.0%}>=50% 土规线）——报警触发复审（PB-14）{tier_note}"
            ),
        })
    tsv = ("\n".join(
        "\t".join("" if r[c] is None else str(r[c]).replace("\t", " ") for c in (
            "run_id", "snapshot_commit", "window_start", "window_end", "node_id", "validation_method",
            "triggers", "hit_ratio", "significance", "verdict", "verdict_reason", "verdict_at", "notes"))
        for r in out_rows
    ) + "\n").encode("utf-8")
    written = False
    if not dry_run:
        written = writer(_VERDICT_TABLE, _VERDICT_COLUMNS, tsv)
        if not written:
            logger.error("decaying 行写入未确认（run_id=%s）", run_id)
    return {"checked": len(rows), "decayed": len(out_rows), "written": written,
            "rows": out_rows, "scan_frequency": scan_frequency,
            "scanned_nodes": scanned_nodes}


__all__ = [
    "detect_decays",
    "run_decay_check",
    "load_node_scan_tiers",
    "ValidationError",
]
