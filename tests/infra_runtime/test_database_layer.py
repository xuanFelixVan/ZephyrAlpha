# [BLUEPRINT] MOD-INF-077 | docs/03_modules/_domain_infrastructure_runtime/database_layer/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-077 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infra_runtime.test_database_layer
# [TESTS] src/zephyr/infra_runtime/database_layer.py
"""MOD-INF-077 单元测试：database_layer 数据库统一抽象层。

蓝图验收（B13-04299/CAND-H1FS-010，A3数据架构）：
DbBackend 协议（query/execute/health/close 语义统一）+ register_backend
注册 + route(key) 统一门面路由 + 连接借还上下文管理器 + 超时重试
（注入时钟/sleeper）。测试用 sqlite3 内存库实现 fake backend 验证门面路由；
flaky backend 验证重试与超时；时钟/sleeper 全注入内存替身。
"""

from __future__ import annotations

import sqlite3

import pytest

pytest.importorskip(
    "zephyr.infra_runtime.database_layer",
    reason="database_layer not importable",
)

from zephyr.infra_runtime.database_layer import (  # noqa: E402
    DatabaseLayer,
    DatabaseLayerError,
)


class _FakeClock:
    """确定性单调时钟替身。"""

    def __init__(self, t0: float = 500.0) -> None:
        self.now = t0

    def __call__(self) -> float:
        return self.now

    def advance(self, dt: float) -> None:
        self.now += dt


class _SqliteMemoryBackend:
    """sqlite3 内存库 fake backend（满足 DbBackend 协议）。"""

    def __init__(self) -> None:
        self._conn = sqlite3.connect(":memory:")
        self.closed = False

    def query(self, sql: str, params: tuple = ()) -> list[tuple]:
        return list(self._conn.execute(sql, params).fetchall())

    def execute(self, sql: str, params: tuple = ()) -> int:
        cur = self._conn.execute(sql, params)
        self._conn.commit()
        return cur.rowcount

    def health(self) -> bool:
        if self.closed:
            return False
        self._conn.execute("SELECT 1")
        return True

    def close(self) -> None:
        self.closed = True
        self._conn.close()


class _FlakyBackend:
    """前 fail_times 次抛异常后恢复的 fake backend。"""

    def __init__(self, fail_times: int, clock: _FakeClock | None = None, slow: float = 0.0) -> None:
        self._fail_left = fail_times
        self.calls = 0
        self._clock = clock
        self._slow = slow

    def query(self, sql: str, params: tuple = ()) -> list[tuple]:
        self.calls += 1
        if self._clock is not None and self._slow:
            self._clock.advance(self._slow)  # 模拟耗时
        if self._fail_left > 0:
            self._fail_left -= 1
            raise RuntimeError("transient db error")
        return [("ok",)]

    def execute(self, sql: str, params: tuple = ()) -> int:
        return self.query(sql, params) and 1

    def health(self) -> bool:
        return True

    def close(self) -> None:
        pass


def _layer(clock: _FakeClock | None = None, sleeps: list | None = None) -> DatabaseLayer:
    return DatabaseLayer(
        clock=clock or _FakeClock(),
        sleeper=(lambda s: sleeps.append(s)) if sleeps is not None else None,
    )


@pytest.fixture()
def layer_with_sqlite():
    layer = _layer()
    backend = _SqliteMemoryBackend()
    layer.register_backend("sqlite_main", backend)
    yield layer, backend
    backend.close()


