# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §AICOLLAB-001-TaskBoard
# [MODULE] scripts.task_board
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib (sqlite3/argparse/json/os/sys/subprocess/uuid/pathlib)
# [CONSUMERS] 全部 AI session（任务认领协调）；66 号提交队列死信标签承载（deadletter 子命令打标 + list --label 查询，metadata_json 承载）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 状态机仅 pending→claimed→completed 三态；认领走单条 UPDATE CAS（changes()>0 即成功）；completed 任务禁止再认领/删除/打标；DB 锚主仓 .runtime（跨 worktree 共享）；死信标签=metadata_json.deadletter{qid,reason,owner,tagged_at}（66 号 §6.4，不改表，重复打标以最新为准）
# [MODIFY-GUARD] 65 号 §11.2.3 规格；66 号 §2.4 #9 schema；CLI 子命令面
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 认领/完成/删除守卫拒绝 → exit 2（DENIED）；参数/DB 错误 → exit 1；成功 → exit 0
# [TESTS] tests/governance/test_task_board.py
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 本文件是 AI/CI 按需调用的 CLI 协调工具（非 cron/非 daemon/非常驻），与 lock_files.py 同类
"""task_board.py — 多 AI 并发任务认领板（SQLite WAL + CAS 三态机）

重建真源
--------
- 66 号 memo §2.4 #9：.runtime/task_board.db（SQLite WAL + CAS，状态机
  pending→claimed→completed，metadata_json + task_events.payload_json 可扩展字段）。
  原文件 2026-08-14 worktree wipe 事故丢失（从未入 git），本文件按该 schema 重建。
- 65 号 §11.2.3：WAL 模式；CAS 原子认领 SQL；精简三态（去 blocked/abandoned/epoch，
  放弃就删 task 重新 create）；CLI create/claim/start/complete/list/show；
  与 #ARCH 议题联动（每议题一 task，认领前先登记）。
- 66 号 §6.4 死信承载：队列死信标签（qid+原因+属主）写入 metadata_json，无需改表。

锚定设计（关键）
----------------
DB 必须在**主仓** .runtime/task_board.db——本板是跨 worktree 协调设施，锚到
worktree 则每个会话各见一板、协调失效（post-S4 paths.find_repo_root 优先
ZEPHYR_WORKTREE_ROOT，故不能用它）。解析序：
1. 环境变量 ZEPHYR_TASK_BOARD_DB（测试覆盖用）
2. ``git rev-parse --git-common-dir`` 与 ``--git-dir`` 不同 → 处于 worktree，
   板根 = common-dir 的父目录（主仓根）；相同 → 板根 = --show-toplevel
3. git 不可用 → 回退 __file__ 派生（scripts/ 上一级；若处于 .worktrees/<sid>/ 下
   则再上溯两级到主仓）

并发安全
--------
- PRAGMA journal_mode=WAL + busy_timeout=5000 + synchronous=NORMAL。
- 认领 = 单条 UPDATE ... WHERE 守卫条件，sqlite3 changes()>0 判成功——
  SQLite 单写者 + WAL 保证该 UPDATE 串行执行，无 TOCTOU。
- 60 分钟认领 TTL：claimed_at 超龄可被他人抢占（防崩溃会话永久占用）。

CLI
---
- create --title T [--description D] [--metadata JSON]   → 打印新 task_id
- claim <id> --session S                                  → CAS 认领；重复/已完成 DENIED(exit 2)
- start <id> --session S                                  → 记 started 事件（状态保持 claimed）
- complete <id> --session S [--result R]                  → 仅当前认领者可完成
- delete <id> --session S                                 → pending 任意；claimed 仅认领者；completed DENIED
- deadletter <id> --session S --qid Q --reason R [--owner O] → 66 号 §6.4 死信打标（metadata_json.deadletter，completed DENIED）
- list [--status S] [--session S] [--label deadletter]    → 表格输出（--label 查死信标签）
- show <id>                                               → 任务全字段 + 事件历史
- --warn-only                                             → 自测（建库建表+空查询）后 exit 0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: CLI 子命令参数
#   fields: title/description/metadata/task_id/session/result/status 过滤
# - id: I2
#   name: task_board.db（WAL）
#   fields: tasks 9 列 / task_events 6 列
# 层: 算法
# - id: A1
#   name_zh: 板根解析
#   intro: git-common-dir≠git-dir → worktree → 主仓根；保证跨 worktree 单板
# - id: A2
#   name_zh: CAS 认领
#   intro: 单 UPDATE 带 WHERE (claimed_by NULL OR 超龄) AND status!=completed；changes()>0 判赢
# - id: A3
#   name_zh: 事件追加
#   intro: 每次状态迁移同步 INSERT task_events（同事务）
# 层: 输出
# - id: O1
#   name: exit code
#   fields: 0 成功 / 2 DENIED / 1 错误
# - id: O2
#   name: stdout
#   fields: task_id / 表格 / show 详情
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

_SQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    task_id      TEXT PRIMARY KEY,
    title        TEXT NOT NULL,
    description  TEXT NOT NULL DEFAULT '',
    status       TEXT NOT NULL DEFAULT 'pending'
                 CHECK (status IN ('pending','claimed','completed')),
    claimed_by   TEXT,
    claimed_at   TEXT,
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS task_events (
    event_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id      TEXT NOT NULL REFERENCES tasks(task_id),
    event_type   TEXT NOT NULL,
    actor        TEXT NOT NULL DEFAULT '',
    timestamp    TEXT NOT NULL DEFAULT (datetime('now')),
    payload_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_claimed_by ON tasks(claimed_by);
CREATE INDEX IF NOT EXISTS idx_events_task ON task_events(task_id);
"""

