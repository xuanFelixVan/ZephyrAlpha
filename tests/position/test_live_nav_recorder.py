# [BLUEPRINT] MOD-POS-023 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-29 行）
# [MODULE] tests.position.test_live_nav_recorder
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.live_nav_recorder
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网不连 QMT（假 broker 鸭子类型）；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=实盘净值记录/曲线逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-POS-023_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-POS-023 实盘净值曲线序列 单元测试（GAP-F-29，合成数据，miniQMT 全假）。

覆盖：NavPoint 计算（总资产=现金+市值、净值比 vs 基准）、模拟源适配（假 broker）、
曲线组装（累计收益/最大回撤/基准超额）、基准序列对齐、落库写入器注入、
输入校验 fail-closed、JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest

from zephyr.position.live_nav_recorder import (
    AssetSnapshot,
    NavPoint,
    SimulatedQmtAssetSource,
    build_nav_curve,
    persist_nav_points,
    record_daily_nav,
)


class _FakePositionSnapshot:
    def __init__(self, cash: float, mv: float):
        self.cash = cash
        self.total_market_value = mv


class _FakeBroker:
    """miniQMT broker 鸭子类型（get_positions → PositionSnapshot 形态）。"""

    def __init__(self, cash: float, mv: float):
        self._snap = _FakePositionSnapshot(cash, mv)
        self.calls = 0

    def get_positions(self):
        self.calls += 1
        return self._snap


def test_record_nav_basic_ratio() -> None:
    p = record_daily_nav(
        AssetSnapshot(cash=500_000.0, market_value=500_000.0),
        trade_date="2026-08-21",
        base_nav=1_000_000.0,
    )
    assert p.total_asset == pytest.approx(1_000_000.0)
    assert p.nav_ratio == pytest.approx(1.0)


def test_record_nav_first_point_base_none() -> None:
    p = record_daily_nav(
        AssetSnapshot(cash=600_000.0, market_value=500_000.0),
        trade_date="2026-08-20",
        base_nav=None,
    )
    assert p.nav_ratio == pytest.approx(1.0)
    assert p.total_asset == pytest.approx(1_100_000.0)


def test_record_nav_with_benchmark() -> None:
    p = record_daily_nav(
        AssetSnapshot(cash=500_000.0, market_value=600_000.0),
        trade_date="2026-08-21",
        base_nav=1_000_000.0,
        benchmark_close=4100.0,
        benchmark_base=4000.0,
    )
    assert p.nav_ratio == pytest.approx(1.1)
    assert p.benchmark_ratio == pytest.approx(1.025)


def test_record_nav_invalid_inputs_fail_closed() -> None:
    with pytest.raises(ValueError, match="asset 非法"):
        record_daily_nav("x", trade_date="2026-08-21")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="trade_date"):
        record_daily_nav(AssetSnapshot(cash=1.0, market_value=1.0), trade_date="2026-13-01")
    with pytest.raises(ValueError, match="cash/market_value 非法"):
        record_daily_nav(AssetSnapshot(cash=-1.0, market_value=0.0), trade_date="2026-08-21")


def test_simulated_source_fetches_asset() -> None:
    src = SimulatedQmtAssetSource(broker=_FakeBroker(cash=700_000.0, mv=300_000.0))
    asset = src.fetch_asset()
    assert isinstance(asset, AssetSnapshot)
    assert asset.cash == pytest.approx(700_000.0)
    assert asset.market_value == pytest.approx(300_000.0)


def test_simulated_source_broker_error_raises_valueerror() -> None:
    class _BadBroker:
        def get_positions(self):
            raise RuntimeError("qmt down")

    src = SimulatedQmtAssetSource(broker=_BadBroker())
    with pytest.raises(ValueError, match="资产快照获取失败"):
        src.fetch_asset()


def _points() -> list[NavPoint]:
    return [
        NavPoint(trade_date="2026-08-19", total_asset=1_000_000.0, cash=5e5, market_value=5e5, nav_ratio=1.0),
        NavPoint(
            trade_date="2026-08-20",
            total_asset=1_050_000.0,
            cash=5e5,
            market_value=5.5e5,
            nav_ratio=1.05,
            benchmark_close=4040.0,
            benchmark_ratio=1.01,
        ),
        NavPoint(
            trade_date="2026-08-21",
            total_asset=1_020_000.0,
            cash=5e5,
            market_value=5.2e5,
            nav_ratio=1.02,
            benchmark_close=4080.0,
            benchmark_ratio=1.02,
        ),
    ]


def test_curve_cum_return_and_drawdown() -> None:
    curve = build_nav_curve(_points())
    assert curve.cum_return_pct == pytest.approx(2.0)
    # 回撤输出=绝对值 %（峰 1.05 → 谷 1.02）
    assert curve.max_drawdown_pct == pytest.approx(abs((1.02 / 1.05 - 1.0) * 100.0), abs=1e-3)
    assert curve.latest_nav == pytest.approx(1_020_000.0)


def test_curve_excess_vs_benchmark() -> None:
    curve = build_nav_curve(_points())
    # 超额=同段（首末有基准比率点 08-20→08-21）净值收益 − 基准收益
    # 净值段 1.02/1.05−1≈−2.857%，基准段 1.02/1.01−1≈+0.990% → ≈−3.847%
    assert curve.excess_vs_benchmark_pct is not None
    assert curve.excess_vs_benchmark_pct == pytest.approx(-3.8472, abs=1e-2)


def test_curve_empty_degraded() -> None:
    curve = build_nav_curve([])
    assert curve.degraded is True


def test_curve_unsorted_input_sorted() -> None:
    pts = _points()
    curve = build_nav_curve([pts[2], pts[0], pts[1]])
    assert [p.trade_date for p in curve.points] == ["2026-08-19", "2026-08-20", "2026-08-21"]


def test_curve_json_serializable() -> None:
    json.dumps(asdict(build_nav_curve(_points())), ensure_ascii=False)


def test_persist_calls_writer_with_points() -> None:
    received: list[list[NavPoint]] = []

    def writer(points: list[NavPoint]) -> int:
        received.append(points)
        return len(points)

    n = persist_nav_points(_points(), writer=writer)
    assert n == 3
    assert received and len(received[0]) == 3


def test_persist_empty_skips_writer() -> None:
    called = []

    def writer(points):
        called.append(points)
        return 0

    assert persist_nav_points([], writer=writer) == 0
    assert not called


def test_persist_writer_error_raises_valueerror() -> None:
    def bad_writer(points):
        raise RuntimeError("db down")

    with pytest.raises(ValueError, match="净值落库失败"):
        persist_nav_points(_points(), writer=bad_writer)
