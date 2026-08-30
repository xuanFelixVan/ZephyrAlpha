# [BLUEPRINT] MOD-RK-045 | docs/03_modules/_domain_risk/var_query_builder/blueprint.md
# [MODULE] zephyr.risk.var_query_builder
# [DOMAIN] D_RISK
# [DEPENDENCIES] 无（协议核心纯内存；结果加载loader全注入，不持有任何连接）
# [CONSUMERS] 运行时装配批（VaR历史模拟查询装配 / 与预取器共用缓存键语义）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 参数白名单闭合(标的正则/频段枚举/窗口上限/表名标识符); 值一律占位符参数化禁止插值; 谓词下推(过滤内层子查询前置); 缓存键=持仓hash+窗口+频段; singleflight防击穿(同键在飞重入Fail-Closed); 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_risk/var_query_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] VarQueryError(占位 ZA-RK-UNREGISTERED-RISK-QUERY)——非法表名/标的/频段/窗口/日期/空标的集/同键在飞重入时抛
# [TESTS] tests/risk/test_var_query_builder.py
# [A_module] module_id=MOD-RK-045 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
VarQueryBuilder — VaR 历史模拟查询构建器（MOD-RK-045）。

B13-04313（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-RSK-049，A3 D-RISK-82）：
历史模拟查询构建——窗口/标的/频段参数化 SQL 生成（参数白名单防注入）+ 谓词
下推（过滤前置内层子查询）+ 结果缓存（键=持仓 hash+窗口，命中统计，
singleflight 防击穿语义）。

查重分工（蓝图 §0）：var_calculator=VaR 数值计算（本件=其数据查询组装，不
做分位数）；var_data_prefetcher=DuckDB 批量预取+环形缓冲（本件=SQL 文本与
参数生成+结果缓存，键语义对齐但互不持有）；本件不持有任何连接，loader 全
注入。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: table 参数
#   fields: 参数 table（无注解）
#   code: var_query_builder.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: allowed_symbols 参数
#   fields: 参数 allowed_symbols（无注解）
#   code: var_query_builder.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: max_window 参数
#   fields: 参数 max_window（无注解）
#   code: var_query_builder.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: cache_capacity 参数
#   fields: 参数 cache_capacity（无注解）
#   code: var_query_builder.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① VarQueryBuilder
#   name_en: VarQueryBuilder
#   intro: 历史模拟查询构建器（白名单参数化 + 谓词下推 + 结果缓存）。
#   desc: 历史模拟查询构建器（白名单参数化 + 谓词下推 + 结果缓存）。；公共方法（定义序）: build, cache_key, fetch, cache_stats, cache_clear；源码 L133-L287
#   inputs: table allowed_symbols max_window cache_capacity
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: VarQueryBuilder
#   downstream: 运行时装配批（VaR历史模拟查询装配 / 与预取器共用缓存键语义）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import hashlib
import logging
import re
from collections import OrderedDict
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Callable, Final, Iterable, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "CacheStats",
    "QueryFrequency",
    "VarQuery",
    "VarQueryBuilder",
    "VarQueryError",
]

_SYMBOL_RE: Final = re.compile(r"^[A-Za-z0-9_.\-]{1,32}$")
_TABLE_RE: Final = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}$")
_DATE_RE: Final = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class VarQueryError(Exception):
    """VaR 查询构建输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-RK-UNREGISTERED-VAR-QUERY。
    """


class QueryFrequency(str, Enum):
    """频段词表（白名单闭合）。"""

    DAY = "1d"
    HOUR = "1h"
    MIN5 = "5m"


@dataclass(frozen=True)
class VarQuery:
    """参数化查询产物（SQL 占位符 + 参数元组 + 缓存键，frozen）。"""

    sql: str
    params: tuple
    cache_key: str


@dataclass(frozen=True)
class CacheStats:
    """结果缓存命中统计（frozen）。"""

    hits: int
    misses: int
    size: int


