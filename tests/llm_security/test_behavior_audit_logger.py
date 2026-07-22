# [A_test] module_id: MOD-GOV_behavior_audit_logger | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] tests.llm_security.test_behavior_audit_logger
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
import json
import tempfile
from pathlib import Path

from zephyr.security.llm_defense.llm_security.behavior_audit_logger import (
    AuditAction,
    AuditEvent,
    AuditLogger,
    AuditQuery,
    open_audit_log,
)


class TestAuditEvent:
    def test_create_event(self):
        event = AuditEvent(
            timestamp="2026-01-01T00:00:00Z",
            model="test-model",
            action="model_call",
            target="test-target",
            result="ok",
            session_id="s1",
        )
        assert event.timestamp == "2026-01-01T00:00:00Z"
        assert event.model == "test-model"
        assert event.action == "model_call"

    def test_to_dict(self):
        event = AuditEvent(
            timestamp="2026-01-01T00:00:00Z",
            model="m",
            action="a",
            target="t",
            result="r",
            session_id="s",
        )
        d = event.to_dict()
        assert "timestamp" in d
        assert d["action"] == "a"

    def test_to_dict_with_extra(self):
        event = AuditEvent(
            timestamp="2026-01-01T00:00:00Z",
            model="m",
            action="a",
            target="t",
            result="r",
            session_id="s",
            extra={"key": "value"},
        )
        d = event.to_dict()
        assert d["extra"]["key"] == "value"

    def test_to_jsonl(self):
        event = AuditEvent(
            timestamp="2026-01-01T00:00:00Z",
            model="m",
            action="a",
            target="t",
            result="r",
            session_id="s",
        )
        line = event.to_jsonl()
        data = json.loads(line)
        assert data["model"] == "m"


class TestAuditQuery:
    def test_query_by_session_id(self):
        event = AuditEvent(
            timestamp="2026-01-01T00:00:00Z",
            model="m",
            action="a",
            target="t",
            result="r",
            session_id="s1",
        )
        q = AuditQuery(session_id="s1")
        assert q.matches(event) is True

    def test_query_by_session_id_no_match(self):
        event = AuditEvent(
            timestamp="2026-01-01T00:00:00Z",
            model="m",
            action="a",
            target="t",
            result="r",
            session_id="s1",
        )
        q = AuditQuery(session_id="s2")
        assert q.matches(event) is False

    def test_query_by_model(self):
        event = AuditEvent(
            timestamp="2026-01-01T00:00:00Z",
            model="gpt-4",
            action="a",
            target="t",
            result="r",
            session_id="s1",
        )
        q = AuditQuery(model="gpt-4")
        assert q.matches(event) is True

    def test_query_by_action(self):
        event = AuditEvent(
            timestamp="2026-01-01T00:00:00Z",
            model="m",
            action="model_call",
            target="t",
            result="r",
            session_id="s1",
        )
        q = AuditQuery(action="model_call")
        assert q.matches(event) is True


class TestAuditLogger:
    def test_log_creates_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = AuditLogger(log_dir=Path(tmp), session_id="test", model="test-model")
            logger.log(action=AuditAction.MODEL_CALL, target="api", result="ok")
            files = list(Path(tmp).glob("*.jsonl"))
            assert len(files) >= 1

    def test_log_and_query(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = AuditLogger(log_dir=Path(tmp), session_id="s1", model="m1")
            logger.log(action=AuditAction.MODEL_CALL, target="api", result="ok")
            logger.log(action=AuditAction.GATE_DECISION, target="gate1", result="blocked")
            results = logger.query(AuditQuery(session_id="s1"))
            assert len(results) == 2

    def test_log_model_call_shortcut(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = AuditLogger(log_dir=Path(tmp), session_id="s1", model="m1")
            logger.log_model_call(target="api", result="ok")
            results = logger.query(AuditQuery(action="model_call"))
            assert len(results) == 1

    def test_log_file_write_shortcut(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = AuditLogger(log_dir=Path(tmp), session_id="s1", model="m1")
            logger.log_file_write(target="/tmp/test.py", result="ok")
            results = logger.query(AuditQuery(action="file_write"))
            assert len(results) == 1

    def test_count_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = AuditLogger(log_dir=Path(tmp), session_id="s1", model="m1")
            logger.log(action=AuditAction.MODEL_CALL, target="api", result="ok")
            logger.log(action=AuditAction.RULE_TRIGGER, target="rule1", result="fired")
            assert logger.count_events() == 2

    def test_log_dir_property(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = AuditLogger(log_dir=Path(tmp))
            assert logger.log_dir == Path(tmp)


class TestOpenAuditLog:
    def test_open_audit_log_factory(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = open_audit_log(log_dir=Path(tmp), session_id="s1")
            assert isinstance(logger, AuditLogger)
