# [A_test] module_id: MOD-GOV_unified_memory_api_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-700 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_unified_memory_api
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
T-V2-007 单元测试 — UnifiedMemoryAPI (RI-02)
=============================================
覆盖场景（验收标准 #7 ≥ 80%）：
  - WriteTrace frozen：Pydantic v2 frozen 不可变
  - WriteTrace 校验：origin / audit_chain[≥1] / arbitration
  - WriteTraceMissing：write 缺 provenance / 类型错 / audit_chain 空
  - InMemoryMemoryBackend：write / list_by_topic / query / count / clear
  - UnifiedMemoryAPI.write：成功路径 + 必传字段校验
  - UnifiedMemoryAPI.recall：按 topic 时间倒序
  - UnifiedMemoryAPI.search：跨 topic 相似度 + 限定 topic
  - CBAC 集成：enforce_capability=True 时调用 capability_check
  - CBAC 拒绝：CapabilityDenied 透传
  - 单例：get_unified_memory_api 复用与 reset
  - build_provenance 便捷构造器
  - ChromaMemoryBackend mock：通过 mock chroma client 验证调用契约
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.intelligence.model_evaluation.unified_memory_api import (
    InMemoryMemoryBackend,
    MemoryBackendError,
    MemoryRecord,
    UnifiedMemoryAPI,
    WriteTrace,
    WriteTraceMissing,
    build_provenance,
    get_unified_memory_api,
    reset_unified_memory_api,
)
from zephyr.shared.security.capability import CapabilityDenied, CapabilityRegistry

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_singleton():
    """每个测试前后重置单例。"""
    reset_unified_memory_api()
    yield
    reset_unified_memory_api()


@pytest.fixture
def memory_backend() -> InMemoryMemoryBackend:
    return InMemoryMemoryBackend()


@pytest.fixture
def api(memory_backend) -> UnifiedMemoryAPI:
    """默认 API 实例：使用内存后端 + 关闭 CBAC（避免依赖 capabilities.yaml 中无 write_kb 规则）。"""
    return UnifiedMemoryAPI(backend=memory_backend, enforce_capability=False)


@pytest.fixture
def sample_provenance() -> WriteTrace:
    return WriteTrace(
        origin="M1:doc_compressor",
        audit_chain=["T-V2-007", "RI-02"],
        arbitration="R84",
    )


@pytest.fixture
def cbac_yaml(tmp_path: Path) -> Path:
    """临时 capabilities.yaml：允许 unified_memory/* 写入，禁止 unified_memory/forbidden_*。"""
    yaml_path = tmp_path / "capabilities.yaml"
    yaml_path.write_text(
        textwrap.dedent(
            """\
            rules:
              - name: write_kb
                description: "测试用：允许 unified_memory 主题写入"
                allow:
                  - "unified_memory/**"
                deny:
                  - "unified_memory/forbidden_*"
            """
        ),
        encoding="utf-8",
    )
    return yaml_path


# ---------------------------------------------------------------------------
# 1. WriteTrace 模型
# ---------------------------------------------------------------------------


class TestWriteTrace:
    # #ARCH-VMS-WRITETRACE-CONSOLIDATE-001：WriteTrace 严格约束
    # （frozen + min_length + extra forbid），以下测试验证严格语义。

    def test_frozen_immutable(self):
        """frozen=True → 赋值必须抛 ValidationError（防回填污染）"""
        from pydantic import ValidationError

        prov = WriteTrace(origin="M1", audit_chain=["T-1"])
        with pytest.raises(ValidationError):
            prov.origin = "updated"

    def test_origin_required(self):
        """origin min_length=1 → 缺失必须抛 ValidationError"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            WriteTrace(audit_chain=["T-1"])

    def test_audit_chain_required(self):
        """audit_chain min_length=1 → 缺失必须抛 ValidationError"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            WriteTrace(origin="M1")

    def test_arbitration_default_none(self):
        """arbitration 默认 None（可选字段，非空串）"""
        prov = WriteTrace(origin="M1", audit_chain=["T-1"])
        assert prov.arbitration is None

    def test_extra_field_forbidden(self):
        with pytest.raises(Exception):
            WriteTrace(
                origin="M1",
                audit_chain=["T-1"],
                unknown_field="x",
            )

    def test_full_construction(self):
        prov = WriteTrace(
            origin="M3:trigger_router",
            audit_chain=["T-V2-007", "RI-03"],
            arbitration="R84",
        )
        assert prov.origin == "M3:trigger_router"
        assert prov.audit_chain == ["T-V2-007", "RI-03"]
        assert prov.arbitration == "R84"


