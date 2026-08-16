# [BLUEPRINT] MOD-INF-016 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""JsonStateStore / AppendOnlyDedupSet / RedisStateStore / RedisDedupSet 单元测试
（#ARCH-QUANT-002 状态外部化原语）。

覆盖：JSON 快照三分语义（无记录/正常/损坏）、原子写、append-only 去重集
重启存活、crash 残行容忍、非法输入拦截；Redis 后端接口契约双后端参数化同跑、
fail-fast（不可用即抛 StateStoreError 不静默降级）、错误映射、无 TTL 裁定。

Redis 实测策略（AI-REDIS-001 裁定）：项目已有真实 Redis 基础设施（redis_config
单真源 + 7.0.15@Hyper-V VM），按施工令"有 infra 则真实"——契约测试用真实 Redis
db15（测试专用隔离库，D3 决策 db0/1/2=sim/live/治理 之外），配置缺失或不可达时
pytest.skip 守卫（不硬失败，保证无 Redis 环境下 tests/shared 套件仍绿）。
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from zephyr.shared.state_store import (
    AppendOnlyDedupSet,
    JsonStateStore,
    RedisDedupSet,
    RedisStateStore,
    StateCorruptError,
    StateStoreError,
    make_dedup_set,
    make_state_store,
)


class TestJsonStateStore:
    def test_load_absent_returns_none(self, tmp_path):
        store = JsonStateStore(tmp_path)
        assert store.load("kill_switch") is None

    def test_save_load_roundtrip(self, tmp_path):
        store = JsonStateStore(tmp_path)
        payload = {"active": True, "event_id": "evt-1", "reason": "dd>25%"}
        store.save("kill_switch", payload)
        assert store.load("kill_switch") == payload

    def test_save_overwrites(self, tmp_path):
        store = JsonStateStore(tmp_path)
        store.save("ns", {"v": 1})
        store.save("ns", {"v": 2})
        assert store.load("ns") == {"v": 2}

    def test_load_corrupt_raises(self, tmp_path):
        store = JsonStateStore(tmp_path)
        (tmp_path / "kill_switch.json").write_bytes(b"{not-json!!")
        with pytest.raises(StateCorruptError):
            store.load("kill_switch")

    def test_load_non_dict_raises(self, tmp_path):
        store = JsonStateStore(tmp_path)
        (tmp_path / "ns.json").write_text("[1,2,3]", encoding="utf-8")
        with pytest.raises(StateCorruptError):
            store.load("ns")

    def test_delete(self, tmp_path):
        store = JsonStateStore(tmp_path)
        store.save("ns", {"v": 1})
        assert store.delete("ns") is True
        assert store.load("ns") is None
        assert store.delete("ns") is False

    def test_namespace_path_traversal_rejected(self, tmp_path):
        store = JsonStateStore(tmp_path)
        with pytest.raises(StateStoreError):
            store.save("../evil", {"v": 1})
        with pytest.raises(StateStoreError):
            store.load("a/b")

    def test_unicode_content(self, tmp_path):
        store = JsonStateStore(tmp_path)
        store.save("ns", {"reason": "回撤>25%熔断"})
        assert store.load("ns")["reason"] == "回撤>25%熔断"

    def test_no_tmp_residue_after_save(self, tmp_path):
        store = JsonStateStore(tmp_path)
        store.save("ns", {"v": 1})
        leftovers = [p.name for p in tmp_path.iterdir() if p.name.endswith(".tmp")]
        assert leftovers == []


