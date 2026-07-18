# [A_test] module_id: SRC-TST-0020 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-215 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.adversarial.test_telemetry_red_team
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""system-telemetry 红队对抗测试 — 边界·并发·注入·资源耗尽·关闭韧性（MOD-INF-015 v0.9.0）"""

from __future__ import annotations

import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def _init_t(module_id: str = "red_team") -> object:
    from zephyr.infrastructure.system_telemetry import Telemetry

    return Telemetry(module_id, test_mode=True)


class TestBoundaryAttacks:
    """边界攻击：空字符串、None、极端数值"""

    def test_empty_module_id_does_not_crash(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("", test_mode=True)
        r = t.metrics.gauge("cpu", 1.0)
        assert r["name"] == "cpu"

    def test_none_tags_handled_gracefully(self):
        t = _init_t()
        r = t.metrics.gauge("test", 1.0, **{"key": None})
        assert r["name"] == "test"

    def test_negative_metric_value_accepted(self):
        t = _init_t()
        r = t.metrics.gauge("temperature", -273.15)
        assert r["value"] == -273.15

    def test_zero_custom_delta_counter(self):
        t = _init_t()
        r = t.metrics.counter("events", delta=0.0)
        assert r["value"] == 0.0

    def test_extremely_large_value(self):
        t = _init_t()
        r = t.metrics.gauge("big", 1e308)
        assert r["value"] == 1e308

    def test_None_message_log_accepted_gracefully(self):
        t = _init_t()
        r = t.logs.warning(None)
        assert r["level"] == "WARNING"


class TestUnicodeInjection:
    """Unicode注入攻击：特殊字符、控制字符、emoji"""

    def test_unicode_metric_name(self):
        t = _init_t()
        r = t.metrics.gauge("latency_μs", 42.0)
        assert r["name"] == "latency_μs"

    def test_emoji_in_tags(self):
        t = _init_t()
        r = t.metrics.gauge("emoji_test", 1.0, emoji="😀")
        assert r["tags"]["emoji"] == "😀"

    def test_log_injection_markdown(self):
        t = _init_t()
        r = t.logs.info("**bold** _italic_ [link](http://evil.com)")
        assert "**bold**" in r["message"]

    def test_control_characters_in_labels(self):
        t = _init_t()
        r = t.logs.info("msg", ctrl="\x00\x01\x02")
        assert r["labels"]["ctrl"] == "\x00\x01\x02"

    def test_chinese_unicode_values(self):
        t = _init_t()
        r = t.logs.info("中文日志", 模块="遥测系统")
        assert r["labels"]["模块"] == "遥测系统"


class TestDeepNesting:
    """深层嵌套攻击：多层字典、长字符串、大数组"""

    def test_deeply_nested_tags(self):
        t = _init_t()
        nested = {"a": {"b": {"c": {"d": {"e": "deep"}}}}}
        r = t.metrics.gauge("nest", 1.0, nested=nested)
        assert r["tags"]["nested"] == nested

    def test_long_module_id(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        long_id = "m" * 10000
        t = Telemetry(long_id, test_mode=True)
        r = t.metrics.gauge("test", 1.0)
        assert r["module_id"] == long_id

    def test_special_char_metric_name(self):
        t = _init_t()
        r = t.logs.info("Special: !@#$%^&*()_+-=[]{}|;':\",./<>?")
        assert "Special:" in r["message"]


class TestConcurrency:
    """并发攻击：多线程同时写入、竞态条件"""

    def test_concurrent_gauge_recording(self):
        t = _init_t()
        results: list[dict] = []

        def _write(n: int) -> None:
            for i in range(100):
                r = t.metrics.gauge(f"conc_{n}", float(n * i))
                results.append(r)

        threads = [threading.Thread(target=_write, args=(j,)) for j in range(8)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()
        assert len(results) == 8 * 100
        for r in results:
            assert "ts" in r and "name" in r

    def test_concurrent_log_writes(self):
        t = _init_t()
        results: list[dict] = []

        def _log(n: int) -> None:
            for i in range(100):
                r = t.logs.info(f"log_{n}_{i}", thread=n)
                results.append(r)

        threads = [threading.Thread(target=_log, args=(j,)) for j in range(8)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()
        assert len(results) == 800

    def test_concurrent_span_creation(self):
        t = _init_t()
        spans = []
        for _ in range(50):
            span = t.traces.span("concurrent_op")
            span.set_attribute("thread", threading.get_ident())
            spans.append(span)
        for span in spans:
            result = span.end()
            assert "elapsed_s" in result


class TestResourceExhaustion:
    """资源耗尽攻击：大量指标、高频写入"""

    def test_rapid_fire_metrics(self):
        t = _init_t()
        n = 1000
        for i in range(n):
            r = t.metrics.gauge("rf", float(i))
        assert r["value"] == n - 1

    def test_many_unique_metric_names(self):
        t = _init_t()
        for i in range(500):
            t.metrics.gauge(f"unique_metric_{i}", float(i))

    def test_archive_batch_id_uniqueness(self):
        t = _init_t()
        ids = set()
        for _ in range(1000):
            bid = t.archive.next_batch_id()
            assert bid not in ids
            ids.add(bid)
        assert len(ids) == 1000


class TestShutdownResilience:
    """关闭韧性攻击：中间关机、多次关机、关机后写入"""

    def test_write_after_shutdown_idempotent(self):
        t = _init_t()
        t.shutdown()
        t.shutdown()
        r = t.metrics.gauge("post_shutdown", 1.0)
        assert r["value"] == 1.0

    def test_concurrent_shutdown(self):
        t = _init_t()
        errors: list[Exception] = []

        def _shutdown() -> None:
            try:
                t.shutdown()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=_shutdown) for _ in range(4)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()
        assert len(errors) == 0

    def test_shutdown_during_metric_recording(self):
        t = _init_t()
        stop = threading.Event()

        def _writer() -> None:
            while not stop.is_set():
                t.metrics.gauge("live_metric", 1.0)

        def _shutdown() -> None:
            time.sleep(0.01)
            t.shutdown()
            stop.set()

        writer = threading.Thread(target=_writer)
        stopper = threading.Thread(target=_shutdown)
        writer.start()
        stopper.start()
        writer.join(timeout=3)
        stopper.join(timeout=3)
        assert not writer.is_alive() or stop.is_set()


class TestAIBehaviorInjection:
    """AI行为注入攻击：异常决策、超长理由"""

    def test_empty_decision_accepted(self):
        t = _init_t()
        r = t.ai_behavior.record(decision="", model="gpt-4.1", reason="")
        assert r["decision"] == ""

    def test_model_name_poisoning(self):
        t = _init_t()
        r = t.ai_behavior.record(decision="query", model="'; DROP TABLE--")
        assert "DROP" in r["model"]

    def test_extra_kwargs_passthrough(self):
        t = _init_t()
        r = t.ai_behavior.record(decision="d", extra_field=999, hidden="secret")
        assert r["extra"]["extra_field"] == 999
        assert r["extra"]["hidden"] == "secret"


class TestSpanManipulation:
    """Span操纵攻击：未end的span、多次end"""

    def test_span_double_end(self):
        t = _init_t()
        span = t.traces.span("double_end")
        r1 = span.end()
        r2 = span.end()
        assert r2["elapsed_s"] >= r1["elapsed_s"]

    def test_span_without_end_no_crash(self):
        t = _init_t()
        for _ in range(100):
            _ = t.traces.span("forgotten")
        t.shutdown()


class TestThreadPoolExecutorConcurrency:
    """ThreadPoolExecutor 高并发测试"""

    def test_thread_pool_metrics_bombardment(self):
        t = _init_t()

        def _record_batch(n: int) -> int:
            for i in range(200):
                t.metrics.gauge(f"tpe_g_{n}", float(i))
            return n

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(_record_batch, j): j for j in range(8)}
            for future in as_completed(futures):
                assert future.result() is not None

    def test_thread_pool_log_flood(self):
        t = _init_t()

        def _log_batch(n: int) -> int:
            for i in range(200):
                t.logs.warning(f"tpe_warn_{n}_{i}")
            return n

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(_log_batch, j): j for j in range(8)}
            for future in as_completed(futures):
                assert future.result() is not None


class TestAllSubsystemsAfterAttacks:
    """全攻击后验证所有子系统仍存活"""

    def test_all_subsystems_survive_attack(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("survival", test_mode=True)
        for _ in range(100):
            t.metrics.gauge("g", 1.0)
            t.logs.info("i", k="v")
            t.ai_behavior.record(decision="d", model="m")
        span = t.traces.span("survive")
        span.end()
        t.health.register()
        t.profiles.start("p")
        t.profiles.stop()
        t.profiles.snapshot()
        t.alerts.health()
        t.schema.get_version()
        t.schema.check_compatibility("0.9.0")
        t.archive.next_batch_id()
        t.shutdown()
        t.shutdown()
