# [A_test] module_id: MOD-SIG-119 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [BLUEPRINT] MOD-SIG-119 | docs/03_modules/_domain_signal/sector_crowding_launch/blueprint.md
# [MODULE] tests.signal_ashare.test_sector_crowding_launch
# [TTL] permanent
# [DEPENDENCIES] zephyr.signal_ashare.sector_crowding_launch

"""板块拥挤度与启动条件（MOD-SIG-119，B10-01384）施工验证测试。

覆盖：分位计算（空历史/严格小于计数/全下 0.0）、三分量契约与配置边界、
合成拥挤度三档判定（normal/elevated/overheated）、过热预警（>90%分位∧
动量衰减>30%，告警注入不阻断、raised_at 时钟注入）、启动状态机
（IDLE→RS_BREAKOUT→CONFIRMING→LAUNCHED、资金非正回退、RS 失守归 IDLE、
LAUNCHED 滞回）、确定性与 frozen。全程内存合成数据，无 DB/无网络。
"""

from __future__ import annotations

import dataclasses
import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.sector_crowding_launch",
    reason="sector_crowding_launch not importable",
)

from zephyr.signal_ashare.sector_crowding_launch import (  # noqa: E402
    CrowdingAssessment,
    CrowdingComponents,
    CrowdingConfig,
    CrowdingLevel,
    LaunchPhase,
    LaunchStateMachine,
    OverheatWarning,
    SectorCrowdingError,
    SectorCrowdingLauncher,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)

#: 0.00 ~ 0.99 的 100 点历史序列：current=0.9X → 分位 0.9X
_HIST = [0.01 * i for i in range(100)]


def _launcher(alerts: list | None = None, **cfg_kw) -> SectorCrowdingLauncher:
    return SectorCrowdingLauncher(
        config=CrowdingConfig(**cfg_kw) if cfg_kw else None,
        clock=lambda: _T0,
        alert_sink=(lambda w: alerts.append(w)) if alerts is not None else None,
    )


def _assess(launcher: SectorCrowdingLauncher, t: float, m: float, c: float,
            decay: float = 0.0) -> CrowdingAssessment:
    return launcher.assess_crowding(
        turnover_history=_HIST, turnover_current=t,
        margin_history=_HIST, margin_current=m,
        correlation_history=_HIST, correlation_current=c,
        momentum_decay=decay,
    )


class TestPercentile:
    def test_empty_history_raises(self):
        with pytest.raises(SectorCrowdingError):
            SectorCrowdingLauncher.percentile_of([], 0.5)

    def test_basic_percentile(self):
        p = SectorCrowdingLauncher.percentile_of(_HIST, 0.95)
        assert p == pytest.approx(0.95)

    def test_current_below_all_zero(self):
        p = SectorCrowdingLauncher.percentile_of(_HIST, -1.0)
        assert p == 0.0


class TestContracts:
    def test_component_out_of_range(self):
        with pytest.raises(SectorCrowdingError):
            CrowdingComponents(turnover_pct=1.5, margin_pct=0.5, correlation_pct=0.5)

    def test_percentile_threshold_order(self):
        with pytest.raises(SectorCrowdingError):
            CrowdingConfig(elevated_percentile=0.95, overheat_percentile=0.90)

    def test_confirm_days_invalid(self):
        with pytest.raises(SectorCrowdingError):
            CrowdingConfig(confirm_days=0)

    def test_momentum_decay_threshold_range(self):
        with pytest.raises(SectorCrowdingError):
            CrowdingConfig(momentum_decay_threshold=1.5)


class TestCrowdingLevels:
    def test_normal(self):
        r = _assess(_launcher(), 0.50, 0.50, 0.50)
        assert r.composite == pytest.approx(0.50)
        assert r.level is CrowdingLevel.NORMAL
        assert r.overheated is False
        assert r.warning is None

    def test_elevated(self):
        r = _assess(_launcher(), 0.95, 0.85, 0.80)
        assert r.composite == pytest.approx((0.95 + 0.85 + 0.80) / 3.0)
        assert r.level is CrowdingLevel.ELEVATED
        assert r.overheated is False

    def test_overheated(self):
        r = _assess(_launcher(), 0.95, 0.96, 0.97)
        assert r.composite > 0.90
        assert r.level is CrowdingLevel.OVERHEATED
        assert r.overheated is True


