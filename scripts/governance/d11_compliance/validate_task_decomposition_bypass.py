# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/validate_task_decomposition_bypass.py | §
# [MODULE] scripts.governance.d11_compliance.validate_task_decomposition_bypass
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d11_compliance.__init__
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
validate_task_decomposition_bypass.py — Task Decomposition Bypass 检测
=====================================================================
检测 AI 是否通过将高危任务拆分为多个「安全」子任务来绕过门禁。

Safety : M（任务拆分绕过 = 门禁体系系统性失效）
Usage  : python scripts/governance/d11_compliance/validate_task_decomposition_bypass.py [--json] [--verbose] [--hours N]

启发式（对标 TB1 / TB3）：
  TB1. 激活任务中 deliverables JSON 有交集，且聚合文本共享同一高风险词干
  TB3. depends_on 链路（2 或 3 节）上共享高风险词干

exit codes: 0=无绕过, 1=发现绕过, 2=执行错误
"""

from __future__ import annotations

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

__manifest__ = """
args:
- --hours
- --warn-only
- --jsonl
description: >
  Task decomposition bypass heuristic (deliverables overlap + depends_on chains vs shared risk stems).
dimensions:
- D11
priority: P0
timeout_seconds: 45
warn_only: false
"""

import argparse
import json
import sqlite3
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

_GOV_DIR = Path(__file__).resolve().parents[1]
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import DB_PATH, EXIT_ERROR, EXIT_PASS

_RISKY_KEYWORDS: list[tuple[str, str]] = [
    ("strategy", "策略——可能涉及 G10/G11/G12 交易门禁"),
    ("leverage", "杠杆——触发 G11 杠杆限制门禁"),
    ("position", "仓位——触发 G10 持仓限制门禁"),
    ("correlation", "相关性——触发 G12 策略相关性门禁"),
    ("blueprint", "蓝图——可能触发 G6 蓝图合规门禁"),
    ("migration", "迁移——可能触发 schema 变更门禁"),
    ("security", "安全——可能触发 G6 安全扫描门禁"),
    ("delete", "删除——可能触发锚文件保护门禁"),
    ("refactor", "重构——被拆分子任务重新组合等于完整重构"),
    ("critical", "关键路径——可能触发多层门禁"),
    ("production", "生产环境——涉及最高安全级别"),
    ("hotfix", "热修复——绕过正常变更流程"),
    ("bypass", "绕过——明确意图的关键词"),
    ("直接", "直接操作——跳过中间检查层"),
    ("跳过门禁", "明确的黑名单意图"),
]


def _parse_json_list(raw: object) -> list[Any]:
    """_parse_json_list implementation."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    if not isinstance(raw, str) or not raw.strip():
        return []
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def _parse_iso_ts(value: object) -> datetime | None:
    """_parse_iso_ts implementation."""
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        s = value.strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)
    except ValueError:
        return None


def _aggregate_text(row: dict[str, Any]) -> str:
    """_aggregate_text implementation."""
    parts = [
        str(row.get("title") or ""),
        str(row.get("directive") or ""),
        " ".join(str(x) for x in _parse_json_list(row.get("deliverables"))),
        " ".join(str(x) for x in _parse_json_list(row.get("files_in_scope"))),
        " ".join(str(x) for x in _parse_json_list(row.get("tags"))),
    ]
    return "\n".join(parts).lower()


def _risky_stems(text: str) -> set[str]:
    """_risky_stems implementation."""
    return {kw for kw, _ in _RISKY_KEYWORDS if kw.lower() in text}


def _get_connection(warn_only: bool) -> sqlite3.Connection | None:
    """_get_connection implementation."""
    if not DB_PATH.exists():
        print(f"[TASK-DECOMP] 数据库不存在: {DB_PATH}", file=sys.stderr)
        if warn_only:
            return None
        sys.exit(EXIT_ERROR)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _load_active_tasks(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """_load_active_tasks implementation."""
    active_status = (
        "PENDING",
        "IN_PROGRESS",
        "READY",
        "RETRY",
        "WAITING",
        "BLOCKED",
    )
    placeholders = ",".join("?" * len(active_status))
    try:
        chk = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='tasks'",
        ).fetchone()
        if not chk:
            return []
        rows = conn.execute(
            f"""
            SELECT rowid AS __rowid, * FROM tasks
            WHERE IFNULL(is_deleted, 0) = 0
              AND status IN ({placeholders})
            ORDER BY datetime(COALESCE(updated_at, created_at)) DESC
            LIMIT 500
            """,
            active_status,
        ).fetchall()
    except sqlite3.Error as exc:
        print(f"[TASK-DECOMP] SQL error: {exc}", file=sys.stderr)
        return []
    return [dict(r) for r in rows]