# CAS 认领（65 号 §11.2.3 真源 SQL + completed 守卫）：changes()>0 即认领成功
_SQL_CLAIM = """
UPDATE tasks
SET claimed_by = ?, claimed_at = datetime('now'), status = 'claimed'
WHERE task_id = ?
  AND status IN ('pending', 'claimed')
  AND (claimed_by IS NULL OR claimed_at < datetime('now', '-60 minutes'))
"""

_SQL_TASK_EXISTS = "SELECT 1 FROM tasks WHERE task_id=?"
_SQL_GET_TASK = "SELECT * FROM tasks WHERE task_id=?"
_SQL_INSERT_TASK = (
    "INSERT INTO tasks (task_id, title, description, status, created_at, metadata_json)"
    " VALUES (?, ?, ?, 'pending', datetime('now'), ?)"
)
_SQL_INSERT_EVENT = (
    "INSERT INTO task_events (task_id, event_type, actor, timestamp, payload_json) VALUES (?, ?, ?, datetime('now'), ?)"
)
_SQL_COMPLETE_TASK = "UPDATE tasks SET status='completed', completed_at=datetime('now') WHERE task_id=?"
_SQL_UPDATE_METADATA = "UPDATE tasks SET metadata_json=? WHERE task_id=?"
_SQL_DELETE_TASK = "DELETE FROM tasks WHERE task_id=?"
_SQL_LIST_TASKS_BASE = "SELECT task_id, status, title, claimed_by, claimed_at, created_at FROM tasks"
_SQL_LIST_EVENTS = (
    "SELECT event_type, actor, timestamp, payload_json FROM task_events WHERE task_id=? ORDER BY event_id"
)
_SQL_COUNT_TASKS = "SELECT count(*) FROM tasks"
_SQL_LATEST_TASK_ID = "SELECT task_id FROM tasks ORDER BY created_at DESC, rowid DESC LIMIT 1"

_CLAIM_TTL_MINUTES = 60


