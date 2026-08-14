# [BLUEPRINT] MOD-XS-014 | docs/03_modules/_domain_ex_sor/api_rate_limiter/blueprint.md | §
# [TTL] permanent
"""ApiRateLimiter 单元测试 (MOD-XS-014)。四级限流架构 L1~L4。"""

from __future__ import annotations

import time
from datetime import datetime, timezone

import pytest

from zephyr.ex_sor.api.api_rate_limiter import (
    ApiRateLimiter,
    InvalidRateLimitConfigError,
    RateLimitConfig,
    RateLimitDecision,
    RateLimitLevel,
    RequestPriority,
    SlidingWindowCounter,
    TokenBucket,
    TradingSession,
)

NOW = datetime(2026, 8, 4, 10, 0, tzinfo=timezone.utc)


# ── TokenBucket ───────────────────────────────────────────────────────────────


def test_token_bucket_initial_full():
    bucket = TokenBucket(capacity=10, refill_rate=5.0)
    assert bucket.capacity == pytest.approx(10.0)
    assert bucket.tokens == pytest.approx(10.0)


def test_token_bucket_consume_success():
    bucket = TokenBucket(capacity=10, refill_rate=5.0)
    assert bucket.try_consume(3) is True
    assert bucket.tokens == pytest.approx(7.0)


def test_token_bucket_consume_until_empty():
    bucket = TokenBucket(capacity=3, refill_rate=1.0)
    assert bucket.try_consume(1) is True
    assert bucket.try_consume(1) is True
    assert bucket.try_consume(1) is True
    assert bucket.try_consume(1) is False  # 桶空


def test_token_bucket_refill_over_time():
    bucket = TokenBucket(capacity=10, refill_rate=10.0)
    bucket.try_consume(10)  # 清空
    assert bucket.tokens == pytest.approx(0.0, abs=0.01)
    time.sleep(0.15)  # 0.15s * 10/s ≈ 1.5 tokens
    assert bucket.tokens == pytest.approx(1.5, abs=0.5)


def test_token_bucket_refill_capped_at_capacity():
    bucket = TokenBucket(capacity=5, refill_rate=100.0)
    bucket.try_consume(3)
    time.sleep(0.05)  # 应补满但不超过 capacity
    assert bucket.tokens <= 5.0 + 1e-9


def test_token_bucket_time_until_available():
    bucket = TokenBucket(capacity=2, refill_rate=2.0)
    bucket.try_consume(2)  # 清空
    # 需要 1 token, 速率 2/s → 0.5s
    wait = bucket.time_until_available(1)
    assert wait == pytest.approx(0.5, abs=0.1)


def test_token_bucket_time_until_available_already_enough():
    bucket = TokenBucket(capacity=10, refill_rate=1.0)
    assert bucket.time_until_available(5) == pytest.approx(0.0)


def test_token_bucket_invalid_capacity():
    with pytest.raises(InvalidRateLimitConfigError):
        TokenBucket(capacity=0, refill_rate=1.0)


def test_token_bucket_invalid_refill_rate():
    with pytest.raises(InvalidRateLimitConfigError):
        TokenBucket(capacity=10, refill_rate=0)


def test_token_bucket_invalid_consume_tokens():
    bucket = TokenBucket(capacity=10, refill_rate=1.0)
    with pytest.raises(InvalidRateLimitConfigError):
        bucket.try_consume(0)
    with pytest.raises(InvalidRateLimitConfigError):
        bucket.try_consume(-1)


# ── SlidingWindowCounter ──────────────────────────────────────────────────────


def test_sliding_window_initial_empty():
    counter = SlidingWindowCounter(limit=5, window_seconds=1.0)
    assert counter.current_count == 0
    assert counter.limit == 5
    assert counter.window_seconds == pytest.approx(1.0)


def test_sliding_window_acquire_until_limit():
    counter = SlidingWindowCounter(limit=3, window_seconds=1.0)
    assert counter.try_acquire() is True
    assert counter.try_acquire() is True
    assert counter.try_acquire() is True
    assert counter.try_acquire() is False  # 达到上限
    assert counter.current_count == 3


