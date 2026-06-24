# [BLUEPRINT] SRC-139 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.shared_services.session.session_continuity
# [DOMAIN] D-SHARED
# [DEPENDENCIES]
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

"""
Session Continuity — AI 对话断点续传。

依据：
    蓝图 MOD-INF-006 §6.11.1 + v0.6.0
    任务卡 TASK-INF-0116
"""

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class SessionState:
    session_id: str
    dialogue_number: int
    current_layer: int
    cards_completed: list[str]
    cards_failed: list[str]
    last_checkpoint_json: str
    last_journal_line: int
    timestamp_utc: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ContinuityContext:
    task_id: str
    progress_summary: str
    remaining_cards: list[str]
    key_state: dict[str, Any]
    next_action: str


class SessionContinuity:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._sessions_dir = self._project_root / "session_logs"

    def save_session_state(self, state: SessionState) -> Path:
        self._sessions_dir.mkdir(parents=True, exist_ok=True)

        session_path = self._sessions_dir / f"{state.session_id}.json"

        session_path.write_text(
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

        return session_path

    def load_session_state(self, session_id: str) -> SessionState | None:
        session_path = self._sessions_dir / f"{session_id}.json"

        if not session_path.exists():
            return None

        try:
            data = json.loads(session_path.read_text(encoding="utf-8"))
            return SessionState(
                session_id=data["session_id"],
                dialogue_number=data["dialogue_number"],
                current_layer=data["current_layer"],
                cards_completed=data["cards_completed"],
                cards_failed=data["cards_failed"],
                last_checkpoint_json=data["last_checkpoint_json"],
                last_journal_line=data["last_journal_line"],
                timestamp_utc=data["timestamp_utc"],
                metadata=data.get("metadata", {}),
            )
        except (json.JSONDecodeError, KeyError):
            return None

    def generate_continuity_context(self, state: SessionState) -> ContinuityContext:
        total_done = len(state.cards_completed)
        failed = state.cards_failed

        progress = f"{total_done} cards completed, {len(failed)} failed"

        next_action = "Continue from checkpoint" if total_done > 0 else "Start fresh"

        return ContinuityContext(
            task_id=f"SESSION-{state.session_id}",
            progress_summary=progress,
            remaining_cards=failed,
            key_state={
                "layer": state.current_layer,
                "last_journal_line": state.last_journal_line,
            },
            next_action=next_action,
        )

    def load_checkpoint(self, dialogue_number: int) -> dict[str, Any] | None:
        checkpoint_path = self._project_root / "_journals" / f"checkpoint_{dialogue_number}.json"

        if not checkpoint_path.exists():
            return None

        try:
            return json.loads(checkpoint_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def print_restore_summary(self) -> None:
        sys_master = self._project_root / "docs" / "03_modules" / "_sys-master" / "blueprint.md"
        sessions = sorted(self._sessions_dir.glob("*.json"), reverse=True)

        print("=" * 60)
        print("  Session Continuity — 上下文恢复")
        print("=" * 60)

        if sessions:
            latest = sessions[0]
            try:
                data = json.loads(latest.read_text(encoding="utf-8"))
                print(f"  上一个 session: {data.get('session_id', 'unknown')}")
                print(f"  完成卡片: {len(data.get('cards_completed', []))}")
                print(f"  失败卡片: {len(data.get('cards_failed', []))}")
                print(f"  时间: {data.get('timestamp_utc', 'unknown')}")
            except (json.JSONDecodeError, KeyError, FileNotFoundError):
                print("  (上一 session 记录不可读)")
        else:
            print("  没有发现历史 session 记录——冷启动")

        dispatch_info = self.validate_sys_master_dispatch()
        if dispatch_info["valid"]:
            print("\n  >>> MUST READ: SYS-MASTER-001 §0 分派表")
            print("  >>> 路径: docs/03_modules/_sys-master/blueprint.md")
            print(f"  >>> 版本: {dispatch_info.get('version', '?')}")
            print(f"  >>> 施工进度: {dispatch_info.get('construction_progress', '?')}")
            print(f"  >>> 分派域数: {dispatch_info.get('dispatch_domains', 0)}")
            print(f"  >>> AI 规则数: {dispatch_info.get('ai_rules_count', 0)}")
        else:
            print(f"\n  ⚠️  SYS-MASTER-001 蓝图验证失败: {dispatch_info.get('error', 'unknown')}")

        print("=" * 60)

    def validate_sys_master_dispatch(self) -> dict[str, Any]:
        sys_master = self._project_root / "docs" / "03_modules" / "_sys-master" / "blueprint.md"
        if not sys_master.exists():
            return {"valid": False, "error": "blueprint file missing"}

        try:
            import re

            text = sys_master.read_text(encoding="utf-8")
            if text.startswith("\ufeff"):
                text = text[1:]
            fm_match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
            if not fm_match:
                return {"valid": False, "error": "no YAML frontmatter"}

            import yaml

            fm = yaml.safe_load(fm_match.group(1)) or {}

            ai_role = fm.get("ai_role_instruction", "")
            if isinstance(ai_role, str):
                rules = re.findall(r"\(\d+\)", ai_role)
                ai_rules_count = len(rules)
            else:
                ai_rules_count = 0

            dispatch_section = re.search(r"### 0\.2 AI Agent 分派表.*?\n\n((?:\|.*\n)+)", text, re.MULTILINE)
            dispatch_domains = 0
            if dispatch_section:
                lines = dispatch_section.group(1).strip().split("\n")
                dispatch_domains = len([l for l in lines if l.startswith("|") and "---" not in l and "任务域" not in l])

            return {
                "valid": True,
                "version": fm.get("version", "unknown"),
                "construction_progress": fm.get("construction_progress", "unknown"),
                "dispatch_domains": max(0, dispatch_domains),
                "ai_rules_count": ai_rules_count,
                "depends_on_count": len(fm.get("depends_on", [])),
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def generate_and_save(
        self,
        session_id: str,
        task_repo: object | None = None,
        cards_completed: list[str] | None = None,
        cards_failed: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        now_utc = datetime.now(UTC).isoformat()

        state = SessionState(
            session_id=session_id,
            dialogue_number=1,
            current_layer=0,
            cards_completed=cards_completed or [],
            cards_failed=cards_failed or [],
            last_checkpoint_json=now_utc,
            last_journal_line=0,
            timestamp_utc=now_utc,
            metadata=metadata or {},
        )

        return self.save_session_state(state)