def _resolve_board_db() -> Path:
    """板根解析：主仓 .runtime/task_board.db（跨 worktree 单板）。"""
    env = os.environ.get("ZEPHYR_TASK_BOARD_DB")
    if env:
        return Path(env)
    try:
        common = subprocess.run(  # noqa: bare-subprocess  治理脚本轻量调用，CREATE_NO_WINDOW 已补
            ["git", "rev-parse", "--git-common-dir"],
            capture_output=True,
            text=True,
            check=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        ).stdout.strip()
        gitdir = subprocess.run(  # noqa: bare-subprocess  板根解析轻量 git 调用，CREATE_NO_WINDOW 已补
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            check=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        ).stdout.strip()
        common_p = Path(common).resolve()
        gitdir_p = Path(gitdir).resolve()
        if common_p != gitdir_p:
            # worktree：common-dir = 主仓/.git → 主仓根 = 其父
            return common_p.parent / ".runtime" / "task_board.db"
        top = subprocess.run(  # noqa: bare-subprocess  板根解析轻量 git 调用，CREATE_NO_WINDOW 已补
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        ).stdout.strip()
        return Path(top) / ".runtime" / "task_board.db"
    except Exception:
        # 回退：__file__ 派生；.worktrees/<sid>/ 下则上溯到主仓
        here = Path(__file__).resolve()
        for parent in here.parents:
            if parent.name == ".worktrees":
                return parent.parent / ".runtime" / "task_board.db"
        return here.parents[1] / ".runtime" / "task_board.db"


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.row_factory = sqlite3.Row
    conn.executescript(_SQL_SCHEMA)
    return conn


def _new_task_id(conn: sqlite3.Connection) -> str:
    for _ in range(10):
        tid = f"T-{uuid.uuid4().hex[:10]}"
        row = conn.execute(_SQL_TASK_EXISTS, (tid,)).fetchone()
        if row is None:
            return tid
    raise RuntimeError("task_id 碰撞重试耗尽")


def _add_event(
    conn: sqlite3.Connection,
    task_id: str,
    event_type: str,
    actor: str,
    payload: dict | None = None,
) -> None:
    conn.execute(
        _SQL_INSERT_EVENT,
        (task_id, event_type, actor, json.dumps(payload or {}, ensure_ascii=False)),
    )


def _get_task(conn: sqlite3.Connection, task_id: str) -> sqlite3.Row | None:
    return conn.execute(_SQL_GET_TASK, (task_id,)).fetchone()


def cmd_create(conn: sqlite3.Connection, args: argparse.Namespace) -> int:
    metadata: dict = {}
    if args.metadata:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError as e:
            print(f"ERROR: --metadata 非法 JSON: {e}", file=sys.stderr)
            return 1
    with conn:
        tid = _new_task_id(conn)
        conn.execute(
            _SQL_INSERT_TASK,
            (tid, args.title, args.description or "", json.dumps(metadata, ensure_ascii=False)),
        )
        _add_event(conn, tid, "created", args.session or "", {"title": args.title, "metadata": metadata})
    print(tid)
    return 0


def cmd_claim(conn: sqlite3.Connection, args: argparse.Namespace) -> int:
    with conn:
        cur = conn.execute(_SQL_CLAIM, (args.session, args.task_id))
        if cur.rowcount > 0:
            _add_event(conn, args.task_id, "claimed", args.session, {"ttl_minutes": _CLAIM_TTL_MINUTES})
            print(f"CLAIMED {args.task_id} by {args.session}")
            return 0
        # DENIED：给出原因
        task = _get_task(conn, args.task_id)
        if task is None:
            print(f"DENIED: task {args.task_id} 不存在", file=sys.stderr)
            return 2
        if task["status"] == "completed":
            print(f"DENIED: task {args.task_id} 已完成，禁止再认领", file=sys.stderr)
            return 2
        print(
            f"DENIED: task {args.task_id} 已被 {task['claimed_by']} 认领"
            f"（{task['claimed_at']}，{_CLAIM_TTL_MINUTES}min 内有效）",
            file=sys.stderr,
        )
        return 2


def cmd_start(conn: sqlite3.Connection, args: argparse.Namespace) -> int:
    with conn:
        task = _get_task(conn, args.task_id)
        if task is None:
            print(f"DENIED: task {args.task_id} 不存在", file=sys.stderr)
            return 2
        if task["status"] != "claimed":
            print(f"DENIED: task {args.task_id} 状态 {task['status']}，须先 claim", file=sys.stderr)
            return 2
        _add_event(conn, args.task_id, "started", args.session or "", {})
        print(f"STARTED {args.task_id}")
        return 0


