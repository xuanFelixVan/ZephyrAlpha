# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4.1
# [MODULE] zephyr.gov_audit.query
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.models
# [CONSUMERS] audit-orchestrator.cli; MCP governance_server
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读操作; 不修改任何审计数据
# [MODIFY-GUARD] 查询接口签名变更必须同步 cli.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询失败返回空结果而非抛异常
# [TESTS] tests/audit-orchestrator/test_query.py
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Final

from zephyr.gov_audit.contracts import AuditQuery as AuditQueryABC  # 5.104.16 修复: 继承ABC契约
from zephyr.gov_audit.models import AuditIssue, IntegrityReport, OrchestratorStatus
from zephyr.shared.io.paths import AUDIT_DATA_DIR, REPO_ROOT  # 路径真源（SSoT）
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__ = ["AuditQueryEngine", "AuditQuery", "MetaAuditLogger", "_sanitize_for_ai_context"]

# 治本（AI-AUDIT12 路径SSoT收敛）：相对路径默认锚定 REPO_ROOT/AUDIT_DATA_DIR 真源。
DEFAULT_REPORT_DIR: Final[Any] = REPO_ROOT / "data" / "audit_history"

# AI context sanitization patterns
_INJECTION_PATTERNS = [
    re.compile(r"ignore all previous instructions", re.IGNORECASE),
    re.compile(r"disregard the above", re.IGNORECASE),
    re.compile(r"forget your instructions", re.IGNORECASE),
]
_ROLE_PATTERNS = [
    re.compile(r"^(system|user|assistant)\s*:", re.IGNORECASE),
]
_TOOL_CALL_PATTERN = re.compile(r"<function_call>|</function_call>|<tool_call>|</tool_call>", re.IGNORECASE)
_MAX_AI_CONTEXT_LENGTH = 530


def _sanitize_for_ai_context(text: str) -> str:
    """净化文本以安全传递给 AI 上下文。"""
    if not text:
        return ""
    result = text
    for pattern in _INJECTION_PATTERNS:
        result = pattern.sub("[REDACTED_INSTRUCTION]", result)
    for pattern in _ROLE_PATTERNS:
        result = pattern.sub("[REDACTED_ROLE]:", result)
    result = _TOOL_CALL_PATTERN.sub("[REDACTED_TAG]", result)
    result = result.replace("```", "")
    if len(result) > _MAX_AI_CONTEXT_LENGTH:
        result = result[:_MAX_AI_CONTEXT_LENGTH]
    return result


class AuditQueryEngine(AuditQueryABC):
    """旧版查询引擎（保留以兼容现有调用方）。"""

    def __init__(self, report_dir: Path | None = None) -> None:
        self._report_dir = Path(report_dir or DEFAULT_REPORT_DIR)

    def get_status(self) -> OrchestratorStatus:
        reports = self._list_reports()
        pending = len([r for r in reports if not self._is_completed(r)])
        return OrchestratorStatus(
            phase="IDLE" if pending == 0 else "EXECUTING",
            active_sessions=0,
            pending_tasks=pending,
            last_audit_id=reports[0].stem if reports else None,
        )

    def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for path in self._list_reports()[:limit]:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                results.append(data)
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("Failed to read report %s: %s", path, exc, exc_info=True)
        return results

    def get_issues(self, audit_id: str) -> list[AuditIssue]:
        report_path = self._report_dir / f"{audit_id}.json"
        if not report_path.exists():
            return []
        try:
            data = json.loads(report_path.read_text(encoding="utf-8"))
            return [AuditIssue(**i) for i in data.get("issues", [])]
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("Failed to read issues for %s: %s", audit_id, exc, exc_info=True)
            return []

    def get_recent_findings(self, hours: int = 24) -> list[dict[str, Any]]:
        cutoff = now_utc() - timedelta(hours=hours)
        findings: list[dict[str, Any]] = []
        for path in self._list_reports():
            if datetime.fromtimestamp(path.stat().st_mtime) < cutoff:
                break
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                for issue in data.get("issues", []):
                    if issue.get("severity") in ("RED", "YELLOW"):
                        findings.append(issue)
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                continue
        return findings

    def _list_reports(self) -> list[Path]:
        if not self._report_dir.exists():
            return []
        return sorted(
            self._report_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

    def _is_completed(self, path: Path) -> bool:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data.get("global_converged", False) or data.get("finished_at") is not None
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            return False


class MetaAuditLogger:
    """元审计日志器（补全测试期望接口）。"""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._entries: list[dict[str, Any]] = []

    @property
    def entries(self) -> list[dict[str, Any]]:
        """返回 entries 的副本，防止外部修改。"""
        return list(self._entries)

    def log_audit_query(self, querier: str, query: dict[str, Any]) -> None:
        self._entries.append(
            {
                "operation": "audit_query",
                "querier": querier,
                "query": query,
                "timestamp": now_utc().isoformat(),
            }
        )

    def log_index_rebuild(self, reason: str, entries_count: int) -> None:
        self._entries.append(
            {
                "operation": "index_rebuild",
                "reason": reason,
                "entries_count": entries_count,
                "timestamp": now_utc().isoformat(),
            }
        )

    def log_integrity_check(self, report: IntegrityReport) -> None:
        self._entries.append(
            {
                "operation": "integrity_check",
                "is_valid": report.is_valid,
                "total_entries": report.total_entries,
                "timestamp": now_utc().isoformat(),
            }
        )

    def log_retention_enforcement(self, count: int, dry_run: bool = False) -> None:
        self._entries.append(
            {
                "operation": "retention_enforcement",
                "count": count,
                "dry_run": dry_run,
                "timestamp": now_utc().isoformat(),
            }
        )

    def log_query(self, query: object, result_count: int = 0) -> None:
        self._entries.append(
            {
                "operation": "query",
                "query": str(query),
                "result_count": result_count,
                "timestamp": now_utc().isoformat(),
            }
        )

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_entries": len(self._entries),
            "operations": list({e.get("operation", "") for e in self._entries}),
        }