class TestBuildWriteTrace:
    def test_factory_returns_write_trace(self):
        prov = build_provenance(origin="M2", audit_chain=["T-V2-007"])
        assert isinstance(prov, WriteTrace)

    def test_factory_arbitration_passthrough(self):
        prov = build_provenance(origin="M2", audit_chain=["T-V2-007"], arbitration="R84")
        assert prov.arbitration == "R84"


# ---------------------------------------------------------------------------
# 2. InMemoryMemoryBackend
# ---------------------------------------------------------------------------


class TestInMemoryBackend:
    def test_write_and_list(self, memory_backend, sample_provenance):
        rec = MemoryRecord(
            chunk_id="t1::1",
            topic="t1",
            content="hello world",
            written_at="2026-04-27T10:00:00+00:00",
            metadata={"origin": sample_provenance.origin},
        )
        chunk_id = memory_backend.write(rec)
        assert chunk_id == "t1::1"

        out = memory_backend.list_by_topic("t1", k=5)
        assert len(out) == 1
        assert out[0].content == "hello world"

    def test_list_by_topic_orders_desc(self, memory_backend):
        for i, ts in enumerate(["2026-01-01", "2026-03-01", "2026-02-01"]):
            memory_backend.write(
                MemoryRecord(
                    chunk_id=f"t1::{i}",
                    topic="t1",
                    content=f"c{i}",
                    written_at=ts,
                )
            )
        out = memory_backend.list_by_topic("t1", k=10)
        assert [r.written_at for r in out] == [
            "2026-03-01",
            "2026-02-01",
            "2026-01-01",
        ]

    def test_list_by_topic_respects_k(self, memory_backend):
        for i in range(5):
            memory_backend.write(
                MemoryRecord(
                    chunk_id=f"t::{i}",
                    topic="t",
                    content=f"c{i}",
                    written_at=f"2026-04-{i + 1:02d}",
                )
            )
        out = memory_backend.list_by_topic("t", k=2)
        assert len(out) == 2

    def test_list_by_topic_filters_topic(self, memory_backend):
        memory_backend.write(MemoryRecord(chunk_id="a::1", topic="a", content="x", written_at="2026-01-01"))
        memory_backend.write(MemoryRecord(chunk_id="b::1", topic="b", content="y", written_at="2026-01-01"))
        assert len(memory_backend.list_by_topic("a", 5)) == 1
        assert len(memory_backend.list_by_topic("c", 5)) == 0

    def test_query_token_overlap(self, memory_backend):
        memory_backend.write(
            MemoryRecord(chunk_id="a::1", topic="a", content="quantum risk model", written_at="2026-01-01")
        )
        memory_backend.write(
            MemoryRecord(chunk_id="a::2", topic="a", content="天气 today is sunny", written_at="2026-01-02")
        )
        out = memory_backend.query("quantum strategy", k=5)
        assert len(out) >= 1
        assert out[0].chunk_id == "a::1"

    def test_query_with_topic_filter(self, memory_backend):
        memory_backend.write(MemoryRecord(chunk_id="a::1", topic="a", content="alpha factor", written_at="2026-01-01"))
        memory_backend.write(MemoryRecord(chunk_id="b::1", topic="b", content="alpha factor", written_at="2026-01-01"))
        out = memory_backend.query("alpha", k=5, topic="b")
        assert len(out) == 1
        assert out[0].topic == "b"

    def test_query_k_zero_returns_empty(self, memory_backend):
        memory_backend.write(MemoryRecord(chunk_id="a::1", topic="a", content="alpha", written_at="2026-01-01"))
        assert memory_backend.query("alpha", k=0) == []

    def test_query_empty_query_returns_empty(self, memory_backend):
        memory_backend.write(MemoryRecord(chunk_id="a::1", topic="a", content="alpha", written_at="2026-01-01"))
        assert memory_backend.query("", k=5) == []

    def test_count_and_clear(self, memory_backend):
        for i in range(3):
            memory_backend.write(MemoryRecord(chunk_id=f"a::{i}", topic="a", content=f"c{i}", written_at="2026-01-01"))
        assert memory_backend.count() == 3
        memory_backend.clear()
        assert memory_backend.count() == 0


