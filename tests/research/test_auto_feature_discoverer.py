# [BLUEPRINT] MOD-FAC-001 | docs/03_modules/_domain_factor/auto_feature_discoverer/blueprint.md | §test
# [A_module] module_id=MOD-FAC-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-FAC-001 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.research.test_auto_feature_discoverer
# [TESTS] src/zephyr/research/auto_feature_discoverer.py
"""MOD-FAC-001 单元测试：auto_feature_discoverer AI 自动特征发现器。

蓝图验收（B1-00630/CAND-FAC-016，C2 74）：
价量算子模板词表闭合笛卡尔组合生成 + IC/IR 初筛（ic_calculator 全注入）+
TopN 人工确认队列（confirm 方入库，未确认不入库）+ 确定性排序。
ic 计算器/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.research.auto_feature_discoverer",
    reason="auto_feature_discoverer not importable",
)

from zephyr.research.auto_feature_discoverer import (  # noqa: E402
    ARITH_OPS,
    BASE_SERIES,
    DEFAULT_WINDOWS,
    ROLLING_OPS,
    AutoFeatureDiscoverer,
    AutoFeatureError,
    FeatureFamily,
)

_T0 = datetime.datetime(2026, 8, 26, 15, 0, 0)

#: 确定性 IC 表（表达式 → (ic, ir)）
_IC_TABLE = {
    "roll_mean(close,5)": (0.10, 0.50),
    "roll_mean(close,10)": (0.08, 0.40),
    "roll_std(close,5)": (0.06, 0.30),
    "roll_mean(volume,5)": (0.04, 0.20),
    "sub(close,open)": (0.03, 0.10),
    "div(close,open)": (0.01, 0.05),  # |ic| < min_ic → 被筛除
    "mul(high,low)": (0.005, 0.01),  # 被筛除
}


def _ic_calc(expr: str) -> tuple[float, float]:
    return _IC_TABLE.get(expr, (0.0, 0.0))


def _discoverer(**kw) -> AutoFeatureDiscoverer:
    kw.setdefault("ic_calculator", _ic_calc)
    kw.setdefault("clock", lambda: _T0)
    return AutoFeatureDiscoverer(**kw)


def _small(**kw) -> AutoFeatureDiscoverer:
    """小词表发现器（表达式全集落在 _IC_TABLE 覆盖内）。"""
    kw.setdefault("base_series", ("close", "volume"))
    kw.setdefault("windows", (5, 10))
    return _discoverer(**kw)


# ──────────────────────────────────────────────────────────────────────────────
# 构造 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_missing_ic_calculator_raises(self) -> None:
        with pytest.raises(AutoFeatureError):
            AutoFeatureDiscoverer(ic_calculator=None)

    def test_threshold_ranges(self) -> None:
        with pytest.raises(AutoFeatureError):
            _discoverer(min_ic=1.0)
        with pytest.raises(AutoFeatureError):
            _discoverer(min_ic=-0.1)
        with pytest.raises(AutoFeatureError):
            _discoverer(min_ir=-0.5)

    def test_top_n_invalid(self) -> None:
        with pytest.raises(AutoFeatureError):
            _discoverer(top_n=0)

    def test_base_series_vocab(self) -> None:
        with pytest.raises(AutoFeatureError):
            _discoverer(base_series=("close", "turnover"))  # turnover 词表外
        with pytest.raises(AutoFeatureError):
            _discoverer(base_series=("close", "close"))  # 重复

    def test_window_vocab(self) -> None:
        with pytest.raises(AutoFeatureError):
            _discoverer(windows=(1, 5))  # 窗口 <2
        with pytest.raises(AutoFeatureError):
            _discoverer(windows=())  # 空词表
        with pytest.raises(AutoFeatureError):
            _discoverer(base_series=())


# ──────────────────────────────────────────────────────────────────────────────
# 生成（词表闭合笛卡尔组合）
# ──────────────────────────────────────────────────────────────────────────────


class TestGenerate:
    def test_generate_count_and_vocab(self) -> None:
        d = _discoverer()
        exprs = d.generate_expressions()
        expected = len(ROLLING_OPS) * len(BASE_SERIES) * len(DEFAULT_WINDOWS) + len(ARITH_OPS) * len(BASE_SERIES) * (
            len(BASE_SERIES) - 1
        )
        assert len(exprs) == expected
        assert len(set(exprs)) == expected  # 无重复

    def test_generate_sorted_deterministic(self) -> None:
        d1, d2 = _discoverer(), _discoverer()
        e1, e2 = d1.generate_expressions(), d2.generate_expressions()
        assert e1 == e2 == tuple(sorted(e1))

    def test_generate_small_vocab_contents(self) -> None:
        d = _small()
        exprs = d.generate_expressions()
        assert "roll_mean(close,5)" in exprs
        assert "sub(close,volume)" in exprs
        assert "add(close,close)" not in exprs  # 自配对排除
        assert all(exprs)  # 无空串


# ──────────────────────────────────────────────────────────────────────────────
# 初筛（IC/IR 注入）
# ──────────────────────────────────────────────────────────────────────────────


class TestScreen:
    def test_screen_filters_by_min_ic(self) -> None:
        d = _small()
        screened = d.screen()
        exprs = {c.expression for c in screened}
        assert "roll_mean(close,5)" in exprs
        assert "div(close,open)" not in exprs  # |ic|=0.01 < 0.02

    def test_screen_filters_by_min_ir(self) -> None:
        d = _small(min_ir=0.45)
        exprs = {c.expression for c in d.screen()}
        assert exprs == {"roll_mean(close,5)"}  # 唯一 |ir|≥0.45

    def test_screen_ranking_deterministic(self) -> None:
        d = _small()
        ranked = [c.expression for c in d.screen()]
        assert ranked[0] == "roll_mean(close,5)"  # |ic| 最大者居首
        ids = [c.feature_id for c in d.screen()]
        assert ids == [f"AF-{i + 1:04d}" for i in range(len(ids))]  # 按名次枚举

    def test_screen_family_tag(self) -> None:
        d = _discoverer()  # 全词表（sub(close,open) 在 IC 表内入围）
        fam = {c.expression: c.family for c in d.screen()}
        assert fam["roll_mean(close,5)"] is FeatureFamily.ROLLING
        assert fam["sub(close,open)"] is FeatureFamily.ARITH

    def test_screen_rejects_blank_expression(self) -> None:
        d = _small()
        with pytest.raises(AutoFeatureError):
            d.screen(["roll_mean(close,5)", "  "])

    def test_screen_empty_input_raises(self) -> None:
        d = _small()
        with pytest.raises(AutoFeatureError):
            d.screen([])

    def test_screen_ic_calculator_exception_fail_closed(self) -> None:
        def boom(expr: str) -> tuple[float, float]:
            raise RuntimeError("后端故障")

        d = _discoverer(ic_calculator=boom, base_series=("close",), windows=(5,))
        with pytest.raises(AutoFeatureError):
            d.screen()

    def test_screen_ic_calculator_bad_return_fail_closed(self) -> None:
        d = _discoverer(ic_calculator=lambda e: ("bad", 0.1), base_series=("close",), windows=(5,))
        with pytest.raises(AutoFeatureError):
            d.screen()


# ──────────────────────────────────────────────────────────────────────────────
# 发现 + 人工确认队列
# ──────────────────────────────────────────────────────────────────────────────


class TestDiscoverAndConfirm:
    def test_discover_top_n_cap_and_queue(self) -> None:
        d = _small(top_n=2)
        top = d.discover()
        assert len(top) == 2
        queue = d.pending_queue()
        assert len(queue) == 2
        assert queue[0].candidate.expression == "roll_mean(close,5)"
        assert queue[0].queued_at == _T0  # 注入时钟留痕

    def test_unconfirmed_not_in_store(self) -> None:
        d = _small()
        d.discover()
        assert d.confirmed_features() == ()  # 未确认不入库

    def test_confirm_moves_to_store(self) -> None:
        d = _small(top_n=2)
        top = d.discover()
        cand = d.confirm(top[0].feature_id)
        assert cand.expression == "roll_mean(close,5)"
        assert [c.feature_id for c in d.confirmed_features()] == [top[0].feature_id]
        assert len(d.pending_queue()) == 1

    def test_confirm_unknown_id_raises(self) -> None:
        d = _small()
        d.discover()
        with pytest.raises(AutoFeatureError):
            d.confirm("AF-9999")

    def test_confirm_twice_raises(self) -> None:
        d = _small(top_n=1)
        top = d.discover()
        d.confirm(top[0].feature_id)
        with pytest.raises(AutoFeatureError):
            d.confirm(top[0].feature_id)

    def test_reject_removes_from_queue(self) -> None:
        d = _small(top_n=2)
        top = d.discover()
        d.reject(top[1].feature_id)
        assert len(d.pending_queue()) == 1
        assert d.confirmed_features() == ()

    def test_reject_unknown_id_raises(self) -> None:
        d = _small()
        d.discover()
        with pytest.raises(AutoFeatureError):
            d.reject("AF-9999")

    def test_discover_idempotent_and_skips_confirmed(self) -> None:
        d = _small(top_n=2)
        top = d.discover()
        d.confirm(top[0].feature_id)
        again = d.discover()  # 同输入再发现
        assert [c.feature_id for c in again] == [c.feature_id for c in top]
        assert len(d.pending_queue()) == 1  # 已确认者不再入队
        assert len(d.confirmed_features()) == 1

    def test_full_determinism(self) -> None:
        def run() -> tuple:
            d = _small(top_n=3)
            top = d.discover()
            d.confirm(top[0].feature_id)
            return (
                tuple(c.expression for c in top),
                tuple(c.expression for c in d.confirmed_features()),
            )

        assert run() == run()  # 同输入必同输出
