# [A_test] module_id: MOD-GOV_gpu_consensus_scheduler | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §17
# [MODULE] tests.test_gpu_consensus_scheduler
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_gpu_consensus_scheduler.py -q
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.trading.gpu_consensus_scheduler import (
    ConsensusPriority,
    ConsensusRequest,
    ConsensusResult,
    ConsensusRoute,
    ConsensusStatus,
    GPUConsensusScheduler,
    GPUStatus,
    SchedulerMetrics,
    _PriorityQueue,
)
from zephyr.trading.verdict_engine import ProtectionLevel, VerdictLevel


def _no_gpu_scheduler(**kwargs) -> GPUConsensusScheduler:
    s = GPUConsensusScheduler(**kwargs)
    s.gpu_status = GPUStatus(
        available=False,
        model_name=s.local_model,
        last_check_time=0.0,
        ollama_responding=False,
    )
    return s


class TestConsensusPriority:
    def test_enum_values(self):
        assert ConsensusPriority.P0_ANCHOR == 0
        assert ConsensusPriority.P1_PROTECTED == 1
        assert ConsensusPriority.P2_NORMAL == 2
        assert ConsensusPriority.P3_BASELINE == 3

    def test_enum_count(self):
        assert len(ConsensusPriority) == 4

    def test_ordering(self):
        assert ConsensusPriority.P0_ANCHOR < ConsensusPriority.P1_PROTECTED
        assert ConsensusPriority.P1_PROTECTED < ConsensusPriority.P2_NORMAL
        assert ConsensusPriority.P2_NORMAL < ConsensusPriority.P3_BASELINE

    def test_is_int_enum(self):
        assert isinstance(ConsensusPriority.P0_ANCHOR, int)


class TestConsensusRoute:
    def test_enum_values(self):
        assert ConsensusRoute.DUAL_API.value == "DUAL_API"
        assert ConsensusRoute.SINGLE_API.value == "SINGLE_API"
        assert ConsensusRoute.LOCAL_GPU.value == "LOCAL_GPU"

    def test_enum_count(self):
        assert len(ConsensusRoute) == 3

    def test_is_str_enum(self):
        assert isinstance(ConsensusRoute.DUAL_API, str)


class TestConsensusStatus:
    def test_enum_values(self):
        assert ConsensusStatus.PENDING.value == "PENDING"
        assert ConsensusStatus.RUNNING.value == "RUNNING"
        assert ConsensusStatus.CONSENSUS_REACHED.value == "CONSENSUS_REACHED"
        assert ConsensusStatus.PARTIAL_CONSENSUS.value == "PARTIAL_CONSENSUS"
        assert ConsensusStatus.FAILED.value == "FAILED"
        assert ConsensusStatus.CANCELLED.value == "CANCELLED"
        assert ConsensusStatus.DEGRADED.value == "DEGRADED"

    def test_enum_count(self):
        assert len(ConsensusStatus) == 7

    def test_is_str_enum(self):
        assert isinstance(ConsensusStatus.PENDING, str)


class TestConsensusRequest:
    def test_default_values(self):
        req = ConsensusRequest()
        assert req.request_id != ""
        assert len(req.request_id) == 16
        assert req.content == ""
        assert req.context == {}
        assert req.priority == ConsensusPriority.P3_BASELINE
        assert req.protection_level == ProtectionLevel.normal
        assert req.expected_verdict is None
        assert req.timeout_s == 30.0

    def test_custom_values(self):
        req = ConsensusRequest(
            content="modify anchor file",
            context={"file": "project_rules.md"},
            priority=ConsensusPriority.P0_ANCHOR,
            protection_level=ProtectionLevel.anchor,
            expected_verdict=VerdictLevel.RED,
            timeout_s=10.0,
        )
        assert req.content == "modify anchor file"
        assert req.priority == ConsensusPriority.P0_ANCHOR
        assert req.protection_level == ProtectionLevel.anchor
        assert req.expected_verdict == VerdictLevel.RED

    def test_unique_request_ids(self):
        ids = {ConsensusRequest().request_id for _ in range(50)}
        assert len(ids) == 50

    def test_extra_fields_forbidden(self):
        with pytest.raises(Exception):
            ConsensusRequest(unknown_field="value")