class TestAppendOnlyDedupSet:
    def test_add_first_true_second_false(self, tmp_path):
        dedup = AppendOnlyDedupSet(tmp_path / "ids.txt")
        assert dedup.add("fill-1") is True
        assert dedup.add("fill-1") is False
        assert len(dedup) == 1

    def test_contains(self, tmp_path):
        dedup = AppendOnlyDedupSet(tmp_path / "ids.txt")
        dedup.add("fill-1")
        assert "fill-1" in dedup
        assert "fill-2" not in dedup

    def test_survives_restart(self, tmp_path):
        path = tmp_path / "ids.txt"
        AppendOnlyDedupSet(path).add("fill-1")
        # 模拟重启：新实例加载同一文件
        dedup2 = AppendOnlyDedupSet(path)
        assert "fill-1" in dedup2
        assert dedup2.add("fill-1") is False

    def test_partial_last_line_tolerated(self, tmp_path):
        """crash 残行（末行无换行）丢弃，该 ID 视为未见过（fail-safe 重判）。"""
        path = tmp_path / "ids.txt"
        path.write_bytes(b"fill-1\nfill-2\nfill-3-partia")
        dedup = AppendOnlyDedupSet(path)
        assert "fill-1" in dedup
        assert "fill-2" in dedup
        assert "fill-3-partia" not in dedup
        # 残行 ID 重新登记后可正常去重
        assert dedup.add("fill-3-partial") is True
        assert dedup.add("fill-3-partial") is False

    def test_blank_lines_ignored(self, tmp_path):
        path = tmp_path / "ids.txt"
        path.write_text("fill-1\n\n  \nfill-2\n", encoding="utf-8")
        dedup = AppendOnlyDedupSet(path)
        assert len(dedup) == 2

    def test_invalid_id_rejected(self, tmp_path):
        dedup = AppendOnlyDedupSet(tmp_path / "ids.txt")
        with pytest.raises(StateStoreError):
            dedup.add("")
        with pytest.raises(StateStoreError):
            dedup.add("has\nnewline")

    def test_persisted_as_lines(self, tmp_path):
        path = tmp_path / "ids.txt"
        dedup = AppendOnlyDedupSet(path)
        dedup.add("a")
        dedup.add("b")
        assert path.read_text(encoding="utf-8") == "a\nb\n"

    def test_unicode_id(self, tmp_path):
        path = tmp_path / "ids.txt"
        dedup = AppendOnlyDedupSet(path)
        dedup.add("成交-600000")
        dedup2 = AppendOnlyDedupSet(path)
        assert "成交-600000" in dedup2


# ────────────────────────────────────────────────────────────────────────────
# Redis 后端（AI-REDIS-001）：真实 Redis db15 实测 + 双后端接口契约参数化同跑
# ────────────────────────────────────────────────────────────────────────────

#: 测试专用 Redis DB 号（D3 决策 db0=sim/db1=live/db2=治理 之外的隔离域，防污染）
_TEST_REDIS_DB: int = 15
_TEST_STATE_PREFIX = "za:test:state"
_TEST_DEDUP_PREFIX = "za:test:dedup"


def _redis_cfg_or_skip() -> dict:
    """加载真实 Redis 配置并探活；配置缺失/不可达 → skip（不硬失败）。"""
    redis = pytest.importorskip("redis")
    from zephyr.infrastructure.redis_config import (
        RedisConfigError,
        load_redis_config,
    )

    try:
        cfg = load_redis_config()
    except RedisConfigError as exc:
        pytest.skip(f"Redis 配置缺失，跳过 Redis 后端实测: {exc}")
    cfg = {
        **cfg,
        "db": _TEST_REDIS_DB,
        "socket_timeout": 2,
        "socket_connect_timeout": 2,
    }
    conn = redis.Redis(**cfg)
    try:
        conn.ping()
    except redis.RedisError as exc:
        pytest.skip(f"Redis 不可达，跳过 Redis 后端实测: {exc}")
    finally:
        conn.close()
    return cfg


@pytest.fixture
def redis_conn():
    """真实 Redis 测试连接（db15 专用），用前后各 flushdb 防串扰。"""
    import redis

    cfg = _redis_cfg_or_skip()
    conn = redis.Redis(**cfg)
    conn.flushdb()
    yield conn
    conn.flushdb()
    conn.close()


