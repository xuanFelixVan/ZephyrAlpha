# [BLUEPRINT] MOD-POS-020 | docs/03_modules/_domain_position/blueprint.md | §
# [MODULE] tests.position.test_cold_start_progression
# [DOMAIN] D_POSITION
# [A_module] module_id=MOD-TEST-POS-CS | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""冷启动 T0/T1/T2 渐进建仓评估单元测试（61 号 §3.1）。

覆盖:
  - T0 晋升：divergence < 0.30 + 未风控降级 + 窗满 → PROMOTE T1
  - T0 回退：风控降级 / divergence ≥ 0.30 → ROLLBACK SIMULATION；窗满数据缺失 → ROLLBACK
  - T0 HOLD：窗内观察（days < 5）/ 数据缺失但窗未满
  - T1 晋升：Rolling Sharpe ≥ OOS×0.7 + 未连续亏损超限 → PROMOTE T2
  - T1 回退：Sharpe < 门槛 / 连续 3 日亏损超限 / 窗满数据缺失 → ROLLBACK T0
  - T2 HOLD：无 Decay 告警 + Sharpe 达标 → HOLD（ratio=1.0）
  - T2 回退：Decay 告警 / Sharpe 不达标 → ROLLBACK T1
  - 连续回退：2 次 → ESCALATE_RETIREMENT（61 号 §3.9）
  - retrain_paused：SIMULATION/T0/T1 为 True，T2 为 False
  - 边界：negative days / NaN / divergence <0 → ColdStartProgressionError