class TestOverheatWarning:
    def test_warning_fired_with_alert(self):
        alerts: list[OverheatWarning] = []
        r = _assess(_launcher(alerts), 0.95, 0.96, 0.97, decay=0.40)
        assert r.warning is not None
        assert r.warning.momentum_decay == pytest.approx(0.40)
        assert r.warning.raised_at == _T0
        assert len(alerts) == 1
        assert alerts[0] is r.warning

    def test_no_warning_when_decay_small(self):
        alerts: list[OverheatWarning] = []
        r = _assess(_launcher(alerts), 0.95, 0.96, 0.97, decay=0.20)
        assert r.overheated is True
        assert r.warning is None
        assert alerts == []

    def test_no_warning_when_not_overheated(self):
        r = _assess(_launcher(), 0.85, 0.85, 0.85, decay=0.50)
        assert r.overheated is False
        assert r.warning is None

    def test_alert_sink_exception_swallowed(self):
        def _boom(w):
            raise RuntimeError("boom")
        launcher = SectorCrowdingLauncher(clock=lambda: _T0, alert_sink=_boom)
        r = _assess(launcher, 0.95, 0.96, 0.97, decay=0.40)
        assert r.warning is not None  # 告警失败不阻断


class TestLaunchStateMachine:
    def test_initial_idle(self):
        assert LaunchStateMachine(confirm_days=3).phase is LaunchPhase.IDLE

    def test_rs_breakout_no_capital(self):
        sm = LaunchStateMachine(confirm_days=3)
        phase = sm.step(rs_breakout=True, capital_flow=-1.0)
        assert phase is LaunchPhase.RS_BREAKOUT
        assert sm.streak == 0

    def test_three_day_confirm_to_launched(self):
        sm = LaunchStateMachine(confirm_days=3)
        assert sm.step(rs_breakout=True, capital_flow=100.0) is LaunchPhase.CONFIRMING
        assert sm.step(rs_breakout=True, capital_flow=200.0) is LaunchPhase.CONFIRMING
        assert sm.step(rs_breakout=True, capital_flow=50.0) is LaunchPhase.LAUNCHED

    def test_negative_capital_resets_streak(self):
        sm = LaunchStateMachine(confirm_days=3)
        sm.step(rs_breakout=True, capital_flow=100.0)
        sm.step(rs_breakout=True, capital_flow=100.0)
        assert sm.step(rs_breakout=True, capital_flow=0.0) is LaunchPhase.RS_BREAKOUT
        assert sm.streak == 0
        # 重新计数
        sm.step(rs_breakout=True, capital_flow=1.0)
        sm.step(rs_breakout=True, capital_flow=1.0)
        assert sm.step(rs_breakout=True, capital_flow=1.0) is LaunchPhase.LAUNCHED

    def test_launched_hysteresis_on_capital_dip(self):
        sm = LaunchStateMachine(confirm_days=3)
        for _ in range(3):
            sm.step(rs_breakout=True, capital_flow=100.0)
        assert sm.phase is LaunchPhase.LAUNCHED
        # 资金转负但 RS 未失守 → 保持 LAUNCHED
        assert sm.step(rs_breakout=True, capital_flow=-1.0) is LaunchPhase.LAUNCHED

    def test_rs_lost_resets_to_idle(self):
        sm = LaunchStateMachine(confirm_days=3)
        for _ in range(3):
            sm.step(rs_breakout=True, capital_flow=100.0)
        assert sm.step(rs_breakout=False, capital_flow=100.0) is LaunchPhase.IDLE
        assert sm.streak == 0

    def test_invalid_inputs_raise(self):
        sm = LaunchStateMachine(confirm_days=3)
        with pytest.raises(SectorCrowdingError):
            sm.step(rs_breakout=True, capital_flow=float("nan"))
        with pytest.raises(SectorCrowdingError):
            sm.step(rs_breakout="yes", capital_flow=1.0)  # type: ignore[arg-type]
        with pytest.raises(SectorCrowdingError):
            LaunchStateMachine(confirm_days=0)

    def test_facade_delegates(self):
        launcher = _launcher()
        assert launcher.launch_phase is LaunchPhase.IDLE
        launcher.step_launch(rs_breakout=True, capital_flow=1.0)
        assert launcher.launch_phase is LaunchPhase.CONFIRMING


class TestDeterminism:
    def test_same_sequence_same_phases(self):
        seq = [(True, 100.0), (True, 100.0), (True, -1.0), (True, 100.0)]
        sm1, sm2 = LaunchStateMachine(confirm_days=3), LaunchStateMachine(confirm_days=3)
        for rs, flow in seq:
            assert sm1.step(rs_breakout=rs, capital_flow=flow) == \
                sm2.step(rs_breakout=rs, capital_flow=flow)

    def test_assessment_frozen(self):
        r = _assess(_launcher(), 0.5, 0.5, 0.5)
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.composite = 0.0  # type: ignore[misc]
