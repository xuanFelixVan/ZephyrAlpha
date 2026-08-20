# [BLUEPRINT] MOD-RK-07 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""ConcentrationMonitor 单元测试 (MOD-RK-07)。"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.risk.core.concentration_monitor import (
    ConcentrationAlertLevel,
    ConcentrationConfig,
    ConcentrationMonitor,
    InvalidConcentrationInputError,
)

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)


# ── 配置校验 ──────────────────────────────────────────────────────────────────


def test_config_invalid_hhi_warning_ge_critical():
    with pytest.raises(InvalidConcentrationInputError):
        ConcentrationConfig(hhi_warning=0.18, hhi_critical=0.18)


def test_config_invalid_threshold_out_of_range():
    with pytest.raises(InvalidConcentrationInputError):
        ConcentrationConfig(max_single_weight=1.5)


def test_config_invalid_warning_ratio():
    with pytest.raises(InvalidConcentrationInputError):
        ConcentrationConfig(single_warning_ratio=0)


# ── 权重归一化 ────────────────────────────────────────────────────────────────


def test_weights_auto_normalized():
    """权重自动归一化 (非 1.0 总和)。"""
    monitor = ConcentrationMonitor()
    snap = monitor.update({"A": 80, "B": 20}, now=T0)
    assert snap.hhi == pytest.approx(0.68)  # 0.8² + 0.2²


def test_negative_weight_raises():
    monitor = ConcentrationMonitor()
    with pytest.raises(InvalidConcentrationInputError):
        monitor.update({"A": -0.1, "B": 1.1}, now=T0)


def test_empty_weights_raises():
    monitor = ConcentrationMonitor()
    with pytest.raises(InvalidConcentrationInputError):
        monitor.update({}, now=T0)


def test_all_zero_weights_raises():
    monitor = ConcentrationMonitor()
    with pytest.raises(InvalidConcentrationInputError):
        monitor.update({"A": 0.0, "B": 0.0}, now=T0)


def test_zero_weights_filtered():
    """0 权重 symbol 应被过滤。"""
    monitor = ConcentrationMonitor()
    snap = monitor.update({"A": 0.5, "B": 0.0, "C": 0.5}, now=T0)
    assert snap.holdings_count == 2
    assert snap.hhi == pytest.approx(0.5)  # 0.5² + 0.5²


# ── HHI 计算 ──────────────────────────────────────────────────────────────────


def test_hhi_equal_weights_10_stocks():
    """10 只等权: HHI = 10 * 0.1² = 0.1。"""
    monitor = ConcentrationMonitor()
    weights = {f"S{i}": 0.1 for i in range(10)}
    snap = monitor.update(weights, now=T0)
    assert snap.hhi == pytest.approx(0.10)


def test_hhi_single_stock():
    """单只满仓: HHI = 1.0。"""
    monitor = ConcentrationMonitor()
    snap = monitor.update({"A": 1.0}, now=T0)
    assert snap.hhi == pytest.approx(1.0)
    assert snap.max_single_weight == pytest.approx(1.0)


def test_hhi_range_bound():
    """HHI ∈ [1/N, 1]。"""
    monitor = ConcentrationMonitor()
    for n in [2, 5, 10, 20]:
        weights = {f"S{i}": 1.0 / n for i in range(n)}
        snap = monitor.update(weights, now=T0)
        assert 1.0 / n <= snap.hhi <= 1.0


def test_is_diversified():
    monitor = ConcentrationMonitor()
    weights = {f"S{i}": 1.0 / 20 for i in range(20)}  # HHI=0.05
    snap = monitor.update(weights, now=T0)
    assert snap.is_diversified


# ── 个股集中度 ────────────────────────────────────────────────────────────────


def test_max_single_weight_and_symbol():
    monitor = ConcentrationMonitor()
    snap = monitor.update({"A": 0.5, "B": 0.3, "C": 0.2}, now=T0)
    assert snap.max_single_weight == pytest.approx(0.5)
    assert snap.max_single_symbol == "A"


def test_single_critical_when_above_limit():
    """单股权重超 10% → CRITICAL。"""
    monitor = ConcentrationMonitor()
    snap = monitor.update({"A": 0.15, "B": 0.85}, now=T0)
    assert snap.level is ConcentrationAlertLevel.CRITICAL
    assert any("max_single" in r for r in snap.breach_reasons)


def test_single_warning_at_8pct():
    """单股权重达 8% (10% × 0.8) → WARNING。"""
    monitor = ConcentrationMonitor()
    snap = monitor.update({"A": 0.08, "B": 0.92}, now=T0)
    # A=8% 触发 warning, 但 B=92% 触发 critical → 取最严重
    assert snap.level is ConcentrationAlertLevel.CRITICAL


def test_single_warning_only():
    """构造仅触发个股 WARNING 的场景 (避开浮点边界, 用 8.5%)。"""
    monitor = ConcentrationMonitor()
    # A=8.5% (高于 8% warning 阈值, 低于 10% critical), 其余 12 只均分 91.5%
    weights = {"A": 0.085}
    others = 12
    each = 0.915 / others  # ≈ 0.0763, 低于 8% warning
    for i in range(others):
        weights[f"S{i}"] = each
    snap = monitor.update(weights, now=T0)
    # HHI 低, 无行业映射, max_single=8.5% → WARNING (不达 critical 10%)
    assert snap.max_single_weight == pytest.approx(0.085, rel=1e-6)
    assert snap.level is ConcentrationAlertLevel.WARNING


# ── 行业暴露 ──────────────────────────────────────────────────────────────────


