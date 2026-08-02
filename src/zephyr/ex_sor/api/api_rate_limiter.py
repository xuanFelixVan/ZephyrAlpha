# [BLUEPRINT] MOD-XS-014 | docs/03_modules/_domain_ex_sor/api_rate_limiter/blueprint.md
# [MODULE] zephyr.ex_sor.api.api_rate_limiter
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] zephyr.shared.foundation.errors; time; collections.deque
# [CONSUMERS] MOD-XS-013(Broker API Connector,限流前置) ; MOD-XS-002(Broker Adapter,熔断联动)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] tokens<=capacity;sliding_window_count<=limit;L1~L4全通过才放行(AND);P0交易不受L3非交易时段限流;令牌非负
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidRateLimitConfigError
# [TESTS] tests/ex_sor/test_api_rate_limiter.py
# [A_module] module_id=MOD-XS-014 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Exchange API Rate Limiter — 交易所 API 限速器 (MOD-XS-014)

D-EX-SOR §12.5 四级限流架构:
    L1 全局限流: 滑动窗口, 所有外部 API 合计 ≤50 QPS
    L2 外部系统级: 令牌桶, miniQMT ≤10 TPS (各系统独立)
    L3 操作级: 令牌桶 + 分时段, 盘前15/集合竞价5/盘中8/盘后15 TPS
    L4 优先级: 优先级队列, 交易>风控>行情>因子>通知, P0 不受非交易限流影响

