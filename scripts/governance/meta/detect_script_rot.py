# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/detect_script_rot.py | §
# [MODULE] scripts.governance.meta.detect_script_rot
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.meta.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""
detect_script_rot.py — Script Rot（脚本静默失效）检测器



对标 B51（Script Rot 检测）+ Google SRE "Dead Man's Switch" pattern。

检测治理脚本是否已经失效——脚本仍存在于 manifest 并可运行，
但扫不到任何 Finding 因为它扫的代码模式已经不存于代码库了。

检测逻辑：
  1. 查询 manifest → 每个脚本的"历史平均 Finding 产出"
  2. 如果一个脚本过去 30 天产出 Finding = 0，但历史上曾产出 > 0
  3. → 报告 "Script Rot: 脚本可能已过时——扫描的代码模式不存在"

可区分"真没问题"（代码确实好了）：查看目标代码模式近年是否有变更。

Usage:
    python scripts/governance/meta/detect_script_rot.py
    python scripts/governance/meta/detect_script_rot.py --days 30
    python scripts/governance/meta/detect_script_rot.py --alert-threshold 0
    python scripts/governance/meta/detect_script_rot.py --json
"""

from __future__ import annotations

__manifest__ = """
args: []
description: ⚠ __manifest__ 缺失——请添加元数据块
dimensions: []
priority: P2
timeout_seconds: 60
warn_only: false
"""


import json as json_mod
import sqlite3
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# 治本(2026-06-30): REPO_ROOT 真源来自 _shared.constants, 消除 parents[N] 硬编码
# 原 parents[2] 实为 scripts 目录而非 repo root, 变量名误导且路径计算有 bug
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT as _REPO_ROOT  # noqa: E402
_DB_PATH = _REPO_ROOT / "scripts" / "governance" / "meta" / "findings_timeseries.db"
_ROT_LOG = _REPO_ROOT / "scripts" / "governance" / "meta" / "script_rot_findings.jsonl"

# SQL 集中化（§5.160.2 NO-BARE-SQL gate）
SQL_COUNT_RECENT = "SELECT COUNT(*) FROM findings WHERE check_id = ? AND timestamp >= ?"
SQL_COUNT_HISTORICAL = "SELECT COUNT(*) FROM findings WHERE check_id = ? AND timestamp >= ? AND timestamp < ?"
SQL_LAST_FINDING_TS = "SELECT timestamp FROM findings WHERE check_id = ? ORDER BY timestamp DESC LIMIT 1"

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _get_db_conn() -> sqlite3.Connection | None:
    """_get_db_conn implementation."""
    if not _DB_PATH.exists():
        return None
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def detect_rot(days: int = 30, alert_threshold: int = 0) -> dict:
    """Detect issues in target and report findings."""
    conn = _get_db_conn()
    if not conn:
        return {"error": "时序数据库不存在——请先运行 manage_finding_timeseries.py --import"}

    now = datetime.now(UTC)
    recent_cutoff = (now - timedelta(days=days)).isoformat()
    historical_cutoff = (now - timedelta(days=90)).isoformat()

    try:
        scripts = conn.execute("SELECT DISTINCT check_id, dimension FROM findings").fetchall()
        rotten: list[dict] = []

        for script in scripts:
            check_id = script["check_id"] or ""
            dimension = script["dimension"] or ""
            if not check_id:
                continue

            recent_count = conn.execute(
                SQL_COUNT_RECENT,
                (check_id, recent_cutoff),
            ).fetchone()[0]

            historical_count = conn.execute(
                SQL_COUNT_HISTORICAL,
                (check_id, historical_cutoff, recent_cutoff),
            ).fetchone()[0]

            total_runs = conn.execute(
                "SELECT COUNT(DISTINCT scan_run_id) FROM findings WHERE check_id = ?",
                (check_id,),
            ).fetchone()[0]

            if recent_count <= alert_threshold and historical_count > 0:
                last_finding = conn.execute(
                    SQL_LAST_FINDING_TS,
                    (check_id,),
                ).fetchone()

                rotten.append(
                    {
                        "check_id": check_id,
                        "dimension": dimension,
                        "severity": "HIGH",
                        "recent_findings": recent_count,
                        "historical_findings": historical_count,
                        "total_scan_runs": total_runs,
                        "last_finding_at": last_finding["timestamp"] if last_finding else "never",
                        "detail": f"脚本 {check_id} 过去 {days} 天产出 0 个 Finding (历史有 {historical_count} 个)——可能已过时",
                        "recommendation": "检查脚本扫描的代码模式是否仍存于代码库，或标记为 DEPRECATED",
                    }
                )
    finally:
        conn.close()

    if rotten:
        _ROT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(_ROT_LOG, "a", encoding="utf-8") as f:
            for r in rotten:
                f.write(json_mod.dumps(r, ensure_ascii=False) + "\n")

    return {
        "timestamp": now.isoformat(),
        "rotten_scripts": len(rotten),
        "total_scripts_analyzed": len(scripts),
        "findings": rotten,
        "clean": len(rotten) == 0,
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    days = 30
    alert_threshold = 0
    for a in sys.argv:
        if a.startswith("--days="):
            days = int(a.split("=")[1])
        elif a.startswith("--alert-threshold="):
            alert_threshold = int(a.split("=")[1])

    result = detect_rot(days, alert_threshold)

    if "--json" in sys.argv:
        print(json_mod.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result.get("error"):
            print(f"[SCRIPT-ROT] ❌ {result['error']}", file=sys.stderr)
        elif result["clean"]:
            print(f"[SCRIPT-ROT] ✅ 全部 {result['total_scripts_analyzed']} 个脚本活跃——无静默失效", file=sys.stderr)
        else:
            print(
                f"[SCRIPT-ROT] 🔴 {result['rotten_scripts']} 个脚本可能已过时 (过去 {days} 天无 Finding)",
                file=sys.stderr,
            )
            for r in result["findings"]:
                print(f"  [{r['dimension']}] {r['check_id']}: {r['detail']}", file=sys.stderr)
        sys.exit(0 if result.get("clean", True) else 1)


if __name__ == "__main__":
    main()
