"""provider_base 单测（MOD-L00-004 阶段1）。

测试内容：
- FetchPayload / FetchResult / DataSourceMeta 数据类
- DataSourceBase._call_with_policy（限流+重试）
- DataSourceBase._rate_limit_sleep
- DataSourceBase._calc_backoff
- 上下文管理（with 语法）

不依赖真实 SDK，用 mock 子类和 mock 函数。
"""
import time
import datetime
import pytest

from src.zephyr.data.provider_base import (
    DataSourceBase,
    DataSourceMeta,
    FetchPayload,
    FetchResult,
)
from src.zephyr.data.policy_registry import SourcePolicy


# ============== 测试用 mock 子类 ==============

class _MockProvider(DataSourceBase):
    """最小可实例化的 DataSourceBase 子类（实现所有抽象方法）。"""
    source_name = "mock"
    meta = DataSourceMeta(
        name="mock", display_name="Mock", auth_type="anonymous",
        requires_process=False, thread_safety="shared", rate_limit_default=0,
    )

    def connect(self):
        self._connected = True

    def health_check(self):
        return self._connected

    def fetch(self, payload, policy):
        yield FetchResult(
            table=payload.table, columns=["a"], rows=[(1,)],
            last_key="x", elapsed_sec=0.0,
        )

    def disconnect(self):
        self._connected = False


# ============== 数据类测试 ==============

class TestFetchPayload:
    def test_construction(self):
        p = FetchPayload(
            table="c1_market.kline_daily",
            symbols=["000001.SZ"],
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 12, 31),
        )
        assert p.table == "c1_market.kline_daily"
        assert p.symbols == ["000001.SZ"]
        assert p.incremental is True
        assert p.extra is None

    def test_full_market(self):
        p = FetchPayload(
            table="t", symbols=None,
            start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 2),
        )
        assert p.symbols is None


class TestFetchResult:
    def test_rows_fetched_autofill(self):
        r = FetchResult(
            table="t", columns=["a"], rows=[(1,), (2,), (3,)],
            last_key="k", elapsed_sec=1.0,
        )
        assert r.rows_fetched == 3

    def test_rows_fetched_explicit(self):
        r = FetchResult(
            table="t", columns=["a"], rows=[(1,)],
            last_key="k", elapsed_sec=1.0, rows_fetched=100,
        )
        assert r.rows_fetched == 100

    def test_error_default_none(self):
        r = FetchResult(table="t", columns=[], rows=[], last_key="", elapsed_sec=0.0)
        assert r.error is None


class TestDataSourceMeta:
    def test_defaults(self):
        m = DataSourceMeta(
            name="x", display_name="X", auth_type="anonymous",
            requires_process=False, thread_safety="shared", rate_limit_default=0,
        )
        assert m.capabilities == []
        assert m.known_issues == []


# ============== _call_with_policy 测试 ==============

class TestCallWithPolicy:
    def test_success_no_retry(self):
        """成功调用不重试。"""
        p = _MockProvider()
        policy = SourcePolicy(max_retries=3, retry_on=["ValueError"])
        calls = []

        def fn():
            calls.append(1)
            return "ok"

        result = p._call_with_policy(fn, policy)
        assert result == "ok"
        assert len(calls) == 1

    def test_retry_then_success(self):
        """失败后重试成功。"""
        p = _MockProvider()
        policy = SourcePolicy(
            max_retries=3, retry_on=["ValueError"],
            backoff="fixed", initial_wait_sec=0.01,
        )
        calls = []

        def fn():
            calls.append(1)
            if len(calls) < 3:
                raise ValueError("transient")
            return "ok"

        result = p._call_with_policy(fn, policy)
        assert result == "ok"
        assert len(calls) == 3

    def test_retry_exhausted(self):
        """重试耗尽抛异常。"""
        p = _MockProvider()
        policy = SourcePolicy(
            max_retries=2, retry_on=["ValueError"],
            backoff="fixed", initial_wait_sec=0.01,
        )

        def fn():
            raise ValueError("permanent")

        with pytest.raises(ValueError, match="permanent"):
            p._call_with_policy(fn, policy)

    def test_no_retry_on_unmatched_error(self):
        """错误不在 retry_on 列表则不重试。"""
        p = _MockProvider()
        policy = SourcePolicy(max_retries=5, retry_on=["ValueError"])
        calls = []

        def fn():
            calls.append(1)
            raise KeyError("not in retry_on")

        with pytest.raises(KeyError):
            p._call_with_policy(fn, policy)
        assert len(calls) == 1

    def test_retry_on_error_message(self):
        """retry_on 匹配错误消息子串。"""
        p = _MockProvider()
        policy = SourcePolicy(
            max_retries=2, retry_on=["-4318"],
            backoff="fixed", initial_wait_sec=0.01,
        )
        calls = []

        def fn():
            calls.append(1)
            if len(calls) == 1:
                raise RuntimeError("quota error -4318 exceeded")
            return "ok"

        result = p._call_with_policy(fn, policy)
        assert result == "ok"
        assert len(calls) == 2

    def test_none_policy(self):
        """policy=None 时不重试不限流。"""
        p = _MockProvider()

        def fn():
            return "ok"

        result = p._call_with_policy(fn, None)
        assert result == "ok"