def test_sliding_window_eviction_after_window():
    counter = SlidingWindowCounter(limit=2, window_seconds=0.1)
    assert counter.try_acquire() is True
    assert counter.try_acquire() is True
    assert counter.try_acquire() is False
    time.sleep(0.15)  # 窗口过期
    assert counter.try_acquire() is True  # 旧请求已驱逐
    assert counter.current_count == 1


def test_sliding_window_invalid_limit():
    with pytest.raises(InvalidRateLimitConfigError):
        SlidingWindowCounter(limit=0, window_seconds=1.0)


def test_sliding_window_invalid_window():
    with pytest.raises(InvalidRateLimitConfigError):
        SlidingWindowCounter(limit=5, window_seconds=0)


# ── RateLimitConfig ───────────────────────────────────────────────────────────


def test_config_defaults():
    cfg = RateLimitConfig()
    assert cfg.l1_global_qps == 50
    assert cfg.l2_system_tps == 10
    assert cfg.l3_pre_open_tps == 15
    assert cfg.l3_auction_tps == 5
    assert cfg.l3_intraday_tps == 8
    assert cfg.l3_post_close_tps == 15
    assert cfg.l3_off_hours_block is True


def test_config_invalid_l1():
    with pytest.raises(InvalidRateLimitConfigError):
        RateLimitConfig(l1_global_qps=0)


def test_config_invalid_l2():
    with pytest.raises(InvalidRateLimitConfigError):
        RateLimitConfig(l2_system_tps=-1)


def test_config_invalid_l3_intraday():
    with pytest.raises(InvalidRateLimitConfigError):
        RateLimitConfig(l3_intraday_tps=0)


def test_config_frozen():
    cfg = RateLimitConfig()
    with pytest.raises(Exception):
        cfg.l1_global_qps = 100  # type: ignore[misc]


# ── ApiRateLimiter: 基本放行 ──────────────────────────────────────────────────


def test_limiter_basic_allow():
    limiter = ApiRateLimiter()
    decision = limiter.check(
        system="miniQMT",
        session=TradingSession.INTRADAY,
        priority=RequestPriority.P0_TRADING,
        now=NOW,
    )
    assert decision.allowed is True
    assert decision.blocked_level is None
    assert decision.retry_after_seconds == pytest.approx(0.0)


def test_limiter_decision_to_dict():
    limiter = ApiRateLimiter()
    decision = limiter.check(
        system="miniQMT",
        session=TradingSession.INTRADAY,
        priority=RequestPriority.P0_TRADING,
        now=NOW,
    )
    d = decision.to_dict()
    assert d["allowed"] is True
    assert d["blocked_level"] is None
    assert d["timestamp"] == NOW.isoformat()


# ── L3: 非交易时段阻断 ────────────────────────────────────────────────────────


def test_l3_off_hours_blocks_non_p0():
    limiter = ApiRateLimiter()
    decision = limiter.check(
        system="miniQMT",
        session=TradingSession.OFF_HOURS,
        priority=RequestPriority.P2_MARKET_DATA,
        now=NOW,
    )
    assert decision.allowed is False
    assert decision.blocked_level == RateLimitLevel.L3_OPERATION
    assert decision.retry_after_seconds == float("inf")


def test_l3_off_hours_p0_bypasses():
    """P0 交易请求在非交易时段仍可放行。"""
    limiter = ApiRateLimiter()
    decision = limiter.check(
        system="miniQMT",
        session=TradingSession.OFF_HOURS,
        priority=RequestPriority.P0_TRADING,
        now=NOW,
    )
    assert decision.allowed is True


def test_l3_off_hours_block_disabled():
    """关闭非交易时段阻断后, 非 P0 也可放行 (但仍受 L1/L2 限制)。"""
    cfg = RateLimitConfig(l3_off_hours_block=False)
    limiter = ApiRateLimiter(cfg)
    decision = limiter.check(
        system="miniQMT",
        session=TradingSession.OFF_HOURS,
        priority=RequestPriority.P2_MARKET_DATA,
        now=NOW,
    )
    assert decision.allowed is True


