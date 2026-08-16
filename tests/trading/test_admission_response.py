# [A_test] module_id: MOD-GOV_admission_response | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-343 | docs/03_modules/_domain_governance/blueprint.md | §3.9
# [MODULE] tests.test_admission_response
# [INVARIANTS] REJECTED must include rejection_reason; queue_position only valid for QUEUED
# [MODIFY-GUARD] Changes must sync with admission_response.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidDecisionError on bad decision
# [TESTS] tests/test_admission_response.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from zephyr.integration.behavioral_admission.admission_response import (
    AdmissionResponse,
    AdmissionResponseBuilder,
    AdmissionResponseStatus,
    InvalidDecisionError,
)
from zephyr.trading.admission_controller import (
    AdmissionDecision,
    AdmissionResult,
)


class TestAdmissionResponseStatus:
    def test_enum_values(self):
        assert AdmissionResponseStatus.ADMITTED.value == "admitted"
        assert AdmissionResponseStatus.QUEUED.value == "queued"
        assert AdmissionResponseStatus.REJECTED.value == "rejected"
        assert AdmissionResponseStatus.DEGRADED.value == "degraded"

    def test_all_statuses_exist(self):
        expected = {"admitted", "queued", "rejected", "degraded"}
        actual = {s.value for s in AdmissionResponseStatus}
        assert actual == expected


class TestAdmissionResponse:
    def test_admitted_response(self):
        resp = AdmissionResponse(
            status=AdmissionResponseStatus.ADMITTED,
            request_id="req-001",
        )
        assert resp.status == AdmissionResponseStatus.ADMITTED
        assert resp.request_id == "req-001"
        assert resp.queue_position is None
        assert resp.rejection_reason is None

    def test_queued_response_with_position(self):
        resp = AdmissionResponse(
            status=AdmissionResponseStatus.QUEUED,
            request_id="req-002",
            queue_position=5,
            estimated_wait_seconds=30.0,
        )
        assert resp.queue_position == 5
        assert resp.estimated_wait_seconds == 30.0

    def test_rejected_without_reason_raises(self):
        with pytest.raises(ValueError, match="rejection_reason"):
            AdmissionResponse(
                status=AdmissionResponseStatus.REJECTED,
                request_id="req-003",
            )

    def test_rejected_with_reason(self):
        resp = AdmissionResponse(
            status=AdmissionResponseStatus.REJECTED,
            request_id="req-003",
            rejection_reason="Rate limit exceeded",
        )
        assert resp.rejection_reason == "Rate limit exceeded"

    def test_queue_position_on_non_queued_raises(self):
        with pytest.raises(ValueError, match="queue_position"):
            AdmissionResponse(
                status=AdmissionResponseStatus.ADMITTED,
                request_id="req-004",
                queue_position=3,
            )

    def test_degraded_capabilities_on_non_degraded_raises(self):
        with pytest.raises(ValueError, match="degraded_capabilities"):
            AdmissionResponse(
                status=AdmissionResponseStatus.ADMITTED,
                request_id="req-005",
                degraded_capabilities=["write"],
            )

    def test_to_mcp_result_admitted(self):
        resp = AdmissionResponse(
            status=AdmissionResponseStatus.ADMITTED,
            request_id="req-006",
        )
        result = resp.to_mcp_result()
        assert result["status"] == "admitted"
        assert result["request_id"] == "req-006"
        assert "queue_position" not in result

    def test_to_mcp_result_rejected(self):
        resp = AdmissionResponse(
            status=AdmissionResponseStatus.REJECTED,
            request_id="req-007",
            rejection_reason="Policy violation",
        )
        result = resp.to_mcp_result()
        assert result["rejection_reason"] == "Policy violation"

    def test_to_mcp_result_with_metadata(self):
        resp = AdmissionResponse(
            status=AdmissionResponseStatus.ADMITTED,
            request_id="req-008",
            metadata={"source": "test"},
        )
        result = resp.to_mcp_result()
        assert result["metadata"]["source"] == "test"


class TestInvalidDecisionError:
    def test_error_message_contains_decision(self):
        err = InvalidDecisionError("bad_decision")
        assert "bad_decision" in str(err)
        assert err.decision == "bad_decision"

    def test_error_is_value_error(self):
        err = InvalidDecisionError(42)
        assert isinstance(err, ValueError)


class TestAdmissionResponseBuilder:
    def test_build_from_admit_decision(self):
        builder = AdmissionResponseBuilder()
        resp = builder.build_response(AdmissionDecision.ADMIT, "req-100")
        assert resp.status == AdmissionResponseStatus.ADMITTED
        assert resp.request_id == "req-100"

    def test_build_from_rejected_decision(self):
        builder = AdmissionResponseBuilder()
        resp = builder.build_response(
            AdmissionDecision.REJECTED,
            "req-101",
            rejection_reason="Blocked",
        )
        assert resp.status == AdmissionResponseStatus.REJECTED
        assert resp.rejection_reason == "Blocked"

    def test_build_from_rate_limited_decision(self):
        builder = AdmissionResponseBuilder()
        resp = builder.build_response(
            AdmissionDecision.RATE_LIMITED,
            "req-102",
            queue_position=2,
            estimated_wait_seconds=10.0,
        )
        assert resp.status == AdmissionResponseStatus.QUEUED

    def test_build_from_circuit_open_decision(self):
        builder = AdmissionResponseBuilder()
        resp = builder.build_response(
            AdmissionDecision.CIRCUIT_OPEN,
            "req-103",
            degraded_capabilities=["read"],
        )
        assert resp.status == AdmissionResponseStatus.DEGRADED
        assert resp.degraded_capabilities == ["read"]

    def test_build_from_admission_result(self):
        builder = AdmissionResponseBuilder()
        result = AdmissionResult(
            decision=AdmissionDecision.ADMIT,
            event_type="file_write",
            retry_after_ms=0,
            remaining_tokens=50.0,
            is_circuit_open=False,
        )
        resp = builder.build_response(result, "req-200")
        assert resp.status == AdmissionResponseStatus.ADMITTED
        assert resp.metadata["event_type"] == "file_write"

    def test_build_from_invalid_decision_raises(self):
        builder = AdmissionResponseBuilder()
        with pytest.raises(InvalidDecisionError):
            builder.build_response("not_a_decision", "req-300")

    def test_build_batch_responses(self):
        builder = AdmissionResponseBuilder()
        items = [
            (AdmissionDecision.ADMIT, "req-a"),
            (AdmissionDecision.REJECTED, "req-b"),
        ]
        responses = builder.build_batch_responses(
            items,
            common_metadata={"batch": True},
        )
        assert len(responses) == 2
        assert responses[0].status == AdmissionResponseStatus.ADMITTED
        assert responses[1].status == AdmissionResponseStatus.REJECTED
        assert responses[0].metadata["batch"] is True

    def test_build_batch_empty_list(self):
        builder = AdmissionResponseBuilder()
        responses = builder.build_batch_responses([])
        assert responses == []

    def test_builder_with_controller_for_queued(self):
        mock_controller = MagicMock()
        mock_controller.get_retry_after.return_value = 5000
        builder = AdmissionResponseBuilder(admission_controller=mock_controller)
        resp = builder.build_response(
            AdmissionDecision.RATE_LIMITED,
            "req-ctrl",
            metadata={"event_type": "file_write"},
        )
        assert resp.estimated_wait_seconds == 5.0
