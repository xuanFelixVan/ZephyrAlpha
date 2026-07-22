# [A_test] module_id: MOD-GOV_ai_behavior_audit_logger_llm_security | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-528 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.llm_security.test_ai_behavior_audit_logger
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
Unit tests for ai_behavior_audit_logger.py (T-2-32)
"""


import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from zephyr.security.llm_defense.llm_security.behavior_audit_logger import (
    AuditAction as BehaviorEventType,
)
from zephyr.security.llm_defense.llm_security.behavior_audit_logger import (
    AuditEvent,
    AuditLogger,
    AuditQuery,
    RotationPolicy,
    open_audit_log,
)


@pytest.fixture
def tmp_log_dir(tmp_path: Path) -> Path:
    log_dir = tmp_path / "audit_logs"
    log_dir.mkdir()
    return log_dir


@pytest.fixture
def logger(tmp_log_dir: Path) -> AuditLogger:
    return AuditLogger(
        log_dir=tmp_log_dir,
        rotation=RotationPolicy.SIZE,
        max_file_size=1024 * 1024,
        session_id="test-session-001",
        model="GLM-5.1",
    )


@pytest.fixture
def logger_date_rotation(tmp_log_dir: Path) -> AuditLogger:
    return AuditLogger(
        log_dir=tmp_log_dir,
        rotation=RotationPolicy.DATE,
        session_id="test-session-002",
        model="Opus-4",
    )


class TestAuditEvent:
    def test_to_dict_contains_all_required_fields(self) -> None:
        event = AuditEvent(
            timestamp="2026-04-23T12:00:00+00:00",
            model="GLM-5.1",
            action="model_call",
            target="gpt-4",
            result="success",
            session_id="s1",
        )
        d = event.to_dict()
        assert d["timestamp"] == "2026-04-23T12:00:00+00:00"
        assert d["model"] == "GLM-5.1"
        assert d["action"] == "model_call"
        assert d["target"] == "gpt-4"
        assert d["result"] == "success"
        assert d["session_id"] == "s1"
        assert "extra" not in d

    def test_to_dict_includes_extra(self) -> None:
        event = AuditEvent(
            timestamp="2026-04-23T12:00:00+00:00",
            model="GLM-5.1",
            action="file_write",
            target="test.md",
            result="ok",
            session_id="s1",
            extra={"bytes_written": 42},
        )
        d = event.to_dict()
        assert d["extra"]["bytes_written"] == 42

    def test_to_jsonl_is_valid_json(self) -> None:
        event = AuditEvent(
            timestamp="2026-04-23T12:00:00+00:00",
            model="GLM-5.1",
            action="gate_decision",
            target="G1",
            result="pass",
            session_id="s1",
        )
        line = event.to_jsonl()
        parsed = json.loads(line)
        assert parsed["action"] == "gate_decision"

    def test_to_jsonl_is_single_line(self) -> None:
        event = AuditEvent(
            timestamp="2026-04-23T12:00:00+00:00",
            model="GLM-5.1",
            action="rule_trigger",
            target="R1",
            result="blocked",
            session_id="s1",
            extra={"reason": "multiline\ntext"},
        )
        line = event.to_jsonl()
        assert "\n" not in line


class TestBehaviorEventType:
    def test_values(self):
        assert BehaviorEventType.MODEL_CALL.value == "model_call"
        assert BehaviorEventType.FILE_WRITE.value == "file_write"
        assert BehaviorEventType.RULE_TRIGGER.value == "rule_trigger"
        assert BehaviorEventType.GATE_DECISION.value == "gate_decision"


class TestAuditLoggerBasic:
    def test_log_creates_jsonl_file(self, logger: AuditLogger, tmp_log_dir: Path) -> None:
        logger.log_model_call(target="gpt-4", result="success")
        jsonl_files = list(tmp_log_dir.glob("*.jsonl"))
        assert len(jsonl_files) == 1

    def test_log_writes_valid_jsonl(self, logger: AuditLogger, tmp_log_dir: Path) -> None:
        logger.log_model_call(target="gpt-4", result="success")
        jsonl_file = next(tmp_log_dir.glob("*.jsonl"))
        line = jsonl_file.read_text(encoding="utf-8").strip()
        data = json.loads(line)
        assert data["action"] == "model_call"
        assert data["target"] == "gpt-4"
        assert data["result"] == "success"
        assert data["session_id"] == "test-session-001"
        assert data["model"] == "GLM-5.1"

    def test_log_file_write(self, logger: AuditLogger, tmp_log_dir: Path) -> None:
        logger.log_file_write(target="docs/test.md", result="ok")
        data = _read_first_event(tmp_log_dir)
        assert data["action"] == "file_write"

    def test_log_rule_trigger(self, logger: AuditLogger, tmp_log_dir: Path) -> None:
        logger.log_rule_trigger(target="R-001", result="blocked")
        data = _read_first_event(tmp_log_dir)
        assert data["action"] == "rule_trigger"

    def test_log_gate_decision(self, logger: AuditLogger, tmp_log_dir: Path) -> None:
        logger.log_gate_decision(target="G1-Ingest", result="pass")
        data = _read_first_event(tmp_log_dir)
        assert data["action"] == "gate_decision"

    def test_log_with_override_session_and_model(self, logger: AuditLogger, tmp_log_dir: Path) -> None:
        logger.log_model_call(
            target="gpt-4",
            result="success",
            session_id="override-session",
            model="Opus-4",
        )
        data = _read_first_event(tmp_log_dir)
        assert data["session_id"] == "override-session"
        assert data["model"] == "Opus-4"

    def test_log_with_extra(self, logger: AuditLogger, tmp_log_dir: Path) -> None:
        logger.log_model_call(
            target="gpt-4",
            result="success",
            extra={"tokens": 150, "latency_ms": 200},
        )
        data = _read_first_event(tmp_log_dir)
        assert data["extra"]["tokens"] == 150
        assert data["extra"]["latency_ms"] == 200

    def test_timestamp_is_iso8601(self, logger: AuditLogger, tmp_log_dir: Path) -> None:
        logger.log_model_call(target="gpt-4", result="success")
        data = _read_first_event(tmp_log_dir)
        ts = data["timestamp"]
        parsed = datetime.fromisoformat(ts)
        assert parsed.tzinfo is not None

    def test_multiple_events_are_appended(self, logger: AuditLogger, tmp_log_dir: Path) -> None:
        for i in range(5):
            logger.log_model_call(target=f"target-{i}", result="ok")
        assert logger.count_events() == 5


class TestAuditLoggerRotation:
    def test_size_rotation_creates_new_file(self, tmp_log_dir: Path) -> None:
        small_logger = AuditLogger(
            log_dir=tmp_log_dir,
            rotation=RotationPolicy.SIZE,
            max_file_size=200,
            session_id="rot-test",
            model="GLM-5.1",
        )
        for i in range(20):
            small_logger.log_model_call(
                target=f"target-{i:04d}",
                result="ok",
                extra={"padding": "x" * 50},
            )
        jsonl_files = list(tmp_log_dir.glob("*.jsonl"))
        assert len(jsonl_files) >= 2

    def test_date_rotation_uses_date_in_filename(self, logger_date_rotation: AuditLogger, tmp_log_dir: Path) -> None:
        logger_date_rotation.log_model_call(target="gpt-4", result="success")
        jsonl_files = list(tmp_log_dir.glob("audit-*.jsonl"))
        assert len(jsonl_files) == 1
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        assert today in jsonl_files[0].name


class TestAuditQuery:
    def test_query_by_session_id(self, logger: AuditLogger) -> None:
        logger.log_model_call(target="t1", result="ok", session_id="s1")
        logger.log_model_call(target="t2", result="ok", session_id="s2")
        results = logger.query(AuditQuery(session_id="s1"))
        assert len(results) == 1
        assert results[0].target == "t1"

    def test_query_by_model(self, logger: AuditLogger) -> None:
        logger.log_model_call(target="t1", result="ok", model="GLM-5.1")
        logger.log_model_call(target="t2", result="ok", model="Opus-4")
        results = logger.query(AuditQuery(model="Opus-4"))
        assert len(results) == 1
        assert results[0].target == "t2"

    def test_query_by_action(self, logger: AuditLogger) -> None:
        logger.log_model_call(target="t1", result="ok")
        logger.log_file_write(target="t2", result="ok")
        results = logger.query(AuditQuery(action="file_write"))
        assert len(results) == 1
        assert results[0].target == "t2"

    def test_query_by_time_range(self, logger: AuditLogger) -> None:
        logger.log_model_call(target="t1", result="ok")
        now = datetime.now(UTC).isoformat()
        results = logger.query(AuditQuery(time_from="2020-01-01T00:00:00+00:00", time_to=now))
        assert len(results) >= 1

    def test_query_no_match(self, logger: AuditLogger) -> None:
        logger.log_model_call(target="t1", result="ok")
        results = logger.query(AuditQuery(session_id="nonexistent"))
        assert len(results) == 0

    def test_query_iter_returns_iterator(self, logger: AuditLogger) -> None:
        logger.log_model_call(target="t1", result="ok")
        logger.log_model_call(target="t2", result="ok")
        events = list(logger.query_iter(AuditQuery()))
        assert len(events) == 2

    def test_query_combined_filters(self, logger: AuditLogger) -> None:
        logger.log_model_call(target="t1", result="ok", session_id="s1")
        logger.log_model_call(target="t2", result="ok", session_id="s1", model="Opus-4")
        logger.log_file_write(target="t3", result="ok", session_id="s1")
        results = logger.query(AuditQuery(session_id="s1", action="model_call"))
        assert len(results) == 2


class TestOpenAuditLog:
    def test_open_audit_log_factory(self, tmp_log_dir: Path) -> None:
        al = open_audit_log(log_dir=tmp_log_dir, session_id="factory-test", model="GLM-5.1")
        assert isinstance(al, AuditLogger)
        al.log_model_call(target="t1", result="ok")
        assert al.count_events() == 1


class TestAppendOnly:
    def test_no_delete_or_update_methods(self) -> None:
        public_methods = [
            m for m in dir(AuditLogger) if not m.startswith("_") and callable(getattr(AuditLogger, m, None))
        ]
        for m in public_methods:
            assert "delete" not in m.lower(), f"Found delete method: {m}"
            assert "update" not in m.lower(), f"Found update method: {m}"
            assert "remove" not in m.lower(), f"Found remove method: {m}"
            assert "modify" not in m.lower(), f"Found modify method: {m}"


def _read_first_event(log_dir: Path) -> dict[str, Any]:
    jsonl_file = next(log_dir.glob("*.jsonl"))
    line = jsonl_file.read_text(encoding="utf-8").strip().split("\n")[0]
    return json.loads(line)