# ── L1: 全局限流 ──────────────────────────────────────────────────────────────


def test_l1_global_limit_blocks():
    """L1 全局 QPS=2, 第 3 个请求被阻断。"""
    cfg = RateLimitConfig(l1_global_qps=2, l2_system_tps=100, l3_intraday_tps=100)
    limiter = ApiRateLimiter(cfg)
    d1 = limiter.check("sys", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW)
    d2 = limiter.check("sys", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW)
    d3 = limiter.check("sys", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW)
    assert d1.allowed and d2.allowed
    assert d3.allowed is False
    assert d3.blocked_level == RateLimitLevel.L1_GLOBAL
    assert d3.retry_after_seconds == pytest.approx(1.0)


# ── L2: 系统级令牌桶 ──────────────────────────────────────────────────────────


def test_l2_system_isolation():
    """不同系统的令牌桶相互独立。"""
    cfg = RateLimitConfig(l1_global_qps=100, l2_system_tps=2, l3_intraday_tps=100)
    limiter = ApiRateLimiter(cfg)
    # miniQMT 用完 2 个
    assert limiter.check("miniQMT", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW).allowed
    assert limiter.check("miniQMT", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW).allowed
    d_mq = limiter.check("miniQMT", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW)
    assert d_mq.allowed is False
    assert d_mq.blocked_level == RateLimitLevel.L2_SYSTEM
    # tushare 仍有令牌
    d_ts = limiter.check("tushare", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW)
    assert d_ts.allowed is True


def test_l2_blocked_reason_contains_system_name():
    cfg = RateLimitConfig(l1_global_qps=100, l2_system_tps=1, l3_intraday_tps=100)
    limiter = ApiRateLimiter(cfg)
    limiter.check("miniQMT", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW)
    d = limiter.check("miniQMT", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW)
    assert d.allowed is False
    assert "miniQMT" in d.reason


# ── L3: 操作级分时段限流 ──────────────────────────────────────────────────────


def test_l3_session_limit_blocks_non_p0():
    """L3 盘中 TPS=2, 第 3 个非 P0 请求被阻断。"""
    cfg = RateLimitConfig(l1_global_qps=100, l2_system_tps=100, l3_intraday_tps=2)
    limiter = ApiRateLimiter(cfg)
    assert limiter.check("s", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW).allowed
    assert limiter.check("s", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW).allowed
    d = limiter.check("s", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW)
    assert d.allowed is False
    assert d.blocked_level == RateLimitLevel.L3_OPERATION
    assert "intraday" in d.reason


def test_l3_p0_trading_skips_session_limit():
    """P0 交易不受 L3 时段限流。"""
    cfg = RateLimitConfig(l1_global_qps=100, l2_system_tps=100, l3_intraday_tps=1)
    limiter = ApiRateLimiter(cfg)
    # P0 连续 5 个都放行 (跳过 L3)
    for _ in range(5):
        d = limiter.check("s", TradingSession.INTRADAY, RequestPriority.P0_TRADING, now=NOW)
        assert d.allowed is True


def test_l3_auction_more_restrictive_than_intraday():
    """集合竞价 TPS(5) < 盘中 TPS(8) 默认配置。"""
    cfg = RateLimitConfig()
    limiter = ApiRateLimiter(cfg)
    assert cfg.l3_auction_tps < cfg.l3_intraday_tps


# ── L4: 优先级语义 ────────────────────────────────────────────────────────────


def test_l4_priority_ordering():
    """优先级枚举值: P0 < P1 < P2 < P3 < P4。"""
    assert RequestPriority.P0_TRADING < RequestPriority.P1_RISK
    assert RequestPriority.P1_RISK < RequestPriority.P2_MARKET_DATA
    assert RequestPriority.P2_MARKET_DATA < RequestPriority.P3_FACTOR
    assert RequestPriority.P3_FACTOR < RequestPriority.P4_NOTIFICATION


