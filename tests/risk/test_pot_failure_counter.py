# [BLUEPRINT] MOD-RK-15 | docs/03_modules/_domain_risk/tail_risk_monitor/blueprint.md | §
# [TTL] permanent
"""PotFailureCounter 跨日持久化计数器测试 (MOD-RK-15, AI-POT-001 #107)。

覆盖裁定要点:
    1. 跨日计数: 同日去重 / 跨日累进 / 连续 5 日 → 阈值 0.90→0.85
    2. 计数重置条件: 拟合成功 → 连续计数清零 + 阈值恢复基准
    3. 时区跨日: date_str 由调用方按本地日期生成, 计数器按字符串比较判日界
    4. 持久化: 新实例读旧档 (模拟进程重启跨日)
    5. 损坏降级 fail-closed: 损坏 JSON / 缺键 / 类型异常 / 读异常 → 按从未失败处理
    6. 写失败不阻断主链路
    7. 双后端契约: JsonStateStore(默认) 与满足 load/save 契约的内存后端(模拟 Redis)
    8. Monitor 集成: assess 注入 state_store 后失败/成功自动落账, 降级阈值真实生效
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from zephyr.risk.core.tail_risk_monitor import (
    POT_FAILURE_COUNTER_NAMESPACE,
    POT_FAILURE_DAYS_FOR_ADJUSTMENT,
    POT_THRESHOLD_ADJUSTED,
    PotFailureCounter,
    TailRiskConfig,
    TailRiskMonitor,
)
from zephyr.shared.state_store import JsonStateStore

BASE_THRESHOLD = TailRiskConfig().pot_threshold_quantile  # 0.90
assert BASE_THRESHOLD == 0.90
assert POT_FAILURE_DAYS_FOR_ADJUSTMENT == 5
assert POT_THRESHOLD_ADJUSTED == 0.85

CST = timezone(timedelta(hours=8))  # Asia/Shanghai


class _MemoryStore:
    """满足 JsonStateStore/RedisStateStore 共有 load/save 契约的内存后端。"""

    def __init__(self) -> None:
        self.data: dict[str, dict] = {}
        self.fail_read = False
        self.fail_write = False

    def load(self, namespace: str):
        if self.fail_read:
            raise RuntimeError("simulated backend read failure")
        rec = self.data.get(namespace)
        return dict(rec) if rec is not None else None

    def save(self, namespace: str, payload: dict):
        if self.fail_write:
            raise RuntimeError("simulated backend write failure")
        self.data[namespace] = dict(payload)


@pytest.fixture
def json_store(tmp_path):
    return JsonStateStore(tmp_path / "state")


@pytest.fixture
def mem_store():
    return _MemoryStore()


def _pot_failing_returns() -> np.ndarray:
    """全正收益 → losses<10 → fit_pot 必返回 None (POT 失败)。"""
    rng = np.random.default_rng(7)
    return np.abs(rng.normal(0.01, 0.005, 100)) + 0.001


def _pot_ok_returns() -> np.ndarray:
    """正态收益 500 样本 → POT 拟合成功。"""
    rng = np.random.default_rng(42)
    return rng.normal(0, 0.02, 500)


# ── 1. 跨日计数 ──


class TestCrossDayCounting:
    @pytest.mark.parametrize("store_kind", ["json", "memory"])
    def test_consecutive_days_increment(self, store_kind, json_store, mem_store):
        """跨日边界: 5 个不同日期 → 计数 1..5 逐日累进, 第 5 日触发阈值降级。"""
        store = json_store if store_kind == "json" else mem_store
        counter = PotFailureCounter(store)
        base = datetime(2026, 8, 10)
        for i in range(POT_FAILURE_DAYS_FOR_ADJUSTMENT):
            day = (base + timedelta(days=i)).strftime("%Y-%m-%d")
            assert counter.record_failure(day) == i + 1
        assert counter.get_adjusted_threshold() == POT_THRESHOLD_ADJUSTED

    def test_below_adjustment_days_keeps_base_threshold(self, json_store):
        """4 日连续失败未达 5 日 → 阈值保持基准 0.90。"""
        counter = PotFailureCounter(json_store)
        base = datetime(2026, 8, 10)
        for i in range(POT_FAILURE_DAYS_FOR_ADJUSTMENT - 1):
            day = (base + timedelta(days=i)).strftime("%Y-%m-%d")
            counter.record_failure(day)
        assert counter.get_adjusted_threshold() == BASE_THRESHOLD

    def test_same_day_dedup(self, json_store):
        """同日多次失败不重复计数 (盘中多次 assess)。"""
        counter = PotFailureCounter(json_store)
        assert counter.record_failure("2026-08-10") == 1
        assert counter.record_failure("2026-08-10") == 1
        assert counter.record_failure("2026-08-10") == 1

    def test_success_then_same_day_failure_counts(self, json_store):
        """红队（AI-R2-001 修复实证）：同日先成功后失败必须计数。

        原缺陷：record_success 把 last_failure_date 写为当天，同日随后
        record_failure 被去重分支误吞（当日失败不计入连续失败）。
        修复：成功时清空 last_failure_date。
        """
        counter = PotFailureCounter(json_store)
        counter.record_failure("2026-08-10")
        counter.record_success("2026-08-11")  # 成功重置
        # 同日（08-11）随后失败：必须重新计数（原实现被误吞返回 0）
        assert counter.record_failure("2026-08-11") == 1
        # 同日再失败仍去重（只计当日一次）
        assert counter.record_failure("2026-08-11") == 1

    def test_day_string_comparison_not_arithmetic(self, json_store):
        """非连续日历日也按"不同日期"累进 (计数器不验证日历连续性, 由调用方语义保证)。"""
        counter = PotFailureCounter(json_store)
        assert counter.record_failure("2026-08-10") == 1
        assert counter.record_failure("2026-08-15") == 2  # 跳日仍累进
        assert counter.record_failure("2026-08-15") == 2


# ── 2. 计数重置条件 ──


class TestResetConditions:
    def test_success_resets_counter(self, json_store):
        """失败后成功 → 连续计数清零。"""
        counter = PotFailureCounter(json_store)
        counter.record_failure("2026-08-10")
        counter.record_failure("2026-08-11")
        counter.record_success("2026-08-12")
        assert counter.record_failure("2026-08-13") == 1  # 重新从 1 计

    def test_success_restores_base_threshold(self, json_store):
        """5 日降级后成功 → 阈值恢复 0.90。"""
        counter = PotFailureCounter(json_store)
        base = datetime(2026, 8, 10)
        for i in range(POT_FAILURE_DAYS_FOR_ADJUSTMENT):
            counter.record_failure((base + timedelta(days=i)).strftime("%Y-%m-%d"))
        assert counter.get_adjusted_threshold() == POT_THRESHOLD_ADJUSTED
        counter.record_success("2026-08-15")
        assert counter.get_adjusted_threshold() == BASE_THRESHOLD

    def test_success_noop_when_fresh(self, mem_store):
        """全新状态下 record_success 不产生写 (省一次 IO)。"""
        counter = PotFailureCounter(mem_store)
        counter.record_success("2026-08-10")
        assert POT_FAILURE_COUNTER_NAMESPACE not in mem_store.data


# ── 3. 时区跨日 ──


class TestTimezoneCrossDay:
    def test_cst_midnight_boundary(self, json_store):
        """东八区跨午夜: 23:59 与次日 00:01 仅差 2 分钟, 但属不同日期 → 计 2 日。"""
        monitor = TailRiskMonitor(state_store=json_store)
        d1 = datetime(2026, 8, 16, 23, 59, tzinfo=CST)
        d2 = datetime(2026, 8, 17, 0, 1, tzinfo=CST)
        monitor.assess(_pot_failing_returns(), now=d1)
        monitor.assess(_pot_failing_returns(), now=d2)
        counter = PotFailureCounter(json_store)
        assert counter._load()["consecutive_failures"] == 2

    def test_same_instant_same_local_date_no_double_count(self, json_store):
        """同一交易日内不同时刻 (09:30 开盘 / 15:00 收盘, 东八区) → 同日去重。"""
        monitor = TailRiskMonitor(state_store=json_store)
        open_ = datetime(2026, 8, 17, 9, 30, tzinfo=CST)
        close = datetime(2026, 8, 17, 15, 0, tzinfo=CST)
        monitor.assess(_pot_failing_returns(), now=open_)
        monitor.assess(_pot_failing_returns(), now=close)
        assert PotFailureCounter(json_store)._load()["consecutive_failures"] == 1


# ── 4. 持久化跨实例 (模拟进程重启跨日) ──


class TestPersistenceAcrossInstances:
    def test_new_instance_reads_old_state(self, json_store):
        """T 日进程 A 记录失败, T+1 日新进程实例 (新 counter) 读到旧档继续累进。"""
        PotFailureCounter(json_store).record_failure("2026-08-16")
        counter_t1 = PotFailureCounter(json_store)  # 模拟次日重启
        assert counter_t1.record_failure("2026-08-17") == 2

    def test_state_file_schema(self, json_store, tmp_path):
        """落盘 schema 三键齐全 (跨版本兼容契约)。"""
        PotFailureCounter(json_store).record_failure("2026-08-16")
        path = json_store.root_dir / f"{POT_FAILURE_COUNTER_NAMESPACE}.json"
        rec = json.loads(path.read_text(encoding="utf-8"))
        assert set(rec) == {"consecutive_failures", "last_failure_date", "adjusted_threshold"}
        assert rec["consecutive_failures"] == 1
        assert rec["last_failure_date"] == "2026-08-16"
        assert rec["adjusted_threshold"] == BASE_THRESHOLD


# ── 5. 损坏降级 (fail-closed) ──


class TestCorruptionDegradation:
    def test_corrupt_json_fails_closed(self, json_store):
        """状态文件损坏 → 按从未失败处理 (最保守: 计数归零, 阈值基准)。"""
        path = json_store.root_dir / f"{POT_FAILURE_COUNTER_NAMESPACE}.json"
        path.write_text("{not valid json!!!", encoding="utf-8")
        counter = PotFailureCounter(json_store)
        assert counter.get_adjusted_threshold() == BASE_THRESHOLD
        assert counter.record_failure("2026-08-16") == 1

    def test_missing_keys_merged_with_defaults(self, json_store):
        """缺键记录 → 合并默认值, 不抛异常。"""
        json_store.save(POT_FAILURE_COUNTER_NAMESPACE, {"consecutive_failures": 3})
        counter = PotFailureCounter(json_store)
        assert counter.record_failure("2026-08-16") == 4
        assert counter.get_adjusted_threshold() == BASE_THRESHOLD

    @pytest.mark.parametrize("bad_value", ["abc", None, [1, 2]])
    def test_bad_counter_type_fails_closed(self, json_store, bad_value):
        """consecutive_failures 类型异常 → 归零重计 (fail-closed)。"""
        json_store.save(
            POT_FAILURE_COUNTER_NAMESPACE,
            {
                "consecutive_failures": bad_value,
                "last_failure_date": "2026-08-15",
                "adjusted_threshold": BASE_THRESHOLD,
            },
        )
        counter = PotFailureCounter(json_store)
        assert counter.record_failure("2026-08-16") == 1

    def test_bad_threshold_type_fails_closed(self, json_store):
        """adjusted_threshold 类型异常 → 回落基准阈值。"""
        json_store.save(
            POT_FAILURE_COUNTER_NAMESPACE,
            {
                "consecutive_failures": 6,
                "last_failure_date": "2026-08-15",
                "adjusted_threshold": "not-a-float",
            },
        )
        assert PotFailureCounter(json_store).get_adjusted_threshold() == BASE_THRESHOLD

    def test_read_exception_fails_closed(self, mem_store):
        """后端读异常 (如 Redis 断连) → 按从未失败处理, 不阻断。"""
        mem_store.fail_read = True
        counter = PotFailureCounter(mem_store)
        assert counter.get_adjusted_threshold() == BASE_THRESHOLD
        assert counter.record_failure("2026-08-16") == 1


# ── 6. 写失败不阻断 ──


class TestWriteFailureNonBlocking:
    def test_write_failure_does_not_raise(self, mem_store):
        """写失败仅 warning, record_failure 正常返回计数 (主链路不阻断)。"""
        mem_store.fail_write = True
        counter = PotFailureCounter(mem_store)
        assert counter.record_failure("2026-08-16") == 1  # 不抛异常

    def test_write_failure_logs_warning(self, mem_store, caplog):
        import logging

        mem_store.fail_write = True
        counter = PotFailureCounter(mem_store)
        with caplog.at_level(logging.WARNING):
            counter.record_failure("2026-08-16")
        assert any("写失败" in r.message for r in caplog.records)


# ── 7. 双后端契约等价 ──


class TestDualBackendContract:
    @pytest.mark.parametrize("store_kind", ["json", "memory"])
    def test_full_lifecycle_both_backends(self, store_kind, json_store, mem_store):
        """同一生命周期在两种后端行为一致: 失败累进→降级→成功重置→恢复。"""
        store = json_store if store_kind == "json" else mem_store
        counter = PotFailureCounter(store)
        base = datetime(2026, 8, 10)
        for i in range(POT_FAILURE_DAYS_FOR_ADJUSTMENT):
            counter.record_failure((base + timedelta(days=i)).strftime("%Y-%m-%d"))
        assert counter.get_adjusted_threshold() == POT_THRESHOLD_ADJUSTED
        counter.record_success("2026-08-15")
        assert counter.get_adjusted_threshold() == BASE_THRESHOLD
        assert counter._load()["consecutive_failures"] == 0


# ── 8. Monitor 集成 ──


class TestMonitorIntegration:
    def test_assess_records_failure_when_pot_fails(self, json_store):
        """POT 拟合失败 (全正收益) → assess 自动落账 1 日失败。"""
        monitor = TailRiskMonitor(state_store=json_store)
        snap = monitor.assess(_pot_failing_returns(), now=datetime(2026, 8, 16, 15, 0, tzinfo=CST))
        assert snap.pot_fallback_historical is True
        assert PotFailureCounter(json_store)._load()["consecutive_failures"] == 1

    def test_assess_records_success_when_pot_ok(self, json_store):
        """POT 拟合成功 → 连续计数清零。"""
        counter = PotFailureCounter(json_store)
        counter.record_failure("2026-08-15")
        monitor = TailRiskMonitor(state_store=json_store)
        snap = monitor.assess(_pot_ok_returns(), now=datetime(2026, 8, 16, 15, 0, tzinfo=CST))
        assert snap.pot_fallback_historical is False
        assert PotFailureCounter(json_store)._load()["consecutive_failures"] == 0

    def test_adjusted_threshold_feeds_fit_pot(self, json_store):
        """5 日失败后, assess 传入 fit_pot 的阈值分位数为 0.85 (降级真实生效)。"""
        counter = PotFailureCounter(json_store)
        base = datetime(2026, 8, 10)
        for i in range(POT_FAILURE_DAYS_FOR_ADJUSTMENT):
            counter.record_failure((base + timedelta(days=i)).strftime("%Y-%m-%d"))
        monitor = TailRiskMonitor(state_store=json_store)
        captured: list[float] = []
        original_fit_pot = monitor.fit_pot

        def spy_fit_pot(returns, threshold_quantile=None):
            captured.append(threshold_quantile)
            return original_fit_pot(returns, threshold_quantile)

        monitor.fit_pot = spy_fit_pot  # type: ignore[method-assign]
        monitor.assess(_pot_ok_returns(), now=datetime(2026, 8, 16, 15, 0, tzinfo=CST))
        assert captured == [POT_THRESHOLD_ADJUSTED]

    def test_no_state_store_no_counter(self):
        """未注入 state_store → 计数器缺省, assess 正常 (向后兼容)。"""
        monitor = TailRiskMonitor()
        assert monitor._pot_counter is None
        snap = monitor.assess(_pot_failing_returns(), now=datetime(2026, 8, 16, 15, 0, tzinfo=CST))
        assert snap.pot_fallback_historical is True


# ── 9. 真 Redis 后端实测 (db15 隔离库, 配置缺失/不可达自动 skip) ──

#: 测试专用 Redis DB（对齐 test_state_store_redis.py 裁定: db0/1/2=sim/live/治理 之外的隔离域）
_TEST_REDIS_DB: int = 15
_TEST_STATE_PREFIX = "za:test:pot_counter"


def _redis_cfg_or_skip() -> dict:
    """加载真实 Redis 配置并探活；缺失/不可达 → skip（不硬失败, 对齐项目既有裁定）。"""
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
def redis_store():
    """真实 RedisStateStore（db15 + 专用前缀），用前后各 flushdb 防串扰。"""
    import redis

    from zephyr.shared.state_store_redis import RedisStateStore

    cfg = _redis_cfg_or_skip()
    conn = redis.Redis(**cfg)
    conn.flushdb()
    yield RedisStateStore(conn, key_prefix=_TEST_STATE_PREFIX)
    conn.flushdb()
    conn.close()


class TestRealRedisBackend:
    """真 Redis 实测（AI-REDIS-001 裁定"有 infra 则真实"：项目已有 7.0.15@Hyper-V VM）。

    补 contract-equivalence 内存替身无法覆盖的部分: 真实 wire 序列化往返、
    服务端持久化跨实例、脏字节注入损坏语义。
    """

    def test_full_lifecycle_real_redis(self, redis_store):
        """5 日失败降级 → 成功重置, 全生命周期在真 Redis 上与 Json 后端行为一致。"""
        counter = PotFailureCounter(redis_store)
        base = datetime(2026, 8, 10)
        for i in range(POT_FAILURE_DAYS_FOR_ADJUSTMENT):
            day = (base + timedelta(days=i)).strftime("%Y-%m-%d")
            assert counter.record_failure(day) == i + 1
        assert counter.get_adjusted_threshold() == POT_THRESHOLD_ADJUSTED
        counter.record_success("2026-08-15")
        assert counter.get_adjusted_threshold() == BASE_THRESHOLD
        assert redis_store.load(POT_FAILURE_COUNTER_NAMESPACE)["consecutive_failures"] == 0

    def test_cross_instance_persistence_real_redis(self, redis_store):
        """T 日实例 A 记录, T+1 日新实例读旧档续计 (服务端数据保留, 模拟进程重启跨日)。"""
        PotFailureCounter(redis_store).record_failure("2026-08-16")
        counter_t1 = PotFailureCounter(redis_store)
        assert counter_t1.record_failure("2026-08-17") == 2

    def test_corrupt_value_fails_closed_real_redis(self, redis_store):
        """绕过 store 直注脏字节 → load 抛 StateCorruptError → 计数器按从未失败处理。"""
        key = f"{_TEST_STATE_PREFIX}:{POT_FAILURE_COUNTER_NAMESPACE}"
        redis_store._conn.set(key, "{corrupted json!!!")
        counter = PotFailureCounter(redis_store)
        assert counter.get_adjusted_threshold() == BASE_THRESHOLD
        assert counter.record_failure("2026-08-16") == 1

    def test_threshold_float_roundtrip_real_redis(self, redis_store):
        """float 阈值经 SET/GET + JSON 往返精度无损 (0.85 精确回读为 float)。"""
        counter = PotFailureCounter(redis_store)
        base = datetime(2026, 8, 10)
        for i in range(POT_FAILURE_DAYS_FOR_ADJUSTMENT):
            counter.record_failure((base + timedelta(days=i)).strftime("%Y-%m-%d"))
        raw = redis_store.load(POT_FAILURE_COUNTER_NAMESPACE)
        assert isinstance(raw["adjusted_threshold"], float)
        assert raw["adjusted_threshold"] == POT_THRESHOLD_ADJUSTED


# ── 10. _load 非 dict 穿透守卫 (AI-R2-001) ──


class TestLoadNonDictGuard:
    """store 返回合法 JSON 的非 dict 类型 → 按从未失败处理 (fail-closed, 不炸 assess 主链路)。

    原缺陷：_load 只判 rec is None，list/str/int/float 穿透到缺键合并循环
    (`k not in rec` / `rec[k] = v`) 抛 TypeError。
    """

    class _RawStore:
        """原样返回预置 payload 的 stub。

        （_MemoryStore.load 对返回值做 dict() 拷贝，无法注入非 dict 类型；
        JsonStateStore 直写非 dict JSON 顶层值即可，但用 stub 更直白。）
        """

        def __init__(self, payload) -> None:
            self._payload = payload

        def load(self, namespace: str):
            return self._payload

        def save(self, namespace: str, payload: dict):
            pass

    def test_load_list_returns_default(self):
        """store 返回 [1,2,3] → 默认 fresh 状态，record_failure 从 1 计。"""
        counter = PotFailureCounter(self._RawStore([1, 2, 3]))
        assert counter.get_adjusted_threshold() == BASE_THRESHOLD
        assert counter.record_failure("2026-08-16") == 1

    def test_load_string_returns_default(self):
        """store 返回 "corrupt" → 默认 fresh 状态。"""
        counter = PotFailureCounter(self._RawStore("corrupt"))
        assert counter.get_adjusted_threshold() == BASE_THRESHOLD
        assert counter.record_failure("2026-08-16") == 1

    def test_load_int_returns_default(self):
        """store 返回 42 → 默认 fresh 状态。"""
        counter = PotFailureCounter(self._RawStore(42))
        assert counter.get_adjusted_threshold() == BASE_THRESHOLD
        assert counter.record_failure("2026-08-16") == 1

    def test_load_float_returns_default(self):
        """store 返回 0.85 → 默认 fresh 状态。"""
        counter = PotFailureCounter(self._RawStore(0.85))
        assert counter.get_adjusted_threshold() == BASE_THRESHOLD
        assert counter.record_failure("2026-08-16") == 1