def cmd_complete(conn: sqlite3.Connection, args: argparse.Namespace) -> int:
    with conn:
        task = _get_task(conn, args.task_id)
        if task is None:
            print(f"DENIED: task {args.task_id} 不存在", file=sys.stderr)
            return 2
        if task["status"] == "completed":
            print(f"DENIED: task {args.task_id} 已完成", file=sys.stderr)
            return 2
        if task["claimed_by"] != args.session:
            print(
                f"DENIED: task {args.task_id} 当前认领者 {task['claimed_by']}，非 {args.session}",
                file=sys.stderr,
            )
            return 2
        conn.execute(_SQL_COMPLETE_TASK, (args.task_id,))
        _add_event(conn, args.task_id, "completed", args.session, {"result": args.result or ""})
        print(f"COMPLETED {args.task_id}")
        return 0


def cmd_delete(conn: sqlite3.Connection, args: argparse.Namespace) -> int:
    with conn:
        task = _get_task(conn, args.task_id)
        if task is None:
            print(f"DENIED: task {args.task_id} 不存在", file=sys.stderr)
            return 2
        if task["status"] == "completed":
            print(f"DENIED: task {args.task_id} 已完成，保留历史禁止删除", file=sys.stderr)
            return 2
        if task["status"] == "claimed" and task["claimed_by"] != args.session:
            print(
                f"DENIED: task {args.task_id} 被 {task['claimed_by']} 认领中，仅认领者可删",
                file=sys.stderr,
            )
            return 2
        _add_event(conn, args.task_id, "deleted", args.session or "", {"title": task["title"]})
        conn.execute(_SQL_DELETE_TASK, (args.task_id,))
        print(f"DELETED {args.task_id}")
        return 0


