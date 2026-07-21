# [A_test] module_id: MOD-GOV_ai_audit_logger | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_ai_audit_logger
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_ai_audit_logger.py
# [TTL] task_bound

from __future__ import annotations

import json

import pytest

from zephyr.trading.ai_audit_logger import AiAuditLogger


class TestAiAuditLoggerInit:
    def test_creates_log_dir(self, tmp_path):
        log_dir = tmp_path / "audit"
        AiAuditLogger(log_dir=log_dir)
        assert log_dir.exists()

    def test_session_id_default(self, tmp_path):
        logger = AiAuditLogger(log_dir=tmp_path)
        assert logger._session_id == ""

    def test_session_id_custom(self, tmp_path):
        logger = AiAuditLogger(log_dir=tmp_path, session_id="sess-001")
        assert logger._session_id == "sess-001"


class TestAiAuditLoggerLogInference:
    def test_log_inference_writes_entry(self, tmp_path):
        logger = AiAuditLogger(log_dir=tmp_path, session_id="s1")
        logger.log_inference(
            model="qwen3:8b",
            work_type="classification",
            input_snippet="hello",
            output_snippet="world",
            latency_ms=100.0,
            layer="local",
        )
        logger.flush()
        log_file = list(tmp_path.glob("ai_audit_*.jsonl"))[0]
        lines = log_file.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["log_type"] == "inference"
        assert entry["session_id"] == "s1"
        assert entry["detail"]["model"] == "qwen3:8b"
        assert entry["detail"]["work_type"] == "classification"
        assert entry["detail"]["latency_ms"] == 100.0
        assert entry["detail"]["layer"] == "local"

    def test_log_inference_snippet_truncation(self, tmp_path):
        logger = AiAuditLogger(log_dir=tmp_path)
        long_text = "x" * 500
        logger.log_inference(model="m", work_type="w", input_snippet=long_text, output_snippet=long_text)
        logger.flush()
        log_file = list(tmp_path.glob("ai_audit_*.jsonl"))[0]
        entry = json.loads(log_file.read_text(encoding="utf-8").strip())
        assert len(entry["detail"]["input_text_snippet"]) <= 200
        assert len(entry["detail"]["output_snippet"]) <= 200


class TestAiAuditLoggerLogEmbedding:
    def test_log_embedding_writes_entry(self, tmp_path):
        logger = AiAuditLogger(log_dir=tmp_path, session_id="s2")
        logger.log_embedding(model="bge-m3", text_length=100, dim=1024, latency_ms=50.0, layer="local")
        logger.flush()
        log_file = list(tmp_path.glob("ai_audit_*.jsonl"))[0]
        entry = json.loads(log_file.read_text(encoding="utf-8").strip())
        assert entry["log_type"] == "embedding"
        assert entry["detail"]["model"] == "bge-m3"
        assert entry["detail"]["text_length"] == 100
        assert entry["detail"]["dim"] == 1024


class TestAiAuditLoggerLogRouting:
    def test_log_routing_writes_entry(self, tmp_path):
        logger = AiAuditLogger(log_dir=tmp_path)
        logger.log_routing(task_id="t1", from_layer="L1", to_layer="L2", reason="capacity")
        logger.flush()
        log_file = list(tmp_path.glob("ai_audit_*.jsonl"))[0]
        entry = json.loads(log_file.read_text(encoding="utf-8").strip())
        assert entry["log_type"] == "routing"
        assert entry["detail"]["task_id"] == "t1"
        assert entry["detail"]["from_layer"] == "L1"
        assert entry["detail"]["to_layer"] == "L2"
        assert entry["detail"]["reason"] == "capacity"


