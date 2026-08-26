# [BLUEPRINT] MOD-SIG-130 | docs/03_modules/_domain_signal/strategy_matrix_3d/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-130 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_strategy_matrix_3d
# [TESTS] src/zephyr/signal_ashare/strategy_matrix_3d.py
"""MOD-SIG-130 单元测试：strategy_matrix_3d 量能体制风格三维策略矩阵。

蓝图验收（B10-01467/CAND-TESTB-048，A1 模块56）：
3×3×2=18 格策略查找表（格值=仓位/选股方向/持仓周期/止损k×ATR 四要素）+
参数由历史回测逐格填参（注入 backtest_runner）+ 格子查询接口 +
参数版本管理（版本递增+按版本查询）。回测/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.strategy_matrix_3d",
    reason="strategy_matrix_3d not importable",
)

from zephyr.regime.style_regime_model import SizeAxis  # noqa: E402
from zephyr.signal_ashare.volume_regime_adaptive import MarketRegime, VolumeState  # noqa: E402
from zephyr.signal_ashare.strategy_matrix_3d import (  # noqa: E402
    MatrixCell,
    MatrixVersion,
    StrategyMatrix3D,
    StrategyMatrixError,
)

_T0 = datetime.datetime(2026, 8, 26, 15, 0, 0)


def _cell(seed: float = 0.5) -> MatrixCell:
    return MatrixCell(position_pct=seed, direction="long", hold_days=5, stop_k=2.0)


def _full_cells(seed: float = 0.5) -> dict:
    return {key: _cell(seed) for key in StrategyMatrix3D.all_keys()}


def _matrix(runner=None, **kwargs) -> StrategyMatrix3D:
    kwargs.setdefault("clock", lambda: _T0)
    if runner is not None:
        kwargs["backtest_runner"] = runner
    return StrategyMatrix3D(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 格值四要素校验
# ──────────────────────────────────────────────────────────────────────────────


class TestMatrixCell:
    def test_ok(self) -> None:
        cell = MatrixCell(0.6, "flat", 10, 1.5)
        assert cell.hold_days == 10

    def test_bad_position_raises(self) -> None:
        for bad in (-0.1, 1.1, float("nan"), float("inf")):
            with pytest.raises(StrategyMatrixError):
                MatrixCell(bad, "long", 5, 2.0)

    def test_bad_direction_raises(self) -> None:
        with pytest.raises(StrategyMatrixError):
            MatrixCell(0.5, "buy", 5, 2.0)

    def test_bad_hold_days_raises(self) -> None:
        for bad in (0, -3, 2.5, True):
            with pytest.raises(StrategyMatrixError):
                MatrixCell(0.5, "long", bad, 2.0)

    def test_bad_stop_k_raises(self) -> None:
        for bad in (0.0, -1.0, float("nan"), float("inf")):
            with pytest.raises(StrategyMatrixError):
                MatrixCell(0.5, "long", 5, bad)


# ──────────────────────────────────────────────────────────────────────────────
# 版本提交（commit）
# ──────────────────────────────────────────────────────────────────────────────


class TestCommit:
    def test_commit_versions_increment(self) -> None:
        m = _matrix()
        assert m.commit(_full_cells(0.5)) == 1
        assert m.commit(_full_cells(0.6)) == 2
        assert m.list_versions() == (1, 2)
        assert m.latest_version() == 2

    def test_commit_missing_cell_raises(self) -> None:
        cells = _full_cells()
        del cells[(VolumeState.SHRINK, MarketRegime.TREND, SizeAxis.LARGE)]
        with pytest.raises(StrategyMatrixError):
            _matrix().commit(cells)

    def test_commit_extra_key_raises(self) -> None:
        cells = _full_cells()
        cells[("spike", "trend", "large", "extra")] = _cell()  # 4 元非法键
        with pytest.raises(StrategyMatrixError):
            _matrix().commit(cells)

    def test_commit_bad_cell_type_raises(self) -> None:
        cells = _full_cells()
        cells[(VolumeState.FLAT, MarketRegime.CHOPPY, SizeAxis.SMALL)] = {"position_pct": 0.5}
        with pytest.raises(StrategyMatrixError):
            _matrix().commit(cells)

    def test_snapshot_uses_injected_clock(self) -> None:
        m = _matrix()
        m.commit(_full_cells())
        snap = m.version_snapshot(1)
        assert isinstance(snap, MatrixVersion)
        assert snap.created_at == _T0
        assert len(snap.cells) == 18

    def test_snapshot_immutable_after_later_commit(self) -> None:
        m = _matrix()
        v1_cells = _full_cells(0.3)
        m.commit(v1_cells)
        m.commit(_full_cells(0.9))
        assert m.version_snapshot(1).cells[
            (VolumeState.SPIKE, MarketRegime.TREND, SizeAxis.LARGE)
        ].position_pct == pytest.approx(0.3)


# ──────────────────────────────────────────────────────────────────────────────
# 逐格回测填参（注入 backtest_runner）
# ──────────────────────────────────────────────────────────────────────────────


class TestFillFromBacktest:
    def test_fill_calls_runner_all_18(self) -> None:
        seen: list[tuple] = []

        def runner(v, r, s) -> MatrixCell:
            seen.append((v, r, s))
            return MatrixCell(0.4, "flat", 3, 1.8)

        m = _matrix(runner=runner)
        assert m.fill_from_backtest() == 1
        assert seen == list(StrategyMatrix3D.all_keys())  # 逐格确定性顺序
        assert m.latest_version() == 1

    def test_fill_mapping_coerced(self) -> None:
        runner = lambda v, r, s: {
            "position_pct": 0.7, "direction": "short", "hold_days": 2, "stop_k": 3.0,
            "extra_ignored": 1,
        }
        m = _matrix(runner=runner)
        m.fill_from_backtest()
        cell = m.query(VolumeState.SPIKE, MarketRegime.MEAN_REVERSION, SizeAxis.SMALL)
        assert cell.direction == "short"
        assert cell.stop_k == pytest.approx(3.0)

    def test_fill_runner_missing_fail_closed(self) -> None:
        with pytest.raises(StrategyMatrixError):
            _matrix().fill_from_backtest()

    def test_fill_runner_exception_no_partial_version(self) -> None:
        def runner(v, r, s):
            if v is VolumeState.FLAT:
                raise RuntimeError("回测爆炸")
            return _cell()

        m = _matrix(runner=runner)
        with pytest.raises(StrategyMatrixError):
            m.fill_from_backtest()
        assert m.list_versions() == ()  # 不残留半版

    def test_fill_bad_output_raises(self) -> None:
        with pytest.raises(StrategyMatrixError):
            _matrix(runner=lambda v, r, s: "not-a-cell").fill_from_backtest()
        with pytest.raises(StrategyMatrixError):
            _matrix(runner=lambda v, r, s: {"position_pct": 0.5}).fill_from_backtest()
        with pytest.raises(StrategyMatrixError):
            _matrix(runner=lambda v, r, s: MatrixCell(9.9, "long", 5, 2.0)).fill_from_backtest()


# ──────────────────────────────────────────────────────────────────────────────
# 格子查询 + 版本回溯
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_query_latest_default(self) -> None:
        m = _matrix()
        m.commit(_full_cells(0.5))
        m.commit(_full_cells(0.8))
        cell = m.query(VolumeState.SHRINK, MarketRegime.CHOPPY, SizeAxis.SMALL)
        assert cell.position_pct == pytest.approx(0.8)

    def test_query_by_version(self) -> None:
        m = _matrix()
        m.commit(_full_cells(0.5))
        m.commit(_full_cells(0.8))
        cell = m.query(VolumeState.SHRINK, MarketRegime.CHOPPY, SizeAxis.SMALL, version=1)
        assert cell.position_pct == pytest.approx(0.5)

    def test_query_before_commit_raises(self) -> None:
        m = _matrix()
        with pytest.raises(StrategyMatrixError):
            m.query(VolumeState.FLAT, MarketRegime.TREND, SizeAxis.LARGE)
        with pytest.raises(StrategyMatrixError):
            m.latest_version()

    def test_query_unknown_version_raises(self) -> None:
        m = _matrix()
        m.commit(_full_cells())
        with pytest.raises(StrategyMatrixError):
            m.query(VolumeState.FLAT, MarketRegime.TREND, SizeAxis.LARGE, version=99)

    def test_query_bad_axis_type_raises(self) -> None:
        m = _matrix()
        m.commit(_full_cells())
        with pytest.raises(StrategyMatrixError):
            m.query("flat", MarketRegime.TREND, SizeAxis.LARGE)
        with pytest.raises(StrategyMatrixError):
            m.query(VolumeState.FLAT, "trend", SizeAxis.LARGE)
        with pytest.raises(StrategyMatrixError):
            m.query(VolumeState.FLAT, MarketRegime.TREND, "large")

    def test_all_18_keys_cover_axes(self) -> None:
        keys = StrategyMatrix3D.all_keys()
        assert len(keys) == 18
        assert len(set(keys)) == 18
        vs = {k[0] for k in keys}
        rs = {k[1] for k in keys}
        ss = {k[2] for k in keys}
        assert vs == set(VolumeState) and rs == set(MarketRegime) and ss == set(SizeAxis)

    def test_determinism(self) -> None:
        def build() -> StrategyMatrix3D:
            m = _matrix(runner=lambda v, r, s: MatrixCell(0.6, "long", 4, 2.5))
            m.fill_from_backtest()
            return m

        q = (VolumeState.SPIKE, MarketRegime.TREND, SizeAxis.LARGE)
        assert build().query(*q) == build().query(*q)
