# [BLUEPRINT] SRC-140 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.session.session_continuity
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_session_continuity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
SessionContinuity — Session 交接包自动生成与恢复
=================================================
依据：MOD-TASK_SYSTEM v0.3.2（零记忆重启机制）

Vibe Coding 最大痛点：AI 每次新 session 是零记忆的。
本模块解决"打开 IDE 不知道上回做到哪了"的问题。

注意：本模块使用纯 Python + sqlite3，不 import zephyr.shared（避让已知导入链断裂）。

用法：
    from zephyr.shared.session.session_continuity import SessionContinuity

    sc = SessionContinuity()

    # session 结束时
    sc.generate_and_save(session_id="sess-2026-05-05", task_repo=repo)

    # session 开始时
    sc.print_restore_summary()
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json
import re
import sqlite3
from zephyr.shared.io.sqlite_factory import get_db_connection
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from zephyr.shared.io.paths import REPO_ROOT

__all__ = ["ContinuityContext", "SessionContinuity", "SessionState"]


@dataclass
class SessionState:
    session_id: str = ""
    dialogue_number: int = 0
    current_layer: int = 0
    cards_completed: list[str] = field(default_factory=list)
    cards_failed: list[str] = field(default_factory=list)
    last_checkpoint_json: str = ""
    last_journal_line: int = 0
    timestamp_utc: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ContinuityContext:
    task_id: str = ""
    progress_summary: str = ""
    remaining_cards: list[str] = field(default_factory=list)
    key_state: dict[str, Any] = field(default_factory=dict)
    next_action: str = ""


_DEFAULT_DB: Path | None = None


def _get_default_db() -> Path:
    global _DEFAULT_DB
    if _DEFAULT_DB is None:
        try:
            from zephyr.shared.protocols.registry import ServiceRegistry

            _DEFAULT_DB = ServiceRegistry.get("db_path")
        except KeyError:
            _DEFAULT_DB = Path.cwd() / "data" / "databases" / "session_continuity.db"
    return _DEFAULT_DB


