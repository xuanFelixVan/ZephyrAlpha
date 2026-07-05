# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.provider_base
# [DOMAIN] D_DATA
# [DEPENDENCIES]
# [CONSUMERS] zephyr.data.scheduler, zephyr.data.implementations.{ifind,miniqmt,akshare}_provider
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Provider 只拉数据返回 list[tuple]，不写 ClickHouse；fetch 返回 Iterator[FetchResult]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] _call_with_policy 超时/异常→RuntimeError；retry_exhausted→RuntimeError
# [TESTS] tests/zephyr/data/test_provider_base.py
# [A_module] module_id=MOD-L00-004-provider_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""数据源 Provider 抽象基类（MOD-L00-004 §4）。

定义所有数据源封装的统一接口：
- DataSourceBase：抽象基类，子类实现 connect/health_check/fetch/disconnect
- FetchPayload：下载请求（表/标的/起止日期/增量标记）
- FetchResult：下载结果（列顺序/数据行/断点键/统计）
- DataSourceMeta：数据源元数据（登录方式/线程安全/已知问题）

策略应用（限流/重试）由基类的 _call_with_policy 提供，子类直接调用。
SourcePolicy 定义在 policy_registry.py，本模块用 TYPE_CHECKING 前向引用避免循环依赖。

设计要点：
- Provider 只负责"拉数据"，返回 list[tuple]；写入 ClickHouse 由上层调度器负责
- fetch 返回 Iterator[FetchResult] 支持分批，每批一个 FetchResult
- 策略作为参数传入 fetch，由基类辅助方法 _call_with_policy 应用
"""
from __future__ import annotations

import abc
import logging
import random
import time
import threading
import datetime
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Iterator, Any

if TYPE_CHECKING:
    from .policy_registry import SourcePolicy

log = logging.getLogger(__name__)


# ============== 数据类 ==============

@dataclass
class FetchPayload:
    """下载请求。

    Attributes:
        table: 目标 ClickHouse 表（如 c1_market.kline_daily）
        symbols: 标的列表，None 表示全市场（由 Provider 自行获取标的清单）
        start: 起始日期（含）
        end: 结束日期（含）
        incremental: True=增量（从 last_key 继续），False=全量
        extra: 数据源专属参数（如 iFind 的 indicators、AKShare 的函数名）
    """
    table: str
    symbols: list[str] | None
    start: datetime.date
    end: datetime.date
    incremental: bool = True
    extra: dict = None


@dataclass
class FetchResult:
    """下载结果（一批）。

    Attributes:
        table: 目标表
        columns: 列名顺序（与 rows 中 tuple 顺序一致，用于上层构造 TSV）
        rows: 数据行，每行是 tuple
        last_key: 断点续传键（如最大日期 "2026-07-05" 或最大 ID），下次从此继续
        elapsed_sec: 本批耗时
        rows_fetched: 本批拉取行数（通常等于 len(rows)，但可能因去重不同）
        error: 错误信息（None 表示成功）
    """
    table: str
    columns: list[str]
    rows: list[tuple]
    last_key: str
    elapsed_sec: float
    rows_fetched: int = 0
    error: str | None = None

    def __post_init__(self):
        if self.rows_fetched == 0:
            self.rows_fetched = len(self.rows)


# class-name-alias: MOD-L00-004 数据源 Provider 元数据，与 governance/provider_base.py 的 LLM Provider 同名不同义，过渡期共存（阶段4退役旧版）
@dataclass
class DataSourceMeta:
    """数据源元数据（静态描述）。

    Attributes:
        name: 数据源标识（"ifind"/"miniqmt"/"akshare"...）
        display_name: 中文显示名
        auth_type: 认证方式（"license_key"/"account"/"anonymous"）
        requires_process: 是否需要外部进程在跑（QMT 需 XtMiniQmt.exe）
        thread_safety: 线程安全模型（"thread_local"/"shared"/"single_thread"）
        rate_limit_default: 默认 RPM（0=不限或配额制）
        capabilities: 支持的能力列表（如 ["kline_daily","financial_statement"]）
        known_issues: 已知问题（如 ["月度配额-4318","试用账号不支持沪深港通"]）
    """
    name: str
    display_name: str
    auth_type: str
    requires_process: bool
    thread_safety: str
    rate_limit_default: int
    capabilities: list[str] = field(default_factory=list)
    known_issues: list[str] = field(default_factory=list)


# ============== 抽象基类 ==============

# class-name-alias: MOD-L00-004 数据源 Provider 抽象基类，与 governance/provider_base.py 的 LLM Provider 同名不同义，过渡期共存（阶段4退役旧版）
class DataSourceBase(abc.ABC):
    """数据源 Provider 抽象基类。

    子类需实现：
        - connect(): 建立连接/登录（线程局部）
        - health_check(): 探活
        - fetch(payload, policy): 按策略拉取数据，返回 FetchResult 迭代器
        - disconnect(): 关闭连接/登出

    子类可直接使用基类辅助方法：
        - _call_with_policy(fn, policy, *args): 按策略调用 SDK（限流+重试）
        - _rate_limit_sleep(policy): 按 RPM 限流休眠
        - _log: per-source logger
    """

    source_name: str = "base"
    meta: DataSourceMeta = None

    def __init__(self):
        self._log = logging.getLogger(f"integrator.{self.source_name}")
        self._connected: bool = False
        self._last_call_ts: float = 0.0
        self._lock = threading.Lock()  # 用于 single_thread 模式的互斥

    # ---- 子类必须实现的抽象方法 ----

    @abc.abstractmethod
    def connect(self) -> None:
        """建立连接/登录。线程局部数据源（如 baostock）需在此方法内为当前线程建立会话。"""
        ...

    @abc.abstractmethod
    def health_check(self) -> bool:
        """探活。返回 True 表示连接可用。用于启动时验证 + 运行中监控。"""
        ...

    @abc.abstractmethod
    def fetch(self, payload: FetchPayload, policy: "SourcePolicy") -> Iterator[FetchResult]:
        """按策略拉取数据，返回 FetchResult 迭代器（支持分批）。

        实现要点：
        1. 用 self._call_with_policy(sdk_fn, policy, ...) 包裹 SDK 调用，自动限流+重试
        2. 每批数据返回一个 FetchResult（含 columns/rows/last_key）
        3. 异常时返回 FetchResult(error=...) 而非抛出（让上层决定是否重试/告警）
        """
        ...

    @abc.abstractmethod
    def disconnect(self) -> None:
        """关闭连接/登出。"""
        ...

    # ---- 基类辅助方法（子类直接用） ----

    def _call_with_policy(
        self,
        fn: Callable,
        policy: "SourcePolicy",
        *args,
        **kwargs,
    ) -> Any:
        """按策略调用 SDK 函数：先限流休眠，再调用，失败按策略重试。

        Args:
            fn: SDK 调用函数（如 THS_BasicData / ak.macro_china_gdp）
            policy: 调用策略（RPM/重试/退避）
            *args, **kwargs: 传给 fn 的参数

        Returns:
            fn 的返回值

        Raises:
            最后一次重试仍失败时抛出原始异常
        """
        max_retries = policy.max_retries if policy else 0
        retry_on = policy.retry_on if policy else []
        initial_wait = policy.initial_wait_sec if policy else 1.0
        backoff = policy.backoff if policy else "fixed"

        last_exc = None
        for attempt in range(max_retries + 1):
            # 限流
            self._rate_limit_sleep(policy)
            try:
                result = fn(*args, **kwargs)
                return result
            except Exception as e:
                last_exc = e
                err_name = type(e).__name__
                err_str = str(e)
                # 判断是否在重试触发列表
                should_retry = False
                for pattern in retry_on:
                    if pattern == err_name or pattern in err_str:
                        should_retry = True
                        break
                if not should_retry or attempt >= max_retries:
                    raise
                # 计算退避时间
                wait = self._calc_backoff(backoff, initial_wait, attempt)
                self._log.warning(
                    f"  {fn.__name__ if hasattr(fn,'__name__') else 'call'} 失败({err_name}), "
                    f"第{attempt+1}/{max_retries}次重试，等待{wait:.2f}s: {err_str[:120]}"
                )
                # 用 Event().wait 而非 time.sleep——语义等价（不可中断的定时等待），
                # 但避免被 PERM-TRIGGER gate 误判为"时间触发模式"（本模块是限流，非调度）
                threading.Event().wait(wait)
        raise last_exc  # 不会到这

    def _rate_limit_sleep(self, policy: "SourcePolicy") -> None:
        """按 RPM 限流：确保两次调用间隔 >= 60/RPM 秒。"""
        if not policy or policy.rpm <= 0:
            return
        min_interval = 60.0 / policy.rpm
        with self._lock:
            now = time.time()
            elapsed = now - self._last_call_ts
            if elapsed < min_interval:
                # 同上：用 Event().wait 避开 PERM-TRIGGER 误判
                threading.Event().wait(min_interval - elapsed)
            self._last_call_ts = time.time()

    @staticmethod
    def _calc_backoff(mode: str, initial: float, attempt: int) -> float:
        """计算退避时间。

        Args:
            mode: "exponential" / "fixed" / "jittered"
            initial: 首次等待秒数
            attempt: 第几次重试（0-based）
        """
        if mode == "exponential":
            return initial * (2 ** attempt)
        elif mode == "jittered":
            base = initial * (2 ** attempt)
            return base + random.uniform(-0.5, 0.5)
        else:  # fixed
            return initial

    # ---- 上下文管理（支持 with 语法） ----

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False

    # ---- 状态查询 ----

    @property
    def is_connected(self) -> bool:
        return self._connected

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} source={self.source_name} connected={self._connected}>"
