# [A_test] module_id: MOD-GOV_structured_sink | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | 蓝图特有§A
# [MODULE] tests.test_structured_sink
# [INVARIANTS] PII自动脱敏;RULE-ONE原子写入;buffer capped at _BUFFER_MAX
# [MODIFY-GUARD] logs/structured_sink.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 写入失败→stderr→内存缓冲→丢弃+告警
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

ss = pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.logs.structured_sink",
    reason="structured_sink import failed",
)


@pytest.fixture(autouse=True)
def _clear_buffer():
    with ss.buffer_lock:
        ss.log_buffer.clear()
    original_dir = ss._DEFAULT_LOG_DIR
    original_max = ss._BUFFER_MAX
    yield
    with ss.buffer_lock:
        ss.log_buffer.clear()
    ss._DEFAULT_LOG_DIR = original_dir
    ss._BUFFER_MAX = original_max


class TestConfigure:
    def test_configure_log_dir(self, tmp_path):
        ss.configure(log_dir=tmp_path / "logs")
        assert tmp_path / "logs" == ss._DEFAULT_LOG_DIR

    def test_configure_buffer_size(self):
        ss.configure(buffer_size=100)
        assert ss._BUFFER_MAX == 100

    def test_configure_max_file_bytes(self):
        ss.configure(max_file_bytes=5 * 1024 * 1024)
        assert ss._MAX_FILE_BYTES == 5 * 1024 * 1024


class TestAppendJsonlRecord:
    def test_appends_to_buffer(self):
        result = ss.append_jsonl_record({"message": "test"})
        assert result is True
        assert ss.buffer_depth() == 1

    def test_with_labels(self):
        ss.append_jsonl_record({"message": "test"}, labels={"type": "unit"})
        assert ss.buffer_depth() == 1

    def test_returns_true(self):
        result = ss.append_jsonl_record({"key": "value"})
        assert result is True


class TestLogRecordStub:
    def test_creates_record(self):
        record = ss.log_record_stub("INFO", "test_message", key="val")
        assert record["level"] == "INFO"
        assert record["message"] == "test_message"
        assert record["labels"]["key"] == "val"

    def test_has_timestamp(self):
        record = ss.log_record_stub("INFO", "msg")
        assert "ts" in record


class TestFlush:
    def test_empty_buffer(self):
        count = ss.flush()
        assert count == 0

    def test_flush_writes_to_file(self, tmp_path):
        ss.configure(log_dir=tmp_path / "logs")
        ss.append_jsonl_record({"message": "flush_test"})
        count = ss.flush()
        assert count == 1


class TestPanicFlush:
    def test_delegates_to_flush(self):
        ss.append_jsonl_record({"message": "panic_test"})
        count = ss.panic_flush()
        assert count == 1


class TestBufferDepth:
    def test_empty(self):
        assert ss.buffer_depth() == 0

    def test_after_append(self):
        ss.append_jsonl_record({"message": "test"})
        assert ss.buffer_depth() == 1


class TestBoundary:
    def test_append_empty_record(self):
        result = ss.append_jsonl_record({})
        assert result is True

    def test_append_none_labels(self):
        result = ss.append_jsonl_record({"msg": "test"}, labels=None)
        assert result is True

    def test_log_record_stub_empty_message(self):
        record = ss.log_record_stub("ERROR", "")
        assert record["message"] == ""

    def test_log_record_stub_various_levels(self):
        for level in ("INFO", "WARNING", "ERROR"):
            record = ss.log_record_stub(level, "msg")
            assert record["level"] == level