def test_industry_aggregation():
    monitor = ConcentrationMonitor()
    weights = {"A": 0.4, "B": 0.3, "C": 0.3}
    mapping = {"A": "银行", "B": "银行", "C": "地产"}
    snap = monitor.update(weights, industry_mapping=mapping, now=T0)
    assert snap.max_industry_name == "银行"
    assert snap.max_industry_weight == pytest.approx(0.7)
    assert snap.industry_weights["银行"] == pytest.approx(0.7)
    assert snap.industry_weights["地产"] == pytest.approx(0.3)


def test_industry_critical_above_30pct():
    """单行业权重 > 30% → CRITICAL。"""
    monitor = ConcentrationMonitor()
    weights = {"A": 0.25, "B": 0.25, "C": 0.25, "D": 0.25}
    mapping = {"A": "银行", "B": "银行", "C": "银行", "D": "地产"}  # 银行 75%
    snap = monitor.update(weights, industry_mapping=mapping, now=T0)
    assert snap.max_industry_weight == pytest.approx(0.75)
    assert snap.level is ConcentrationAlertLevel.CRITICAL


def test_industry_warning_at_24pct():
    """单行业 24% (30%×0.8) → WARNING (前提其他指标不超 critical)。"""
    monitor = ConcentrationMonitor()
    # 5 只, 银行 24%, 其余分散
    weights = {"A": 0.12, "B": 0.12, "C": 0.20, "D": 0.28, "E": 0.28}
    mapping = {"A": "银行", "B": "银行", "C": "地产", "D": "消费", "E": "科技"}
    snap = monitor.update(weights, industry_mapping=mapping, now=T0)
    # 银行 24% → warning; 但 D/E=28% > 8% 单股 warning, 且 D=28% < 30% 行业 limit
    # max_single=28% > 10% → critical. 所以整体 critical.
    # 改测试: 让单股都 < 8% warning
    weights = {f"S{i}": 0.04 for i in range(25)}  # 25 只 4%
    # 6 只归银行 = 24%
    mapping = {f"S{i}": "银行" for i in range(6)}
    for i in range(6, 25):
        mapping[f"S{i}"] = f"行业{i}"
    snap = monitor.update(weights, industry_mapping=mapping, now=T0)
    assert snap.max_industry_weight == pytest.approx(0.24)
    assert snap.level is ConcentrationAlertLevel.WARNING


def test_no_industry_mapping():
    """无行业映射: 跳过行业检查, industry_weights 为空, max_industry_weight=None。"""
    monitor = ConcentrationMonitor()
    snap = monitor.update({"A": 0.5, "B": 0.5}, now=T0)
    assert snap.industry_weights == {}
    assert snap.max_industry_weight is None
    assert snap.max_industry_name is None


# ── 告警事件去抖 ──────────────────────────────────────────────────────────────


def test_alert_emitted_on_level_change():
    monitor = ConcentrationMonitor()
    events: list = []
    monitor.on_concentration_alerted(events.append)
    # NONE → CRITICAL (单只满仓)
    monitor.update({"A": 1.0}, now=T0)
    assert len(events) == 1
    assert events[0].level is ConcentrationAlertLevel.CRITICAL


def test_no_duplicate_alert_on_same_level():
    monitor = ConcentrationMonitor()
    events: list = []
    monitor.on_concentration_alerted(events.append)
    monitor.update({"A": 1.0}, now=T0)  # NONE→CRITICAL
    monitor.update({"B": 1.0}, now=T0)  # CRITICAL→CRITICAL (不重复)
    assert len(events) == 1


def test_alert_on_deescalation():
    monitor = ConcentrationMonitor()
    events: list = []
    monitor.on_concentration_alerted(events.append)
    monitor.update({"A": 1.0}, now=T0)  # CRITICAL
    # 分散到 20 只
    weights = {f"S{i}": 1.0 / 20 for i in range(20)}
    monitor.update(weights, now=T0)  # → NONE
    assert len(events) == 2
    assert events[1].level is ConcentrationAlertLevel.NONE
    assert events[1].previous_level is ConcentrationAlertLevel.CRITICAL


# ── 综合场景 ──────────────────────────────────────────────────────────────────


def test_well_diversified_portfolio_no_alert():
    """充分分散组合 (20 只等权, 多行业) → NONE。"""
    monitor = ConcentrationMonitor()
    weights = {f"S{i}": 1.0 / 20 for i in range(20)}
    mapping = {f"S{i}": f"行业{i % 4}" for i in range(20)}  # 4 行业各 25%
    snap = monitor.update(weights, industry_mapping=mapping, now=T0)
    # 行业 25% < 24%? 不, 25% > 24% → warning. 改 5 行业各 20%
    mapping = {f"S{i}": f"行业{i % 5}" for i in range(20)}  # 5 行业各 20%
    snap = monitor.update(weights, industry_mapping=mapping, now=T0)
    assert snap.level is ConcentrationAlertLevel.NONE
    assert snap.is_diversified


def test_listener_exception_isolated():
    """监听器抛异常不影响监控器。"""
    monitor = ConcentrationMonitor()

    def bad_listener(_):
        raise RuntimeError("boom")

    monitor.on_concentration_alerted(bad_listener)
    # 不应抛异常
    snap = monitor.update({"A": 1.0}, now=T0)
    assert snap.level is ConcentrationAlertLevel.CRITICAL


def test_snapshot_breach_reasons_format():
    monitor = ConcentrationMonitor()
    snap = monitor.update({"A": 1.0}, now=T0)
    assert len(snap.breach_reasons) > 0
    assert all(isinstance(r, str) for r in snap.breach_reasons)