class _StoreBackend:
    """状态存取双后端契约句柄：统一 当前实例/重开实例/注入脏数据 三操作。"""

    def __init__(self, reopen, inject_raw):
        self._reopen = reopen
        self.inject_raw = inject_raw
        self.store = reopen()

    def reopen(self):
        """模拟进程重启：同位置新建实例（服务端/磁盘数据保留）。"""
        self.store = self._reopen()
        return self.store


@pytest.fixture(params=["json", "redis"])
def store_backend(request, tmp_path):
    """接口契约参数化：同一套用例跑 JsonStateStore 与 RedisStateStore。"""
    if request.param == "json":
        return _StoreBackend(
            reopen=lambda: JsonStateStore(tmp_path),
            inject_raw=lambda ns, raw: (tmp_path / f"{ns}.json").write_text(
                raw, encoding="utf-8"
            ),
        )
    cfg = _redis_cfg_or_skip()
    import redis

    conn = redis.Redis(**cfg)
    conn.flushdb()
    request.addfinalizer(lambda: (conn.flushdb(), conn.close()))
    return _StoreBackend(
        reopen=lambda: RedisStateStore(conn, key_prefix=_TEST_STATE_PREFIX),
        inject_raw=lambda ns, raw: conn.set(f"{_TEST_STATE_PREFIX}:{ns}", raw),
    )


@pytest.fixture(params=["json", "redis"])
def dedup_backend(request, tmp_path):
    """接口契约参数化：同一套用例跑 AppendOnlyDedupSet 与 RedisDedupSet。"""

    class _DedupBackend:
        def __init__(self, reopen):
            self._reopen = reopen
            self.dedup = reopen()

        def reopen(self):
            self.dedup = self._reopen()
            return self.dedup

    if request.param == "json":
        return _DedupBackend(reopen=lambda: AppendOnlyDedupSet(tmp_path / "ids.txt"))
    cfg = _redis_cfg_or_skip()
    import redis

    conn = redis.Redis(**cfg)
    conn.flushdb()
    request.addfinalizer(lambda: (conn.flushdb(), conn.close()))
    return _DedupBackend(
        reopen=lambda: RedisDedupSet(
            conn, set_name="test_fill_ids", key_prefix=_TEST_DEDUP_PREFIX
        ),
    )


class TestStateStoreContract:
    """接口契约双后端参数化同跑（验收②）：逐方法对齐文件后端语义。"""

    def test_load_absent_returns_none(self, store_backend):
        assert store_backend.store.load("kill_switch") is None

    def test_save_load_roundtrip(self, store_backend):
        payload = {"active": True, "event_id": "evt-1", "reason": "dd>25%"}
        store_backend.store.save("kill_switch", payload)
        assert store_backend.store.load("kill_switch") == payload

    def test_save_overwrites(self, store_backend):
        store_backend.store.save("ns", {"v": 1})
        store_backend.store.save("ns", {"v": 2})
        assert store_backend.store.load("ns") == {"v": 2}

    def test_survives_restart(self, store_backend):
        store_backend.store.save("ns", {"v": 1})
        assert store_backend.reopen().load("ns") == {"v": 1}

    def test_load_corrupt_raises(self, store_backend):
        store_backend.inject_raw("kill_switch", "{not-json!!")
        with pytest.raises(StateCorruptError):
            store_backend.store.load("kill_switch")

    def test_load_non_dict_raises(self, store_backend):
        store_backend.inject_raw("ns", "[1,2,3]")
        with pytest.raises(StateCorruptError):
            store_backend.store.load("ns")

    def test_delete(self, store_backend):
        store_backend.store.save("ns", {"v": 1})
        assert store_backend.store.delete("ns") is True
        assert store_backend.store.load("ns") is None
        assert store_backend.store.delete("ns") is False

    def test_namespace_path_traversal_rejected(self, store_backend):
        with pytest.raises(StateStoreError):
            store_backend.store.save("../evil", {"v": 1})
        with pytest.raises(StateStoreError):
            store_backend.store.load("a/b")

    def test_unicode_content(self, store_backend):
        store_backend.store.save("ns", {"reason": "回撤>25%熔断"})
        assert store_backend.store.load("ns")["reason"] == "回撤>25%熔断"

    def test_save_returns_location(self, store_backend):
        """save 返回落位标识（文件后端=路径 / Redis 后端=键）。"""
        loc = store_backend.store.save("kill_switch", {"v": 1})
        assert "kill_switch" in str(loc)