def cmd_deadletter(conn: sqlite3.Connection, args: argparse.Namespace) -> int:
    """66 号 §6.4 死信打标：qid+原因+属主写入 metadata_json.deadletter（不改表）。

    重复打标以最新为准（死信取回重入队后再失败须更新原因）；completed 任务
    禁止打标（与禁删/禁认领同守卫）。标签经 list --label deadletter 可查。
    """
    with conn:
        task = _get_task(conn, args.task_id)
        if task is None:
            print(f"DENIED: task {args.task_id} 不存在", file=sys.stderr)
            return 2
        if task["status"] == "completed":
            print(f"DENIED: task {args.task_id} 已完成，禁止死信打标", file=sys.stderr)
            return 2
        try:
            metadata = json.loads(task["metadata_json"] or "{}")
        except json.JSONDecodeError as e:
            print(f"ERROR: task {args.task_id} metadata_json 损坏: {e}", file=sys.stderr)
            return 1
        owner = args.owner or args.session
        tag = {
            "qid": args.qid,
            "reason": args.reason,
            "owner": owner,
            "tagged_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        metadata["deadletter"] = tag
        conn.execute(_SQL_UPDATE_METADATA, (json.dumps(metadata, ensure_ascii=False), args.task_id))
        _add_event(conn, args.task_id, "deadlettered", args.session, dict(tag))
        print(f"DEADLETTER {args.task_id} qid={args.qid}")
        return 0


def cmd_list(conn: sqlite3.Connection, args: argparse.Namespace) -> int:
    label = getattr(args, "label", "")
    sql = (
        "SELECT task_id, status, title, claimed_by, claimed_at, created_at, metadata_json FROM tasks"
        if label
        else _SQL_LIST_TASKS_BASE
    )
    conds: list[str] = []
    params: list[str] = []
    if args.status:
        conds.append("status=?")
        params.append(args.status)
    if args.session:
        conds.append("claimed_by=?")
        params.append(args.session)
    if conds:
        sql += " WHERE " + " AND ".join(conds)
    sql += " ORDER BY created_at DESC"
    if not label:
        sql += " LIMIT 100"
    rows = conn.execute(sql, params).fetchall()
    if label:
        # 标签过滤（Python 端解析 metadata_json，不依赖 SQLite JSON1 扩展）
        filtered = []
        for r in rows:
            try:
                meta = json.loads(r["metadata_json"] or "{}")
            except json.JSONDecodeError:
                continue
            if label in meta:
                filtered.append(r)
        rows = filtered[:100]
    if not rows:
        print("(empty)")
        return 0
    print(f"{'TASK_ID':<14} {'STATUS':<10} {'CLAIMED_BY':<14} {'CREATED_AT':<20} TITLE")
    for r in rows:
        print(
            f"{r['task_id']:<14} {r['status']:<10} {(r['claimed_by'] or '-'):<14}"
            f" {r['created_at']:<20} {r['title'][:60]}"
        )
    return 0


def cmd_show(conn: sqlite3.Connection, args: argparse.Namespace) -> int:
    task = _get_task(conn, args.task_id)
    if task is None:
        print(f"ERROR: task {args.task_id} 不存在", file=sys.stderr)
        return 1
    print(json.dumps(dict(task), ensure_ascii=False, indent=2))
    events = conn.execute(_SQL_LIST_EVENTS, (args.task_id,)).fetchall()
    print("--- events ---")
    for e in events:
        print(f"  {e['timestamp']} {e['event_type']:<10} {e['actor']:<14} {e['payload_json']}")
    return 0


def cmd_warn_only(conn: sqlite3.Connection) -> int:
    conn.execute(_SQL_COUNT_TASKS).fetchone()
    print("task_board --warn-only OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="task_board.py",
        description="多 AI 并发任务认领板（SQLite WAL + CAS 三态机，66 号 §2.4 #9 schema 重建）",
    )
    parser.add_argument("--warn-only", action="store_true", help="自测后退出（RULE-SEVEN）")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("create", help="建任务，打印 task_id")
    p.add_argument("--title", required=True)
    p.add_argument("--description", default="")
    p.add_argument("--metadata", default="", help="JSON 字符串（66 号死信标签承载：qid/reason/owner）")
    p.add_argument("--session", default="")

    p = sub.add_parser("claim", help="CAS 认领（重复/已完成 DENIED exit 2）")
    p.add_argument("task_id")
    p.add_argument("--session", required=True)

    p = sub.add_parser("start", help="记 started 事件（状态保持 claimed）")
    p.add_argument("task_id")
    p.add_argument("--session", default="")

    p = sub.add_parser("complete", help="完成任务（仅当前认领者）")
    p.add_argument("task_id")
    p.add_argument("--session", required=True)
    p.add_argument("--result", default="")

    p = sub.add_parser("delete", help="删任务（pending 任意；claimed 仅认领者；completed DENIED）")
    p.add_argument("task_id")
    p.add_argument("--session", default="")

    p = sub.add_parser("deadletter", help="死信打标（66 号 §6.4：qid+原因+属主入 metadata_json，completed DENIED）")
    p.add_argument("task_id")
    p.add_argument("--session", required=True)
    p.add_argument("--qid", required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--owner", default="", help="属主（缺省=--session）")

    p = sub.add_parser("list", help="列表（--status/--session/--label 过滤）")
    p.add_argument("--status", choices=["pending", "claimed", "completed"], default="")
    p.add_argument("--session", default="")
    p.add_argument("--label", choices=["deadletter"], default="", help="标签过滤（deadletter=死信任务）")

    p = sub.add_parser("show", help="任务全字段 + 事件历史")
    p.add_argument("task_id")

    args = parser.parse_args(argv)
    db_path = _resolve_board_db()
    conn = _connect(db_path)
    try:
        if args.warn_only:
            return cmd_warn_only(conn)
        if args.cmd == "create":
            return cmd_create(conn, args)
        if args.cmd == "claim":
            return cmd_claim(conn, args)
        if args.cmd == "start":
            return cmd_start(conn, args)
        if args.cmd == "complete":
            return cmd_complete(conn, args)
        if args.cmd == "delete":
            return cmd_delete(conn, args)
        if args.cmd == "deadletter":
            return cmd_deadletter(conn, args)
        if args.cmd == "list":
            return cmd_list(conn, args)
        if args.cmd == "show":
            return cmd_show(conn, args)
        parser.print_help()
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