class TestConsensusResult:
    def test_default_values(self):
        result = ConsensusResult()
        assert result.request_id == ""
        assert result.status == ConsensusStatus.PENDING
        assert result.route == ConsensusRoute.LOCAL_GPU
        assert result.verdict is None
        assert result.confidence == 0.0
        assert result.model_responses == []
        assert result.latency_ms == 0.0
        assert result.reason == ""

    def test_custom_values(self):
        result = ConsensusResult(
            request_id="abc123",
            status=ConsensusStatus.CONSENSUS_REACHED,
            route=ConsensusRoute.DUAL_API,
            verdict=VerdictLevel.RED,
            confidence=0.95,
            reason="2/2_consensus",
        )
        assert result.request_id == "abc123"
        assert result.status == ConsensusStatus.CONSENSUS_REACHED
        assert result.verdict == VerdictLevel.RED

    def test_extra_fields_forbidden(self):
        with pytest.raises(Exception):
            ConsensusResult(unknown_field="value")


class TestGPUStatus:
    def test_default_values(self):
        status = GPUStatus()
        assert status.available is False
        assert status.model_name == ""
        assert status.vram_used_mb == 0.0
        assert status.vram_total_mb == 0.0
        assert status.last_check_time == 0.0
        assert status.ollama_responding is False

    def test_custom_values(self):
        status = GPUStatus(
            available=True,
            model_name="qwen3:8b",
            vram_used_mb=4096.0,
            vram_total_mb=24576.0,
            ollama_responding=True,
        )
        assert status.available is True
        assert status.model_name == "qwen3:8b"
        assert status.vram_total_mb == 24576.0


class TestSchedulerMetrics:
    def test_default_values(self):
        m = SchedulerMetrics()
        assert m.total_submitted == 0
        assert m.consensus_reached == 0
        assert m.partial_consensus == 0
        assert m.failed == 0
        assert m.degraded == 0
        assert m.cancelled == 0
        assert m.avg_latency_ms == 0.0
        assert m.queue_depth == 0
        assert m.gpu_available is False
        assert m.dual_api_count == 0
        assert m.single_api_count == 0
        assert m.local_gpu_count == 0


class TestPriorityQueue:
    def test_push_and_pop(self):
        q = _PriorityQueue()
        req_p3 = ConsensusRequest(priority=ConsensusPriority.P3_BASELINE)
        req_p0 = ConsensusRequest(priority=ConsensusPriority.P0_ANCHOR)
        q.push(req_p3)
        q.push(req_p0)
        popped = q.pop()
        assert popped is not None
        assert popped.priority == ConsensusPriority.P0_ANCHOR
        popped2 = q.pop()
        assert popped2 is not None
        assert popped2.priority == ConsensusPriority.P3_BASELINE

    def test_pop_respects_priority_order(self):
        q = _PriorityQueue()
        for p in [3, 1, 2, 0]:
            q.push(ConsensusRequest(priority=ConsensusPriority(p)))
        priorities = []
        while q.depth > 0:
            item = q.pop()
            priorities.append(item.priority)
        assert priorities == [0, 1, 2, 3]

    def test_depth(self):
        q = _PriorityQueue()
        assert q.depth == 0
        q.push(ConsensusRequest())
        assert q.depth == 1
        q.push(ConsensusRequest())
        assert q.depth == 2
        q.pop()
        assert q.depth == 1

    def test_max_size_limits_push(self):
        q = _PriorityQueue(max_size=2)
        assert q.push(ConsensusRequest()) is True
        assert q.push(ConsensusRequest()) is True
        assert q.push(ConsensusRequest()) is False
        assert q.depth == 2

    def test_remove_existing(self):
        q = _PriorityQueue()
        req = ConsensusRequest(request_id="test-remove-001")
        q.push(req)
        assert q.depth == 1
        assert q.remove("test-remove-001") is True
        assert q.depth == 0

    def test_remove_nonexistent(self):
        q = _PriorityQueue()
        assert q.remove("no-such-id") is False

    def test_pop_empty_returns_none(self):
        q = _PriorityQueue()
        assert q.pop() is None

    def test_push_returns_bool(self):
        q = _PriorityQueue(max_size=1)
        assert q.push(ConsensusRequest()) is True
        assert q.push(ConsensusRequest()) is False

    def test_remove_from_correct_priority_bucket(self):
        q = _PriorityQueue()
        req0 = ConsensusRequest(request_id="p0-item", priority=ConsensusPriority.P0_ANCHOR)
        req2 = ConsensusRequest(request_id="p2-item", priority=ConsensusPriority.P2_NORMAL)
        q.push(req0)
        q.push(req2)
        assert q.remove("p2-item") is True
        assert q.depth == 1
        popped = q.pop()
        assert popped.request_id == "p0-item"