class TestDedupSetContract:
    """去重集接口契约双后端参数化同跑（验收②）。"""

    def test_add_first_true_second_false(self, dedup_backend):
        assert dedup_backend.dedup.add("fill-1") is True
        assert dedup_backend.dedup.add("fill-1") is False
        assert len(dedup_backend.dedup) == 1

    def test_contains(self, dedup_backend):
        dedup_backend.dedup.add("fill-1")
        assert "fill-1" in dedup_backend.dedup
        assert "fill-2" not in dedup_backend.dedup

    def test_survives_restart(self, dedup_backend):
        dedup_backend.dedup.add("fill-1")
        dedup2 = dedup_backend.reopen()
        assert "fill-1" in dedup2
        assert dedup2.add("fill-1") is False

    def test_invalid_id_rejected(self, dedup_backend):
        with pytest.raises(StateStoreError):
            dedup_backend.dedup.add("")
        with pytest.raises(StateStoreError):
            dedup_backend.dedup.add("has\nnewline")

    def test_unicode_id(self, dedup_backend):
        dedup_backend.dedup.add("成交-600000")
        assert "成交-600000" in dedup_backend.reopen()


class TestRedisFailFast:
    """红队：Redis 不可用 → fail-fast StateStoreError（禁静默降级文件后端）。"""

    def test_constructor_ping_failure_raises(self):
        import redis

        conn = MagicMock()
        conn.ping.side_effect = redis.ConnectionError("boom")
        with pytest.raises(StateStoreError):
            RedisStateStore(conn)
        with pytest.raises(StateStoreError):
            RedisDedupSet(conn, set_name="x")

    def test_dead_port_real_conn_fail_fast(self):
        """真实连接到死端口：构造即抛 StateStoreError（不依赖外部 Redis）。"""
        import redis

        dead = redis.Redis(
            host="127.0.0.1", port=1, socket_connect_timeout=0.5, socket_timeout=0.5
        )
        with pytest.raises(StateStoreError):
            RedisStateStore(dead)

    def test_state_store_operation_failure_mapped(self):
        """运行期 Redis 故障（超时/断连）→ StateStoreError，不裸抛 redis 异常。"""
        import redis

        conn = MagicMock()  # ping 默认成功，构造通过
        store = RedisStateStore(conn)
        conn.get.side_effect = redis.TimeoutError("timeout")
        with pytest.raises(StateStoreError):
            store.load("ns")
        conn.set.side_effect = redis.TimeoutError("timeout")
        with pytest.raises(StateStoreError):
            store.save("ns", {"v": 1})
        conn.delete.side_effect = redis.ConnectionError("down")
        with pytest.raises(StateStoreError):
            store.delete("ns")

    def test_dedup_set_operation_failure_mapped(self):
        import redis

        conn = MagicMock()
        dedup = RedisDedupSet(conn, set_name="x")
        conn.sadd.side_effect = redis.TimeoutError("t")
        with pytest.raises(StateStoreError):
            dedup.add("a")
        conn.sismember.side_effect = redis.ConnectionError("c")
        with pytest.raises(StateStoreError):
            "a" in dedup
        conn.scard.side_effect = redis.RedisError("e")
        with pytest.raises(StateStoreError):
            len(dedup)


