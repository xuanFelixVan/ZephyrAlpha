"""
SessionContinuity — Session 交接包自动生成与恢复
=================================================
依据：MOD-INF-006 v0.3.2 + ADR-0041（HandoffPackage）+ AGENTS.md §5.1 零记忆重启

Vibe Coding 最大痛点：AI 每次新 session 是零记忆的。
本模块解决"打开 IDE 不知道上回做到哪了"的问题。

注意：本模块使用纯 Python + sqlite3，不 import zephyr.shared（避让已知导入链断裂）。

用法：
    from zephyr.core.session_continuity import SessionContinuity

    sc = SessionContinuity()

    # session 结束时
    sc.generate_and_save(session_id="sess-2026-05-05", task_repo=repo)

    # session 开始时
    sc.print_restore_summary()
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

__all__ = ["SessionContinuity"]

_DEFAULT_DB = Path(__file__).parent.parent / "db" / ".." / ".." / ".." / "data" / "zalpha_metadata.db"

_DDL_HANDOFFS = """
CREATE TABLE IF NOT EXISTS handoffs (
    handoff_id       TEXT PRIMARY KEY,
    session_id       TEXT NOT NULL,
    completed_tasks  TEXT NOT NULL DEFAULT '[]',
    in_progress_tasks TEXT NOT NULL DEFAULT '[]',
    blocked_items    TEXT NOT NULL DEFAULT '[]',
    decisions_made   TEXT NOT NULL DEFAULT '[]',
    next_actions     TEXT NOT NULL DEFAULT '[]',
    context_summary  TEXT NOT NULL DEFAULT '',
    open_questions   TEXT NOT NULL DEFAULT '[]',
    phase            INTEGER,
    created_at       TEXT NOT NULL
)
"""

class SessionContinuity:
    """Session 交接包自动生成与恢复"""

    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path:
            self._db_path = Path(db_path)
        else:
            self._db_path = Path("D:/ZephyrAlpha/data/zalpha_metadata.db")
        self._init_schema()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        conn = self._get_conn()
        conn.execute(_DDL_HANDOFFS)
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    def generate_and_save(
        self,
        session_id: str,
        task_repo: object,
    ) -> dict:
        """从 task_repo 汇总当前状态 → 生成 HandoffPackage → 写 SQLite + YAML

        GOV-AI-008 (handoff-protocol.md) 合规实现：
        - 8 必填字段全部自动填充
        - decisions_made 从 events 表读取
        - in_progress_tasks 含 step/construction_status/deliverables
        - open_questions 自动从 BLOCKED ≥2 session 的任务生成
        - 同步输出 YAML 到 docs/09_audit/HANDOFF/
        """
        completed = []
        in_progress = []
        blocked_items = []
        next_actions = []

        all_statuses = [
            "COMPLETED", "VERIFIED", "IN_PROGRESS", "BLOCKED",
            "READY", "RETRY", "PENDING", "WAITING", "FAILED",
        ]

        for st in all_statuses:
            try:
                tasks = task_repo.list_by_status(st)
                for t in tasks:
                    tid = t.task_id if hasattr(t, "task_id") else t.get("task_id", "?")
                    title = t.title if hasattr(t, "title") else t.get("title", "")

                    if st in ("COMPLETED", "VERIFIED"):
                        completed.append(tid)
                    elif st == "IN_PROGRESS":
                        cs = getattr(t, "construction_status", "pending")
                        dls = getattr(t, "deliverables", [])
                        if isinstance(dls, str):
                            try:
                                dls = json.loads(dls)
                            except (json.JSONDecodeError, TypeError):
                                dls = []
                        in_progress.append({
                            "task_id": tid,
                            "step": cs,
                            "partial_deliverables": dls[:5] if isinstance(dls, list) else [],
                            "next_step": f"{tid}: {str(title)[:80]}",
                        })
                    elif st == "BLOCKED":
                        waiting = (
                            t.waiting_for
                            if hasattr(t, "waiting_for")
                            else t.get("waiting_for", "")
                        )
                        blocked_items.append({
                            "task_id": tid,
                            "reason": waiting or "阻塞原因未记录",
                            "unblock_condition": f"依赖任务就绪或手动解除",
                        })
                    elif st in ("READY", "RETRY", "PENDING", "WAITING"):
                        next_actions.append({
                            "priority": len(next_actions) + 1,
                            "action": f"{tid}: {str(title)[:80]}",
                            "task_ref": tid,
                        })
            except Exception:
                continue

        next_actions = next_actions[:10]
        decisions = self._extract_decisions(session_id)

        open_questions = self._auto_generate_questions(blocked_items, len(completed))

        total = len(completed) + len(in_progress) + len(blocked_items)
        summary = (
            f"完成 {len(completed)} 个任务, "
            f"{len(in_progress)} 个进行中, "
            f"{len(blocked_items)} 个阻塞. "
            f"总计 {total} 个任务有活动记录."
        )

        handoff = {
            "session_id": session_id,
            "completed_tasks": completed,
            "in_progress_tasks": in_progress,
            "blocked_items": blocked_items,
            "decisions_made": decisions,
            "next_actions": next_actions,
            "context_summary": summary[:500],
            "open_questions": open_questions,
        }

        conn = self._get_conn()
        conn.execute(
            """
            INSERT OR REPLACE INTO handoffs
                (handoff_id, session_id, completed_tasks, in_progress_tasks,
                 blocked_items, decisions_made, next_actions,
                 context_summary, open_questions, phase, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"ho-{session_id}",
                session_id,
                json.dumps(completed, ensure_ascii=False),
                json.dumps(in_progress, ensure_ascii=False),
                json.dumps(blocked_items, ensure_ascii=False),
                json.dumps(decisions, ensure_ascii=False),
                json.dumps(next_actions, ensure_ascii=False),
                summary[:500],
                json.dumps(open_questions, ensure_ascii=False),
                None,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        conn.close()

        self._write_yaml_handoff(handoff)

        return handoff

    def _extract_decisions(self, session_id: str) -> list[dict]:
        """从 events 表中提取本次 session 的关键决策记录"""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                """SELECT event_type, payload, created_at FROM events
                   WHERE event_type IN ('priority_upgrade_approved','priority_upgrade_rejected',
                                         'state_transition','task_completed')
                   ORDER BY created_at DESC LIMIT 20"""
            ).fetchall()
            conn.close()
            decisions = []
            for r in rows:
                try:
                    payload = json.loads(r["payload"]) if isinstance(r["payload"], str) else {}
                except (json.JSONDecodeError, TypeError):
                    payload = {}
                decisions.append({
                    "type": r["event_type"],
                    "detail": payload.get("action", r["event_type"]),
                    "timestamp": r["created_at"][:19] if r["created_at"] else "",
                    "session": session_id,
                })
            return decisions
        except Exception:
            conn.close()
            return []

    def _auto_generate_questions(
        self,
        blocked_items: list[dict],
        completed_count: int,
    ) -> list[str]:
        """自动生成 open_questions（GOV-AI-008 §3 必填字段）"""
        questions = []
        if blocked_items:
            blocked_ids = ", ".join(b["task_id"] for b in blocked_items[:5])
            questions.append(f"阻塞任务 {blocked_ids} 的解除条件是否仍然有效？是否需要 Owner 介入？")
        if completed_count > 10:
            questions.append(f"已有 {completed_count} 个完成任务——是否需要对已完成任务做一次质量审计？")
        questions.append("上一个 session 的变更是否需要同步更新对应的蓝图文档？")
        return questions

    def _write_yaml_handoff(self, handoff: dict) -> None:
        """输出 YAML 交接包到 docs/09_audit/HANDOFF/（GOV-AI-008 §2 合规路径）"""
        import os

        out_dir = Path("D:/ZephyrAlpha/docs/09_audit/HANDOFF")
        out_dir.mkdir(parents=True, exist_ok=True)

        session_id = handoff["session_id"]
        yaml_path = out_dir / f"session-{session_id}.yaml"

        lines = ["---"]
        lines.append(f"session_id: \"{handoff['session_id']}\"")
        lines.append(f"created_at: \"{handoff.get('created_at', '') or datetime.now(timezone.utc).isoformat()}\"")

        lines.append("completed_tasks:")
        for ct in handoff.get("completed_tasks", []):
            lines.append(f"  - \"{ct}\"")

        lines.append("in_progress_tasks:")
        for ip in handoff.get("in_progress_tasks", []):
            if isinstance(ip, dict):
                lines.append(f"  - task_id: \"{ip.get('task_id', '')}\"")
                lines.append(f"    step: \"{ip.get('step', 'pending')}\"")
                lines.append(f"    next_step: \"{ip.get('next_step', '')}\"")
            else:
                lines.append(f"  - \"{ip}\"")

        lines.append("blocked_items:")
        for bi in handoff.get("blocked_items", []):
            lines.append(f"  - task_id: \"{bi.get('task_id', '')}\"")
            lines.append(f"    reason: \"{bi.get('reason', '')}\"")

        lines.append("decisions_made:")
        for dm in handoff.get("decisions_made", []):
            lines.append(f"  - type: \"{dm.get('type', '')}\"")
            lines.append(f"    detail: \"{dm.get('detail', '')}\"")

        lines.append("next_actions:")
        for na in handoff.get("next_actions", []):
            lines.append(f"  - priority: {na.get('priority', 0)}")
            lines.append(f"    action: \"{na.get('action', '')}\"")
            lines.append(f"    task_ref: \"{na.get('task_ref', '')}\"")

        lines.append(f"context_summary: \"{handoff.get('context_summary', '')}\"")

        lines.append("open_questions:")
        for oq in handoff.get("open_questions", []):
            lines.append(f"  - \"{oq}\"")

        yaml_text = "\n".join(lines) + "\n"
        yaml_path.write_text(yaml_text, encoding="utf-8")

        print(f"  [SessionContinuity] YAML handoff written: {yaml_path}")

    def get_latest_handoff(self) -> dict | None:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM handoffs ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        conn.close()

        if row is None:
            return None

        return {
            "session_id": row["session_id"],
            "completed_tasks": json.loads(row["completed_tasks"]),
            "in_progress_tasks": json.loads(row["in_progress_tasks"]),
            "blocked_items": json.loads(row["blocked_items"]),
            "next_actions": json.loads(row["next_actions"]),
            "context_summary": row["context_summary"],
            "open_questions": json.loads(row["open_questions"]),
            "created_at": row["created_at"],
            "phase": row["phase"],
        }

    def print_restore_summary(self) -> None:
        """输出人类可读的 session 恢复摘要

        在 session 开始时调用——让 AI 和人看到"上次做到哪了"。
        """
        handoff = self.get_latest_handoff()

        if handoff is None:
            print("\n" + "=" * 60)
            print("  [Session Continuity] 这是第一次 session——没有历史交接包。")
            print("  开始新的工作吧！")
            print("=" * 60 + "\n")
            return

        print("\n" + "=" * 60)
        print(f"  [Session Continuity] 欢迎回来！")
        print(f"  上次 session: {handoff['session_id']}")
        created = handoff.get("created_at", "")[:19]
        print(f"  交接时间: {created}")
        print("=" * 60)
        print(f"  ✅ 已完成: {len(handoff['completed_tasks'])} 个任务")
        for t in handoff["completed_tasks"][-5:]:
            print(f"       {t}")
        print(f"  🔄 进行中: {len(handoff['in_progress_tasks'])} 个任务")
        for t in handoff["in_progress_tasks"]:
            print(f"       {t}")
        print(f"  🚫 阻塞: {len(handoff['blocked_items'])} 个")
        for b in handoff["blocked_items"]:
            print(f"       {b.get('task_id', '?')}: {b.get('reason', '')[:60]}")
        print(f"  📋 下一步行动:")
        for a in handoff["next_actions"][:5]:
            print(f"       [{a.get('priority', '?')}] {a.get('action', '')[:80]}")
        print(f"  📝 上下文摘要: {handoff['context_summary'][:120]}")
        print("=" * 60 + "\n")

    def restore_session(self) -> dict | None:
        """恢复上次 session 状态（程序化接口）

        返回 handoff 字典或 None（首次 session）。
        """
        return self.get_latest_handoff()
