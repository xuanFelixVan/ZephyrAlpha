# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/manage_finding_timeseries.py | §
# [MODULE] scripts.governance.meta.manage_finding_timeseries
# [DOMAIN] D_GOV_SCRIPTS
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
manage_finding_timeseries.py — Finding 时序数据库 + 趋势分析引擎



对标 B50（Finding 时序数据库）+ Nertflix Kayenta Metric Retrieval + SQLite columnar storage。

将 Finding 数据导入 SQLite 时序数据库，支持：
- 趋势查询（本周 vs 上周、本月 vs 上月）
- 按维度/严重度/文件分组聚合
- 时间窗口筛选（过去 7d / 30d / 90d）
- 趋势方向判断（improving / stable / degrading）

Usage:
    python scripts/governance/meta/manage_finding_timeseries.py --import findings.jsonl
    python scripts/governance/meta/manage_finding_timeseries.py --trend 30d
    python scripts/governance/meta/manage_finding_timeseries.py --top-files 10
    python scripts/governance/meta/manage_finding_timeseries.py --severity-distribution
    python scripts/governance/meta/manage_finding_timeseries.py --query "SELECT severity, COUNT(*) FROM findings GROUP BY severity"
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

# SQL 集中化（§5.160.2 NO-BARE-SQL gate）
SQL_INSERT_SCAN_RUN = "INSERT INTO scan_runs (run_id, started_at, completed_at, total_findings, exit_code) VALUES (?, ?, ?, ?, ?)"
SQL_COUNT_SINCE = "SELECT COUNT(*) FROM findings WHERE timestamp >= ?"
SQL_COUNT_RANGE = "SELECT COUNT(*) FROM findings WHERE timestamp >= ? AND timestamp < ?"

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _get_conn() -> sqlite3.Connection:
    """_get_conn implementation."""
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            finding_id TEXT,
            timestamp TEXT,
            scan_run_id TEXT,
            dimension TEXT,
            check_id TEXT,
            severity TEXT,
            description TEXT,
            file_path TEXT,
            confidence REAL,
            status TEXT DEFAULT 'OPEN',
            imported_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_timestamp ON findings(timestamp);
        CREATE INDEX IF NOT EXISTS idx_dimension ON findings(dimension);
        CREATE INDEX IF NOT EXISTS idx_severity ON findings(severity);
        CREATE INDEX IF NOT EXISTS idx_file_path ON findings(file_path);
        CREATE INDEX IF NOT EXISTS idx_status ON findings(status);
        CREATE TABLE IF NOT EXISTS scan_runs (
            run_id TEXT PRIMARY KEY,
            started_at TEXT,
            completed_at TEXT,
            total_findings INTEGER,
            exit_code INTEGER
        );
        CREATE TABLE IF NOT EXISTS daily_summary (
            date TEXT PRIMARY KEY,
            total_findings INTEGER,
            opened INTEGER,
            closed INTEGER,
            by_severity TEXT
        );
    """)
    return conn


def import_findings(source: str | Path) -> dict:
    """import_findings implementation."""
    conn = _get_conn()
    try:
        now = datetime.now(UTC).isoformat()
        run_id = f"run-{now[:19]}"
        count = 0

        with open(source, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    finding = json_mod.loads(line)
                except json_mod.JSONDecodeError:
                    continue

                target = finding.get("target", {})
                conn.execute(
                    """INSERT INTO findings
                       (finding_id, timestamp, scan_run_id, dimension, check_id,
                        severity, description, file_path, confidence, status, imported_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        finding.get("finding_id", ""),
                        finding.get("timestamp", now),
                        run_id,
                        finding.get("dimension", ""),
                        finding.get("check_id", ""),
                        finding.get("severity", "LOW"),
                        finding.get("description", ""),
                        target.get("file_path", ""),
                        finding.get("confidence", 0.5),
                        finding.get("status", "OPEN"),
                        now,
                    ),
                )
                count += 1

        conn.execute(
            SQL_INSERT_SCAN_RUN,
            (run_id, now, now, count, 0),
        )
        conn.commit()
        return {"imported": count, "run_id": run_id}
    finally:
        conn.close()


