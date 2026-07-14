# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §
# [MODULE] zephyr.integration.mcp.audit_logger
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.io.paths; zephyr.gov_audit.writer
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
# [A_module] module_id=MOD-INT_audit_logger | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""MCP 全量工具调用审计日志（MOD-INF-013 §12 Step 4）。

盲点关闭：B9（缺审计日志 -> 无 trace/无 accountability）。

审计字段：
- timestamp + client_session_id + tool_name + arguments_hash
- result_status + duration_ms + error_code（如有）
- 对标 R81 ZephyrLogger 格式
- 同时写入核心 zephyr.gov_audit.writer.AuditWriter 不可变审计链
"""

from __future__ import annotations

from typing import Final
import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import REPO_ROOT

_CORE_AUDIT_AVAILABLE = False
try:
    from zephyr.gov_audit.writer import AuditWriter as _CoreAuditWriter

    _CORE_AUDIT_AVAILABLE = True
except ImportError:
    _CoreAuditWriter = None

__all__ = ["AUDIT_JSONL_PATH", "AUDIT_LOG_DIR", "AuditLogger", "create_audit_logger"]

AUDIT_LOG_DIR: Final[Path] = REPO_ROOT / "logs" / "mcp_audit"
AUDIT_JSONL_PATH: Final[Path] = AUDIT_LOG_DIR / "tools_call.jsonl"

AUDIT_FIELDS: Final[list] = [
    "timestamp",
    "client_session_id",
    "tool_name",
    "arguments_hash",
    "result_status",
    "duration_ms",
    "error_code",
    "error_message",
    "byte_in",
    "byte_out",
]

_logger = logging.getLogger(__name__)


class AuditLogger:
    """MCP Gateway 审计日志器——全量 tools/call 记录。

    Usage::

        logger = AuditLogger()
        logger.log_call(
            client_session_id="session-xyz",
            tool_name="task_manager.create_task",
            arguments_hash="abc123",
            result_status="success",
            duration_ms=45,
        )
    """

    def __init__(self, log_dir: Path | None = None) -> None:
        self._dir = Path(log_dir) if log_dir else AUDIT_LOG_DIR
        self._dir.mkdir(parents=True, exist_ok=True)
        self._path = self._dir / "tools_call.jsonl"
        self._index: dict[str, list[dict[str, Any]]] = {}
        self._core_writer: _CoreAuditWriter | None = None
        if _CORE_AUDIT_AVAILABLE:
            try:
                self._core_writer = _CoreAuditWriter()
            except Exception as e:
                _logger.warning("suppressed error in audit_logger", exc_info=True)

    def hash_args(self, arguments: dict[str, Any]) -> str:
        raw = json.dumps(arguments, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]

    def log_call(
        self,
        *,
        client_session_id: str,
        tool_name: str,
        arguments_hash: str | None = None,
        result_status: str,
        duration_ms: int = 0,
        error_code: int | None = None,
        error_message: str | None = None,
        byte_in: int = 0,
        byte_out: int = 0,
    ) -> dict[str, Any]:
        entry: dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "client_session_id": client_session_id,
            "tool_name": tool_name,
            "arguments_hash": arguments_hash or "",
            "result_status": result_status,
            "duration_ms": duration_ms,
            "error_code": error_code,
            "error_message": error_message,
            "byte_in": byte_in,
            "byte_out": byte_out,
        }

        try:
            with open(self._path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as exc:
            _logger.error("audit write failed: %s", exc)

        if self._core_writer is not None:
            try:
                core_event = dict(entry)
                core_event["event_type"] = "mcp_tool_call"
                core_event["agent_id"] = client_session_id
                core_event["session_id"] = client_session_id
                core_event["target_path"] = tool_name
                core_event["status"] = result_status
                self._core_writer.write(core_event)
            except Exception as e:
                _logger.warning("suppressed error in audit_logger", exc_info=True)

        self._index.setdefault(client_session_id, []).append(entry)
        return entry

    def recent(self, client_session_id: str, limit: int = 20) -> list[dict[str, Any]]:
        entries = self._index.get(client_session_id, [])
        return entries[-limit:]

    def stats(self, client_session_id: str) -> dict[str, Any]:
        entries = self._index.get(client_session_id, [])
        succeeded = sum(1 for e in entries if e["result_status"] == "success")
        failed = sum(1 for e in entries if e["result_status"] == "error")
        rate_limited = sum(1 for e in entries if e["result_status"] == "rate_limited")
        total_ms = sum(e.get("duration_ms", 0) for e in entries)
        return {
            "total_calls": len(entries),
            "succeeded": succeeded,
            "failed": failed,
            "rate_limited": rate_limited,
            "total_duration_ms": total_ms,
            "avg_duration_ms": total_ms // max(len(entries), 1),
        }


def create_audit_logger(log_dir: Path | None = None) -> AuditLogger:
    return AuditLogger(log_dir)