# ──────────────────────────────────────────────────────────────────────────────
# 注册与路由
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterRoute:
    def test_register_and_route(self, layer_with_sqlite) -> None:
        layer, backend = layer_with_sqlite
        assert layer.route("sqlite_main") is backend

    def test_register_empty_name_raises(self) -> None:
        with pytest.raises(DatabaseLayerError):
            _layer().register_backend("", _SqliteMemoryBackend())

    def test_register_duplicate_raises(self, layer_with_sqlite) -> None:
        layer, _ = layer_with_sqlite
        with pytest.raises(DatabaseLayerError):
            layer.register_backend("sqlite_main", _SqliteMemoryBackend())

    def test_register_protocol_mismatch_raises(self) -> None:
        class _NotBackend:
            def query(self, sql: str, params: tuple = ()) -> list[tuple]:
                return []

        with pytest.raises(DatabaseLayerError):
            _layer().register_backend("bad", _NotBackend())  # type: ignore[arg-type]

    def test_route_unknown_raises(self) -> None:
        with pytest.raises(DatabaseLayerError):
            _layer().route("ghost")

    def test_route_closed_raises(self, layer_with_sqlite) -> None:
        layer, _ = layer_with_sqlite
        layer.close("sqlite_main")
        with pytest.raises(DatabaseLayerError):
            layer.route("sqlite_main")


# ──────────────────────────────────────────────────────────────────────────────
# 门面路由（真实 sqlite 内存库读写）
# ──────────────────────────────────────────────────────────────────────────────