class TestGPUConsensusSchedulerInit:
    def test_custom_init_model_name(self):
        scheduler = _no_gpu_scheduler(local_model="custom-model")
        gpu = scheduler.get_gpu_status()
        assert gpu.model_name == "custom-model"
        assert gpu.available is False

    def test_initial_metrics_no_gpu(self):
        scheduler = _no_gpu_scheduler()
        m = scheduler.get_metrics()
        assert m.total_submitted == 0
        assert m.gpu_available is False

    def test_initial_queue_depth(self):
        scheduler = _no_gpu_scheduler()
        assert scheduler.get_queue_depth() == 0


class TestDetermineRoute:
    def test_anchor_with_gpu(self):
        scheduler = GPUConsensusScheduler()
        scheduler.gpu_status = GPUStatus(available=True, model_name="qwen3:8b")
        req = ConsensusRequest(protection_level=ProtectionLevel.anchor)
        assert scheduler.determine_route(req) == ConsensusRoute.DUAL_API

    def test_anchor_without_gpu(self):
        scheduler = _no_gpu_scheduler()
        req = ConsensusRequest(protection_level=ProtectionLevel.anchor)
        assert scheduler.determine_route(req) == ConsensusRoute.SINGLE_API

    def test_protected_with_gpu(self):
        scheduler = GPUConsensusScheduler()
        scheduler.gpu_status = GPUStatus(available=True, model_name="qwen3:8b")
        req = ConsensusRequest(protection_level=ProtectionLevel.protected)
        assert scheduler.determine_route(req) == ConsensusRoute.DUAL_API

    def test_protected_without_gpu(self):
        scheduler = _no_gpu_scheduler()
        req = ConsensusRequest(protection_level=ProtectionLevel.protected)
        assert scheduler.determine_route(req) == ConsensusRoute.SINGLE_API

    def test_normal_with_gpu(self):
        scheduler = GPUConsensusScheduler()
        scheduler.gpu_status = GPUStatus(available=True, model_name="qwen3:8b")
        req = ConsensusRequest(protection_level=ProtectionLevel.normal)
        assert scheduler.determine_route(req) == ConsensusRoute.LOCAL_GPU

    def test_normal_without_gpu(self):
        scheduler = _no_gpu_scheduler()
        req = ConsensusRequest(protection_level=ProtectionLevel.normal)
        assert scheduler.determine_route(req) == ConsensusRoute.SINGLE_API

    def test_public_with_gpu(self):
        scheduler = GPUConsensusScheduler()
        scheduler.gpu_status = GPUStatus(available=True, model_name="qwen3:8b")
        req = ConsensusRequest(protection_level=ProtectionLevel.public)
        assert scheduler.determine_route(req) == ConsensusRoute.LOCAL_GPU

    def test_public_without_gpu(self):
        scheduler = _no_gpu_scheduler()
        req = ConsensusRequest(protection_level=ProtectionLevel.public)
        assert scheduler.determine_route(req) == ConsensusRoute.SINGLE_API