_DDL_handoffS = """
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

    def __init__(self, db_path: str | Path | None = None, project_root: str | Path | None = None) -> None:
        if project_root:
            self._project_root = Path(project_root)
        else:
            self._project_root = Path.cwd()
        self._sessions_dir = self._project_root / "session_logs"
        if db_path:
            self._db_path = Path(db_path)
        else:
            try:
                from zephyr.shared.protocols.registry import ServiceRegistry

                if ServiceRegistry.is_registered("db_path"):
                    self._db_path = ServiceRegistry.get("db_path")
                else:
                    self._db_path = self._project_root / "data" / "databases" / "session_continuity.db"
            except Exception:
                self._db_path = self._project_root / "data" / "databases" / "session_continuity.db"
        self._init_schema()

    def _get_conn(self) -> sqlite3.Connection:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = get_db_connection(str(self._db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        conn = self._get_conn()
        conn.execute(_DDL_handoffS)
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    def save_session_state(self, state: SessionState) -> Path:
        if not state.timestamp_utc:
            state.timestamp_utc = datetime.now(UTC).isoformat()
        state_dir = self._sessions_dir
        state_dir.mkdir(parents=True, exist_ok=True)
        state_path = state_dir / f"{state.session_id}.json"
        state_path.write_text(
            json.dumps(
                {
                    "session_id": state.session_id,
                    "dialogue_number": state.dialogue_number,
                    "current_layer": state.current_layer,
                    "cards_completed": state.cards_completed,
                    "cards_failed": state.cards_failed,
                    "last_checkpoint_json": state.last_checkpoint_json,
                    "last_journal_line": state.last_journal_line,
                    "timestamp_utc": state.timestamp_utc,
                    "metadata": state.metadata,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        conn = self._get_conn()
        conn.execute(
            "INSERT INTO handoffs (session_id, completed_tasks, in_progress_tasks, blocked_items, next_actions, context_summary, open_questions, phase, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                state.session_id,
                json.dumps(state.cards_completed),
                json.dumps([]),
                json.dumps([]),
                json.dumps([]),
                "",
                json.dumps([]),
                "",
                state.timestamp_utc,
            ),
        )
        conn.commit()
        conn.close()

        return state_path

    def load_session_state(self, session_id: str) -> SessionState | None:
        state_path = self._sessions_dir / f"{session_id}.json"
        if not state_path.exists():
            return None
        try:
            data = json.loads(state_path.read_text(encoding="utf-8"))
            required_keys = {
                "session_id",
                "dialogue_number",
                "current_layer",
                "cards_completed",
                "cards_failed",
                "last_checkpoint_json",
                "last_journal_line",
                "timestamp_utc",
            }
            if not required_keys.issubset(data.keys()):
                return None
            return SessionState(
                session_id=data.get("session_id", ""),
                dialogue_number=data.get("dialogue_number", 0),
                current_layer=data.get("current_layer", 0),
                cards_completed=data.get("cards_completed", []),
                cards_failed=data.get("cards_failed", []),
                last_checkpoint_json=data.get("last_checkpoint_json", ""),
                last_journal_line=data.get("last_journal_line", 0),
                timestamp_utc=data.get("timestamp_utc", ""),
                metadata=data.get("metadata", {}),
            )
        except (json.JSONDecodeError, OSError):
            return None

    def generate_continuity_context(self, state: SessionState) -> ContinuityContext:
        completed = len(state.cards_completed)
        failed = len(state.cards_failed)
        summary = f"{completed} cards completed, {failed} failed"
        remaining = list(state.cards_failed)
        if state.last_checkpoint_json:
            next_action = "Continue from checkpoint"
        elif not completed and not failed:
            next_action = "Start fresh"
        elif state.cards_completed:
            next_action = f"Continue from last completed: {state.cards_completed[-1]}"
        elif state.cards_failed:
            next_action = f"Retry failed: {state.cards_failed[0]}"
        else:
            next_action = "Start fresh"
        return ContinuityContext(
            task_id=f"SESSION-{state.session_id}",
            progress_summary=summary,
            remaining_cards=remaining,
            key_state={"layer": state.current_layer, "last_journal_line": state.last_journal_line},
            next_action=next_action,
        )

    def generate_and_save(
        self,
        session_id: str = "",
        task_repo: object | None = None,
        *,
        cards_completed: list[str] | None = None,
        cards_failed: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Path | dict[str, Any]:
        if cards_completed is not None or cards_failed is not None:
            state = SessionState(
                session_id=session_id,
                cards_completed=cards_completed or [],
                cards_failed=cards_failed or [],
                timestamp_utc=datetime.now(UTC).isoformat(),
                metadata=metadata or {},
            )
            path = self.save_session_state(state)
            return path
        if task_repo is not None:
            return self._generate_and_save_legacy(session_id, task_repo)
        state = SessionState(session_id=session_id, timestamp_utc=datetime.now(UTC).isoformat())
        return self.save_session_state(state)

    def load_checkpoint(self, step: int) -> dict | None:
        """从 _journals 目录加载检查点"""
        cp_path = self._project_root / "_journals" / f"checkpoint_{step}.json"
        if not cp_path.exists():
            return None
        try:
            return json.loads(cp_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def validate_sys_master_dispatch(self) -> dict:
        """验证 _sys_master 蓝图的分派表"""
        bp_path = self._project_root / "docs" / "03_modules" / "_system_master" / "blueprint.md"
        if not bp_path.exists():
            return {"valid": False, "error": "missing: docs/03_modules/_system_master/blueprint.md"}
        try:
            content = bp_path.read_text(encoding="utf-8")
        except OSError:
            return {"valid": False, "error": "missing: docs/03_modules/_system_master/blueprint.md"}
        if not content.startswith("---"):
            return {"valid": False, "error": "no frontmatter found"}
        fm_end = content.find("---", 3)
        if fm_end == -1:
            return {"valid": False, "error": "no frontmatter found"}
        fm_text = content[3:fm_end]
        fm = {}
        for line in fm_text.strip().splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                fm[k.strip()] = v.strip().strip("'\"")
        version = fm.get("version", "")
        construction_progress = fm.get("construction_progress", "")
        ai_role = fm.get("ai_role_instruction", "")
        rule_count = len(re.findall(r"\(\d+\)", ai_role))
        # 解析分派表数据行数
        body = content[fm_end + 3 :]
        table_lines = [
            line
            for line in body.splitlines()
            if line.strip().startswith("|") and "---" not in line
        ]
        dispatch_domains = max(0, len(table_lines) - 1)
        return {
            "valid": True,
            "version": version,
            "construction_progress": construction_progress,
            "ai_rules_count": rule_count,
            "dispatch_domains": dispatch_domains,
        }

    def _generate_and_save_legacy(self, session_id: str, task_repo: object) -> dict:
        """从 task_repo 汇总当前状态 -> 生成 HandoffPackage -> 写 SQLite + YAML

        GOV-AI-008 (handoff-protocol.md) 合规实现：
        - 8 必填字段全部自动填充
        - decisions_made 从 events 表读取
        - in_progress_tasks 含 step/construction_status/deliverables
        - open_questions 自动从 BLOCKED ≥2 session 的任务生成
        - 同步输出 YAML 到 docs/_working/audit/handoff/
        """
        completed = []
        in_progress = []
        blocked_items = []
        next_actions = []

        all_statuses = [
            "COMPLETED",
            "VERIFIED",
            "IN_PROGRESS",
            "BLOCKED",
            "READY",
            "RETRY",
            "PENDING",
            "WAITING",
            "FAILED",
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
                        in_progress.append(
                            {
                                "task_id": tid,
                                "step": cs,
                                "partial_deliverables": dls[:5] if isinstance(dls, list) else [],
                                "next_step": f"{tid}: {str(title)[:80]}",
                            }
                        )
                    elif st == "BLOCKED":
                        waiting = t.waiting_for if hasattr(t, "waiting_for") else t.get("waiting_for", "")
                        blocked_items.append(
                            {
                                "task_id": tid,
                                "reason": waiting or "阻塞原因未记录",
                                "unblock_condition": "依赖任务就绪或手动解除",
                            }
                        )
                    elif st in ("READY", "RETRY", "PENDING", "WAITING"):
                        next_actions.append(
                            {
                                "priority": len(next_actions) + 1,
                                "action": f"{tid}: {str(title)[:80]}",
                                "task_ref": tid,
                            }
                        )
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
                datetime.now(UTC).isoformat(),
            ),
        )
        conn.commit()
        conn.close()

        self._write_yaml_handoff(handoff)

        write_to_core(
            "session_handoff",
            {
                "session_id": session_id,
                "completed": len(completed),
                "in_progress": len(in_progress),
                "blocked": len(blocked_items),
            },
        )

        self._auto_sync_registries()

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
                decisions.append(
                    {
                        "type": r["event_type"],
                        "detail": payload.get("action", r["event_type"]),
                        "timestamp": r["created_at"][:19] if r["created_at"] else "",
                        "session": session_id,
                    }
                )
            return decisions
        except Exception:
            conn.close()
            return []

    @staticmethod
    def _auto_sync_registries() -> None:
        try:
            import subprocess

            script = (
                REPO_ROOT
                / "scripts"
                / "governance"
                / "auto_sync_all_registries.py"
            )
            if script.exists():
                subprocess.run(
                    [sys.executable, str(script), "--all", "--warn-only"],
                    timeout=30,
                    capture_output=True,
                )
        except Exception as e:
            logger.warning("suppressed error in session_continuity", exc_info=True)

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
        """输出 YAML 交接包到 docs/_working/audit/handoff/（GOV-AI-008 §2 合规路径）"""

        out_dir = self._project_root / "docs" / "_working" / "audit" / "handoff"
        out_dir.mkdir(parents=True, exist_ok=True)

        session_id = handoff["session_id"]
        yaml_path = out_dir / f"session-{session_id}.yaml"

        lines = ["---"]
        lines.append(f'session_id: "{handoff["session_id"]}"')
        lines.append(f'created_at: "{handoff.get("created_at", "") or datetime.now(UTC).isoformat()}"')

        lines.append("completed_tasks:")
        for ct in handoff.get("completed_tasks", []):
            lines.append(f'  - "{ct}"')

        lines.append("in_progress_tasks:")
        for ip in handoff.get("in_progress_tasks", []):
            if isinstance(ip, dict):
                lines.append(f'  - task_id: "{ip.get("task_id", "")}"')
                lines.append(f'    step: "{ip.get("step", "pending")}"')
                lines.append(f'    next_step: "{ip.get("next_step", "")}"')
            else:
                lines.append(f'  - "{ip}"')

        lines.append("blocked_items:")
        for bi in handoff.get("blocked_items", []):
            lines.append(f'  - task_id: "{bi.get("task_id", "")}"')
            lines.append(f'    reason: "{bi.get("reason", "")}"')

        lines.append("decisions_made:")
        for dm in handoff.get("decisions_made", []):
            lines.append(f'  - type: "{dm.get("type", "")}"')
            lines.append(f'    detail: "{dm.get("detail", "")}"')

        lines.append("next_actions:")
        for na in handoff.get("next_actions", []):
            lines.append(f"  - priority: {na.get('priority', 0)}")
            lines.append(f'    action: "{na.get("action", "")}"')
            lines.append(f'    task_ref: "{na.get("task_ref", "")}"')

        lines.append(f'context_summary: "{handoff.get("context_summary", "")}"')

        lines.append("open_questions:")
        for oq in handoff.get("open_questions", []):
            lines.append(f'  - "{oq}"')

        yaml_text = "\n".join(lines) + "\n"
        yaml_path.write_text(yaml_text, encoding="utf-8")

        print(f"  [SessionContinuity] YAML handoff written: {yaml_path}")

    def get_latest_handoff(self) -> dict | None:
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM handoffs ORDER BY created_at DESC LIMIT 1").fetchone()
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

    def _detect_agent_context(self) -> dict:
        """检测当前 Agent 的 IDE 来源与可能的身份信息。

        通过环境变量检测 IDE 来源，尝试读取 rbac_roles.yaml 获取身份推断。
        所有检测均为 best-effort——检测不到时返回保守默认值。
        """
        import os

        ide_source = "unknown"
        if os.environ.get("TRAE_BRAND_NAME") or os.environ.get("TRAE_AI_SHELL_ID"):
            ide_source = "trae"
        elif os.environ.get("CURSOR") or os.environ.get("CURSOR_TRACE_ID"):
            ide_source = "cursor"
        elif os.environ.get("VSCODE_PID") or os.environ.get("VSCODE_IPC_HOOK_CLI"):
            ide_source = "vscode"

        rbac_info = self._try_load_rbac_config(ide_source)

        return {
            "ide_source": ide_source,
            "maturity": rbac_info.get("maturity", "unknown"),
            "role": rbac_info.get("role", "unknown"),
            "auto_guard_eligible": rbac_info.get("auto_guard_eligible", False),
            "owner_approved": rbac_info.get("owner_approved", False),
        }

    @staticmethod
    def _try_load_rbac_config(ide_source: str) -> dict:
        """尝试从 rbac_roles.yaml 加载当前 IDE 对应的 Agent 配置。"""
        try:
            import yaml

            rbac_path = self._project_root / "config" / "rbac_roles.yaml"
            if not rbac_path.exists():
                return {}

            with open(rbac_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if not config or "agents" not in config:
                return {}

            agent_map = {
                "trae": "agent_architect",
                "cursor": "agent_writer",
                "vscode": "agent_writer",
            }
            agent_name = agent_map.get(ide_source)

            if agent_name and agent_name in config["agents"]:
                agent_cfg = config["agents"][agent_name]
                return {
                    "maturity": agent_cfg.get("maturity", "unknown"),
                    "role": agent_name,
                    "auto_guard_eligible": agent_cfg.get("auto_guard_eligible", False),
                    "owner_approved": agent_cfg.get("owner_approved", False),
                }

            return {}
        except Exception:
            return {}

    def print_restore_summary(self) -> None:
        """输出人类可读的 session 恢复摘要

        在 session 开始时调用——让 AI 和人看到"上次做到哪了"以及当前 Agent 身份。
        """
        agent_ctx = self._detect_agent_context()

        if agent_ctx["ide_source"] != "unknown":
            owner_flag = " ✓Owner已审批" if agent_ctx["owner_approved"] else ""
            auto_flag = " [auto_guard]" if agent_ctx["auto_guard_eligible"] else ""
            print(f"\n{'=' * 60}")
            print(
                f"  [Agent Identity] IDE={agent_ctx['ide_source']}"
                f" | Maturity={agent_ctx['maturity']}"
                f" | Role={agent_ctx['role']}{auto_flag}{owner_flag}"
            )
            print(f"{'=' * 60}")

        handoff = self.get_latest_handoff()

        if handoff is None:
            print(f"\n{'=' * 60}")
            print("  [Session Continuity] 冷启动——没有发现历史交接包。")
            print("  开始新的工作吧！")
            print("=" * 60 + "\n")
            return

        print("\n" + "=" * 60)
        print("  [Session Continuity] 欢迎回来！")
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
        print("  📋 下一步行动:")
        for a in handoff["next_actions"][:5]:
            print(f"       [{a.get('priority', '?')}] {a.get('action', '')[:80]}")
        print(f"  📝 上下文摘要: {handoff['context_summary'][:120]}")
        print("=" * 60 + "\n")

    @staticmethod
    def _print_asset_summary() -> None:
        try:
            import yaml as _yaml

            index_path = self._project_root / "data" / "asset_index" / "unified-asset-index.yaml"
            if not index_path.exists():
                return
            with open(index_path, encoding="utf-8") as f:
                data = _yaml.safe_load(f) or {}
            health_data = data.get("health", {})
            health = health_data.get("health_grade", health_data.get("health_score", "?"))
            total = data.get("total_assets", "?")
            orphan_data = data.get("orphan_risk", {})
            orphan_rate = orphan_data.get("orphan_rate", "?")
            if orphan_rate != "?" and isinstance(orphan_rate, (int, float)):
                orphan_rate = f"{orphan_rate * 100:.1f}"
            gen = str(data.get("generated_at", "?"))[:19]
            print(f"  [Asset Inventory] 资产: {total} | 健康: {health} | 孤儿率: {orphan_rate}% | 生成: {gen}")
        except Exception as e:
            logger.debug("suppressed error in session_continuity", exc_info=True)

    def restore_session(self) -> dict | None:
        """恢复上次 session 状态（程序化接口）

        返回 handoff 字典或 None（首次 session）。
        """
        return self.get_latest_handoff()
