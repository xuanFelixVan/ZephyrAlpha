# [BLUEPRINT] MOD-EXE-AGENTS | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/14_execution_layer.md | §4-S1.2
# [MODULE] zephyr.autonomy_core.agents.ticket_queue
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] stdlib ; zephyr.autonomy_core.agents._run_store（信封 schema_version/human_gated 纪律复用）
# [CONSUMERS] tests/autonomy/test_agent_ticket_queue.py ; 四类 Agent 薄入口 CLI ; 人调度多会话（61号文 §3.6）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 四态落盘 pending/claimed/done/dead（.runtime/agent_runs/_queue/）；认领=O_EXCL 原子创建（多会话抢单先到先得，不双领）；工单携带 61号文 §3.6 交接三件套（design_memo 引用+depgraph path+占用者 owner）；done/dead 越 owner 拒操作；recover 须显式给判据（fail-closed 防误全量重派）；信封 100% human_gated
# [MODIFY-GUARD] Owner approval required; 变更须同步 14号文 §4-S1.2 验收口径
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ticket_id 非法/重复/状态不符 → ValueError（fail-closed）；越 owner 操作 → PermissionError；落盘 OSError 上抛（队列写即操作本体，不静默）；坏行/坏文件只告警跳过不阻断扫描
# [TESTS] tests/autonomy/test_agent_ticket_queue.py
# [A_module] module_id=MOD-EXE-AGENTS | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
S1.2 工单队列落盘化（14号文 §4-S1.2，61号文 §3.6 人调度多会话交接载体）.

队列目录：<runtime>/agent_runs/_queue/{pending,claimed,done,dead}/<ticket_id>.json。
单工单手动触发形态（Phase 0）之上加多会话交接：人/会话 enqueue 工单入队，
执行会话 claim 原子认领（O_EXCL 防双会话抢单）→ 跑入口 → done 完结；
会话中断后 recover 扫描 claimed 按判据（孤儿会话/陈旧认领）重派回 pending。
断点语义：claim 成功但 pending 未摘除的崩溃残留，以 claimed 为真源去重。

CLI：
  python -m zephyr.autonomy_core.agents.ticket_queue enqueue --ticket <path> [--runtime-dir D]
  python -m zephyr.autonomy_core.agents.ticket_queue list [--state pending] [--runtime-dir D]
  python -m zephyr.autonomy_core.agents.ticket_queue claim --session-id S [--role R] [--ticket-id T]
  python -m zephyr.autonomy_core.agents.ticket_queue done --ticket-id T --session-id S [--status S]
  python -m zephyr.autonomy_core.agents.ticket_queue dead --ticket-id T --reason R [--session-id S]
  python -m zephyr.autonomy_core.agents.ticket_queue recover [--alive-sessions a,b] [--stale-minutes N]

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: argv 参数
#   fields: 参数 argv，类型注解 list[str] | None
#   code: ticket_queue.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① TicketQueue
#   name_en: TicketQueue
#   intro: 四态落盘工单队列（O_EXCL 原子认领 + 断点恢复重派）.
#   desc: 四态落盘工单队列（O_EXCL 原子认领 + 断点恢复重派）.；公共方法（定义序）: enqueue, claim, done, mark_dead, recover, list_tickets；源码 L109-L337
#   inputs: runtime_dir repo_root
#   outputs: 返回值
# - id: A2
#   name_zh: ② main
#   name_en: main
#   intro: CLI：enqueue/list/claim/done/dead/recover（打印 JSON 结果行）.
#   desc: CLI：enqueue/list/claim/done/dead/recover（打印 JSON 结果行）.；源码 L340-L386
#   inputs: argv
#   outputs: int
# 层: 输出
# - id: O1
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/autonomy/test_agent_ticket_queue.py ; 四类 Agent 薄入口 CLI ; 人调度多会话（61号文 §3.6）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final, final

from zephyr.autonomy_core.agents._run_store import AI_AUTONOMY_MARK, SCHEMA_VERSION, TRIGGERED_BY

logger = logging.getLogger(__name__)

