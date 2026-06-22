# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/trace_finding_lifecycle.py | §
"""trace_finding_lifecycle.py — Finding C1→C5 全链路追踪引擎

对标 B56（C1→C5 全链路 Tracing）+ OpenTelemetry distributed tracing 概念。

追踪每个 Finding 从 C1扫描到C5知识的完整生命周期：
  C1 Scan → 脚本运行 → 产出Finding → C2分类 → C3报告 → C4跟踪 → C5知识沉淀

提供:
  --trace <finding_id>  追踪指定 Finding 的全链路
  --overview            系统级的链路健康总览
  --bottleneck          找出链路瓶颈（哪阶段最慢/丢失最多）

Usage:
    python scripts/governance/meta/trace_finding_lifecycle.py --trace F-101
    python scripts/governance/meta/trace_finding_lifecycle.py --overview
    python scripts/governance/meta/trace_finding_lifecycle.py --bottleneck
"""

from __future__ import annotations

__manifest__ = """
args: []
description: >
  Finding C1→C5 全链路追踪引擎——追踪每个 Finding 从 C1 扫描到 C5 知识沉淀的完整生命周期，
  包括链路健康总览和瓶颈检测。
dimensions:
- D1
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""


import json as json_mod
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DB_PATH = _REPO_ROOT / "scripts" / "governance" / "meta" / "findings_timeseries.db"
_TRACE_DB_PATH = _REPO_ROOT / "scripts" / "governance" / "meta" / "lifecycle_traces.db"

# C1-C5 阶段定义
PHASES = {
    "C1_SCAN": {"order": 1, "label": "扫描执行"},
    "C2_CLASSIFY": {"order": 2, "label": "分类"},
    "C3_REPORT": {"order": 3, "label": "报告"},
    "C4_TRACK": {"order": 4, "label": "跟踪"},
    "C5_DEPOSIT": {"order": 5, "label": "知识沉淀"},
}

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _get_conn() -> sqlite3.Connection:
    """_get_conn implementation."""
    _TRACE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_TRACE_DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS traces (
            trace_id TEXT PRIMARY KEY,
            finding_id TEXT,
            phase TEXT,
            started_at TEXT,
            completed_at TEXT,
            duration_ms REAL,
            status TEXT,
            metadata TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_finding_phase ON traces(finding_id, phase);
        CREATE INDEX IF NOT EXISTS idx_trace_status ON traces(status);
    """)
    return conn


def record_trace(finding_id: str, phase: str, duration_ms: float, status: str = "completed") -> None:
    """record_trace implementation."""
    conn = _get_conn()
    now = datetime.now(UTC).isoformat()
    trace_id = f"trace-{finding_id}-{phase}-{now[:19]}"
    conn.execute(
        "INSERT OR REPLACE INTO traces (trace_id, finding_id, phase, started_at, completed_at, duration_ms, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (trace_id, finding_id, phase, now, now, duration_ms, status),
    )
    conn.commit()
    conn.close()


