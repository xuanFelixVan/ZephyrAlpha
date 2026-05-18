# [BLUEPRINT] MOD-INF-020 | 03_modules/l01_infrastructure/audit-trail/blueprint.md | §

# [MODULE] zephyr.audit_trail.query

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
audit_trail.query — MOD-INF-020 · 审计查询接口
==================================================
蓝图 §4 · 结构化查询 + trail_for_ai_context() + Prompt 注入防护

功能
----
  - by_agent / by_session / by_timerange / by_event_type / by_task / by_target
  - by_permission_level / by_anomaly / by_drift / by_cost
  - search(keyword): 全文关键词搜索
  - trail_for_ai_context(session_id): 新AI session上线——返回最近审计上下文（含 Prompt 注入防护 D-020-31）
  - verify_integrity(fast_mode): 完整性快速校验
  - rebuild_index(): 从 JSONL 重建 SQLite 索引
  - meta_audit_log: 元审计（谁查了审计日志）
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import unicodedata
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.audit_trail.models import IntegrityReport

_logger = logging.getLogger(__name__)

DEFAULT_EVENT_LOG: Path = Path("data/audit_trail/events.jsonl")
MAX_TRAIL_ENTRIES = 50
TRAIL_TOKEN_BUDGET = 2000
_MAX_ENTRY_CHARS_FOR_AI = 500

_INJECTION_PATTERNS = re.compile(
    r"(ignore|disregard|override|bypass|forget|skip)\s+(all|previous|above|prior|instructions|rules)",
    re.IGNORECASE,
)
_ROLE_PREFIX_PATTERN = re.compile(r"^(system|assistant|user|function|tool)\s*:", re.IGNORECASE | re.MULTILINE)
_CODE_FENCE_PATTERN = re.compile(r"```", re.MULTILINE)
_MARKDOWN_HR_PATTERN = re.compile(r"^(---|===)\s*$", re.MULTILINE)
_TOOL_CALL_PATTERN = re.compile(r"<(function_call|invoke|tool_call)", re.IGNORECASE)


def _sanitize_for_ai_context(text: str) -> str:
    if not text:
        return text
    text = unicodedata.normalize("NFKC", text)
    text = _INJECTION_PATTERNS.sub("[REDACTED_INSTRUCTION]", text)
    text = _ROLE_PREFIX_PATTERN.sub("[REDACTED_ROLE]", text)
    text = _CODE_FENCE_PATTERN.sub("` ` `", text)
    text = _MARKDOWN_HR_PATTERN.sub("—", text)
    text = _TOOL_CALL_PATTERN.sub("[REDACTED_TAG]", text)
    if len(text) > _MAX_ENTRY_CHARS_FOR_AI:
        text = text[:_MAX_ENTRY_CHARS_FOR_AI] + "...[truncated]"
    return text


