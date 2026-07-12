# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.session.session_audit
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.gov_audit.writer
# [CONSUMERS] governance/constitutional_update.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_session_audit | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
session_audit.py —— Session 审计轨迹（Phase 12 | 盲点 B32）

痛点修复：每次 AI session 的记录——prompts/decisions/tool_calls/costs/errors/outcomes。
1人+AI 维护下唯一的学习来源。

设计对标：
  - PydanticAI Logfire audit: 结构化审计日志
  - LangChain callback system: 事件追踪
  - Session Log Schema (GOV-AI-007 v2.2.0): 字段对齐

AI 施工约定：
  - 每个 session MUST 通过 SessionAuditTrail 记录
  - JSONL 格式追加写入——不可变审计
  - 与 session_logs/ YAML 互补（此模块负责运行时实时记录）

SSoT: MOD-INF-016 §12 盲点 B32 + GOV-AI-007 Session Log Schema
"""

from __future__ import annotations

import json
import logging
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PromptRecord:
    """单次 prompt 记录。"""

    timestamp: str
    role: str
    content_preview: str
    token_count: int = 0


@dataclass
class DecisionRecord:
    """单次决策记录。"""

    timestamp: str
    decision_id: str
    summary: str
    rationale: str
    alternatives: list[str] = field(default_factory=list)


@dataclass
class ToolCallRecord:
    """单次工具调用记录。"""

    timestamp: str
    tool_name: str
    parameters_preview: str
    result_summary: str
    duration_ms: float = 0.0
    success: bool = True


@dataclass
class CostRecord:
    """单次成本记录。"""

    timestamp: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0


@dataclass
class ErrorRecord:
    """单次错误记录。"""

    timestamp: str
    error_type: str
    message: str
    recovery_action: str = ""
    recovered: bool = False


@dataclass
class OutcomeRecord:
    """最终产出记录。"""

    timestamp: str
    files_created: list[str] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)
    tests_run: int = 0
    tests_passed: int = 0
    knowledge_extracted: int = 0
    deviations_found: int = 0


@dataclass
class SessionRecord:
    """一次 AI session 的完整审计记录。

    与 GOV-AI-007 Session Log Schema 字段对齐。
    """

    session_id: str
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    ended_at: str | None = None

    prompts: list[PromptRecord] = field(default_factory=list)
    decisions: list[DecisionRecord] = field(default_factory=list)
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    costs: list[CostRecord] = field(default_factory=list)
    errors: list[ErrorRecord] = field(default_factory=list)
    outcomes: OutcomeRecord | None = None

    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def total_cost_usd(self) -> float:
        return sum(c.cost_usd for c in self.costs)

    @property
    def total_tokens(self) -> int:
        return sum(c.input_tokens + c.output_tokens for c in self.costs)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def recovered_count(self) -> int:
        return sum(1 for e in self.errors if e.recovered)

    def add_prompt(self, role: str, content: str, token_count: int = 0) -> PromptRecord:
        preview = content[:200] + "..." if len(content) > 200 else content
        record = PromptRecord(
            timestamp=datetime.now(UTC).isoformat(),
            role=role,
            content_preview=preview,
            token_count=token_count,
        )
        self.prompts.append(record)
        return record

    def add_decision(
        self, decision_id: str, summary: str, rationale: str, alternatives: list[str] | None = None
    ) -> DecisionRecord:
        record = DecisionRecord(
            timestamp=datetime.now(UTC).isoformat(),
            decision_id=decision_id,
            summary=summary,
            rationale=rationale,
            alternatives=alternatives or [],
        )
        self.decisions.append(record)
        return record

    def add_tool_call(
        self, tool_name: str, params: str, result: str, duration_ms: float = 0.0, success: bool = True
    ) -> ToolCallRecord:
        record = ToolCallRecord(
            timestamp=datetime.now(UTC).isoformat(),
            tool_name=tool_name,
            parameters_preview=params[:200],
            result_summary=result[:200],
            duration_ms=duration_ms,
            success=success,
        )
        self.tool_calls.append(record)
        return record

    def add_cost(
        self, provider: str, model: str, input_tokens: int = 0, output_tokens: int = 0, cost_usd: float = 0.0
    ) -> CostRecord:
        record = CostRecord(
            timestamp=datetime.now(UTC).isoformat(),
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
        )
        self.costs.append(record)
        return record

    def add_error(
        self, error_type: str, message: str, recovery_action: str = "", recovered: bool = False
    ) -> ErrorRecord:
        record = ErrorRecord(
            timestamp=datetime.now(UTC).isoformat(),
            error_type=error_type,
            message=message,
            recovery_action=recovery_action,
            recovered=recovered,
        )
        self.errors.append(record)
        return record

    def set_outcomes(self, **kwargs: Any) -> OutcomeRecord:
        self.outcomes = OutcomeRecord(
            timestamp=datetime.now(UTC).isoformat(),
            **kwargs,
        )
        return self.outcomes

    def finish(self) -> None:
        self.ended_at = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "prompts_count": len(self.prompts),
            "decisions_count": len(self.decisions),
            "tool_calls_count": len(self.tool_calls),
            "total_cost_usd": round(self.total_cost_usd, 6),
            "total_tokens": self.total_tokens,
            "error_count": self.error_count,
            "recovered_count": self.recovered_count,
            "prompts": [
                {"ts": p.timestamp, "role": p.role, "preview": p.content_preview, "tokens": p.token_count}
                for p in self.prompts
            ],
            "decisions": [
                {"ts": d.timestamp, "id": d.decision_id, "summary": d.summary, "rationale": d.rationale}
                for d in self.decisions
            ],
            "tool_calls": [
                {
                    "ts": t.timestamp,
                    "tool": t.tool_name,
                    "params": t.parameters_preview,
                    "result": t.result_summary,
                    "duration_ms": t.duration_ms,
                    "success": t.success,
                }
                for t in self.tool_calls
            ],
            "costs": [
                {
                    "ts": c.timestamp,
                    "provider": c.provider,
                    "model": c.model,
                    "input": c.input_tokens,
                    "output": c.output_tokens,
                    "cost_usd": c.cost_usd,
                }
                for c in self.costs
            ],
            "errors": [
                {
                    "ts": e.timestamp,
                    "type": e.error_type,
                    "message": e.message,
                    "recovery": e.recovery_action,
                    "recovered": e.recovered,
                }
                for e in self.errors
            ],
        }
        if self.outcomes:
            result["outcomes"] = {
                "files_created": self.outcomes.files_created,
                "files_modified": self.outcomes.files_modified,
                "tests_run": self.outcomes.tests_run,
                "tests_passed": self.outcomes.tests_passed,
                "knowledge_extracted": self.outcomes.knowledge_extracted,
                "deviations_found": self.outcomes.deviations_found,
            }
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class SessionAuditTrail:
    """Session 审计轨迹管理器——JSONL 格式追加写入。

    Usage::

        trail = SessionAuditTrail(audit_dir="logs/audit/")
        record = trail.start_session("session-20260507-001")
        record.add_decision("D1", "Use SQLite", "Lightweight, zero-config")
        trail.append_record(record)
        results = trail.query("session-20260507-001")
    """

    def __init__(self, audit_dir: str = "logs/session_audit/"):
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    @staticmethod
    def _sanitize_session_id(session_id: str) -> str:
        return session_id.replace("\\", "_").replace("/", "_").replace("..", "_")

    def _session_path(self, session_id: str) -> Path:
        safe_id = self._sanitize_session_id(session_id)
        return self.audit_dir / f"{safe_id}.jsonl"

    def start_session(self, session_id: str) -> SessionRecord:
        return SessionRecord(session_id=session_id)

    def append_record(self, record: SessionRecord) -> Path:
        filepath = self._session_path(record.session_id)
        record_dict = record.to_dict()
        with self._lock, open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(record_dict, ensure_ascii=False) + "\n")
        try:
            from zephyr.gov_audit.writer import get_audit_writer
        except ImportError as e:
            logger.warning(
                "session_audit: audit_trail.writer import failed, skipping audit (%s: %s)",
                type(e).__name__,
                e,
            )
        else:
            try:
                get_audit_writer().write(
                    {
                        "event_type": "session_record",
                        "action_type": "session_record",
                        "agent_id": record_dict.get("session_id", "unknown"),
                        "session_id": record_dict.get("session_id", ""),
                        "target_path": str(filepath),
                        "operation": "append_record",
                    }
                )
            except Exception as e:
                logger.warning("suppressed error in session_audit", exc_info=True)
        return filepath

    def query(self, session_id: str) -> list[dict[str, Any]]:
        filepath = self._session_path(session_id)
        if not filepath.exists():
            return []
        results: list[dict[str, Any]] = []
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    results.append(json.loads(line))
        return results

    def export_jsonl(self, session_id: str) -> str:
        filepath = self._session_path(session_id)
        if not filepath.exists():
            return ""
        with open(filepath, encoding="utf-8") as f:
            return f.read()

    def list_sessions(self) -> list[str]:
        sessions: list[str] = []
        for f in self.audit_dir.glob("*.jsonl"):
            sessions.append(f.stem)
        return sorted(sessions)

    def get_summary(self, session_id: str) -> dict[str, Any]:
        records = self.query(session_id)
        if not records:
            return {"session_id": session_id, "record_count": 0}
        total_cost = sum(r.get("total_cost_usd", 0) for r in records)
        total_tokens = sum(r.get("total_tokens", 0) for r in records)
        total_errors = sum(r.get("error_count", 0) for r in records)
        total_decisions = sum(r.get("decisions_count", 0) for r in records)
        return {
            "session_id": session_id,
            "record_count": len(records),
            "total_cost_usd": round(total_cost, 6),
            "total_tokens": total_tokens,
            "total_errors": total_errors,
            "total_decisions": total_decisions,
        }


__all__ = [
    "CostRecord",
    "DecisionRecord",
    "ErrorRecord",
    "OutcomeRecord",
    "PromptRecord",
    "SessionAuditTrail",
    "SessionRecord",
    "ToolCallRecord",
]