def trace_finding(finding_id: str) -> dict:
    """trace_finding implementation."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM traces WHERE finding_id = ? ORDER BY completed_at",
        (finding_id,),
    ).fetchall()
    conn.close()

    phases_found: dict[str, dict] = {}
    for r in rows:
        phases_found[r["phase"]] = {
            "phase": r["phase"],
            "label": PHASES.get(r["phase"], {}).get("label", r["phase"]),
            "duration_ms": r["duration_ms"],
            "status": r["status"],
            "completed_at": r["completed_at"],
        }

    missing_phases = set(PHASES.keys()) - set(phases_found.keys())
    return {
        "finding_id": finding_id,
        "phases_completed": list(phases_found.keys()),
        "phases_missing": list(missing_phases),
        "phases": phases_found,
        "complete": len(missing_phases) == 0,
        "total_duration_ms": sum(p.get("duration_ms", 0) for p in phases_found.values()),
    }


def overview() -> dict:
    """overview implementation."""
    conn = _get_conn()
    total_traces = conn.execute("SELECT COUNT(*) FROM traces").fetchone()[0]
    completed = conn.execute("SELECT COUNT(*) FROM traces WHERE status='completed'").fetchone()[0]
    failed = conn.execute("SELECT COUNT(*) FROM traces WHERE status='failed'").fetchone()[0]

    phase_stats = {}
    for phase in PHASES:
        count = conn.execute("SELECT COUNT(*) FROM traces WHERE phase=?", (phase,)).fetchone()[0]
        avg_dur = conn.execute("SELECT AVG(duration_ms) FROM traces WHERE phase=?", (phase,)).fetchone()[0] or 0
        phase_stats[phase] = {"count": count, "avg_duration_ms": round(avg_dur, 2)}

    conn.close()
    return {
        "total_traces": total_traces,
        "completed": completed,
        "failed": failed,
        "completion_rate": round(completed / max(1, total_traces) * 100, 1),
        "phase_stats": phase_stats,
    }


def bottleneck_analysis() -> dict:
    """bottleneck_analysis implementation."""
    conn = _get_conn()
    bottlenecks = []
    for phase in PHASES:
        row = conn.execute(
            "SELECT AVG(duration_ms) as avg_dur, COUNT(*) as cnt FROM traces WHERE phase=?",
            (phase,),
        ).fetchone()
        bottlenecks.append(
            {
                "phase": phase,
                "label": PHASES[phase]["label"],
                "avg_duration_ms": round(row["avg_dur"] or 0, 2),
                "count": row["cnt"],
            }
        )

    bottlenecks.sort(key=lambda x: x["avg_duration_ms"], reverse=True)

    worst = bottlenecks[0] if bottlenecks else {}
    conn.close()
    return {
        "worst_phase": worst.get("phase", ""),
        "worst_label": worst.get("label", ""),
        "worst_duration_ms": worst.get("avg_duration_ms", 0),
        "all_phases": bottlenecks,
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    if "--trace" in sys.argv:
        idx = sys.argv.index("--trace")
        fid = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
        result = trace_finding(fid)
        if "--json" in sys.argv:
            print(json_mod.dumps(result, ensure_ascii=False, indent=2))
        else:
            status = "✅" if result["complete"] else "⚠️"
            print(
                f"\n[TRACE] {status} {result['finding_id']}: {len(result['phases_completed'])}/{len(PHASES)} 阶段完成",
                file=sys.stderr,
            )
            for phase, info in result.get("phases", {}).items():
                print(f"  ✅ {info['label']} ({info['duration_ms']:.0f}ms)", file=sys.stderr)
            for phase in result["phases_missing"]:
                print(f"  ❌ {PHASES[phase]['label']} — 缺失", file=sys.stderr)
    elif "--overview" in sys.argv:
        result = overview()
        print("\n[TRACE] C1→C5 链路健康总览", file=sys.stderr)
        print(f"  总计: {result['total_traces']} traces, {result['completion_rate']}% 完成", file=sys.stderr)
        for phase, stats in result["phase_stats"].items():
            print(
                f"  [{phase}] {PHASES[phase]['label']}: {stats['count']} traces, avg {stats['avg_duration_ms']}ms",
                file=sys.stderr,
            )
    elif "--bottleneck" in sys.argv:
        result = bottleneck_analysis()
        print("\n[TRACE] 链路瓶颈分析", file=sys.stderr)
        print(f"  最大瓶颈: {result['worst_label']} ({result['worst_duration_ms']}ms)", file=sys.stderr)
        for b in result["all_phases"]:
            bar = "█" * min(int(b["avg_duration_ms"] / 10), 50)
            print(f"  {b['label']:10s}: {b['avg_duration_ms']:8.1f}ms {bar}")
    else:
        print("Usage: trace_finding_lifecycle.py --trace <id> | --overview | --bottleneck", file=sys.stderr)


if __name__ == "__main__":
    main()