STATES: Final[tuple[str, ...]] = ("pending", "claimed", "done", "dead")
# 崩溃残留去重优先级：done > dead > claimed > pending（后者为真源）
_STATE_PRECEDENCE: Final[tuple[str, ...]] = ("pending", "claimed", "dead", "done")
_TICKET_ID_RE: Final = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_ENVELOPE_KEYS: Final[frozenset[str]] = frozenset(
    {"ticket_id", "role", "kind", "payload", "design_memo", "depgraph_path", "owner", "note"}
)
_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[4]


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _parse_ts(raw: Any) -> datetime | None:
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(str(raw))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


@final
class TicketQueue:
    """四态落盘工单队列（O_EXCL 原子认领 + 断点恢复重派）."""

    def __init__(self, runtime_dir: str | Path | None = None, repo_root: str | Path | None = None) -> None:
        root = Path(repo_root) if repo_root else _REPO_ROOT
        base = Path(runtime_dir) if runtime_dir else root / ".runtime"
        self.queue_dir: Final[Path] = base / "agent_runs" / "_queue"

    # ── 入队 ──────────────────────────────────────────────

    def enqueue(self, ticket: dict[str, Any]) -> Path:
        """工单入队到 pending/（信封+三件套；同 id 任意态已存在即拒，返回落盘路径）."""
        ticket_id = str(ticket.get("ticket_id") or "").strip()
        if not _TICKET_ID_RE.match(ticket_id):
            raise ValueError(f"ticket_id 非法（须 1-128 位字母数字._-，禁路径符）: {ticket_id!r}")
        role = str(ticket.get("role") or "").strip()
        kind = str(ticket.get("kind") or "").strip()
        if not role or not kind:
            raise ValueError("工单缺 role/kind（队列按角色派发，kind 为入口工单类型）")
        for state in STATES:
            if self._path(state, ticket_id).exists():
                raise ValueError(f"工单 {ticket_id} 已存在（{state} 态），拒绝重复入队")
        payload = ticket.get("payload")
        if payload is None:  # 未显式给 payload 时：信封字段之外的全部字段即工单本体
            payload = {k: v for k, v in ticket.items() if k not in _ENVELOPE_KEYS}
        record = {
            "schema_version": SCHEMA_VERSION,
            "ai_autonomy": AI_AUTONOMY_MARK,
            "triggered_by": TRIGGERED_BY,
            "ticket_id": ticket_id,
            "role": role,
            "kind": kind,
            "state": "pending",
            "payload": payload,
            # 61号文 §3.6 交接三件套
            "design_memo": str(ticket.get("design_memo") or ""),
            "depgraph_path": str(ticket.get("depgraph_path") or ""),
            "owner": str(ticket.get("owner") or ""),
            "note": str(ticket.get("note") or ""),
            "attempts": 0,
            "created_at": _utc_now(),
            "claimed_at": None,
            "finished_at": None,
        }
        path = self._path("pending", ticket_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise ValueError(f"工单 {ticket_id} 已存在（pending 竞争），拒绝重复入队") from exc
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
        return path

    # ── 认领（O_EXCL 原子，多会话先到先得）────────────────

    def claim(
        self,
        session_id: str,
        *,
        role: str | None = None,
        ticket_id: str | None = None,
    ) -> dict[str, Any] | None:
        """认领一张 pending 工单到 claimed/（占用者=session_id；无单可领返回 None）."""
        session_id = str(session_id or "").strip()
        if not session_id:
            raise ValueError("claim 须带 session_id（占用者字段，61号文 §3.6 三件套）")
        (self.queue_dir / "claimed").mkdir(parents=True, exist_ok=True)
        for record in self._pending_candidates(role=role, ticket_id=ticket_id):
            tid = record["ticket_id"]
            claimed = {
                **record,
                "state": "claimed",
                "owner": session_id,
                "claimed_at": _utc_now(),
                "attempts": int(record.get("attempts", 0)) + 1,
            }
            try:  # O_EXCL 原子创建=认领锁：已存在即他会话先抢到，换下一候选
                fd = os.open(str(self._path("claimed", tid)), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                continue
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as fh:
                    fh.write(json.dumps(claimed, ensure_ascii=False, indent=2) + "\n")
            except OSError:
                self._path("claimed", tid).unlink(missing_ok=True)  # 写失败释放锁，不留死单
                raise
            try:
                self._path("pending", tid).unlink(missing_ok=True)
            except OSError as exc:  # 崩溃残留以 claimed 为真源去重，不阻断认领
                logger.warning("工单 %s 认领后摘除 pending 失败（以 claimed 为准）: %r", tid, exc)
            return claimed
        return None

    # ── 完结/死信 ─────────────────────────────────────────

    def done(
        self,
        ticket_id: str,
        session_id: str,
        *,
        status: str = "completed",
        summary: dict[str, Any] | None = None,
    ) -> Path:
        """claimed → done（仅占有人会话可完结；返回 done 落盘路径）."""
        record = self._load("claimed", ticket_id)
        if record is None:
            raise ValueError(f"工单 {ticket_id} 不在 claimed 态（未认领不可完结）")
        self._check_owner(record, session_id)
        record.update(
            {"state": "done", "result_status": str(status), "summary": summary or {}, "finished_at": _utc_now()}
        )
        return self._transition(record, "claimed", "done")

    def mark_dead(self, ticket_id: str, *, reason: str, session_id: str | None = None) -> Path:
        """pending/claimed → dead（死信；claimed 态给 session_id 时校验占用者）."""
        for source in ("claimed", "pending"):
            record = self._load(source, ticket_id)
            if record is not None:
                break
        else:
            raise ValueError(f"工单 {ticket_id} 不存在（pending/claimed 均无）")
        if source == "claimed" and session_id is not None:
            self._check_owner(record, session_id)
        record.update({"state": "dead", "dead_reason": str(reason), "finished_at": _utc_now()})
        return self._transition(record, source, "dead")

    # ── 断点恢复 ──────────────────────────────────────────

    def recover(
        self,
        *,
        alive_sessions: set[str] | None = None,
        stale_minutes: float | None = None,
    ) -> list[str]:
        """claimed 扫描重派：占用会话不在存活集 或 认领超龄 → 回 pending（返回重派 id 表）.

        两判据至少给一（fail-closed 防误全量重派）；owner 清空、attempts 保留留痕。
        """
        if alive_sessions is None and stale_minutes is None:
            raise ValueError("recover 须给 alive_sessions 或 stale_minutes 判据之一")
        now = datetime.now(UTC)
        requeued: list[str] = []
        for record in self._scan("claimed"):
            orphaned = alive_sessions is not None and record.get("owner") not in alive_sessions
            stale = False
            if stale_minutes is not None:
                claimed_at = _parse_ts(record.get("claimed_at"))
                stale = claimed_at is None or (now - claimed_at).total_seconds() > stale_minutes * 60
            if not (orphaned or stale):
                continue
            requeue = {**record, "state": "pending", "owner": "", "claimed_at": None}
            self._atomic_write(self._path("pending", record["ticket_id"]), requeue)
            self._path("claimed", record["ticket_id"]).unlink(missing_ok=True)
            requeued.append(record["ticket_id"])
        return requeued

    # ── 扫描 ──────────────────────────────────────────────

    def list_tickets(self, state: str | None = None) -> list[dict[str, Any]]:
        """队列扫描（state=None 时跨态去重：崩溃残留以高优先级态为真源）."""
        if state is not None:
            if state not in STATES:
                raise ValueError(f"未知队列态: {state!r}（合法={list(STATES)}）")
            return self._scan(state)
        merged: dict[str, dict[str, Any]] = {}
        for name in _STATE_PRECEDENCE:
            for record in self._scan(name):
                merged[record["ticket_id"]] = record
        return sorted(merged.values(), key=lambda r: (str(r.get("created_at") or ""), r["ticket_id"]))

    # ── 内部件 ────────────────────────────────────────────

    def _path(self, state: str, ticket_id: str) -> Path:
        return self.queue_dir / state / f"{ticket_id}.json"

    def _load(self, state: str, ticket_id: str) -> dict[str, Any] | None:
        path = self._path(state, ticket_id)
        if not path.is_file():
            return None
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("工单 %s（%s 态）读取失败: %r", ticket_id, state, exc)
            return None
        return record if isinstance(record, dict) else None

    def _scan(self, state: str) -> list[dict[str, Any]]:
        directory = self.queue_dir / state
        if not directory.is_dir():
            return []
        records: list[dict[str, Any]] = []
        for path in sorted(directory.glob("*.json")):
            record = self._load(state, path.stem)
            if record is not None:
                records.append(record)
        records.sort(key=lambda r: (str(r.get("created_at") or ""), str(r.get("ticket_id") or "")))
        return records

    def _pending_candidates(self, *, role: str | None, ticket_id: str | None) -> list[dict[str, Any]]:
        candidates = []
        for record in self._scan("pending"):
            if role is not None and record.get("role") != role:
                continue
            if ticket_id is not None and record.get("ticket_id") != ticket_id:
                continue
            if self._path("claimed", str(record.get("ticket_id"))).exists():
                continue  # 崩溃残留：已被认领的 pending 残影不可再领
            candidates.append(record)
        return candidates

    @staticmethod
    def _check_owner(record: dict[str, Any], session_id: str) -> None:
        owner = str(record.get("owner") or "")
        if owner != str(session_id or ""):
            raise PermissionError(f"工单 {record.get('ticket_id')} owner（占用者）={owner!r}，非 {session_id!r} 拒操作")

    def _transition(self, record: dict[str, Any], source: str, target: str) -> Path:
        dest = self._path(target, record["ticket_id"])
        self._atomic_write(dest, record)
        self._path(source, record["ticket_id"]).unlink(missing_ok=True)
        return dest

    @staticmethod
    def _atomic_write(path: Path, record: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.parent / (path.name + ".tmp")
        tmp.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, path)


def main(argv: list[str] | None = None) -> int:
    """CLI：enqueue/list/claim/done/dead/recover（打印 JSON 结果行）."""
    parser = argparse.ArgumentParser(description="S1.2 工单队列（_queue 四态落盘）")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--runtime-dir", default=None, help="落盘根（默认仓根 .runtime/）")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("enqueue", parents=[common], help="工单入队 pending")
    p.add_argument("--ticket", required=True, help="工单 JSON 路径")
    p = sub.add_parser("list", parents=[common], help="队列扫描")
    p.add_argument("--state", default=None, choices=list(STATES))
    p = sub.add_parser("claim", parents=[common], help="原子认领")
    p.add_argument("--session-id", required=True)
    p.add_argument("--role", default=None)
    p.add_argument("--ticket-id", default=None)
    p = sub.add_parser("done", parents=[common], help="完结 claimed→done")
    p.add_argument("--ticket-id", required=True)
    p.add_argument("--session-id", required=True)
    p.add_argument("--status", default="completed")
    p = sub.add_parser("dead", parents=[common], help="死信 →dead")
    p.add_argument("--ticket-id", required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--session-id", default=None)
    p = sub.add_parser("recover", parents=[common], help="断点恢复重派 claimed→pending")
    p.add_argument("--alive-sessions", default=None, help="存活会话 id 逗号表")
    p.add_argument("--stale-minutes", type=float, default=None, help="认领超龄分钟数")
    args = parser.parse_args(argv)

    queue = TicketQueue(runtime_dir=args.runtime_dir)
    if args.command == "enqueue":
        ticket = json.loads(Path(args.ticket).read_text(encoding="utf-8"))
        queue.enqueue(ticket)
        out: Any = {"enqueued": ticket.get("ticket_id"), "state": "pending"}
    elif args.command == "list":
        out = queue.list_tickets(state=args.state)
    elif args.command == "claim":
        out = {"claimed": queue.claim(args.session_id, role=args.role, ticket_id=args.ticket_id)}
    elif args.command == "done":
        queue.done(args.ticket_id, args.session_id, status=args.status)
        out = {"done": args.ticket_id, "status": args.status}
    elif args.command == "dead":
        queue.mark_dead(args.ticket_id, reason=args.reason, session_id=args.session_id)
        out = {"dead": args.ticket_id}
    else:  # recover
        alive = {s for s in str(args.alive_sessions or "").split(",") if s} or None
        out = {"requeued": queue.recover(alive_sessions=alive, stale_minutes=args.stale_minutes)}
    print(json.dumps(out, ensure_ascii=False))
    return 0


__all__ = ["STATES", "TicketQueue", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