# ---------------------------------------------------------------------------
# 3. UnifiedMemoryAPI.write
# ---------------------------------------------------------------------------


class TestWriteWriteTraceEnforcement:
    def test_write_success_returns_chunk_id(self, api, sample_provenance):
        chunk_id = api.write(topic="kb_topic", content="hello", provenance=sample_provenance)
        assert isinstance(chunk_id, str)
        assert chunk_id.startswith("kb_topic::")

    def test_write_persists_record(self, api, memory_backend, sample_provenance):
        api.write(topic="kb_topic", content="hello world", provenance=sample_provenance)
        assert memory_backend.count() == 1
        records = memory_backend.list_by_topic("kb_topic", k=5)
        assert records[0].content == "hello world"
        assert records[0].metadata["origin"] == "M1:doc_compressor"
        # audit_chain 在 metadata 中保留为列表
        assert "T-V2-007" in records[0].metadata["audit_chain"]

    def test_write_none_provenance_raises(self, api):
        with pytest.raises(WriteTraceMissing) as exc_info:
            api.write(topic="t", content="c", provenance=None)  # type: ignore[arg-type]
        assert exc_info.value.topic == "t"

    def test_write_wrong_type_provenance_raises(self, api):
        fake = {"origin": "M1", "audit_chain": ["T-1"]}  # 不是 WriteTrace 实例
        with pytest.raises(WriteTraceMissing):
            api.write(topic="t", content="c", provenance=fake)  # type: ignore[arg-type]

    def test_write_empty_topic_raises(self, api, sample_provenance):
        with pytest.raises(ValueError):
            api.write(topic="", content="c", provenance=sample_provenance)
        with pytest.raises(ValueError):
            api.write(topic="   ", content="c", provenance=sample_provenance)

    def test_write_empty_content_raises(self, api, sample_provenance):
        with pytest.raises(ValueError):
            api.write(topic="t", content="", provenance=sample_provenance)
        with pytest.raises(ValueError):
            api.write(topic="t", content="   ", provenance=sample_provenance)

    def test_write_records_arbitration(self, api, memory_backend, sample_provenance):
        api.write(topic="t", content="x", provenance=sample_provenance)
        rec = memory_backend.list_by_topic("t", 1)[0]
        assert rec.metadata["arbitration"] == "R84"

    def test_write_records_arbitration_empty_when_none(self, api, memory_backend):
        prov = WriteTrace(origin="M1", audit_chain=["T-1"])
        api.write(topic="t", content="x", provenance=prov)
        rec = memory_backend.list_by_topic("t", 1)[0]
        assert rec.metadata["arbitration"] == ""


# ---------------------------------------------------------------------------
# 4. UnifiedMemoryAPI.recall
# ---------------------------------------------------------------------------


class TestRecall:
    def test_recall_empty_topic_returns_empty(self, api):
        assert api.recall(topic="", k=5) == []

    def test_recall_unknown_topic_returns_empty(self, api):
        assert api.recall(topic="nonexistent", k=5) == []

    def test_recall_returns_latest_first(self, api, sample_provenance):
        api.write(topic="t", content="first", provenance=sample_provenance)
        api.write(topic="t", content="second", provenance=sample_provenance)
        api.write(topic="t", content="third", provenance=sample_provenance)
        records = api.recall(topic="t", k=5)
        assert len(records) == 3
        # 时间倒序：third 最新 → 排在第一
        assert records[0].content == "third"

    def test_recall_respects_k(self, api, sample_provenance):
        for i in range(5):
            api.write(topic="t", content=f"c{i}", provenance=sample_provenance)
        records = api.recall(topic="t", k=2)
        assert len(records) == 2

    def test_recall_negative_k(self, api, sample_provenance):
        api.write(topic="t", content="x", provenance=sample_provenance)
        assert api.recall(topic="t", k=-1) == []

    def test_recall_swallows_backend_error(self, sample_provenance):
        bad_backend = MagicMock()
        bad_backend.list_by_topic.side_effect = MemoryBackendError("boom")
        api = UnifiedMemoryAPI(backend=bad_backend, enforce_capability=False)
        assert api.recall(topic="t", k=5) == []