def test_l4_p0_off_hours_bypass():
    """P0 在非交易时段放行, P4 在非交易时段阻断。"""
    limiter = ApiRateLimiter()
    d_p0 = limiter.check("s", TradingSession.OFF_HOURS, RequestPriority.P0_TRADING, now=NOW)
    d_p4 = limiter.check("s", TradingSession.OFF_HOURS, RequestPriority.P4_NOTIFICATION, now=NOW)
    assert d_p0.allowed is True
    assert d_p4.allowed is False


# ── 诊断 API ──────────────────────────────────────────────────────────────────


def test_get_l1_count():
    cfg = RateLimitConfig(l1_global_qps=100, l2_system_tps=100, l3_intraday_tps=100)
    limiter = ApiRateLimiter(cfg)
    assert limiter.get_l1_count() == 0
    limiter.check("s", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW)
    limiter.check("s", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW)
    assert limiter.get_l1_count() == 2


def test_get_l2_tokens():
    limiter = ApiRateLimiter()
    initial = limiter.get_l2_tokens("miniQMT")
    assert initial == pytest.approx(float(RateLimitConfig().l2_system_tps))
    limiter.check("miniQMT", TradingSession.INTRADAY, RequestPriority.P0_TRADING, now=NOW)
    after = limiter.get_l2_tokens("miniQMT")
    assert after < initial


def test_get_l2_tokens_unknown_system():
    """未使用的系统返回满桶令牌数。"""
    limiter = ApiRateLimiter()
    tokens = limiter.get_l2_tokens("unknown_system")
    assert tokens == pytest.approx(float(RateLimitConfig().l2_system_tps))


def test_get_l3_tokens():
    limiter = ApiRateLimiter()
    tokens = limiter.get_l3_tokens(TradingSession.INTRADAY)
    assert tokens == pytest.approx(float(RateLimitConfig().l3_intraday_tps))


def test_get_l3_tokens_off_hours_returns_zero():
    """OFF_HOURS 无令牌桶 (设计如此, 通过阻断逻辑处理)。"""
    limiter = ApiRateLimiter()
    assert limiter.get_l3_tokens(TradingSession.OFF_HOURS) == pytest.approx(0.0)


# ── 集成: 四级联合 ────────────────────────────────────────────────────────────


def test_integration_four_levels_all_pass():
    """四级全通过 → 放行。"""
    limiter = ApiRateLimiter()
    d = limiter.check("miniQMT", TradingSession.INTRADAY, RequestPriority.P0_TRADING, now=NOW)
    assert d.allowed is True
    assert d.reason == "OK"


def test_integration_l1_blocks_before_l2():
    """L1 满时, 即使 L2 有令牌也阻断。"""
    cfg = RateLimitConfig(l1_global_qps=1, l2_system_tps=100, l3_intraday_tps=100)
    limiter = ApiRateLimiter(cfg)
    limiter.check("s", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW)
    d = limiter.check("s", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW)
    assert d.allowed is False
    assert d.blocked_level == RateLimitLevel.L1_GLOBAL


def test_integration_l2_blocks_before_l3():
    """L2 满时, L3 不被检查。"""
    cfg = RateLimitConfig(l1_global_qps=100, l2_system_tps=1, l3_intraday_tps=100)
    limiter = ApiRateLimiter(cfg)
    limiter.check("s", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW)
    d = limiter.check("s", TradingSession.INTRADAY, RequestPriority.P1_RISK, now=NOW)
    assert d.allowed is False
    assert d.blocked_level == RateLimitLevel.L2_SYSTEM


def test_config_property_accessible():
    limiter = ApiRateLimiter()
    assert limiter.config.l1_global_qps == 50


def test_all_trading_sessions_have_l3_buckets():
    """除 OFF_HOURS 外, 各时段都有令牌桶。"""
    limiter = ApiRateLimiter()
    for session in (
        TradingSession.PRE_OPEN,
        TradingSession.AUCTION,
        TradingSession.INTRADAY,
        TradingSession.POST_CLOSE,
    ):
        assert session in limiter._l3_buckets
    assert TradingSession.OFF_HOURS not in limiter._l3_buckets
