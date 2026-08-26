# [BLUEPRINT] MOD-RK-043 | docs/03_modules/_domain_risk/var_data_prefetcher/blueprint.md
# [MODULE] zephyr.risk.var_data_prefetcher
# [DOMAIN] D_RISK
# [DEPENDENCIES] 无（协议核心纯内存；duckdb连接/单调时钟 全注入，parquet路径为构造参数）
# [CONSUMERS] 运行时装配批（VaR计算前批量预取装配 / 与查询构建器共用缓存语义）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 收益率序列按(symbol,trade_date)排序确定性落缓冲; 环形缓冲容量护栏(超出FIFO逐出); 窗口≤0/空标的集Fail-Closed; duckdb连接未注入Fail-Closed; 命中率/IO耗时指标单调累计; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_risk/var_data_prefetcher/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] VarPrefetchError(占位 ZA-RK-UNREGISTERED-VAR-PREFETCH)——容量非法/连接未注入/parquet路径为空/标的集为空/窗口非正/查询失败时抛
# [TESTS] tests/risk/test_var_data_prefetcher.py
# [A_module] module_id=MOD-RK-043 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""VarDataPrefetcher — VaR 数据预取器（MOD-RK-043）。

B13-04254（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-RSK-047，A3 D-DATA-44）：
VaR 计算数据预取——DuckDB 读 Parquet 批量预取（持仓相关收益率序列，duckdb
连接注入）+ 内存环形缓冲（容量护栏，FIFO 逐出）+ prefetch 命中率/IO 耗时指
标 + 与查询构建器共用缓存语义（键=标的+窗口）。

查重分工（蓝图 §0）：var_calculator=VaR 数值计算（本件=其上游数据供给，不
做分位数计算）；var_query_builder=参数化 SQL 生成+结果缓存（本件=批量预取
+环形缓冲，缓存键语义对齐但不共用实现）；risk_data_pipeline=风控数据管道
编排（本件=单职责预取件，不做管道编排）。
"""

from __future__ import annotations

import logging
import time
from collections import OrderedDict
from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, Final, Iterable, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "PrefetchMetrics",
    "PrefetchReport",
    "VarDataPrefetcher",
    "VarPrefetchError",
]


class VarPrefetchError(Exception):
    """VaR 数据预取输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-RK-UNREGISTERED-VAR-PREFETCH。
    """


@dataclass(frozen=True)
class PrefetchMetrics:
    """预取指标快照（命中率/IO 耗时，frozen）。"""

    hits: int
    misses: int
    io_calls: int
    io_seconds: float
    evictions: int
    buffered_symbols: int

    @property
    def hit_rate(self) -> float:
        """命中率（无查询时 0.0）。"""
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


@dataclass(frozen=True)
class PrefetchReport:
    """单次批量预取报告（frozen）。"""

    symbols_loaded: int
    rows_loaded: int
    io_seconds: float
    evicted: int


@dataclass(frozen=True)
class _BufferEntry:
    """环形缓冲条目：标的 → 收益率序列（窗口长度为注入窗口）。"""

    window_days: int
    returns: tuple[Decimal, ...]


class VarDataPrefetcher:
    """VaR 数据预取器（DuckDB 批量预取 + 环形缓冲容量护栏 + 指标）。"""

    def __init__(
        self,
        *,
        duckdb_conn=None,
        parquet_path: str,
        capacity: int = 1024,
        time_source: Callable[[], float] | None = None,
    ) -> None:
        if capacity <= 0:
            raise VarPrefetchError(f"环形缓冲容量非正: {capacity!r}")
        if not parquet_path:
            raise VarPrefetchError("parquet_path 为空")
        self._conn = duckdb_conn
        self._parquet_path = parquet_path
        self._capacity = capacity
        self._time = time_source or time.monotonic
        self._buffer: OrderedDict[str, _BufferEntry] = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._io_calls = 0
        self._io_seconds = 0.0
        self._evictions = 0

    # ── 批量预取 ──────────────────────────────────────────────────────────

    def prefetch(self, symbols: Iterable[str], window_days: int) -> PrefetchReport:
        """DuckDB 读 Parquet 批量预取持仓相关收益率序列（容量护栏 FIFO 逐出）。"""
        if self._conn is None:
            raise VarPrefetchError("duckdb_conn 未注入（Fail-Closed 不旁路）")
        symbol_list = sorted({s for s in symbols if s})
        if not symbol_list:
            raise VarPrefetchError("标的集为空")
        if window_days <= 0:
            raise VarPrefetchError(f"窗口非正: {window_days!r}")

        placeholders = ", ".join("?" for _ in symbol_list)
        sql = (
            "SELECT symbol, trade_date, ret FROM read_parquet(?) "
            f"WHERE symbol IN ({placeholders}) ORDER BY symbol, trade_date"
        )
        t0 = self._time()
        try:
            rows: Sequence = self._conn.execute(
                sql, [self._parquet_path, *symbol_list]
            ).fetchall()
        except VarPrefetchError:
            raise
        except Exception as exc:  # noqa: BLE001 — IO 失败统一 Fail-Closed 包装
            raise VarPrefetchError(f"parquet 批量预取失败: {exc}") from exc
        io_elapsed = self._time() - t0
        self._io_calls += 1
        self._io_seconds += io_elapsed

        grouped: dict[str, list[Decimal]] = {s: [] for s in symbol_list}
        rows_loaded = 0
        for symbol, _trade_date, ret in rows:
            grouped[symbol].append(Decimal(str(ret)))
            rows_loaded += 1

        for symbol in symbol_list:
            series = tuple(grouped[symbol][-window_days:])
            if symbol in self._buffer:
                del self._buffer[symbol]
            self._buffer[symbol] = _BufferEntry(window_days=window_days, returns=series)

        evicted = 0
        while len(self._buffer) > self._capacity:
            victim, _ = self._buffer.popitem(last=False)  # FIFO 逐出最旧
            evicted += 1
            _log.debug("环形缓冲容量护栏逐出: %s", victim)
        self._evictions += evicted
        return PrefetchReport(
            symbols_loaded=len(symbol_list),
            rows_loaded=rows_loaded,
            io_seconds=io_elapsed,
            evicted=evicted,
        )

    # ── 缓存语义（键=标的+窗口，与查询构建器对齐） ────────────────────────

    def get_returns(self, symbol: str, window_days: int) -> tuple[Decimal, ...] | None:
        """缓冲命中 → 最近 window_days 收益率序列；未命中 → None（miss 计数）。"""
        if not symbol:
            raise VarPrefetchError("symbol 为空")
        if window_days <= 0:
            raise VarPrefetchError(f"窗口非正: {window_days!r}")
        entry = self._buffer.get(symbol)
        if entry is None or len(entry.returns) < window_days:
            self._misses += 1
            return None
        self._hits += 1
        self._buffer.move_to_end(symbol)
        return entry.returns[-window_days:]

    def contains(self, symbol: str) -> bool:
        """标的是否已在缓冲（不计命中率）。"""
        return symbol in self._buffer

    def clear(self) -> None:
        """清空缓冲（指标保留）。"""
        self._buffer.clear()

    # ── 指标 ─────────────────────────────────────────────────────────────

    def metrics(self) -> PrefetchMetrics:
        """命中率/IO 耗时指标快照。"""
        return PrefetchMetrics(
            hits=self._hits,
            misses=self._misses,
            io_calls=self._io_calls,
            io_seconds=self._io_seconds,
            evictions=self._evictions,
            buffered_symbols=len(self._buffer),
        )
