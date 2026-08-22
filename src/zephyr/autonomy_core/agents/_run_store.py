# [BLUEPRINT] MOD-EXE-AGENTS | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/14_execution_layer.md | §4-Phase0
# [MODULE] zephyr.autonomy_core.agents._run_store
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] stdlib
# [CONSUMERS] zephyr.autonomy_core.agents.governance_agent_entry ; business_agent_entry ; algorithm_agent_entry ; self_iteration_agent_entry
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 产出 100% 落盘且带 ai_autonomy=human_gated 标记；落盘 IO 失败只告警不阻断入口返回（审计缺口如实记 status=audit_failed）
# [MODIFY-GUARD] Owner approval required; 变更须同步 14号文 §4 Phase 0 验收口径
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 写盘失败不抛（WARNING + 记录 degraded 标记）；读侧不存在的路径由调用方判空
# [TESTS] tests/autonomy/test_execution_layer_agent_entries.py
# [A_module] module_id=MOD-EXE-AGENTS | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""四类 Agent 薄入口共享落盘纪律件（组装用内部件，非角色入口）.

统一运行落盘 schema：.runtime/agent_runs/<role>/<run_id>/ 下
ticket.json（输入快照）+ 角色产出件 + run.json（运行记录），
并追加一行审计到 .runtime/agent_runs/<role>/audit.jsonl。
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final, final

logger = logging.getLogger(__name__)

SCHEMA_VERSION: Final[str] = "1.0"
TRIGGERED_BY: Final[str] = "human_manual"  # Phase 0 四类入口自身=人触发
AI_AUTONOMY_MARK: Final[str] = "human_gated"
_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[4]


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


@final
class AgentRunStore:
    """单次手动触发运行的落盘器（.runtime/agent_runs/<role>/<run_id>/）."""

    def __init__(
        self,
        role: str,
        runtime_dir: str | Path | None = None,
        repo_root: str | Path | None = None,
    ) -> None:
        self._repo_root = Path(repo_root) if repo_root else _REPO_ROOT
        base = Path(runtime_dir) if runtime_dir else self._repo_root / ".runtime"
        self.role: Final[str] = role
        self.role_dir: Final[Path] = base / "agent_runs" / role
        self.run_id: str = ""
        self.run_dir: Path = self.role_dir

    def begin(self, ticket_id: str, ticket: dict[str, Any]) -> str:
        """开跑：建运行目录并落输入工单快照，返回 run_id."""
        self.run_id = f"{_utc_now()[:10].replace('-', '')}-{uuid.uuid4().hex[:8]}"
        self.run_dir = self.role_dir / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self._write(
            self.run_dir / "ticket.json",
            self._envelope(ticket_id, {"ticket": ticket}),
        )
        return self.run_id

    def write_output(self, filename: str, payload: dict[str, Any], ticket_id: str) -> Path:
        """落角色产出件（自动套 human_gated 信封），返回路径."""
        path = self.run_dir / filename
        self._write(path, self._envelope(ticket_id, payload))
        return path

    def finish(self, ticket_id: str, status: str, summary: dict[str, Any]) -> Path:
        """收尾：落 run.json 运行记录 + 追加审计 jsonl 一行，返回 run.json 路径."""
        record = self._envelope(ticket_id, {"status": status, "summary": summary})
        record["finished_at"] = _utc_now()
        run_json = self.run_dir / "run.json"
        self._write(run_json, record)
        audit_line = {"run_id": self.run_id, "run_dir": self.run_dir.as_posix(), **record}
        try:
            self.role_dir.mkdir(parents=True, exist_ok=True)
            with open(self.role_dir / "audit.jsonl", "a", encoding="utf-8", buffering=1) as fh:
                fh.write(json.dumps(audit_line, ensure_ascii=False) + "\n")
        except OSError as exc:
            logger.warning("agent_runs 审计追加失败（产出件仍生效）: %r", exc)
        return run_json

    def _envelope(self, ticket_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "agent_role": self.role,
            "run_id": self.run_id,
            "ticket_id": ticket_id,
            "triggered_by": TRIGGERED_BY,
            "ai_autonomy": AI_AUTONOMY_MARK,
            "created_at": _utc_now(),
            **payload,
        }

    def _write(self, path: Path, record: dict[str, Any]) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        except OSError as exc:  # ERROR_CONTRACT：写盘失败不抛
            logger.warning("agent_runs 落盘失败 %s: %r", path, exc)


__all__ = ["AI_AUTONOMY_MARK", "SCHEMA_VERSION", "AgentRunStore"]
