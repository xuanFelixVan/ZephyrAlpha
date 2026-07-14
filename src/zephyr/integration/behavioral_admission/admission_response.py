# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §3.9
# [MODULE] zephyr.integration.behavioral_admission.admission_response
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS] GovernanceServer;run_all.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 响应状态必须与AdmissionDecision一致;REJECTED必须包含原因
# [MODIFY-GUARD] MCP协议格式变更需同步mcp/gateway_server.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidDecisionError
# [TESTS] tests/test_admission_response.py
# [A_module] module_id=MOD-INT_admission_response | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from __future__ import annotations
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from zephyr.trading.admission_controller import (
    AdmissionDecision,
    AdmissionResult,
)


class AdmissionResponseStatus(str, Enum):
    ADMITTED = "admitted"
    QUEUED = "queued"
    REJECTED = "rejected"
    DEGRADED = "degraded"


_DECISION_TO_STATUS: dict[AdmissionDecision, AdmissionResponseStatus] = {
    AdmissionDecision.ADMIT: AdmissionResponseStatus.ADMITTED,
    AdmissionDecision.RATE_LIMITED: AdmissionResponseStatus.QUEUED,
    AdmissionDecision.CIRCUIT_OPEN: AdmissionResponseStatus.DEGRADED,
    AdmissionDecision.REJECTED: AdmissionResponseStatus.REJECTED,
}


class InvalidDecisionError(ValueError):
    error_code = "ZA-IG-0017"

    def __init__(self, decision: Any, error_code: str | None = None) -> None:
        self.decision = decision
        super().__init__(
            f"Cannot map decision '{decision}' to AdmissionResponseStatus. "
            f"Expected AdmissionDecision enum or valid string: "
            f"{[d.value for d in AdmissionDecision]}"
        )
        if error_code is not None:
            self.error_code = error_code


class AdmissionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: AdmissionResponseStatus
    request_id: str
    queue_position: int | None = None
    estimated_wait_seconds: float | None = None
    rejection_reason: str | None = None
    degraded_capabilities: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_invariants(self) -> AdmissionResponse:
        if self.status == AdmissionResponseStatus.REJECTED and not self.rejection_reason:
            raise ValueError("REJECTED status must include rejection_reason")
        if self.status != AdmissionResponseStatus.QUEUED:
            if self.queue_position is not None:
                raise ValueError("queue_position only valid for QUEUED status")
            if self.estimated_wait_seconds is not None:
                raise ValueError("estimated_wait_seconds only valid for QUEUED status")
        if self.status != AdmissionResponseStatus.DEGRADED and self.degraded_capabilities:
            raise ValueError("degraded_capabilities only valid for DEGRADED status")
        return self

    def to_mcp_result(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "status": self.status.value,
            "request_id": self.request_id,
        }
        if self.queue_position is not None:
            result["queue_position"] = self.queue_position
        if self.estimated_wait_seconds is not None:
            result["estimated_wait_seconds"] = self.estimated_wait_seconds
        if self.rejection_reason is not None:
            result["rejection_reason"] = self.rejection_reason
        if self.degraded_capabilities:
            result["degraded_capabilities"] = self.degraded_capabilities
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class AdmissionResponseBuilder:
    def __init__(self, admission_controller: Any = None) -> None:
        self._controller = admission_controller

    def build_response(
        self,
        decision: AdmissionDecision | AdmissionResult,
        request_id: str,
        *,
        queue_position: int | None = None,
        estimated_wait_seconds: float | None = None,
        rejection_reason: str | None = None,
        degraded_capabilities: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AdmissionResponse:
        if isinstance(decision, AdmissionResult):
            return self._from_result(decision, request_id, metadata=metadata)
        if isinstance(decision, AdmissionDecision):
            return self._from_decision(
                decision,
                request_id,
                queue_position=queue_position,
                estimated_wait_seconds=estimated_wait_seconds,
                rejection_reason=rejection_reason,
                degraded_capabilities=degraded_capabilities,
                metadata=metadata,
            )
        raise InvalidDecisionError(decision)

    def build_batch_responses(
        self,
        items: list[tuple[AdmissionDecision | AdmissionResult, str]],
        *,
        common_metadata: dict[str, Any] | None = None,
    ) -> list[AdmissionResponse]:
        responses: list[AdmissionResponse] = []
        for decision, request_id in items:
            merged_metadata: dict[str, Any] = {}
            if common_metadata:
                merged_metadata.update(common_metadata)
            if isinstance(decision, AdmissionResult):
                merged_metadata["event_type"] = decision.event_type
                merged_metadata["remaining_tokens"] = decision.remaining_tokens
            response = self.build_response(decision, request_id, metadata=merged_metadata or None)
            responses.append(response)
        return responses

    def _from_decision(
        self,
        decision: AdmissionDecision,
        request_id: str,
        *,
        queue_position: int | None,
        estimated_wait_seconds: float | None,
        rejection_reason: str | None,
        degraded_capabilities: list[str] | None,
        metadata: dict[str, Any] | None,
    ) -> AdmissionResponse:
        status = _DECISION_TO_STATUS.get(decision)
        if status is None:
            raise InvalidDecisionError(decision)

        kwargs: dict[str, Any] = {
            "status": status,
            "request_id": request_id,
        }

        if status == AdmissionResponseStatus.QUEUED:
            kwargs["queue_position"] = queue_position
            kwargs["estimated_wait_seconds"] = estimated_wait_seconds
            if self._controller is not None and estimated_wait_seconds is None:
                event_type = (metadata or {}).get("event_type", "default")
                retry_ms = self._controller.get_retry_after(event_type)
                kwargs["estimated_wait_seconds"] = retry_ms / 1000.0

        if status == AdmissionResponseStatus.REJECTED:
            kwargs["rejection_reason"] = rejection_reason or "Request rejected by admission policy"

        if status == AdmissionResponseStatus.DEGRADED:
            kwargs["degraded_capabilities"] = degraded_capabilities or []

        if metadata:
            kwargs["metadata"] = metadata

        return AdmissionResponse(**kwargs)

    def _from_result(
        self,
        result: AdmissionResult,
        request_id: str,
        *,
        metadata: dict[str, Any] | None,
    ) -> AdmissionResponse:
        status = _DECISION_TO_STATUS.get(result.decision)
        if status is None:
            raise InvalidDecisionError(result.decision)

        kwargs: dict[str, Any] = {
            "status": status,
            "request_id": request_id,
        }

        if status == AdmissionResponseStatus.QUEUED:
            kwargs["estimated_wait_seconds"] = result.retry_after_ms / 1000.0

        if status == AdmissionResponseStatus.REJECTED:
            kwargs["rejection_reason"] = "Request rejected by admission policy"

        if status == AdmissionResponseStatus.DEGRADED:
            kwargs["degraded_capabilities"] = []

        result_metadata: dict[str, Any] = {
            "event_type": result.event_type,
            "remaining_tokens": result.remaining_tokens,
            "circuit_open": result.is_circuit_open,  # 5.153.4 修复: AdmissionResult字段重命名
        }
        if result.retry_after_ms > 0:
            result_metadata["retry_after_ms"] = result.retry_after_ms
        if metadata:
            result_metadata.update(metadata)
        kwargs["metadata"] = result_metadata

        return AdmissionResponse(**kwargs)
