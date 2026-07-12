# [A_test] module_id: SRC-TST-0164 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-321 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.integration.test_audit08_service_layer_wiring
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""AUDIT-08：FLE 背压桥与 KB 门禁链接、VMS 委托适配器 集成测试。"""

from __future__ import annotations

import importlib.util

import pytest

from zephyr.integration.vector_memory import MemoryEntry, UnifiedVectorMemoryAdapter
from zephyr.infrastructure.pipeline.backpressure_manager import BackpressureManager
from zephyr.shared.utils.time_utils import default_now
from zephyr.intelligence.model_evaluation.unified_memory_api import InMemoryMemoryBackend, UnifiedMemoryAPI
from zephyr.feedback_loop.backpressure_bridge import sync_evolution_proposals_to_backpressure
from zephyr.feedback_loop.evolution_engine import (
    EvolutionProposal,
    EvolutionSignal,
    FeedbackLayer,
    Severity,
)


def test_sync_evolution_triggers_throttle_on_critical() -> None:
    mgr = BackpressureManager()
    p = EvolutionProposal(
        proposal_id="EP-0001",
        signal=EvolutionSignal.CONTEXT_OVERFLOW,
        layer=FeedbackLayer.L2_PATTERN,
        severity=Severity.CRITICAL,
        title="t",
        rationale="r",
        evidence=[],
        affected_task_ids=[],
        recommended_action="a",
        estimated_impact="i",
        created_at=default_now(),
    )
    out = sync_evolution_proposals_to_backpressure([p], mgr)
    assert out["throttled"] is True
    assert out["critical_count"] == 1
    stats = mgr.get_stats()
    assert stats["throttled_count"] >= 1


def test_sync_evolution_skips_when_no_critical() -> None:
    mgr = BackpressureManager()
    p = EvolutionProposal(
        proposal_id="EP-0002",
        signal=EvolutionSignal.HIGH_RETRY_RATE,
        layer=FeedbackLayer.L1_TASK,
        severity=Severity.HIGH,
        title="t",
        rationale="r",
        evidence=[],
        affected_task_ids=[],
        recommended_action="a",
        estimated_impact="i",
        created_at=default_now(),
    )
    out = sync_evolution_proposals_to_backpressure([p], mgr)
    assert out["throttled"] is False
    assert out["critical_count"] == 0


@pytest.mark.parametrize(
    "mod,gate_id",
    [
        ("zephyr.data.storage.ingest", "G1"),
        ("zephyr.data.storage.triage", "G2"),
        ("zephyr.alt_data.kb.analyze", "G3"),
        ("zephyr.intelligence.model_evaluation.activate", "G4"),
        ("zephyr.alt_data.kb.extract", "G5"),
    ],
)
def test_kb_stage_wires_expected_gate_id(mod: str, gate_id: str) -> None:
    spec = importlib.util.find_spec(mod)
    assert spec is not None and spec.origin is not None
    with open(spec.origin, encoding="utf-8") as f:
        text = f.read()
    assert f'"{gate_id}"' in text or f"'{gate_id}'" in text


def test_unified_vector_memory_adapter_roundtrip() -> None:
    api = UnifiedMemoryAPI(backend=InMemoryMemoryBackend(), enforce_capability=False)
    mem = UnifiedVectorMemoryAdapter(api=api)
    e = MemoryEntry(
        entry_id="e1",
        collection="knowledge",
        content="hello vector world " * 20,
        metadata={"origin": "test:vms", "audit_chain": ["TEST"]},
    )
    chunk = mem.store(e)
    assert chunk
    hits = mem.search("hello", "knowledge", top_k=3)
    assert len(hits) >= 1
    stats = mem.get_collection_stats("knowledge")
    assert stats.get("entries", 0) >= 1
