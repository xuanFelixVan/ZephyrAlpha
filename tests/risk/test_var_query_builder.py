# [BLUEPRINT] MOD-RK-045 | docs/03_modules/_domain_risk/var_query_builder/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-RK-045 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.risk.test_var_query_builder
# [TESTS] src/zephyr/risk/var_query_builder.py
"""MOD-RK-045 单元测试：var_query_builder VaR 历史模拟查询构建器。

蓝图验收（B13-04313/CAND-RSK-049，A3 D-RISK-82）：
窗口/标的/频段参数化 SQL 生成（参数白名单防注入）+ 谓词下推（过滤前置内层
子查询）+ 结果缓存（键=持仓hash+窗口，命中统计，singleflight 防击穿）。
loader 全注入内存替身，不触网不持有连接。
"""

from __future__ import annotations

from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.risk.var_query_builder",
    reason="var_query_builder not importable",
)

from zephyr.risk.var_query_builder import (  # noqa: E402
    QueryFrequency,
    VarQueryBuilder,
    VarQueryError,
)


def _builder(**overrides) -> VarQueryBuilder:
    kwargs = {"table": "position_returns", "max_window": 2500, "cache_capacity": 4}
    kwargs.update(overrides)
    return VarQueryBuilder(**kwargs)


def _build(b: VarQueryBuilder | None = None, **overrides):
    b = b or _builder()
    kwargs = {
        "symbols": ["000001", "600000"],
        "window_days": 250,
        "frequency": QueryFrequency.DAY,
    }
    kwargs.update(overrides)
    return b.build(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 构造白名单
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_illegal_table_name_raises(self) -> None:
        with pytest.raises(VarQueryError):
            _builder(table="x; DROP TABLE t--")
        with pytest.raises(VarQueryError):
            _builder(table="1abc")

    def test_non_positive_limits_raise(self) -> None:
        with pytest.raises(VarQueryError):
            _builder(max_window=0)
        with pytest.raises(VarQueryError):
            _builder(cache_capacity=0)


# ──────────────────────────────────────────────────────────────────────────────
# 参数化 SQL 生成（白名单防注入 + 谓词下推）
# ──────────────────────────────────────────────────────────────────────────────


class TestBuild:
    def test_sql_parameterized_no_value_interpolation(self) -> None:
        q = _build()
        assert "000001" not in q.sql  # 值一律占位符，禁止插值
        assert "1d" not in q.sql
        assert q.sql.count("?") == len(q.params)
        assert q.params[:2] == ("000001", "600000")
        assert q.params[2] == "1d"

    def test_predicate_pushdown_inner_subquery(self) -> None:
        q = _build(start_date="2026-01-01", end_date="2026-08-01")
        inner = q.sql[q.sql.index("FROM ("):]
        # 过滤谓词下推至内层（贴扫描侧），外层仅投影+LIMIT
        assert "WHERE symbol IN (?, ?) AND frequency = ?" in inner
        assert "trade_date >= ?" in inner and "trade_date <= ?" in inner
        assert q.sql.rstrip().endswith("LIMIT ?")
        assert q.params[-3:] == ("2026-01-01", "2026-08-01", 500)

    def test_limit_is_window_times_symbols(self) -> None:
        q = _build(window_days=10, symbols=["000001"])
        assert q.params[-1] == 10

    def test_symbols_sorted_deduped(self) -> None:
        q = _build(symbols=["600000", "000001", "600000"])
        assert q.params[:2] == ("000001", "600000")

    def test_empty_symbols_raises(self) -> None:
        with pytest.raises(VarQueryError):
            _build(symbols=[])
        with pytest.raises(VarQueryError):
            _build(symbols=["", ""])

    def test_injection_payload_symbol_rejected(self) -> None:
        with pytest.raises(VarQueryError):
            _build(symbols=["000001' OR '1'='1"])
        with pytest.raises(VarQueryError):
            _build(symbols=["x" * 33])

    def test_allowed_symbols_whitelist(self) -> None:
        b = _builder(allowed_symbols={"000001", "600000"})
        _build(b)  # 白名单内通过
        with pytest.raises(VarQueryError):
            _build(b, symbols=["000002"])

    def test_frequency_whitelist_closed(self) -> None:
        for freq in (QueryFrequency.DAY, QueryFrequency.HOUR, QueryFrequency.MIN5):
            assert _build(frequency=freq).params[2] == freq.value
        with pytest.raises(VarQueryError):
            _build(frequency="1d")  # 裸字符串非枚举 → 拒绝

    def test_window_out_of_range_raises(self) -> None:
        with pytest.raises(VarQueryError):
            _build(window_days=0)
        with pytest.raises(VarQueryError):
            _build(window_days=2501)

    def test_date_validation(self) -> None:
        with pytest.raises(VarQueryError):
            _build(start_date="2026/01/01")
        with pytest.raises(VarQueryError):
            _build(end_date="2026-13-01")
        with pytest.raises(VarQueryError):
            _build(start_date="2026-08-01", end_date="2026-01-01")

    def test_build_deterministic(self) -> None:
        assert _build() == _build()


# ──────────────────────────────────────────────────────────────────────────────
# 结果缓存（键=持仓hash+窗口，命中统计，singleflight）
# ──────────────────────────────────────────────────────────────────────────────


class TestResultCache:
    def test_cache_key_changes_with_holdings_and_window(self) -> None:
        b = _builder()
        q1 = b.build(symbols=["000001"], window_days=250, frequency=QueryFrequency.DAY)
        q2 = b.build(symbols=["000001"], window_days=500, frequency=QueryFrequency.DAY)
        q3 = b.build(
            symbols=["000001"], window_days=250, frequency=QueryFrequency.DAY,
            holdings={"000001": Decimal("100")},
        )
        assert q1.cache_key != q2.cache_key  # 窗口入键
        assert q1.cache_key != q3.cache_key  # 持仓 hash 入键
        q1_again = b.build(
            symbols=["000001"], window_days=250, frequency=QueryFrequency.DAY
        )
        assert q1.cache_key == q1_again.cache_key  # 同输入同键（holdings=None→symbols）

    def test_fetch_hit_and_miss_stats(self) -> None:
        b = _builder()
        q = _build(b)
        calls: list[tuple] = []
        loader = lambda sql, params: calls.append(params) or [("r1",)]
        assert b.fetch(q, loader) == [("r1",)]
        assert b.fetch(q, loader) == [("r1",)]  # 命中不再调 loader
        assert len(calls) == 1
        stats = b.cache_stats()
        assert (stats.hits, stats.misses, stats.size) == (1, 1, 1)

    def test_fetch_lru_eviction(self) -> None:
        b = _builder(cache_capacity=2)
        loader = lambda sql, params: [params]
        q1 = b.build(symbols=["000001"], window_days=10, frequency=QueryFrequency.DAY)
        q2 = b.build(symbols=["000002"], window_days=10, frequency=QueryFrequency.DAY)
        q3 = b.build(symbols=["600000"], window_days=10, frequency=QueryFrequency.DAY)
        b.fetch(q1, loader)
        b.fetch(q2, loader)
        b.fetch(q3, loader)  # 容量 2 → 逐出 q1
        assert b.cache_stats().size == 2
        b.fetch(q1, loader)  # 重新 miss（并逐出 q2）
        assert b.cache_stats().misses == 4
        b.fetch(q2, loader)  # q2 已被逐出 → 再 miss
        assert b.cache_stats().misses == 5

    def test_singleflight_reentry_raises(self) -> None:
        b = _builder()
        q = _build(b)

        def reentrant_loader(sql, params):
            b.fetch(q, lambda s, p: [])  # 同键在飞重入
            return []

        with pytest.raises(VarQueryError, match="singleflight"):
            b.fetch(q, reentrant_loader)

    def test_loader_exception_not_cached(self) -> None:
        b = _builder()
        q = _build(b)

        def boom(sql, params):
            raise RuntimeError("IO 失败")

        with pytest.raises(RuntimeError):
            b.fetch(q, boom)
        assert b.cache_stats().size == 0
        assert b.fetch(q, lambda s, p: ["ok"]) == ["ok"]  # 在飞标记已释放

    def test_fetch_invalid_query_raises(self) -> None:
        with pytest.raises(VarQueryError):
            _builder().fetch("not-a-query", lambda s, p: [])

    def test_cache_clear_keeps_stats(self) -> None:
        b = _builder()
        b.fetch(_build(b), lambda s, p: [])
        b.cache_clear()
        stats = b.cache_stats()
        assert stats.size == 0
        assert stats.misses == 1
