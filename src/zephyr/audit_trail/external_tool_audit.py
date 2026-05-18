# [BLUEPRINT] MOD-INF-020 | 03_modules/l01_infrastructure/audit-trail/blueprint.md | §

# [MODULE] zephyr.audit_trail.external_tool_audit

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
audit_trail.external_tool_audit — MOD-INF-020 · 外部工具调用审计
=================================================================
蓝图 D-020-20 · 外部工具调用追踪 + 调用链验证

特性
----
  - 追踪所有外部工具调用 (MCP, shell, API 等)
  - 验证工具调用链完整性
  - 检测异常工具调用模式
"""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from zephyr.audit_trail.models import AuditEventType

_logger = logging.getLogger(__name__)


class ToolCallStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    BLOCKED = "blocked"


class ToolCallRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    call_id: str = ""
    tool_name: str = ""
    tool_type: str = ""
    caller_agent: str = ""
    session_id: str = ""
    timestamp: str = ""
    status: ToolCallStatus = ToolCallStatus.PENDING
    input_hash: str = ""
    output_hash: str = ""
    duration_ms: int = 0
    parent_call_id: str = ""
    chain_depth: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChainValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_valid: bool = True
    chain_length: int = 0
    issues: list[str] = Field(default_factory=list)
    chain: list[ToolCallRecord] = Field(default_factory=list)
    validated_at: str = ""


class ExternalToolCallAuditor:
    def __init__(self, max_chain_depth: int = 10) -> None:
        self._max_chain_depth = max_chain_depth
        self._call_records: dict[str, ToolCallRecord] = {}

    def audit_call(
        self,
        tool_name: str,
        tool_type: str,
        caller_agent: str,
        session_id: str = "",
        input_data: str = "",
        output_data: str = "",
        parent_call_id: str = "",
        duration_ms: int = 0,
        status: ToolCallStatus = ToolCallStatus.SUCCESS,
        metadata: dict[str, Any] | None = None,
    ) -> ToolCallRecord:
        call_id = f"TOOL-{hashlib.sha256(f'{tool_name}:{caller_agent}:{datetime.now(UTC).isoformat()}'.encode()).hexdigest()[:16]}"
        chain_depth = 0
        if parent_call_id and parent_call_id in self._call_records:
            chain_depth = self._call_records[parent_call_id].chain_depth + 1

        record = ToolCallRecord(
            call_id=call_id,
            tool_name=tool_name,
            tool_type=tool_type,
            caller_agent=caller_agent,
            session_id=session_id,
            timestamp=datetime.now(UTC).isoformat(),
            status=status,
            input_hash=hashlib.sha256(input_data.encode()).hexdigest() if input_data else "",
            output_hash=hashlib.sha256(output_data.encode()).hexdigest() if output_data else "",
            duration_ms=duration_ms,
            parent_call_id=parent_call_id,
            chain_depth=chain_depth,
            metadata=metadata or {},
        )

        self._call_records[call_id] = record

        if chain_depth > self._max_chain_depth:
            _logger.warning(
                "ExternalToolCallAuditor: chain depth %d exceeds max %d for call %s",
                chain_depth, self._max_chain_depth, call_id,
            )

        _logger.info(
            "ExternalToolCallAuditor: audited %s call %s by %s (depth=%d, status=%s)",
            tool_name, call_id, caller_agent, chain_depth, status.value,
        )
        return record

    def validate_chain(self, call_id: str) -> ChainValidationResult:
        chain: list[ToolCallRecord] = []
        issues: list[str] = []
        current_id = call_id

        visited: set[str] = set()
        while current_id and current_id in self._call_records:
            if current_id in visited:
                issues.append(f"Circular reference detected at call {current_id}")
                break
            visited.add(current_id)
            record = self._call_records[current_id]
            chain.append(record)
            current_id = record.parent_call_id

        chain.reverse()

        if len(chain) > self._max_chain_depth:
            issues.append(f"Chain length {len(chain)} exceeds maximum {self._max_chain_depth}")

        for i in range(1, len(chain)):
            if chain[i].timestamp < chain[i - 1].timestamp:
                issues.append(f"Timestamp ordering violation at index {i}: child before parent")

        is_valid = len(issues) == 0
        return ChainValidationResult(
            is_valid=is_valid,
            chain_length=len(chain),
            issues=issues,
            chain=chain,
            validated_at=datetime.now(UTC).isoformat(),
        )

    def get_call(self, call_id: str) -> ToolCallRecord | None:
        return self._call_records.get(call_id)

    def get_calls_by_agent(self, agent_id: str) -> list[ToolCallRecord]:
        return [r for r in self._call_records.values() if r.caller_agent == agent_id]

    def get_calls_by_session(self, session_id: str) -> list[ToolCallRecord]:
        return [r for r in self._call_records.values() if r.session_id == session_id]
