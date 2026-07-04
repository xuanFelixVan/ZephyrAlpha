# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4.1
# [MODULE] zephyr.governance.audit_trail.query
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_trail.models
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
# [A_module] module_id=MOD-GOV_query | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from zephyr.governance.audit_trail.models import AuditIssue, OrchestratorStatus

logger = logging.getLogger(__name__)

__all__ = ["AuditQueryEngine"]

DEFAULT_REPORT_DIR = Path("data/audit_history")


class AuditQueryEngine:
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
            except Exception as exc:
                logger.warning("Failed to read report %s: %s", path, exc)
        return results

    def get_issues(self, audit_id: str) -> list[AuditIssue]:
        report_path = self._report_dir / f"{audit_id}.json"
        if not report_path.exists():
            return []
        try:
            data = json.loads(report_path.read_text(encoding="utf-8"))
            return [AuditIssue(**i) for i in data.get("issues", [])]
        except Exception as exc:
            logger.warning("Failed to read issues for %s: %s", audit_id, exc)
            return []

    def get_recent_findings(self, hours: int = 24) -> list[dict[str, Any]]:
        cutoff = datetime.now() - timedelta(hours=hours)
        findings: list[dict[str, Any]] = []
        for path in self._list_reports():
            if datetime.fromtimestamp(path.stat().st_mtime) < cutoff:
                break
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                for issue in data.get("issues", []):
                    if issue.get("severity") in ("RED", "YELLOW"):
                        findings.append(issue)
            except Exception:
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
        except Exception:
            return False


class AuditQuery:
    def __init__(self, filters=None, sort_by="", limit=100, offset=0):
        self.filters = filters or {}
        self.sort_by = sort_by
        self.limit = limit
        self.offset = offset


class MetaAuditLogger:
    def __init__(self, config=None):
        self.config = config or {}

    def log_query(self, query, result_count=0):
        pass

    def get_stats(self):
        return {}


def _sanitize_for_ai_context(data: Any) -> Any:
    return data