class TestRedisSemantics:
    """Redis 后端特有风险面：损坏语义/字节解码/无 TTL/键规约。"""

    def test_bytes_value_decoded(self):
        """decode_responses=False 的连接返回 bytes 也能正确解析（契约健壮性）。"""
        conn = MagicMock()
        conn.get.return_value = b'{"v": 1}'
        store = RedisStateStore(conn)
        assert store.load("ns") == {"v": 1}

    def test_invalid_utf8_bytes_corrupt(self):
        conn = MagicMock()
        conn.get.return_value = b"\xff\xfe\xfd"
        store = RedisStateStore(conn)
        with pytest.raises(StateCorruptError):
            store.load("ns")

    def test_no_ttl_on_state_key(self, redis_conn):
        """状态键无 TTL——kill switch 状态是永久记录（裁定语义实证）。"""
        store = RedisStateStore(redis_conn, key_prefix=_TEST_STATE_PREFIX)
        store.save("kill_switch", {"active": True})
        assert redis_conn.ttl(f"{_TEST_STATE_PREFIX}:kill_switch") == -1

    def test_no_ttl_on_dedup_key(self, redis_conn):
        """去重集键无 TTL——fill_id'见过即永久'，TTL 会破坏幂等保证。"""
        dedup = RedisDedupSet(redis_conn, set_name="fills", key_prefix=_TEST_DEDUP_PREFIX)
        dedup.add("fill-1")
        assert redis_conn.ttl(f"{_TEST_DEDUP_PREFIX}:fills") == -1

    def test_key_convention(self, redis_conn):
        """键规约 {prefix}:{namespace}；set_name 非法（路径分隔符）→ 拦截。"""
        store = RedisStateStore(redis_conn, key_prefix=_TEST_STATE_PREFIX)
        key = store.save("kill_switch", {"v": 1})
        assert key == f"{_TEST_STATE_PREFIX}:kill_switch"
        assert redis_conn.get(key) is not None
        with pytest.raises(StateStoreError):
            RedisDedupSet(redis_conn, set_name="a/b", key_prefix=_TEST_DEDUP_PREFIX)


class TestFactories:
    """消费方切换机制（验收③）：工厂选择后端，默认文件后端。"""

    def test_make_state_store_default_json(self, tmp_path):
        store = make_state_store(root_dir=tmp_path)
        assert isinstance(store, JsonStateStore)

    def test_make_state_store_json(self, tmp_path):
        store = make_state_store("json", root_dir=tmp_path)
        assert isinstance(store, JsonStateStore)

    def test_make_state_store_redis_with_conn(self, redis_conn):
        store = make_state_store(
            "redis", redis_conn=redis_conn, key_prefix=_TEST_STATE_PREFIX
        )
        assert isinstance(store, RedisStateStore)

    def test_make_state_store_redis_requires_conn(self):
        """redis 后端缺 conn → 拦截（建连归接线层：shared→infrastructure 层级纪律）。"""
        with pytest.raises(StateStoreError):
            make_state_store("redis", key_prefix=_TEST_STATE_PREFIX)

    def test_make_dedup_set_default_json(self, tmp_path):
        dedup = make_dedup_set(path=tmp_path / "ids.txt")
        assert isinstance(dedup, AppendOnlyDedupSet)

    def test_make_dedup_set_redis_with_conn(self, redis_conn):
        dedup = make_dedup_set(
            "redis",
            redis_conn=redis_conn,
            set_name="fills",
            key_prefix=_TEST_DEDUP_PREFIX,
        )
        assert isinstance(dedup, RedisDedupSet)

    def test_unknown_backend_rejected(self):
        with pytest.raises(StateStoreError):
            make_state_store("etcd", root_dir="/tmp/x")
        with pytest.raises(StateStoreError):
            make_dedup_set("etcd", path="/tmp/x")

    def test_missing_required_args_rejected(self):
        with pytest.raises(StateStoreError):
            make_state_store("json")  # 缺 root_dir
        with pytest.raises(StateStoreError):
            make_dedup_set("json")  # 缺 path
        with pytest.raises(StateStoreError):
            make_dedup_set("redis", redis_conn=MagicMock())  # 缺 set_name
        with pytest.raises(StateStoreError):
            make_dedup_set("redis", set_name="fills")  # 缺 redis_conn