class MetaAuditLogger:
    def __init__(self) -> None:
        self._log: list[dict[str, Any]] = []

    def log_audit_query(self, querier: str, query_params: dict[str, Any]) -> None:
        self._log.append({
            "operation": "audit_query",
            "querier": querier,
            "params": query_params,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    def log_index_rebuild(self, trigger: str, entries_count: int) -> None:
        self._log.append({
            "operation": "index_rebuild",
            "trigger": trigger,
            "entries_count": entries_count,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    def log_integrity_check(self, result: IntegrityReport) -> None:
        self._log.append({
            "operation": "integrity_check",
            "is_valid": result.is_valid,
            "total_entries": result.total_entries,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    def log_retention_enforcement(self, deleted_entries: int, dry_run: bool) -> None:
        self._log.append({
            "operation": "retention_enforcement",
            "deleted_entries": deleted_entries,
            "dry_run": dry_run,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    @property
    def entries(self) -> list[dict[str, Any]]:
        return list(self._log)


class AuditQuery:
    def __init__(self, event_log_path: Path | str = DEFAULT_EVENT_LOG) -> None:
        self._event_log_path = Path(event_log_path)
        self._events: list[dict[str, Any]] | None = None
        self._meta_audit_log: list[dict[str, Any]] = []
        self._meta_logger = MetaAuditLogger()

    def _load_events(self) -> list[dict[str, Any]]:
        if self._events is not None:
            return self._events
        if not self._event_log_path.exists():
            self._events = []
            return self._events
        events: list[dict[str, Any]] = []
        with open(self._event_log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        self._events = events
        return self._events

    def _meta_log(self, operation: str, params: dict[str, Any]) -> None:
        self._meta_audit_log.append({
            "operation": operation,
            "params": params,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    def by_agent(self, agent_id: str) -> list[dict[str, Any]]:
        self._meta_log("by_agent", {"agent_id": agent_id})
        return [e for e in self._load_events() if e.get("agent_id") == agent_id]

    def by_session(self, session_id: str) -> list[dict[str, Any]]:
        self._meta_log("by_session", {"session_id": session_id})
        return [e for e in self._load_events() if e.get("session_id") == session_id]

    def by_timerange(self, start: str, end: str) -> list[dict[str, Any]]:
        self._meta_log("by_timerange", {"start": start, "end": end})
        return [
            e for e in self._load_events()
            if start <= e.get("timestamp", "") <= end
        ]

    def by_event_type(self, event_type: str) -> list[dict[str, Any]]:
        self._meta_log("by_event_type", {"event_type": event_type})
        return [e for e in self._load_events() if e.get("event_type") == event_type]

    def by_task(self, task_id: str) -> list[dict[str, Any]]:
        self._meta_log("by_task", {"task_id": task_id})
        return [e for e in self._load_events() if e.get("task_id") == task_id]

    def by_task_details(self, task_id: str) -> list[dict[str, Any]]:
        self._meta_log("by_task_details", {"task_id": task_id})
        task_audit_id = ""
        for e in self._load_events():
            if e.get("task_id") == task_id and e.get("event_type") == "task_summary":
                task_audit_id = e.get("entry_id", "")
                break
        if not task_audit_id:
            return [e for e in self._load_events() if e.get("task_id") == task_id]
        return [e for e in self._load_events() if e.get("task_audit_id") == task_audit_id or e.get("task_id") == task_id]

    def by_target(self, file_path: str) -> list[dict[str, Any]]:
        self._meta_log("by_target", {"file_path": file_path})
        return [
            e for e in self._load_events()
            if e.get("target_path") == file_path or e.get("file_path") == file_path
        ]

    def by_permission_level(self, level: str) -> list[dict[str, Any]]:
        self._meta_log("by_permission_level", {"level": level})
        return [e for e in self._load_events() if e.get("permission_level") == level]

    def by_anomaly(self, anomaly_type: str | None = None, min_score: float = 0.7) -> list[dict[str, Any]]:
        self._meta_log("by_anomaly", {"anomaly_type": anomaly_type, "min_score": min_score})
        results: list[dict[str, Any]] = []
        for e in self._load_events():
            if not e.get("anomaly_detected"):
                continue
            score = e.get("anomaly_score", 0.0)
            if score < min_score:
                continue
            if anomaly_type and e.get("anomaly_type") != anomaly_type:
                continue
            results.append(e)
        return results

    def by_drift(self, severity: str | None = None) -> list[dict[str, Any]]:
        self._meta_log("by_drift", {"severity": severity})
        results: list[dict[str, Any]] = []
        for e in self._load_events():
            if not e.get("drift_detected"):
                continue
            if severity and e.get("drift_severity") != severity:
                continue
            results.append(e)
        return results

    def by_cost(self, min_cost_usd: float = 0.0) -> list[dict[str, Any]]:
        self._meta_log("by_cost", {"min_cost_usd": min_cost_usd})
        results: list[dict[str, Any]] = []
        for e in self._load_events():
            cost = e.get("cost_estimate_usd", 0.0)
            if cost and cost >= min_cost_usd:
                results.append(e)
        return results

    def by_cot_hash(self, cot_hash: str) -> list[dict[str, Any]]:
        self._meta_log("by_cot_hash", {"cot_hash": cot_hash})
        return [e for e in self._load_events() if e.get("cot_hash") == cot_hash]

    def events_with_reasoning(self) -> list[dict[str, Any]]:
        self._meta_log("events_with_reasoning", {})
        return [e for e in self._load_events() if e.get("reasoning_trace") or e.get("cot_hash")]

    def search(self, keyword: str) -> list[dict[str, Any]]:
        self._meta_log("search", {"keyword": keyword})
        keyword_lower = keyword.lower()
        results: list[dict[str, Any]] = []
        for e in self._load_events():
            event_str = json.dumps(e, ensure_ascii=False).lower()
            if keyword_lower in event_str:
                results.append(e)
        return results

    def trail_for_ai_context(
        self,
        session_id: str = "",
        max_entries: int = MAX_TRAIL_ENTRIES,
    ) -> dict[str, Any]:
        self._meta_log("trail_for_ai_context", {"session_id": session_id})
        events = self._load_events()
        if session_id:
            events = [e for e in events if e.get("session_id") == session_id]

        recent = events[-max_entries:]

        summary_lines: list[str] = []
        injection_detected = False
        for e in recent:
            ts = e.get("timestamp", "?")[:19]
            agent = _sanitize_for_ai_context(str(e.get("agent_id", "?")))
            etype = _sanitize_for_ai_context(str(e.get("event_type", "?")))
            target = _sanitize_for_ai_context(str(e.get("target_path", e.get("operation", "?"))))
            status = _sanitize_for_ai_context(str(e.get("status", "")))
            line = f"[AUDIT_ENTRY_START][{ts}] {agent} {etype} {target}"
            if status:
                line += f" -> {status}"
            line += "[AUDIT_ENTRY_END]"
            summary_lines.append(line)

            raw_str = json.dumps(e, ensure_ascii=False)
            if _INJECTION_PATTERNS.search(raw_str) or _ROLE_PREFIX_PATTERN.search(raw_str) or _TOOL_CALL_PATTERN.search(raw_str):
                injection_detected = True

        summary = "\n".join(summary_lines)
        token_estimate = len(summary) // 3

        result: dict[str, Any] = {
            "total_events": len(events),
            "recent_events": len(recent),
            "summary": summary,
            "token_estimate": token_estimate,
            "within_budget": token_estimate <= TRAIL_TOKEN_BUDGET,
            "injection_detected": injection_detected,
            "entries": recent if token_estimate <= TRAIL_TOKEN_BUDGET else recent[-10:],
        }

        if injection_detected:
            _logger.warning(
                "trail_for_ai_context: prompt injection patterns detected in audit entries — sanitized"
            )

        return result

    def verify_integrity(self, fast_mode: bool = True) -> IntegrityReport:
        self._meta_log("verify_integrity", {"fast_mode": fast_mode})
        from zephyr.audit_trail.integrity import IntegrityVerifier
        verifier = IntegrityVerifier()
        raw = verifier.verify_chain()
        return IntegrityReport(
            is_valid=raw.get("status") == "valid",
            total_entries=raw.get("events_checked", 0),
            hash_chain_breaks=[],
            hmac_failures=[],
            merkle_mismatches=[],
            checked_at=datetime.now(UTC).isoformat(),
        )

    def rebuild_index(self) -> int:
        self._meta_log("rebuild_index", {})
        from zephyr.audit_trail.indexer import AuditIndexer
        indexer = AuditIndexer()
        result = indexer.rebuild()
        return result.events_indexed

    def meta_audit_report(self) -> list[dict[str, Any]]:
        return self._meta_audit_log

    def count(self) -> int:
        return len(self._load_events())

    def refresh(self) -> None:
        self._events = None