class VarQueryBuilder:
    """历史模拟查询构建器（白名单参数化 + 谓词下推 + 结果缓存）。"""

    def __init__(
        self,
        *,
        table: str = "position_returns",
        allowed_symbols: Iterable[str] | None = None,
        max_window: int = 5000,
        cache_capacity: int = 256,
    ) -> None:
        if not _TABLE_RE.match(table):
            raise VarQueryError(f"非法表名标识符: {table!r}")
        if max_window <= 0:
            raise VarQueryError(f"窗口上限非正: {max_window!r}")
        if cache_capacity <= 0:
            raise VarQueryError(f"缓存容量非正: {cache_capacity!r}")
        self._table = table
        self._allowed = frozenset(allowed_symbols) if allowed_symbols is not None else None
        self._max_window = max_window
        self._cache_capacity = cache_capacity
        self._cache: OrderedDict[str, Sequence] = OrderedDict()
        self._in_flight: set[str] = set()
        self._hits = 0
        self._misses = 0

    # ── 白名单校验 ────────────────────────────────────────────────────────

    def _validate_symbols(self, symbols: Iterable[str]) -> tuple[str, ...]:
        cleaned = tuple(sorted({s for s in symbols if s}))
        if not cleaned:
            raise VarQueryError("标的集为空")
        for symbol in cleaned:
            if not _SYMBOL_RE.match(symbol):
                raise VarQueryError(f"标的格式非法（白名单拒绝）: {symbol!r}")
            if self._allowed is not None and symbol not in self._allowed:
                raise VarQueryError(f"标的不在白名单: {symbol!r}")
        return cleaned

    def _validate_date(self, value: str | None, label: str) -> str | None:
        if value is None:
            return None
        if not _DATE_RE.match(value):
            raise VarQueryError(f"{label} 日期格式非法（须 YYYY-MM-DD）: {value!r}")
        try:
            datetime.date.fromisoformat(value)
        except ValueError as exc:
            raise VarQueryError(f"{label} 日期不存在: {value!r}") from exc
        return value

    # ── 参数化 SQL 生成（谓词下推） ───────────────────────────────────────

    def build(
        self,
        *,
        symbols: Iterable[str],
        window_days: int,
        frequency: QueryFrequency,
        start_date: str | None = None,
        end_date: str | None = None,
        holdings: Mapping[str, Decimal] | None = None,
    ) -> VarQuery:
        """窗口/标的/频段 → 参数化 SQL（值一律占位符，过滤谓词下推内层）。"""
        cleaned = self._validate_symbols(symbols)
        if not isinstance(frequency, QueryFrequency):
            raise VarQueryError(f"非法频段（白名单拒绝）: {frequency!r}")
        if not (1 <= window_days <= self._max_window):
            raise VarQueryError(f"窗口越界[1,{self._max_window}]: {window_days!r}")
        start = self._validate_date(start_date, "start_date")
        end = self._validate_date(end_date, "end_date")
        if start is not None and end is not None and start > end:
            raise VarQueryError(f"日期区间倒置: {start} > {end}")

        placeholders = ", ".join("?" for _ in cleaned)
        predicates = [f"symbol IN ({placeholders})", "frequency = ?"]
        params: list = [*cleaned, frequency.value]
        if start is not None:
            predicates.append("trade_date >= ?")
            params.append(start)
        if end is not None:
            predicates.append("trade_date <= ?")
            params.append(end)
        # 谓词下推：过滤前置到内层子查询（贴扫描侧），外层仅投影+窗口截断
        where = " AND ".join(predicates)
        sql = (
            "SELECT symbol, trade_date, ret FROM ("
            f"SELECT symbol, trade_date, ret FROM {self._table} WHERE {where} "
            "ORDER BY symbol, trade_date"
            ") LIMIT ?"
        )
        params.append(window_days * len(cleaned))
        return VarQuery(
            sql=sql,
            params=tuple(params),
            cache_key=self.cache_key(
                holdings=holdings,
                symbols=cleaned,
                window_days=window_days,
                frequency=frequency,
            ),
        )

    # ── 缓存键（持仓 hash + 窗口 + 频段） ────────────────────────────────

    def cache_key(
        self,
        *,
        holdings: Mapping[str, Decimal] | None,
        symbols: Iterable[str],
        window_days: int,
        frequency: QueryFrequency,
    ) -> str:
        """缓存键 = sha256(持仓规范化 hash + 窗口 + 频段)（确定性）。"""
        if holdings:
            body = ";".join(f"{k}={holdings[k]}" for k in sorted(holdings))
        else:
            body = ";".join(sorted(symbols))
        digest = hashlib.sha256(f"{body}|w={window_days}|f={frequency.value}".encode()).hexdigest()
        return digest

    # ── 结果缓存（命中统计 + singleflight 防击穿） ────────────────────────

    def fetch(
        self,
        query: VarQuery,
        loader: Callable[[str, tuple], Sequence],
    ) -> Sequence:
        """缓存命中直返；未命中经 loader 加载并回填（singleflight：同键在飞重入 → Fail-Closed）。"""
        if not isinstance(query, VarQuery):
            raise VarQueryError(f"非法查询产物: {query!r}")
        key = query.cache_key
        if key in self._cache:
            self._hits += 1
            self._cache.move_to_end(key)
            return self._cache[key]
        if key in self._in_flight:
            raise VarQueryError(f"singleflight 防击穿: 同键查询在飞重入 {key[:12]}…")
        self._misses += 1
        self._in_flight.add(key)
        try:
            result = loader(query.sql, query.params)
        finally:
            self._in_flight.discard(key)
        self._cache[key] = result
        while len(self._cache) > self._cache_capacity:
            self._cache.popitem(last=False)  # LRU 逐出最旧
        return result

    def cache_stats(self) -> CacheStats:
        """缓存命中统计快照。"""
        return CacheStats(hits=self._hits, misses=self._misses, size=len(self._cache))

    def cache_clear(self) -> None:
        """清空结果缓存（统计保留）。"""
        self._cache.clear()