def analyze_bypasses(rows: list[dict[str, Any]], hours: int) -> list[str]:
    """Analyze target and report insights."""
    flags: list[str] = []
    cutoff = datetime.now(UTC) - timedelta(hours=hours)

    windowed: list[dict[str, Any]] = []
    for r in rows:
        ts = _parse_iso_ts(r.get("updated_at")) or _parse_iso_ts(r.get("created_at"))
        if ts is None or ts >= cutoff:
            windowed.append(r)

    by_id: dict[str, dict[str, Any]] = {}
    for r in windowed:
        tid = r.get("task_id")
        if isinstance(tid, str) and tid:
            by_id[tid] = r

    ids = list(by_id.keys())
    for i, iid in enumerate(ids):
        ri = by_id[iid]
        di = {str(x) for x in _parse_json_list(ri.get("deliverables")) if str(x).strip()}
        if not di:
            continue
        risks_i = _risky_stems(_aggregate_text(ri))
        if not risks_i:
            continue
        for jid in ids[i + 1 :]:
            rj = by_id[jid]
            dj = {str(x) for x in _parse_json_list(rj.get("deliverables")) if str(x).strip()}
            overlap = di & dj
            if not overlap:
                continue
            risks_j = _risky_stems(_aggregate_text(rj))
            shared_kw = risks_i & risks_j
            if shared_kw:
                flags.append(
                    f"TB1 tasks={iid},{jid} deliverable_overlap={sorted(overlap)[:3]} risk_kw={sorted(shared_kw)[:5]}"
                )

    for tid, r in by_id.items():
        deps_raw = _parse_json_list(r.get("depends_on"))
        deps = [str(d) for d in deps_raw if isinstance(d, str) and d in by_id]
        if not deps:
            continue
        tr = _risky_stems(_aggregate_text(r))
        if not tr:
            continue
        for d in deps:
            br = by_id[d]
            common = tr & _risky_stems(_aggregate_text(br))
            if not common:
                continue
            chain = f"{tid}->{d}"
            next_deps = [str(x) for x in _parse_json_list(br.get("depends_on")) if isinstance(x, str) and x in by_id]
            extended = False
            for e in next_deps:
                er = by_id[e]
                trip = common & _risky_stems(_aggregate_text(er))
                if trip:
                    flags.append(f"TB3 chain={tid}->{d}->{e} risk_kw={sorted(trip)[:5]}")
                    extended = True
            if not extended:
                flags.append(f"TB3 chain={chain} risk_kw={sorted(common)[:5]}")

    seen: set[str] = set()
    out: list[str] = []
    for f in flags:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Task decomposition bypass heuristic scan")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--jsonl", action="store_true", help="输出单行 JSON（含 severity，供冒烟链使用）")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="告警模式：无数据库或跳过时不以 exit 2 失败",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=72,
        help="时间窗（小时）：仅纳入最近 updated_at/created_at 落在窗内或无时间戳的记录",
    )
    args = parser.parse_args()

    conn = _get_connection(args.warn_only)
    if conn is None:
        stub = {
            "severity": "INFO",
            "check_id": "TASK-DECOMP",
            "message": "skip_no_database",
            "hits": [],
            "rows_loaded": 0,
        }
        if args.jsonl:
            print(json.dumps(stub, ensure_ascii=False))
        elif args.json:
            print(json.dumps({**stub, "hours": args.hours}, ensure_ascii=False))
        return EXIT_PASS

    try:
        rows = _load_active_tasks(conn)
    finally:
        conn.close()
    flags = analyze_bypasses(rows, args.hours)
    payload = {"rows_loaded": len(rows), "hits": flags, "hours": args.hours}

    if args.verbose:
        print(f"[TASK-DECOMP] loaded {len(rows)} task rows window={args.hours}h", file=sys.stderr)
        for line in flags:
            print(f"  {line}", file=sys.stderr)

    sev = "HIGH" if flags else "INFO"
    jsonl_body = {
        "severity": sev,
        "check_id": "TASK-DECOMP",
        "hits": flags,
        "rows_loaded": len(rows),
        "hours": args.hours,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    elif args.jsonl:
        print(json.dumps(jsonl_body, ensure_ascii=False))
    else:
        for line in flags:
            print(line, file=sys.stderr)
        print(f"[TASK-DECOMP] rows={len(rows)} hits={len(flags)}", file=sys.stderr)

    if flags:
        return 0 if args.warn_only else 1
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