class TestFacadeRouting:
    def test_query_execute_roundtrip(self, layer_with_sqlite) -> None:
        layer, _ = layer_with_sqlite
        layer.route("sqlite_main").execute("CREATE TABLE factors (name TEXT, val REAL)")
        layer.route("sqlite_main").execute("INSERT INTO factors VALUES (?, ?)", ("momentum", 0.42))
        rows = layer.route("sqlite_main").query("SELECT name, val FROM factors")
        assert rows == [("momentum", 0.42)]

    def test_multi_backend_isolation(self) -> None:
        layer = _layer()
        b1 = _SqliteMemoryBackend()
        b2 = _SqliteMemoryBackend()
        layer.register_backend("db_a", b1)
        layer.register_backend("db_b", b2)
        layer.route("db_a").execute("CREATE TABLE t (x INTEGER)")
        layer.route("db_a").execute("INSERT INTO t VALUES (1)")
        assert layer.route("db_a").query("SELECT x FROM t") == [(1,)]
        with pytest.raises(sqlite3.OperationalError):
            layer.route("db_b").query("SELECT x FROM t")  # 互不可见
        b1.close()
        b2.close()

    def test_connection_borrow_return(self, layer_with_sqlite) -> None:
        layer, _ = layer_with_sqlite
        assert layer.borrowed("sqlite_main") == 0
        with layer.connection("sqlite_main") as conn:
            assert layer.borrowed("sqlite_main") == 1
            conn.execute("CREATE TABLE t (x INTEGER)")
        assert layer.borrowed("sqlite_main") == 0

    def test_connection_returned_on_exception(self, layer_with_sqlite) -> None:
        layer, _ = layer_with_sqlite
        with pytest.raises(sqlite3.OperationalError):
            with layer.connection("sqlite_main") as conn:
                conn.execute("SELECT * FROM missing_table")
        assert layer.borrowed("sqlite_main") == 0  # 异常亦归还

    def test_connection_unknown_raises(self) -> None:
        with pytest.raises(DatabaseLayerError):
            with _layer().connection("ghost"):
                pass

    def test_borrowed_unknown_raises(self) -> None:
        with pytest.raises(DatabaseLayerError):
            _layer().borrowed("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# 超时重试（注入时钟/sleeper）
# ──────────────────────────────────────────────────────────────────────────────


class TestRetry:
    def test_retry_recovers_after_transient_failure(self) -> None:
        sleeps: list[float] = []
        layer = _layer(sleeps=sleeps)
        backend = _FlakyBackend(fail_times=2)
        layer.register_backend("flaky", backend)
        rows = layer.query_with_retry("flaky", "SELECT 1", attempts=3, backoff=0.5)
        assert rows == [("ok",)]
        assert backend.calls == 3
        assert sleeps == [0.5, 1.0]  # backoff*attempt 逐次退避

    def test_retry_exhausted_raises(self) -> None:
        layer = _layer()
        backend = _FlakyBackend(fail_times=99)
        layer.register_backend("flaky", backend)
        with pytest.raises(DatabaseLayerError):
            layer.query_with_retry("flaky", "SELECT 1", attempts=3)
        assert backend.calls == 3

    def test_retry_invalid_params_raise(self) -> None:
        layer = _layer()
        layer.register_backend("ok", _FlakyBackend(fail_times=0))
        with pytest.raises(DatabaseLayerError):
            layer.query_with_retry("ok", "SELECT 1", attempts=0)
        with pytest.raises(DatabaseLayerError):
            layer.query_with_retry("ok", "SELECT 1", backoff=-0.1)
        with pytest.raises(DatabaseLayerError):
            layer.query_with_retry("ok", "SELECT 1", timeout=0.0)

    def test_timeout_detected_via_injected_clock(self) -> None:
        clock = _FakeClock()
        layer = _layer(clock=clock)
        backend = _FlakyBackend(fail_times=0, clock=clock, slow=2.0)  # 每次调用耗时 2s
        layer.register_backend("slow", backend)
        with pytest.raises(DatabaseLayerError):
            layer.query_with_retry("slow", "SELECT 1", attempts=2, timeout=1.0)
        assert backend.calls == 2

    def test_within_timeout_succeeds(self) -> None:
        clock = _FakeClock()
        layer = _layer(clock=clock)
        backend = _FlakyBackend(fail_times=0, clock=clock, slow=0.5)
        layer.register_backend("fast", backend)
        rows = layer.query_with_retry("fast", "SELECT 1", attempts=1, timeout=1.0)
        assert rows == [("ok",)]

    def test_execute_with_retry(self) -> None:
        layer = _layer()
        backend = _FlakyBackend(fail_times=1)
        layer.register_backend("w", backend)
        assert layer.execute_with_retry("w", "INSERT", attempts=2) == 1

    def test_no_sleep_by_default(self) -> None:
        layer = _layer()  # 未注入 sleeper → 默认空操作不真睡
        backend = _FlakyBackend(fail_times=1)
        layer.register_backend("f", backend)
        assert layer.query_with_retry("f", "SELECT 1", attempts=2, backoff=99.0) == [("ok",)]


# ──────────────────────────────────────────────────────────────────────────────
# 健康 / 关闭 / 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestHealthCloseDeterminism:
    def test_health_sorted_view(self) -> None:
        layer = _layer()
        b_b = _SqliteMemoryBackend()
        b_a = _SqliteMemoryBackend()
        layer.register_backend("b_db", b_b)
        layer.register_backend("a_db", b_a)
        assert list(layer.health().keys()) == ["a_db", "b_db"]
        assert all(layer.health().values())
        b_a.close()
        b_b.close()

    def test_health_probe_exception_false(self) -> None:
        class _SickBackend(_FlakyBackend):
            def health(self) -> bool:
                raise RuntimeError("probe failed")

        layer = _layer()
        layer.register_backend("sick", _SickBackend(fail_times=0))
        assert layer.health() == {"sick": False}

    def test_close_idempotent_and_close_all(self, layer_with_sqlite) -> None:
        layer, backend = layer_with_sqlite
        layer.close("sqlite_main")
        layer.close("sqlite_main")  # 幂等
        assert layer.health() == {"sqlite_main": False}
        layer.close_all()
        with pytest.raises(DatabaseLayerError):
            layer.close("ghost")

    def test_same_inputs_same_outputs(self) -> None:
        def _run() -> tuple:
            clock = _FakeClock(7.0)
            sleeps: list[float] = []
            layer = DatabaseLayer(clock=clock, sleeper=lambda s: sleeps.append(s))
            backend = _FlakyBackend(fail_times=1)
            layer.register_backend("db", backend)
            rows = layer.query_with_retry("db", "SELECT 1", attempts=2, backoff=0.25)
            return rows, tuple(sleeps), tuple(layer.health().items())

        assert _run() == _run()