class TestParseModelResponse:
    def test_valid_json_response(self):
        scheduler = _no_gpu_scheduler()
        text = '{"verdict": "RED", "confidence": 0.9, "reasoning": "dangerous op"}'
        result = scheduler.parse_model_response(text, "model-a")
        assert result["verdict"] == "RED"
        assert result["confidence"] == 0.9
        assert result["reasoning"] == "dangerous op"
        assert result["model_id"] == "model-a"

    def test_json_with_surrounding_text(self):
        scheduler = _no_gpu_scheduler()
        text = 'Here is my analysis: {"verdict": "YELLOW", "confidence": 0.7, "reasoning": "suspicious"} end'
        result = scheduler.parse_model_response(text, "model-b")
        assert result["verdict"] == "YELLOW"
        assert result["confidence"] == 0.7

    def test_fallback_red_on_invalid_json(self):
        scheduler = _no_gpu_scheduler()
        text = "{this is not valid json and contains red flag}"
        result = scheduler.parse_model_response(text, "model-c")
        assert result["verdict"] == "RED"

    def test_fallback_yellow_on_invalid_json(self):
        scheduler = _no_gpu_scheduler()
        text = "{invalid json with yellow warning}"
        result = scheduler.parse_model_response(text, "model-d")
        assert result["verdict"] == "YELLOW"

    def test_fallback_no_keyword_pass_on_invalid_json(self):
        scheduler = _no_gpu_scheduler()
        text = "{broken json no color keyword}"
        result = scheduler.parse_model_response(text, "model-e")
        assert result["verdict"] == "PASS"

    def test_plain_text_no_braces_defaults_pass(self):
        scheduler = _no_gpu_scheduler()
        text = "Everything looks fine here"
        result = scheduler.parse_model_response(text, "model-e")
        assert result["verdict"] == "PASS"
        assert result["confidence"] == 0.5

    def test_json_with_invalid_verdict(self):
        scheduler = _no_gpu_scheduler()
        text = '{"verdict": "INVALID", "confidence": 0.5}'
        result = scheduler.parse_model_response(text, "model-f")
        assert result["verdict"] == "PASS"

    def test_empty_text(self):
        scheduler = _no_gpu_scheduler()
        result = scheduler.parse_model_response("", "model-g")
        assert result["verdict"] == "PASS"
        assert result["confidence"] == 0.5

    def test_json_missing_confidence_defaults(self):
        scheduler = _no_gpu_scheduler()
        text = '{"verdict": "PASS"}'
        result = scheduler.parse_model_response(text, "model-h")
        assert result["verdict"] == "PASS"
        assert result["confidence"] == 0.5
        assert result["reasoning"] == ""

    def test_red_takes_precedence_over_yellow_in_fallback(self):
        scheduler = _no_gpu_scheduler()
        text = "{broken json with both red and yellow}"
        result = scheduler.parse_model_response(text, "model-i")
        assert result["verdict"] == "RED"


class TestGetMetrics:
    def test_initial_metrics(self):
        scheduler = _no_gpu_scheduler()
        m = scheduler.get_metrics()
        assert isinstance(m, SchedulerMetrics)
        assert m.total_submitted == 0
        assert m.gpu_available is False

    def test_metrics_returns_copy(self):
        scheduler = _no_gpu_scheduler()
        m1 = scheduler.get_metrics()
        m2 = scheduler.get_metrics()
        assert m1.total_submitted == m2.total_submitted
        assert m1 is not m2


class TestHealthCheck:
    def test_degraded_when_no_gpu(self):
        scheduler = _no_gpu_scheduler()
        result = scheduler.health_check()
        assert result["status"] == "degraded"
        assert "gpu_status" in result
        assert "metrics" in result

    def test_healthy_when_gpu_available(self):
        scheduler = GPUConsensusScheduler()
        scheduler.gpu_status = GPUStatus(available=True, model_name="qwen3:8b")
        result = scheduler.health_check()
        assert result["status"] == "healthy"

    def test_gpu_status_in_result(self):
        scheduler = _no_gpu_scheduler()
        result = scheduler.health_check()
        assert isinstance(result["gpu_status"], dict)
        assert result["gpu_status"]["available"] is False

    def test_metrics_in_result(self):
        scheduler = _no_gpu_scheduler()
        result = scheduler.health_check()
        assert isinstance(result["metrics"], dict)
        assert result["metrics"]["total_submitted"] == 0


class TestGetGPUStatus:
    def test_returns_copy(self):
        scheduler = _no_gpu_scheduler()
        s1 = scheduler.get_gpu_status()
        s2 = scheduler.get_gpu_status()
        assert s1 is not s2
        assert s1.available == s2.available

    def test_no_gpu_when_forced(self):
        scheduler = _no_gpu_scheduler()
        status = scheduler.get_gpu_status()
        assert status.available is False