# ============== _rate_limit_sleep 测试 ==============

class TestRateLimitSleep:
    def test_no_sleep_when_rpm_zero(self):
        """rpm=0 不限流。"""
        p = _MockProvider()
        policy = SourcePolicy(rpm=0)
        t0 = time.time()
        p._rate_limit_sleep(policy)
        p._rate_limit_sleep(policy)
        assert time.time() - t0 < 0.1

    def test_sleep_enforces_interval(self):
        """rpm=600 → 间隔 0.1s，连续调用应 sleep。"""
        p = _MockProvider()
        policy = SourcePolicy(rpm=600)  # 60/600=0.1s 间隔
        p._rate_limit_sleep(policy)  # 第一次不 sleep
        t0 = time.time()
        p._rate_limit_sleep(policy)  # 第二次应 sleep ~0.1s
        elapsed = time.time() - t0
        assert elapsed >= 0.08  # 允许少量误差


# ============== _calc_backoff 测试 ==============

class TestCalcBackoff:
    def test_fixed(self):
        assert DataSourceBase._calc_backoff("fixed", 2.0, 0) == 2.0
        assert DataSourceBase._calc_backoff("fixed", 2.0, 3) == 2.0

    def test_exponential(self):
        assert DataSourceBase._calc_backoff("exponential", 1.0, 0) == 1.0
        assert DataSourceBase._calc_backoff("exponential", 1.0, 1) == 2.0
        assert DataSourceBase._calc_backoff("exponential", 1.0, 2) == 4.0
        assert DataSourceBase._calc_backoff("exponential", 1.0, 3) == 8.0

    def test_jittered(self):
        """jittered = exponential ± 0.5。"""
        for attempt in range(5):
            val = DataSourceBase._calc_backoff("jittered", 1.0, attempt)
            base = 1.0 * (2 ** attempt)
            assert base - 0.5 <= val <= base + 0.5

    def test_unknown_mode_defaults_fixed(self):
        assert DataSourceBase._calc_backoff("unknown", 3.0, 2) == 3.0


# ============== 上下文管理测试 ==============

class TestContextManager:
    def test_with_connects_and_disconnects(self):
        p = _MockProvider()
        assert not p.is_connected
        with p:
            assert p.is_connected
        assert not p.is_connected

    def test_repr(self):
        p = _MockProvider()
        assert "MockProvider" in repr(p)
        assert "source=mock" in repr(p)


# ============== fetch 迭代器测试 ==============

class TestFetchIterator:
    def test_mock_fetch_yields_result(self):
        p = _MockProvider()
        payload = FetchPayload(
            table="t", symbols=["x"],
            start=datetime.date(2024, 1, 1), end=datetime.date(2024, 1, 2),
        )
        results = list(p.fetch(payload, SourcePolicy()))
        assert len(results) == 1
        assert results[0].rows == [(1,)]
        assert results[0].last_key == "x"