class TestAiAuditLoggerLogAmbiguity:
    def test_log_ambiguity_writes_entry(self, tmp_path):
        logger = AiAuditLogger(log_dir=tmp_path)
        logger.log_ambiguity(
            entry_id="e1",
            task_id="t1",
            context="unclear requirement",
            options=[{"label": "A"}, {"label": "B"}],
        )
        logger.flush()
        log_file = list(tmp_path.glob("ai_audit_*.jsonl"))[0]
        entry = json.loads(log_file.read_text(encoding="utf-8").strip())
        assert entry["log_type"] == "ambiguity"
        assert entry["detail"]["entry_id"] == "e1"
        assert len(entry["detail"]["options"]) == 2

    def test_log_ambiguity_default_options(self, tmp_path):
        logger = AiAuditLogger(log_dir=tmp_path)
        logger.log_ambiguity(entry_id="e2", task_id="t2", context="test")
        logger.flush()
        log_file = list(tmp_path.glob("ai_audit_*.jsonl"))[0]
        entry = json.loads(log_file.read_text(encoding="utf-8").strip())
        assert entry["detail"]["options"] == []


class TestAiAuditLoggerLogHealth:
    def test_log_health_writes_entry(self, tmp_path):
        logger = AiAuditLogger(log_dir=tmp_path)
        logger.log_health(capability_id="cap-1", status="ACTIVE", latency_ms=10.0, error="")
        logger.flush()
        log_file = list(tmp_path.glob("ai_audit_*.jsonl"))[0]
        entry = json.loads(log_file.read_text(encoding="utf-8").strip())
        assert entry["log_type"] == "health"
        assert entry["detail"]["capability_id"] == "cap-1"
        assert entry["detail"]["status"] == "ACTIVE"


class TestAiAuditLoggerLogRegistration:
    def test_log_registration_writes_entry(self, tmp_path):
        logger = AiAuditLogger(log_dir=tmp_path)
        logger.log_registration(capability_id="cap-2", event="REGISTERED")
        logger.flush()
        log_file = list(tmp_path.glob("ai_audit_*.jsonl"))[0]
        entry = json.loads(log_file.read_text(encoding="utf-8").strip())
        assert entry["log_type"] == "registration"
        assert entry["detail"]["capability_id"] == "cap-2"
        assert entry["detail"]["event"] == "REGISTERED"


class TestAiAuditLoggerFlushAndPending:
    def test_has_pending_flush_after_write(self, tmp_path):
        logger = AiAuditLogger(log_dir=tmp_path)
        assert logger.has_pending_flush() is False
        logger.log_inference(model="m", work_type="w")
        assert logger.has_pending_flush() is True

    def test_flush_resets_pending(self, tmp_path):
        logger = AiAuditLogger(log_dir=tmp_path)
        logger.log_inference(model="m", work_type="w")
        logger.flush()
        assert logger.has_pending_flush() is False


@pytest.mark.filterwarnings("ignore::ResourceWarning")
class TestAiAuditLoggerQuery:
    def test_query_by_log_type(self, tmp_path):
        logger = AiAuditLogger(log_dir=tmp_path)
        logger.log_inference(model="m1", work_type="w1")
        logger.log_embedding(model="m2", text_length=10, dim=128)
        logger.flush()
        results = logger.query({"log_type": "inference"})
        assert len(results) == 1
        assert results[0]["detail"]["model"] == "m1"

    def test_query_by_detail_field(self, tmp_path):
        logger = AiAuditLogger(log_dir=tmp_path)
        logger.log_inference(model="qwen3", work_type="classify")
        logger.log_inference(model="bge", work_type="embed")
        logger.flush()
        results = logger.query({"model": "qwen3"})
        assert len(results) == 1
        assert results[0]["detail"]["model"] == "qwen3"

    def test_query_no_match(self, tmp_path):
        logger = AiAuditLogger(log_dir=tmp_path)
        logger.log_inference(model="m", work_type="w")
        logger.flush()
        results = logger.query({"log_type": "nonexistent"})
        assert len(results) == 0

    def test_query_empty_dir(self, tmp_path):
        logger = AiAuditLogger(log_dir=tmp_path)
        results = logger.query({"log_type": "inference"})
        assert results == []