class AuditQuery:
    """审计查询接口（补全测试期望接口）。

    支持按 agent/session/event_type/timerange/target/anomaly/drift/cost/task/permission_level 查询。
    """

    def __init__(self, event_log_path: Path | None = None) -> None:
        # 治本（AI-AUDIT12 路径SSoT收敛）：原 Path("data/audit_trail/events.jsonl")
        # （下划线+相对）与 SSoT AUDIT_DATA_DIR（连字符绝对）不一致——默认构造的查询
        # 永远读不到 writer 真实写入目录。收敛为真源。
        self._event_log_path = Path(event_log_path) if event_log_path is not None else AUDIT_DATA_DIR / "events.jsonl"
        self._events: list[dict[str, Any]] | None = None
        self._meta_logger = MetaAuditLogger()

    @property
    def events(self) -> list[dict[str, Any]] | None:
        """只读：events（Stage 4 公共化）。"""
        return self._events

    @events.setter
    def events(self, value):
        """写入：events（Stage 4 公共化）。"""
        self._events = value

    def load_events(self) -> None:
        """公共接口：load_events（Stage 4 公共化）。"""
        return self._load_events()

    def _load_events(self) -> None:
        """加载事件到缓存。"""
        if self._event_log_path is None or not self._event_log_path.exists():
            self._events = []
            return
        events: list[dict[str, Any]] = []
        try:
            with open(self._event_log_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("Failed to load events from %s: %s", self._event_log_path, exc, exc_info=True)
            events = []
        self._events = events

    def _get_events(self) -> list[dict[str, Any]]:
        if self._events is None:
            self._load_events()
        return self._events or []

    def refresh(self) -> None:
        """清除缓存，下次查询时重新加载。"""
        self._events = None

    def count(self) -> int:
        return len(self._get_events())

    def _record_query(self, operation: str, **kwargs: Any) -> None:
        """记录元审计查询。"""
        self._meta_logger.log_audit_query(operation, kwargs)

    def by_agent(self, agent_id: str) -> list[dict[str, Any]]:
        result = [e for e in self._get_events() if e.get("agent_id") == agent_id]
        self._record_query("by_agent", agent_id=agent_id, result_count=len(result))
        return result

    def by_session(self, session_id: str) -> list[dict[str, Any]]:
        result = [e for e in self._get_events() if e.get("session_id") == session_id]
        self._record_query("by_session", session_id=session_id, result_count=len(result))
        return result

    def by_event_type(self, event_type: str) -> list[dict[str, Any]]:
        result = [e for e in self._get_events() if e.get("event_type") == event_type]
        self._record_query("by_event_type", event_type=event_type, result_count=len(result))
        return result

    def by_timerange(self, start: str, end: str) -> list[dict[str, Any]]:
        start_dt = self._parse_ts(start)
        end_dt = self._parse_ts(end)
        if start_dt is None or end_dt is None:
            return []
        result = []
        for e in self._get_events():
            ts = e.get("timestamp")
            if not ts:
                continue
            event_dt = self._parse_ts(ts)
            if event_dt is None:
                continue
            if start_dt <= event_dt <= end_dt:
                result.append(e)
        self._record_query("by_timerange", start=start, end=end, result_count=len(result))
        return result

    def by_target(self, target: str) -> list[dict[str, Any]]:
        result = [e for e in self._get_events() if e.get("target_path") == target]
        self._record_query("by_target", target=target, result_count=len(result))
        return result

    def by_anomaly(self, min_score: float = 0.0) -> list[dict[str, Any]]:
        result = []
        for e in self._get_events():
            if e.get("anomaly_detected"):
                score = e.get("anomaly_score", 0.0)
                if score >= min_score:
                    result.append(e)
        self._record_query("by_anomaly", min_score=min_score, result_count=len(result))
        return result

    def by_drift(self, severity: str = "") -> list[dict[str, Any]]:
        result = []
        for e in self._get_events():
            if e.get("drift_detected"):
                if not severity or e.get("drift_severity", "").upper() == severity.upper():
                    result.append(e)
        self._record_query("by_drift", severity=severity, result_count=len(result))
        return result

    def by_cost(self, min_cost_usd: float = 0.0) -> list[dict[str, Any]]:
        result = []
        for e in self._get_events():
            cost = e.get("cost_estimate_usd", 0.0)
            if cost >= min_cost_usd:
                result.append(e)
        self._record_query("by_cost", min_cost_usd=min_cost_usd, result_count=len(result))
        return result

    def by_task(self, task_id: str) -> list[dict[str, Any]]:
        result = [e for e in self._get_events() if e.get("task_id") == task_id]
        self._record_query("by_task", task_id=task_id, result_count=len(result))
        return result

    def by_permission_level(self, level: str) -> list[dict[str, Any]]:
        result = [e for e in self._get_events() if e.get("permission_level") == level]
        self._record_query("by_permission_level", level=level, result_count=len(result))
        return result

    def search(self, keyword: str) -> list[dict[str, Any]]:
        """在事件中搜索关键词。"""
        result = []
        for e in self._get_events():
            for v in e.values():
                if isinstance(v, str) and keyword in v:
                    result.append(e)
                    break
        self._record_query("search", keyword=keyword, result_count=len(result))
        return result

    def trail_for_ai_context(self, session_id: str | None = None) -> dict[str, Any]:
        """生成 AI 上下文审计轨迹。"""
        events = self._get_events()
        if session_id:
            events = [e for e in events if e.get("session_id") == session_id]

        total = len(events)
        injection_detected = False
        for e in events:
            for v in e.values():
                if isinstance(v, str):
                    sanitized = _sanitize_for_ai_context(v)
                    if "[REDACTED_INSTRUCTION]" in sanitized or "[REDACTED_ROLE]" in sanitized:
                        injection_detected = True
                        break
            if injection_detected:
                break

        summary_parts = []
        for e in events[:10]:
            entry = {
                "entry_id": e.get("entry_id", ""),
                "agent_id": e.get("agent_id", ""),
                "event_type": e.get("event_type", ""),
                "timestamp": e.get("timestamp", ""),
            }
            for k, v in entry.items():
                if isinstance(v, str):
                    entry[k] = _sanitize_for_ai_context(v)
            summary_parts.append(entry)

        return {
            "total_events": total,
            "summary": summary_parts,
            "injection_detected": injection_detected,
            "within_budget": total <= 1000,
        }

    def meta_audit_report(self) -> list[dict[str, Any]]:
        """返回元审计日志。"""
        return self._meta_logger.entries

    def verify_integrity(self) -> IntegrityReport:
        """验证审计链完整性。"""
        from zephyr.gov_audit import integrity

        verifier = integrity.IntegrityVerifier(event_log_path=self._event_log_path)
        result = verifier.verify_chain()
        is_valid = result.get("status") == "valid"
        total = result.get("events_checked", 0)
        report = IntegrityReport(
            is_valid=is_valid,
            total_entries=total,
            checked_at=now_utc().isoformat(),
        )
        self._meta_logger.log_integrity_check(report)
        return report

    def rebuild_index(self) -> int:
        """重建审计索引。"""
        from zephyr.gov_audit import indexer

        idx = indexer.AuditIndexer(events_path=self._event_log_path)
        result = idx.rebuild()
        count = getattr(result, "events_indexed", 0)
        self._meta_logger.log_index_rebuild("manual", count)
        return count

    def _parse_ts(self, ts: str | None) -> datetime | None:
        if not ts:
            return None
        try:
            if ts.endswith("Z"):
                ts = ts[:-1] + "+00:00"
            return datetime.fromisoformat(ts)
        except (TypeError, ValueError):
            return None
