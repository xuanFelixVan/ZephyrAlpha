# [A_test] module_id: MOD-GOV_observability_logging | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_observability_logging

# [INVARIANTS] trace_context自动传播trace_id;get_logger缓存;ZephyrLogger注入z_trace_id

# [MODIFY-GUARD] logging.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 无

# [TESTS] pytest tests/test_observability_logging.py -q
# [TTL] task_bound

import logging

import pytest

from zephyr.shared.utils.logging import (
    LogLevel,
    ZephyrLogger,
    _logger_cache,
    _StructuredFormatter,
    get_logger,
    module_id_var,
    session_id_var,
    trace_context,
    trace_id_var,
)


@pytest.fixture(autouse=True)
def _clear_cache():
    _logger_cache.clear()
    trace_id_var.set("")
    session_id_var.set("")
    module_id_var.set("")
    yield
    _logger_cache.clear()
    trace_id_var.set("")
    session_id_var.set("")
    module_id_var.set("")


class TestLogLevel:
    def test_constants(self):
        assert LogLevel.DEBUG == "DEBUG"
        assert LogLevel.INFO == "INFO"
        assert LogLevel.WARNING == "WARNING"
        assert LogLevel.ERROR == "ERROR"
        assert LogLevel.CRITICAL == "CRITICAL"


class TestZephyrLogger:
    def test_creates_logger(self):
        zl = ZephyrLogger("test.module")
        assert zl._name == "test.module"

    def test_info_logs_without_error(self):
        zl = ZephyrLogger("test.info")
        zl.info("hello world")

    def test_debug_logs(self):
        zl = ZephyrLogger("test.debug")
        zl.debug("debug msg")

    def test_warning_logs(self):
        zl = ZephyrLogger("test.warn")
        zl.warning("warn msg")

    def test_error_logs(self):
        zl = ZephyrLogger("test.err")
        zl.error("err msg")

    def test_critical_logs(self):
        zl = ZephyrLogger("test.crit")
        zl.critical("crit msg")

    def test_info_with_extra(self):
        zl = ZephyrLogger("test.extra")
        zl.info("msg", extra={"key": "val"})

    def test_error_with_exc_info(self):
        zl = ZephyrLogger("test.exc")
        try:
            raise ValueError("test")
        except ValueError:
            zl.error("caught", exc_info=True)

    def test_bind_returns_bound_logger(self):
        zl = ZephyrLogger("test.bind")
        bound = zl.bind(request_id="req-123")
        assert bound is not None
        bound.info("bound msg")


class TestGetLogger:
    def test_returns_zephyr_logger(self):
        logger = get_logger("test.get")
        assert isinstance(logger, ZephyrLogger)

    def test_caches_by_name(self):
        l1 = get_logger("test.cache")
        l2 = get_logger("test.cache")
        assert l1 is l2

    def test_different_names_different_loggers(self):
        l1 = get_logger("test.a")
        l2 = get_logger("test.b")
        assert l1 is not l2

    def test_sets_session_id(self):
        get_logger("test.sess", session_id="sess-001")
        assert session_id_var.get() == "sess-001"

    def test_sets_module_id(self):
        get_logger("test.mod", module_id="MOD-INF-016")
        assert module_id_var.get() == "MOD-INF-016"


class TestTraceContext:
    def test_sets_trace_id(self):
        with trace_context("trace-abc") as tid:
            assert tid == "trace-abc"
            assert trace_id_var.get() == "trace-abc"

    def test_generates_trace_id_if_none(self):
        with trace_context() as tid:
            assert tid != ""
            assert len(tid) == 36

    def test_restores_after_exit(self):
        trace_id_var.set("before")
        with trace_context("during"):
            assert trace_id_var.get() == "during"
        assert trace_id_var.get() == "before"

    def test_sets_session_id(self):
        with trace_context("t1", session_id="s1"):
            assert session_id_var.get() == "s1"

    def test_sets_module_id(self):
        with trace_context("t2", module_id="m2"):
            assert module_id_var.get() == "m2"

    def test_nested_contexts(self):
        with trace_context("outer") as outer_id:
            assert trace_id_var.get() == "outer"
            with trace_context("inner") as inner_id:
                assert trace_id_var.get() == "inner"
            assert trace_id_var.get() == "outer"


class TestStructuredFormatter:
    def test_format_produces_json(self):
        formatter = _StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="hello",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        import json

        parsed = json.loads(output)
        assert parsed["message"] == "hello"
        assert parsed["level"] == "INFO"
        assert "timestamp" in parsed