def trend(days: int = 30) -> dict:
    """trend implementation."""
    conn = _get_conn()
    try:
        cutoff = (datetime.now(UTC) - timedelta(days=days)).isoformat()

        total = conn.execute(SQL_COUNT_SINCE, (cutoff,)).fetchone()[0]
        by_severity = {}
        for row in conn.execute(
            "SELECT severity, COUNT(*) as cnt FROM findings WHERE timestamp >= ? GROUP BY severity", (cutoff,)
        ):
            by_severity[row[0]] = row[1]
        by_dimension = {}
        for row in conn.execute(
            "SELECT dimension, COUNT(*) as cnt FROM findings WHERE timestamp >= ? GROUP BY dimension ORDER BY cnt DESC",
            (cutoff,),
        ):
            by_dimension[row[0]] = row[1]

        prev_cutoff = (datetime.now(UTC) - timedelta(days=days * 2)).isoformat()
        prev_cutoff_end = cutoff
        prev_total = conn.execute(
            SQL_COUNT_RANGE, (prev_cutoff, prev_cutoff_end)
        ).fetchone()[0]

        if prev_total == 0:
            direction = "stable"
            change_pct = 0
        else:
            change_pct = round((total - prev_total) / prev_total * 100, 1)
            if change_pct > 20:
                direction = "degrading"
            elif change_pct < -20:
                direction = "improving"
            else:
                direction = "stable"

        return {
            "period": f"{days}d",
            "current_total": total,
            "previous_total": prev_total,
            "change_pct": change_pct,
            "direction": direction,
            "by_severity": by_severity,
            "by_dimension": by_dimension,
        }
    finally:
        conn.close()


def top_files(limit: int = 10, days: int = 90) -> list[dict]:
    """top_files implementation."""
    conn = _get_conn()
    try:
        cutoff = (datetime.now(UTC) - timedelta(days=days)).isoformat()
        rows = conn.execute(
            "SELECT file_path, COUNT(*) as cnt FROM findings WHERE timestamp >= ? GROUP BY file_path ORDER BY cnt DESC LIMIT ?",
            (cutoff, limit),
        ).fetchall()
        return [{"file_path": r[0], "finding_count": r[1]} for r in rows]
    finally:
        conn.close()


def severity_distribution(days: int = 90) -> dict:
    """severity_distribution implementation."""
    conn = _get_conn()
    try:
        cutoff = (datetime.now(UTC) - timedelta(days=days)).isoformat()
        rows = conn.execute(
            "SELECT severity, COUNT(*) as cnt FROM findings WHERE timestamp >= ? GROUP BY severity ORDER BY cnt DESC",
            (cutoff,),
        ).fetchall()
        return {r[0]: r[1] for r in rows}
    finally:
        conn.close()


def raw_query(sql: str) -> list[dict]:
    """raw_query implementation."""
    conn = _get_conn()
    try:
        rows = conn.execute(sql).fetchall()
        return [{k: r[k] for k in r.keys()} for r in rows]
    finally:
        conn.close()


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    if "--import" in sys.argv:
        idx = sys.argv.index("--import")
        src = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
        if src:
            result = import_findings(src)
            print(f"[TIMESERIES] ✅ 导入 {result['imported']} 条 Finding (Run: {result['run_id']})", file=sys.stderr)
    elif "--trend" in sys.argv:
        days = 30
        for a in sys.argv:
            if a.endswith("d") and a[:-1].isdigit():
                days = int(a[:-1])
                break
        result = trend(days)
        icon = {"improving": "📉", "stable": "➡️", "degrading": "📈"}.get(result["direction"], "❓")
        print(
            f"\n[TIMESERIES] {days}d 趋势: {icon} {result['direction']} — {result['change_pct']:+.1f}%", file=sys.stderr
        )
        print(f"  当前: {result['current_total']}, 上期: {result['previous_total']}", file=sys.stderr)
        print(f"  按严重度: {result['by_severity']}", file=sys.stderr)
        print(f"  按维度: {dict(list(result['by_dimension'].items())[:5])}", file=sys.stderr)
    elif "--top-files" in sys.argv:
        limit = 10
        try:
            idx = sys.argv.index("--top-files")
            limit = int(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else 10
        except (ValueError, IndexError):
            pass
        files = top_files(limit)
        for f in files:
            print(f"  {f['finding_count']:4d}  {f['file_path']}")
    elif "--severity-distribution" in sys.argv:
        dist = severity_distribution()
        for sev, cnt in dist.items():
            bar = "█" * min(cnt // max(1, max(dist.values()) // 20), 50)
            print(f"  {sev:12s}: {cnt:4d} {bar}")
    elif "--query" in sys.argv:
        idx = sys.argv.index("--query")
        sql = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
        rows = raw_query(sql)
        for r in rows:
            print(json_mod.dumps(r, ensure_ascii=False))
    else:
        print(
            'Usage: manage_finding_timeseries.py --import | --trend 30d | --top-files 10 | --severity-distribution | --query "..."',
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