class TestCancel:
    def test_cancel_nonexistent(self):
        scheduler = _no_gpu_scheduler()
        assert scheduler.cancel("no-such-id") is False

    def test_cancel_updates_metrics(self):
        scheduler = _no_gpu_scheduler()
        req = ConsensusRequest(request_id="cancel-me")
        scheduler.queue.push(req)
        assert scheduler.cancel("cancel-me") is True
        m = scheduler.get_metrics()
        assert m.cancelled == 1


class TestSubmitNoGPU:
    @pytest.mark.asyncio
    async def test_submit_anchor_no_gpu_degraded(self):
        scheduler = _no_gpu_scheduler()
        req = ConsensusRequest(
            protection_level=ProtectionLevel.anchor,
            priority=ConsensusPriority.P0_ANCHOR,
        )
        result = await scheduler.submit(req)
        assert result.route == ConsensusRoute.SINGLE_API
        assert result.status == ConsensusStatus.DEGRADED

    @pytest.mark.asyncio
    async def test_submit_normal_no_gpu_degraded(self):
        scheduler = _no_gpu_scheduler()
        req = ConsensusRequest(
            protection_level=ProtectionLevel.normal,
            priority=ConsensusPriority.P2_NORMAL,
        )
        result = await scheduler.submit(req)
        assert result.route == ConsensusRoute.SINGLE_API
        assert result.status == ConsensusStatus.DEGRADED

    @pytest.mark.asyncio
    async def test_submit_increments_total_submitted(self):
        scheduler = _no_gpu_scheduler()
        req = ConsensusRequest()
        await scheduler.submit(req)
        m = scheduler.get_metrics()
        assert m.total_submitted == 1

    @pytest.mark.asyncio
    async def test_submit_tracks_route_count(self):
        scheduler = _no_gpu_scheduler()
        await scheduler.submit(ConsensusRequest(protection_level=ProtectionLevel.normal))
        m = scheduler.get_metrics()
        assert m.single_api_count == 1
        assert m.dual_api_count == 0
        assert m.local_gpu_count == 0

    @pytest.mark.asyncio
    async def test_submit_records_latency(self):
        scheduler = _no_gpu_scheduler()
        result = await scheduler.submit(ConsensusRequest())
        assert result.latency_ms >= 0

    @pytest.mark.asyncio
    async def test_submit_preserves_request_id(self):
        scheduler = _no_gpu_scheduler()
        req = ConsensusRequest(request_id="test-req-001")
        result = await scheduler.submit(req)
        assert result.request_id == "test-req-001"


class TestSubmitBatch:
    @pytest.mark.asyncio
    async def test_batch_submit(self):
        scheduler = _no_gpu_scheduler()
        requests = [
            ConsensusRequest(request_id=f"batch-{i}", protection_level=ProtectionLevel.normal) for i in range(3)
        ]
        results = await scheduler.submit_batch(requests)
        assert len(results) == 3
        assert all(isinstance(r, ConsensusResult) for r in results)

    @pytest.mark.asyncio
    async def test_batch_empty(self):
        scheduler = _no_gpu_scheduler()
        results = await scheduler.submit_batch([])
        assert results == []

    @pytest.mark.asyncio
    async def test_batch_increments_total(self):
        scheduler = _no_gpu_scheduler()
        requests = [ConsensusRequest() for _ in range(5)]
        await scheduler.submit_batch(requests)
        m = scheduler.get_metrics()
        assert m.total_submitted == 5


class TestSchedulerMetricsAfterOperations:
    @pytest.mark.asyncio
    async def test_degraded_count_after_no_gpu_submit(self):
        scheduler = _no_gpu_scheduler()
        await scheduler.submit(ConsensusRequest())
        m = scheduler.get_metrics()
        assert m.degraded == 1

    @pytest.mark.asyncio
    async def test_avg_latency_computed(self):
        scheduler = _no_gpu_scheduler()
        await scheduler.submit(ConsensusRequest())
        m = scheduler.get_metrics()
        assert m.avg_latency_ms >= 0.0