"""
from __future__ import annotations

import math

import pytest

from zephyr.position.core.cold_start_progression import (
    ColdStartAction,
    ColdStartEvalInput,
    ColdStartProgressionConfig,
    ColdStartProgressionError,
    ColdStartStage,
    evaluate_cold_start,
)


class TestT0:
    def test_promote_t1(self):
        inp = ColdStartEvalInput(
            stage=ColdStartStage.T0_OBSERVE, days_in_stage=5,
            sim_live_divergence=0.10, risk_downgraded=False,
        )
        r = evaluate_cold_start(inp)
        assert r.action is ColdStartAction.PROMOTE
        assert r.stage is ColdStartStage.T1_SMALL
        assert r.position_ratio == pytest.approx(0.60)
        assert r.retrain_paused is True
        assert r.consecutive_rollbacks == 0

    def test_risk_downgraded_rollback(self):
        inp = ColdStartEvalInput(
            stage=ColdStartStage.T0_OBSERVE, days_in_stage=5,
            sim_live_divergence=0.10, risk_downgraded=True,
        )
        r = evaluate_cold_start(inp)
        assert r.action is ColdStartAction.ROLLBACK
        assert r.stage is ColdStartStage.SIMULATION

    def test_divergence_above_rollback(self):
        inp = ColdStartEvalInput(
            stage=ColdStartStage.T0_OBSERVE, days_in_stage=5,
            sim_live_divergence=0.35, risk_downgraded=False,
        )
        r = evaluate_cold_start(inp)
        assert r.action is ColdStartAction.ROLLBACK

    def test_below_window_hold(self):
        inp = ColdStartEvalInput(
            stage=ColdStartStage.T0_OBSERVE, days_in_stage=3,
            sim_live_divergence=0.10, risk_downgraded=False,
        )
        r = evaluate_cold_start(inp)
        assert r.action is ColdStartAction.HOLD
        assert r.stage is ColdStartStage.T0_OBSERVE

    def test_missing_data_window_not_full_hold(self):
        """数据缺失但窗未满 → HOLD 观察。"""
        inp = ColdStartEvalInput(
            stage=ColdStartStage.T0_OBSERVE, days_in_stage=6, sim_live_divergence=None,
        )
        r = evaluate_cold_start(inp)
        assert r.action is ColdStartAction.HOLD

    def test_missing_data_window_full_rollback(self):
        """窗满（max_days=10）仍无数据 → 回退。"""
        inp = ColdStartEvalInput(
            stage=ColdStartStage.T0_OBSERVE, days_in_stage=10, sim_live_divergence=None,
        )
        r = evaluate_cold_start(inp)
        assert r.action is ColdStartAction.ROLLBACK


class TestT1:
    def test_promote_t2(self):
        inp = ColdStartEvalInput(
            stage=ColdStartStage.T1_SMALL, days_in_stage=10,
            rolling_sharpe=1.4, oos_sharpe=2.0,
            consecutive_loss_days=0,
        )
        r = evaluate_cold_start(inp)
        assert r.action is ColdStartAction.PROMOTE
        assert r.stage is ColdStartStage.T2_FULL
        assert r.position_ratio == pytest.approx(1.0)
        assert r.retrain_paused is False

    def test_sharpe_below_rollback(self):
        """Rolling Sharpe < OOS×0.7 → 回退 T0。"""
        inp = ColdStartEvalInput(
            stage=ColdStartStage.T1_SMALL, days_in_stage=10,
            rolling_sharpe=0.5, oos_sharpe=2.0,
        )
        r = evaluate_cold_start(inp)
        assert r.action is ColdStartAction.ROLLBACK
        assert r.stage is ColdStartStage.T0_OBSERVE

    def test_loss_days_exceeded_rollback(self):
        inp = ColdStartEvalInput(
            stage=ColdStartStage.T1_SMALL, days_in_stage=10,
            rolling_sharpe=1.4, oos_sharpe=2.0,
            consecutive_loss_days=3,
        )
        r = evaluate_cold_start(inp)
        assert r.action is ColdStartAction.ROLLBACK

    def test_below_window_hold(self):
        inp = ColdStartEvalInput(
            stage=ColdStartStage.T1_SMALL, days_in_stage=5,
            rolling_sharpe=1.4, oos_sharpe=2.0,
        )
        r = evaluate_cold_start(inp)
        assert r.action is ColdStartAction.HOLD


class TestT2:
    def test_hold_healthy(self):
        inp = ColdStartEvalInput(
            stage=ColdStartStage.T2_FULL, days_in_stage=30,
            rolling_sharpe=1.8, oos_sharpe=2.0,
            decay_alert_active=False,
        )
        r = evaluate_cold_start(inp)
        assert r.action is ColdStartAction.HOLD
        assert r.stage is ColdStartStage.T2_FULL

    def test_decay_alert_rollback(self):
        inp = ColdStartEvalInput(
            stage=ColdStartStage.T2_FULL, days_in_stage=30,
            rolling_sharpe=1.8, oos_sharpe=2.0,
            decay_alert_active=True,
        )
        r = evaluate_cold_start(inp)
        assert r.action is ColdStartAction.ROLLBACK
        assert r.stage is ColdStartStage.T1_SMALL

    def test_sharpe_below_rollback(self):
        """Sharpe < OOS×0.85 → 回退 T1。"""
        inp = ColdStartEvalInput(
            stage=ColdStartStage.T2_FULL, days_in_stage=30,
            rolling_sharpe=1.6, oos_sharpe=2.0,
            decay_alert_active=False,
        )
        r = evaluate_cold_start(inp)
        assert r.action is ColdStartAction.ROLLBACK

    def test_missing_data_t2_hold(self):
        """T2 数据缺失 → 不回退（T2 是常规阶段，无证据不降级）。"""
        inp = ColdStartEvalInput(stage=ColdStartStage.T2_FULL, days_in_stage=30)
        r = evaluate_cold_start(inp)
        assert r.action is ColdStartAction.HOLD
        assert r.stage is ColdStartStage.T2_FULL


class TestEscalation:
    def test_consecutive_rollbacks_2(self):
        """连续 2 次回退 → ESCALATE_RETIREMENT。"""
        inp = ColdStartEvalInput(
            stage=ColdStartStage.T1_SMALL, days_in_stage=10,
            rolling_sharpe=0.5, oos_sharpe=2.0,
            consecutive_rollbacks=1,
        )
        r = evaluate_cold_start(inp)
        assert r.action is ColdStartAction.ESCALATE_RETIREMENT
        assert r.consecutive_rollbacks == 2

    def test_t0_to_simulation_first_rollback(self):
        inp = ColdStartEvalInput(
            stage=ColdStartStage.T0_OBSERVE, days_in_stage=5,
            sim_live_divergence=0.35, risk_downgraded=False,
            consecutive_rollbacks=0,
        )
        r = evaluate_cold_start(inp)
        assert r.action is ColdStartAction.ROLLBACK
        assert r.consecutive_rollbacks == 1


class TestInvalidInput:
    @pytest.mark.parametrize("kw", [{"days_in_stage": -1}, {"consecutive_loss_days": -1}, {"consecutive_rollbacks": -1}])
    def test_negative_values(self, kw):
        base = dict(stage=ColdStartStage.T0_OBSERVE, days_in_stage=5)
        base.update(kw)
        with pytest.raises(ColdStartProgressionError):
            evaluate_cold_start(ColdStartEvalInput(**base))

    def test_nan_divergence(self):
        with pytest.raises(ColdStartProgressionError):
            evaluate_cold_start(ColdStartEvalInput(
                stage=ColdStartStage.T0_OBSERVE, days_in_stage=5,
                sim_live_divergence=float("nan"),
            ))

    def test_negative_divergence(self):
        with pytest.raises(ColdStartProgressionError):
            evaluate_cold_start(ColdStartEvalInput(
                stage=ColdStartStage.T0_OBSERVE, days_in_stage=5,
                sim_live_divergence=-0.1,
            ))

    def test_inf_sharpe(self):
        with pytest.raises(ColdStartProgressionError):
            evaluate_cold_start(ColdStartEvalInput(
                stage=ColdStartStage.T1_SMALL, days_in_stage=10,
                rolling_sharpe=math.inf, oos_sharpe=2.0,
            ))