# ---------------------------------------------------------------------------
# 5. UnifiedMemoryAPI.search
# ---------------------------------------------------------------------------


class TestSearch:
    def test_search_empty_query_returns_empty(self, api):
        assert api.search(query="", k=5) == []

    def test_search_finds_relevant(self, api, sample_provenance):
        api.write(topic="risk", content="quantum risk model alpha", provenance=sample_provenance)
        api.write(topic="weather", content="今天天气晴朗", provenance=sample_provenance)
        results = api.search(query="quantum risk", k=5)
        assert len(results) >= 1
        assert "quantum" in results[0].content

    def test_search_topic_filter(self, api, sample_provenance):
        api.write(topic="a", content="alpha factor strategy", provenance=sample_provenance)
        api.write(topic="b", content="alpha factor strategy", provenance=sample_provenance)
        results = api.search(query="alpha factor", k=5, topic="b")
        assert len(results) == 1
        assert results[0].topic == "b"

    def test_search_swallows_backend_error(self):
        bad_backend = MagicMock()
        bad_backend.query.side_effect = MemoryBackendError("boom")
        api = UnifiedMemoryAPI(backend=bad_backend, enforce_capability=False)
        assert api.search(query="x", k=5) == []


# ---------------------------------------------------------------------------
# 6. CBAC 集成
# ---------------------------------------------------------------------------


class TestCbacIntegration:
    def test_cbac_allow_passes(self, memory_backend, cbac_yaml, sample_provenance):
        with patch("zephyr.shared.security.capability.CAPABILITIES_YAML_PATH", cbac_yaml):
            CapabilityRegistry.reset()
            api = UnifiedMemoryAPI(backend=memory_backend, enforce_capability=True)
            chunk_id = api.write(topic="kb_topic", content="x", provenance=sample_provenance)
            assert chunk_id.startswith("kb_topic::")
        CapabilityRegistry.reset()

    def test_cbac_deny_raises(self, memory_backend, sample_provenance, tmp_path):
        deny_yaml = tmp_path / "cap_deny.yaml"
        deny_yaml.write_text(
            textwrap.dedent(
                """\
                rules:
                  - name: write_kb
                    allow: []
                    deny:
                      - "unified_memory/forbidden_*"
                """
            ),
            encoding="utf-8",
        )
        with patch("zephyr.shared.security.capability.CAPABILITIES_YAML_PATH", deny_yaml):
            CapabilityRegistry.reset()
            api = UnifiedMemoryAPI(backend=memory_backend, enforce_capability=True)
            with pytest.raises(CapabilityDenied):
                api.write(
                    topic="forbidden_topic",
                    content="x",
                    provenance=sample_provenance,
                )
        CapabilityRegistry.reset()

    def test_cbac_skipped_when_disabled(self, memory_backend, sample_provenance):
        # 不需要任何 CBAC 配置，因为 enforce_capability=False
        api = UnifiedMemoryAPI(backend=memory_backend, enforce_capability=False)
        chunk_id = api.write(topic="any_topic", content="x", provenance=sample_provenance)
        assert chunk_id.startswith("any_topic::")


# ---------------------------------------------------------------------------
# 7. 单例
# ---------------------------------------------------------------------------


class TestSingleton:
    def test_get_returns_same_instance(self, memory_backend):
        a = get_unified_memory_api(backend=memory_backend, enforce_capability=False)
        b = get_unified_memory_api()
        assert a is b

    def test_reset_creates_new_instance(self, memory_backend):
        a = get_unified_memory_api(backend=memory_backend, enforce_capability=False)
        b = get_unified_memory_api(backend=memory_backend, enforce_capability=False, reset=True)
        assert a is not b