属 A 类基础设施 (令牌桶+滑动窗口标准算法, 阈值为 C 类可调参数)。
依据: D:\\临时工作区\\依赖图\\09-D-EX-SOR-执行路由域.md §12.5
SSoT: depgraph MOD-XS-014
Version: 0.1.0
"""

from __future__ import annotations

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, IntEnum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "TokenBucket",
    "SlidingWindowCounter",
    "RateLimitLevel",
    "RequestPriority",
    "TradingSession",
    "RateLimitConfig",
    "RateLimitDecision",
    "ApiRateLimiter",
    "InvalidRateLimitConfigError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidRateLimitConfigError(ZephyrBaseError):
    """限速器配置非法 (如容量≤0、速率≤0)。"""

    error_code = "ZA-XS-0014"


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class RateLimitLevel(IntEnum):
    """限流层级。"""

    L1_GLOBAL = 1
    L2_SYSTEM = 2
    L3_OPERATION = 3
    L4_PRIORITY = 4


class RequestPriority(IntEnum):
    """请求优先级 (L4 优先级限流)。"""

    P0_TRADING = 0  # 交易 — 最高优先级, 不受 L3 非交易时段限流
    P1_RISK = 1  # 风控
    P2_MARKET_DATA = 2  # 行情
    P3_FACTOR = 3  # 因子
    P4_NOTIFICATION = 4  # 通知 — 最低优先级


class TradingSession(Enum):
    """交易时段 (L3 操作级限流分时段)。"""

    PRE_OPEN = "pre_open"  # 盘前
    AUCTION = "auction"  # 集合竞价
    INTRADAY = "intraday"  # 盘中
    POST_CLOSE = "post_close"  # 盘后
    OFF_HOURS = "off_hours"  # 非交易时段


# ──────────────────────────────────────────────────────────────────────────────
# 令牌桶
# ──────────────────────────────────────────────────────────────────────────────


class TokenBucket:
    """令牌桶算法——按固定速率补充令牌, 请求消耗令牌。

    线程安全: 单线程适用 (Phase 1); 多线程需外加锁。
    不变量: 0 <= tokens <= capacity

    用法:
        bucket = TokenBucket(capacity=10, refill_rate=10.0)
        if bucket.try_consume(1):
            # 放行
        else:
            # 限流
    """

    def __init__(self, capacity: float, refill_rate: float) -> None:
        if capacity <= 0:
            raise InvalidRateLimitConfigError(f"capacity must be >0, got {capacity}")
        if refill_rate <= 0:
            raise InvalidRateLimitConfigError(f"refill_rate must be >0, got {refill_rate}")
        self._capacity = capacity
        self._refill_rate = refill_rate  # tokens per second
        self._tokens = capacity  # 初始满桶
        self._last_refill = time.monotonic()

    @property
    def capacity(self) -> float:
        return self._capacity

    @property
    def refill_rate(self) -> float:
        return self._refill_rate

    @property
    def tokens(self) -> float:
        """当前可用令牌数 (含未刷新的补充)。"""
        self._refill()
        return self._tokens

    def _refill(self) -> None:
        """按经过时间补充令牌。"""
        now = time.monotonic()
        elapsed = now - self._last_refill
        if elapsed > 0:
            self._tokens = min(self._capacity, self._tokens + elapsed * self._refill_rate)
            self._last_refill = now

    def try_consume(self, tokens: float = 1.0) -> bool:
        """尝试消耗令牌, 成功返回 True。"""
        if tokens <= 0:
            raise InvalidRateLimitConfigError(f"consume tokens must be >0, got {tokens}")
        self._refill()
        if self._tokens >= tokens:
            self._tokens -= tokens
            return True
        return False

    def time_until_available(self, tokens: float = 1.0) -> float:
        """等待多少秒后才有足够的令牌。"""
        self._refill()
        if self._tokens >= tokens:
            return 0.0
        needed = tokens - self._tokens
        return needed / self._refill_rate


# ──────────────────────────────────────────────────────────────────────────────
# 滑动窗口计数器
# ──────────────────────────────────────────────────────────────────────────────


class SlidingWindowCounter:
    """滑动窗口计数器——在时间窗口内限制请求总数。

    不变量: 窗口内计数 <= limit

    用法:
        counter = SlidingWindowCounter(limit=50, window_seconds=1.0)
        if counter.try_acquire():
            # 放行
    """

    def __init__(self, limit: int, window_seconds: float) -> None:
        if limit <= 0:
            raise InvalidRateLimitConfigError(f"limit must be >0, got {limit}")
        if window_seconds <= 0:
            raise InvalidRateLimitConfigError(f"window_seconds must be >0, got {window_seconds}")
        self._limit = limit
        self._window = window_seconds
        self._timestamps: deque[float] = deque()

    @property
    def limit(self) -> int:
        return self._limit

    @property
    def window_seconds(self) -> float:
        return self._window

    @property
    def current_count(self) -> int:
        """当前窗口内请求数。"""
        self._evict_expired()
        return len(self._timestamps)

    def _evict_expired(self) -> None:
        """清除窗口外的过期时间戳。"""
        cutoff = time.monotonic() - self._window
        while self._timestamps and self._timestamps[0] <= cutoff:
            self._timestamps.popleft()

    def try_acquire(self) -> bool:
        """尝试获取一个请求配额, 成功返回 True。"""
        self._evict_expired()
        if len(self._timestamps) < self._limit:
            self._timestamps.append(time.monotonic())
            return True
        return False


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RateLimitConfig:
    """四级限流配置。

    Attributes:
        l1_global_qps: L1 全局限流 (QPS), 默认 50
        l2_system_tps: L2 外部系统级 (TPS), miniQMT 默认 10
        l3_session_tps: L3 操作级分时段 (TPS), 盘前15/集合竞价5/盘中8/盘后15
        l3_off_hours_block: L3 非交易时段是否阻断 (P0 除外), 默认 True
    """

    l1_global_qps: int = 50
    l2_system_tps: int = 10
    l3_pre_open_tps: int = 15
    l3_auction_tps: int = 5
    l3_intraday_tps: int = 8
    l3_post_close_tps: int = 15
    l3_off_hours_block: bool = True

    def __post_init__(self) -> None:
        for name, val in [
            ("l1_global_qps", self.l1_global_qps),
            ("l2_system_tps", self.l2_system_tps),
            ("l3_pre_open_tps", self.l3_pre_open_tps),
            ("l3_auction_tps", self.l3_auction_tps),
            ("l3_intraday_tps", self.l3_intraday_tps),
            ("l3_post_close_tps", self.l3_post_close_tps),
        ]:
            if val <= 0:
                raise InvalidRateLimitConfigError(f"{name} must be >0, got {val}")


# ──────────────────────────────────────────────────────────────────────────────
# 限流决策
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RateLimitDecision:
    """限流决策结果。

    Attributes:
        allowed: 是否放行
        blocked_level: 被哪一层阻断 (None=放行)
        retry_after_seconds: 建议重试等待秒数 (0=立即)
        reason: 决策原因
        timestamp: 决策时间
    """

    allowed: bool
    blocked_level: RateLimitLevel | None
    retry_after_seconds: float
    reason: str
    timestamp: datetime

    def to_dict(self) -> dict[str, object]:
        return {
            "allowed": self.allowed,
            "blocked_level": self.blocked_level.name if self.blocked_level else None,
            "retry_after_seconds": self.retry_after_seconds,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
        }


# ──────────────────────────────────────────────────────────────────────────────
# API 限速器
# ──────────────────────────────────────────────────────────────────────────────


class ApiRateLimiter:
    """四级限速器——L1 滑动窗口 + L2/L3 令牌桶 + L4 优先级。

    用法:
        limiter = ApiRateLimiter()
        decision = limiter.check(
            system="miniQMT",
            session=TradingSession.INTRADAY,
            priority=RequestPriority.P0_TRADING,
        )
        if decision.allowed:
            # 发送请求
        else:
            # 等待 retry_after_seconds
    """

    def __init__(self, config: RateLimitConfig | None = None) -> None:
        self._config = config or RateLimitConfig()

        # L1: 全局滑动窗口 (1 秒窗口)
        self._l1_global = SlidingWindowCounter(limit=self._config.l1_global_qps, window_seconds=1.0)

        # L2: 各系统令牌桶 (按 system_name 隔离)
        self._l2_buckets: dict[str, TokenBucket] = {}

        # L3: 各时段令牌桶 (按 session 隔离)
        session_tps = {
            TradingSession.PRE_OPEN: self._config.l3_pre_open_tps,
            TradingSession.AUCTION: self._config.l3_auction_tps,
            TradingSession.INTRADAY: self._config.l3_intraday_tps,
            TradingSession.POST_CLOSE: self._config.l3_post_close_tps,
        }
        self._l3_buckets: dict[TradingSession, TokenBucket] = {
            session: TokenBucket(capacity=tps, refill_rate=float(tps)) for session, tps in session_tps.items()
        }

    @property
    def config(self) -> RateLimitConfig:
        return self._config

    # ── 公开 API: 限流检查 ──

    def check(
        self,
        system: str,
        session: TradingSession,
        priority: RequestPriority,
        now: datetime | None = None,
    ) -> RateLimitDecision:
        """四级限流检查 (L1→L2→L3→L4, 全通过才放行)。

        Args:
            system: 外部系统名 (如 "miniQMT", "iFind")
            session: 当前交易时段
            priority: 请求优先级
            now: 时间戳 (测试用)

        Returns:
            RateLimitDecision
        """
        now = now or datetime.now(timezone.utc)
        cfg = self._config

        # L4 优先级检查: P0 交易不受 L3 非交易时段限流
        is_p0_trading = priority == RequestPriority.P0_TRADING

        # L3 非交易时段阻断 (P0 除外)
        if session == TradingSession.OFF_HOURS:
            if cfg.l3_off_hours_block and not is_p0_trading:
                return RateLimitDecision(
                    allowed=False,
                    blocked_level=RateLimitLevel.L3_OPERATION,
                    retry_after_seconds=float("inf"),
                    reason=f"L3: 非交易时段阻断 (priority={priority.name}, P0除外)",
                    timestamp=now,
                )

        # L1: 全局滑动窗口
        if not self._l1_global.try_acquire():
            return RateLimitDecision(
                allowed=False,
                blocked_level=RateLimitLevel.L1_GLOBAL,
                retry_after_seconds=1.0,
                reason=f"L1: 全局限流 ({cfg.l1_global_qps} QPS 已满)",
                timestamp=now,
            )

        # L2: 系统级令牌桶
        l2_bucket = self._get_l2_bucket(system)
        if not l2_bucket.try_consume():
            retry = l2_bucket.time_until_available()
            return RateLimitDecision(
                allowed=False,
                blocked_level=RateLimitLevel.L2_SYSTEM,
                retry_after_seconds=retry,
                reason=f"L2: 系统级限流 ({system} {cfg.l2_system_tps} TPS 已满)",
                timestamp=now,
            )

        # L3: 操作级令牌桶 (P0 交易跳过)
        if not is_p0_trading and session != TradingSession.OFF_HOURS:
            l3_bucket = self._l3_buckets.get(session)
            if l3_bucket is not None and not l3_bucket.try_consume():
                retry = l3_bucket.time_until_available()
                return RateLimitDecision(
                    allowed=False,
                    blocked_level=RateLimitLevel.L3_OPERATION,
                    retry_after_seconds=retry,
                    reason=f"L3: 操作级限流 ({session.value} TPS 已满)",
                    timestamp=now,
                )

        # L4: 优先级已在前置逻辑中处理 (P0 优先, 非 P0 受 L3 约束)
        logger.debug(
            "Rate limit passed: system=%s session=%s priority=%s",
            system,
            session.value,
            priority.name,
        )

        return RateLimitDecision(
            allowed=True,
            blocked_level=None,
            retry_after_seconds=0.0,
            reason="OK",
            timestamp=now,
        )

    # ── 内部方法 ──

    def _get_l2_bucket(self, system: str) -> TokenBucket:
        """获取或创建系统级令牌桶。"""
        if system not in self._l2_buckets:
            self._l2_buckets[system] = TokenBucket(
                capacity=self._config.l2_system_tps,
                refill_rate=float(self._config.l2_system_tps),
            )
        return self._l2_buckets[system]

    # ── 诊断 API ──

    def get_l1_count(self) -> int:
        """L1 当前窗口请求数。"""
        return self._l1_global.current_count

    def get_l2_tokens(self, system: str) -> float:
        """L2 指定系统可用令牌数。"""
        bucket = self._l2_buckets.get(system)
        return bucket.tokens if bucket else self._config.l2_system_tps

    def get_l3_tokens(self, session: TradingSession) -> float:
        """L3 指定时段可用令牌数。"""
        bucket = self._l3_buckets.get(session)
        return bucket.tokens if bucket else 0.0
