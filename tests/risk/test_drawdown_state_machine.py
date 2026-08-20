# [A_test] module_id: MOD-RK-DSM | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] 35_drawdown_protocol_impl | §3.11/§3.14/§3.20/§6.6
# [MODULE] tests.risk.test_drawdown_state_machine
# [INVARIANTS] 升级单调取最严; 降级三重守卫不可跳级; KILL仅人工复位; RECOVERY阶梯毕业准则; 持久化往返一致+损坏fail-closed
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] no exceptions raised from tests
# [TESTS] tests/risk/test_drawdown_state_machine.py
# [TTL] task_bound
"""DrawdownStateMachine 测试（35 号 §6.6：§3.11 状态机 + §3.20 hysteresis + §3.14 复位守卫）。"""

from __future__ import annotations

import json
from datetime import date, timedelta

import pytest

from zephyr.risk.core.drawdown_state_machine import (
    DRAWDOWN_STATE_NAMESPACE,
    DrawdownState,
    DrawdownStateMachine,
    DrawdownStateMachineConfig,
    InvalidDrawdownStateError,
    RefuseResetError,
    ResetConfirmation,
)
from zephyr.shared.state_store import JsonStateStore, StateCorruptError

D0 = date(2026, 8, 3)  # 周一


def _day(n: int) -> date:
    return D0 + timedelta(days=n)


def _good_trades(n: int = 5) -> list[dict]:
    """毕业准则全达标交易序列：连盈 + 均 0.5R + 全合规。"""
    return [{"pnl": 100.0 + i, "r_multiple": 0.5, "rule_followed": True} for i in range(n)]


def _run_days(sm: DrawdownStateMachine, start: int, days: int, **kwargs) -> None:
    for i in range(start, start + days):
        sm.evaluate(trade_date=_day(i), **kwargs)


# ── 升级（单调取最严，§3.11）──


class TestEscalation:
    def test_normal_to_warn_by_drawdown(self):
        sm = DrawdownStateMachine()
        t = sm.evaluate(trade_date=_day(0), drawdown_pct=-0.06)
        assert sm.current is DrawdownState.WARN
        assert t is not None and t.to_state is DrawdownState.WARN
        assert sm.position_cap == 0.8

    def test_normal_to_danger_by_var(self):
        sm = DrawdownStateMachine()
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.01, var_95=0.05)
        assert sm.current is DrawdownState.DANGER

    def test_direct_jump_normal_to_crisis(self):
        """取最严：单日深回撤 NORMAL 直接 CRISIS（不逐级）。"""
        sm = DrawdownStateMachine()
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.16)
        assert sm.current is DrawdownState.CRISIS
        assert sm.position_cap == 0.3
        assert sm.defensive_only is True

    def test_kill_by_drawdown_25(self):
        sm = DrawdownStateMachine()
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.26)
        assert sm.current is DrawdownState.KILL
        assert sm.position_cap == 0.0
        assert sm.kill_switch_closed is True

    def test_kill_by_cvar(self):
        sm = DrawdownStateMachine()
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.03, var_95=0.03, cvar_95=0.11)
        assert sm.current is DrawdownState.KILL

    def test_kill_by_black_swan(self):
        sm = DrawdownStateMachine()
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.01, black_swan_systemic=True)
        assert sm.current is DrawdownState.KILL

    def test_boundary_dd_exactly_5pct_not_warn(self):
        """边界：dd == 5% 不触发（严格大于）。"""
        sm = DrawdownStateMachine()
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.05)
        assert sm.current is DrawdownState.NORMAL


# ── hysteresis 降级（§3.20 三重守卫）──


class TestHysteresisDeescalation:
    def _enter_warn(self, sm: DrawdownStateMachine) -> None:
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.06)  # → WARN

    def test_warn_to_normal_full_path(self):
        """WARN→NORMAL：min_hold 5 日 + dd<2.5% 持续 3 日 + var<2% → 降级。"""
        sm = DrawdownStateMachine()
        self._enter_warn(sm)
        for i in range(1, 6):  # day1..day5 dd 回到 2%（< 2.5% 半阈值）
            t = sm.evaluate(trade_date=_day(i), drawdown_pct=-0.02, var_95=0.01)
        assert sm.current is DrawdownState.NORMAL
        assert t is not None and t.reason.startswith("hysteresis_recovery")
        assert sm.position_cap == 1.0

    def test_min_hold_blocks_early_deescalation(self):
        """min_hold 不足（< 5 日）即使 dd 已回半阈值下也不降级。"""
        sm = DrawdownStateMachine()
        self._enter_warn(sm)
        for i in range(1, 4):  # 仅 3 日
            sm.evaluate(trade_date=_day(i), drawdown_pct=-0.01, var_95=0.01)
        assert sm.current is DrawdownState.WARN

    def test_sustained_window_blocks_thrashing(self):
        """持续窗：窗口尾部一日 dd ≥ 2.5% → 不降级；连续 3 日干净后才降级。"""
        sm = DrawdownStateMachine()
        self._enter_warn(sm)
        dds = [-0.02, -0.02, -0.02, -0.02, -0.03]  # day5 dd=3% 破坏窗口尾部
        for i, dd in enumerate(dds, start=1):
            sm.evaluate(trade_date=_day(i), drawdown_pct=dd, var_95=0.01)
        assert sm.current is DrawdownState.WARN  # last3=[2%,2%,3%] 不持续
        sm.evaluate(trade_date=_day(6), drawdown_pct=-0.02, var_95=0.01)
        assert sm.current is DrawdownState.WARN  # last3=[2%,3%,2%] 仍不持续
        sm.evaluate(trade_date=_day(7), drawdown_pct=-0.02, var_95=0.01)
        assert sm.current is DrawdownState.WARN  # last3=[3%,2%,2%] 仍不持续
        t = sm.evaluate(trade_date=_day(8), drawdown_pct=-0.02, var_95=0.01)
        assert sm.current is DrawdownState.NORMAL  # last3=[2%,2%,2%] 持续 → 降级
        assert t is not None

    def test_var_cross_check_blocks_deescalation(self):
        """VaR 交叉验证：dd 回落但 var 仍 ≥ 2% → 假恢复不降级。"""
        sm = DrawdownStateMachine()
        self._enter_warn(sm)
        for i in range(1, 7):
            sm.evaluate(trade_date=_day(i), drawdown_pct=-0.02, var_95=0.025)
        assert sm.current is DrawdownState.WARN

    def test_crisis_cannot_skip_to_normal(self):
        """不可跳级：CRISIS 满足条件只降 DANGER（不能直接回 NORMAL）。"""
        cfg = DrawdownStateMachineConfig(min_hold_crisis=2, sustained_crisis=2)
        sm = DrawdownStateMachine(config=cfg)
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.16)  # → CRISIS
        sm.evaluate(trade_date=_day(1), drawdown_pct=-0.06, var_95=0.01)
        t = sm.evaluate(trade_date=_day(2), drawdown_pct=-0.06, var_95=0.01)
        assert sm.current is DrawdownState.DANGER
        assert t is not None and t.from_state is DrawdownState.CRISIS

    def test_half_threshold_gap(self):
        """半阈值缓冲带：dd 在 2.5%-5% 间波动保持 WARN（不升级也不降级）。"""
        sm = DrawdownStateMachine()
        self._enter_warn(sm)
        for i in range(1, 8):
            sm.evaluate(trade_date=_day(i), drawdown_pct=-0.04, var_95=0.01)
        assert sm.current is DrawdownState.WARN  # 4% ≥ 2.5% 半阈值，不降级


# ── 持久化（§6.6 跨重启记忆）──


class TestPersistence:
    def test_roundtrip_survives_restart(self, tmp_path):
        store = JsonStateStore(tmp_path)
        sm = DrawdownStateMachine(store)
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.06)  # → WARN
        sm.evaluate(trade_date=_day(1), drawdown_pct=-0.04)
        # 模拟重启：新实例从 store 恢复
        sm2 = DrawdownStateMachine(store)
        snap = sm2.load_or_none()
        assert snap is not None
        assert sm2.current is DrawdownState.WARN
        assert sm2.days_in_state == 1
        assert list(snap.dd_history) == [0.06, 0.04]
        assert snap.as_of_date == _day(1).isoformat()

    def test_cold_start_returns_none(self, tmp_path):
        sm = DrawdownStateMachine(JsonStateStore(tmp_path))
        assert sm.load_or_none() is None
        assert sm.current is DrawdownState.NORMAL  # 保守默认

    def test_corrupt_state_fail_closed(self, tmp_path):
        store = JsonStateStore(tmp_path)
        (tmp_path / f"{DRAWDOWN_STATE_NAMESPACE}.json").write_text("{not json", encoding="utf-8")
        sm = DrawdownStateMachine(store)
        with pytest.raises(StateCorruptError):
            sm.load_or_none()

    def test_invalid_field_raises(self, tmp_path):
        store = JsonStateStore(tmp_path)
        store.save(DRAWDOWN_STATE_NAMESPACE, {"current": "BOGUS"})
        sm = DrawdownStateMachine(store)
        with pytest.raises(InvalidDrawdownStateError):
            sm.load_or_none()

    def test_no_store_memory_mode(self):
        sm = DrawdownStateMachine()  # store=None 纯内存
        assert sm.load_or_none() is None
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.06)
        sm.persist()  # 不抛错


# ── KILL 人工复位（§3.14/§3.7）──


class TestManualReset:
    def _enter_kill(self, sm: DrawdownStateMachine) -> None:
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.30)

    def _confirmation(self, **overrides) -> ResetConfirmation:
        base = {
            "confirmed_by": "owner",
            "override_reason": "root_cause_analyzed_and_fixed",
            "holdings_verified_zero": True,
            "orders_cancelled_verified": True,
            "new_open_locked_verified": True,
        }
        base.update(overrides)
        return ResetConfirmation(**base)

    def test_kill_no_auto_exit(self):
        """KILL 态 dd 回落也不自动恢复（§3.7 不可覆盖）。"""
        sm = DrawdownStateMachine()
        self._enter_kill(sm)
        t = sm.evaluate(trade_date=_day(1), drawdown_pct=-0.01)
        assert sm.current is DrawdownState.KILL
        assert t is None

    def test_reset_happy_path(self, tmp_path):
        sm = DrawdownStateMachine(JsonStateStore(tmp_path))
        self._enter_kill(sm)
        t = sm.request_manual_reset(self._confirmation(), trade_date=_day(1))
        assert sm.current is DrawdownState.RECOVERY
        assert sm.recovery_step == 0
        assert t.to_state is DrawdownState.RECOVERY
        assert sm.position_cap == 0.25
        assert sm.recovery_factor == 0.25

    @pytest.mark.parametrize(
        "missing",
        ["holdings_verified_zero", "orders_cancelled_verified", "new_open_locked_verified"],
    )
    def test_reset_missing_confirmation_refused(self, missing):
        sm = DrawdownStateMachine()
        self._enter_kill(sm)
        with pytest.raises(RefuseResetError):
            sm.request_manual_reset(self._confirmation(**{missing: False}), trade_date=_day(1))

    def test_reset_only_from_kill(self):
        sm = DrawdownStateMachine()  # NORMAL
        with pytest.raises(RefuseResetError):
            sm.request_manual_reset(self._confirmation(), trade_date=_day(0))

    def test_cooldown_blocks_quick_rereset(self, tmp_path):
        sm = DrawdownStateMachine(JsonStateStore(tmp_path))
        self._enter_kill(sm)
        sm.request_manual_reset(self._confirmation(), trade_date=_day(1))
        # 再次 KILL（RECOVERY step0 dd>15% → KILL）
        sm.evaluate(trade_date=_day(2), drawdown_pct=-0.30)
        assert sm.current is DrawdownState.KILL
        with pytest.raises(RefuseResetError, match="冷却期"):
            sm.request_manual_reset(self._confirmation(), trade_date=_day(2))

    def test_window_limit_blocks_4th_reset(self, tmp_path):
        sm = DrawdownStateMachine(JsonStateStore(tmp_path))
        for k in range(3):  # 20 日窗内 3 次复位（冷却 3 日间隔 4 日）
            base = k * 4
            sm.evaluate(trade_date=_day(base), drawdown_pct=-0.30)
            sm.request_manual_reset(self._confirmation(), trade_date=_day(base + 1))
        sm.evaluate(trade_date=_day(12), drawdown_pct=-0.30)
        assert sm.current is DrawdownState.KILL
        with pytest.raises(RefuseResetError, match="超上限"):
            sm.request_manual_reset(self._confirmation(), trade_date=_day(13))

    def test_permanent_lock_at_5_total(self, tmp_path):
        store = JsonStateStore(tmp_path)
        sm = DrawdownStateMachine(store)
        # 直接注入 5 次复位历史（跨 20 日窗避免窗口守卫先触发）
        store.save(
            "drawdown_reset_history",
            {
                "total_resets": 5,
                "records": [{"date": _day(i * 30).isoformat(), "confirmed_by": "o", "reason": "r"} for i in range(5)],
            },
        )
        self._enter_kill(sm)
        with pytest.raises(RefuseResetError, match="永久锁定"):
            sm.request_manual_reset(self._confirmation(), trade_date=_day(200))


# ── RECOVERY 阶梯机（§3.14/§3.20）──


class TestRecoveryLadder:
    def _enter_recovery(self, sm: DrawdownStateMachine) -> None:
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.30)  # → KILL
        sm.request_manual_reset(
            ResetConfirmation(
                confirmed_by="owner",
                override_reason="fixed",
                holdings_verified_zero=True,
                orders_cancelled_verified=True,
                new_open_locked_verified=True,
            ),
            trade_date=_day(1),
        )

    def test_step_up_requires_all_gates(self):
        """step 0→1：min_hold 5 日 + recovered≥50% + 毕业准则，缺一不晋升。"""
        sm = DrawdownStateMachine()
        self._enter_recovery(sm)
        # min_hold 不足
        for i in range(2, 5):
            sm.evaluate(
                trade_date=_day(i),
                drawdown_pct=-0.02,
                recovered_pct=0.6,
                strategy_pnls=_good_trades(),
            )
        assert sm.recovery_step == 0
        # 毕业准则不满足（亏损交易）
        bad = [{"pnl": -50.0, "r_multiple": 0.5, "rule_followed": True}] * 5
        sm.evaluate(trade_date=_day(6), drawdown_pct=-0.02, recovered_pct=0.6, strategy_pnls=bad)
        assert sm.recovery_step == 0
        # 全达标 → step 1
        t = sm.evaluate(
            trade_date=_day(7),
            drawdown_pct=-0.02,
            recovered_pct=0.6,
            strategy_pnls=_good_trades(),
        )
        assert sm.recovery_step == 1
        assert t is not None and "step_up" in t.reason
        assert sm.recovery_factor == 0.5

    def test_full_ladder_to_normal(self):
        """0→1→2→NORMAL 全阶梯（recovered 50%/75%/100% + 毕业准则）。"""
        sm = DrawdownStateMachine()
        self._enter_recovery(sm)
        for step, (rec, days) in enumerate([(0.6, 5), (0.8, 5), (1.0, 5)]):
            start = 2 + step * 6
            for i in range(start, start + days):
                t = sm.evaluate(
                    trade_date=_day(i),
                    drawdown_pct=-0.01,
                    recovered_pct=rec,
                    strategy_pnls=_good_trades(),
                )
        assert sm.current is DrawdownState.NORMAL
        assert t is not None and t.reason == "recovery_graduated_new_high"
        assert sm.position_cap == 1.0

    def test_retreat_on_dd_15_step_exhaustion_to_kill(self):
        """dd>15%：阶梯逐步回退（2→1），step0 再加深 → KILL（§3.11 分级保护）。"""
        sm = DrawdownStateMachine()
        self._enter_recovery(sm)
        sm._recovery_step = 2  # 直接置阶梯（测试聚焦回退逻辑）
        t = sm.evaluate(trade_date=_day(2), drawdown_pct=-0.16)
        assert sm.current is DrawdownState.RECOVERY and sm.recovery_step == 1
        assert t is not None and "retreat" in t.reason
        # step 0 再 dd>15% → KILL
        sm._recovery_step = 0
        sm.evaluate(trade_date=_day(3), drawdown_pct=-0.16)
        assert sm.current is DrawdownState.KILL

    def test_retreat_on_dd_10_only_when_step_positive(self):
        """dd 10-15%：step>0 回退；step=0 不回退（空档由 freeze 兜底）。"""
        sm = DrawdownStateMachine()
        self._enter_recovery(sm)
        sm._recovery_step = 1
        sm.evaluate(trade_date=_day(2), drawdown_pct=-0.12)
        assert sm.recovery_step == 0
        # step=0 同区间：不退不 KILL，触发 freeze
        t = sm.evaluate(trade_date=_day(3), drawdown_pct=-0.12)
        assert sm.current is DrawdownState.RECOVERY and sm.recovery_step == 0
        assert t is None
        assert sm._freeze_days_remaining == 5

    def test_freeze_blocks_step_up_5_days(self):
        """dd>5% 冻结 5 日：冻结期内达标也不晋升，第 6 日解禁。"""
        sm = DrawdownStateMachine()
        self._enter_recovery(sm)
        sm.evaluate(trade_date=_day(2), drawdown_pct=-0.07)  # → freeze 5 日
        assert sm._freeze_days_remaining == 5
        for i in range(3, 8):  # day3..day7 冻结期（5 日）达标不晋升
            sm.evaluate(
                trade_date=_day(i),
                drawdown_pct=-0.02,
                recovered_pct=0.6,
                strategy_pnls=_good_trades(),
            )
            assert sm.recovery_step == 0
        t = sm.evaluate(  # day8 解禁 + 全达标 → step 1
            trade_date=_day(8),
            drawdown_pct=-0.02,
            recovered_pct=0.6,
            strategy_pnls=_good_trades(),
        )
        assert sm.recovery_step == 1
        assert t is not None


# ── 毕业准则单元（§3.20 四准则）──


class TestGraduationCriteria:
    def setup_method(self):
        self.sm = DrawdownStateMachine()

    def test_none_or_insufficient_samples(self):
        assert self.sm.graduation_criteria_met(None) is False
        assert self.sm.graduation_criteria_met(_good_trades(2)) is False

    def test_profit_streak_required(self):
        trades = _good_trades()
        trades[-1] = {"pnl": -1.0, "r_multiple": 0.5, "rule_followed": True}
        assert self.sm.graduation_criteria_met(trades) is False

    def test_expectancy_r_required(self):
        trades = [{"pnl": 100.0, "r_multiple": 0.1, "rule_followed": True} for _ in range(5)]
        assert self.sm.graduation_criteria_met(trades) is False  # 均 0.1R < 0.3R

    def test_rule_compliance_required(self):
        trades = _good_trades(10)
        for t in trades[:3]:  # 7/10 合规 = 70% < 80%
            t["rule_followed"] = False
        assert self.sm.graduation_criteria_met(trades) is False

    def test_max_single_loss_required(self):
        trades = _good_trades(5)
        trades[0] = {"pnl": -500.0, "r_multiple": -1.5, "rule_followed": True}
        assert self.sm.graduation_criteria_met(trades) is False  # 单笔 -1.5R 超 1.2R

    def test_boundary_loss_exactly_1_2r_passes(self):
        """边界：单笔恰 -1.2R 不算超阈（严格小于才违例），其余准则达标即毕业。"""
        trades = _good_trades(10)
        trades[0] = {"pnl": -400.0, "r_multiple": -1.2, "rule_followed": True}
        # 期望 = (-1.2 + 9×0.5)/10 = 0.33 ≥ 0.3R；合规 10/10；近 3 笔连盈
        assert self.sm.graduation_criteria_met(trades) is True


# ── 输入校验与同日幂等 ──


class TestInputValidation:
    def test_date_regression_raises(self):
        sm = DrawdownStateMachine()
        sm.evaluate(trade_date=_day(2), drawdown_pct=-0.01)
        with pytest.raises(InvalidDrawdownStateError):
            sm.evaluate(trade_date=_day(1), drawdown_pct=-0.01)

    def test_same_day_idempotent(self):
        """同日重复 evaluate：不重复计日，dd_history 更新末位。"""
        sm = DrawdownStateMachine()
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.03)
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.04)
        assert sm.days_in_state == 1
        assert sm._dd_history == [0.04]

    def test_negative_var_raises(self):
        sm = DrawdownStateMachine()
        with pytest.raises(InvalidDrawdownStateError):
            sm.evaluate(trade_date=_day(0), drawdown_pct=-0.01, var_95=-0.01)

    def test_recovered_pct_out_of_range_raises(self):
        sm = DrawdownStateMachine()
        with pytest.raises(InvalidDrawdownStateError):
            sm.evaluate(trade_date=_day(0), drawdown_pct=-0.01, recovered_pct=1.5)

    def test_config_threshold_order_validated(self):
        with pytest.raises(InvalidDrawdownStateError):
            DrawdownStateMachineConfig(warn_dd=0.10, danger_dd=0.05)

    def test_json_serialization_of_persisted_state(self, tmp_path):
        """持久化载荷可 JSON 序列化（JsonStateStore 契约）。"""
        store = JsonStateStore(tmp_path)
        sm = DrawdownStateMachine(store)
        sm.evaluate(trade_date=_day(0), drawdown_pct=-0.06)
        raw = json.loads((tmp_path / f"{DRAWDOWN_STATE_NAMESPACE}.json").read_text(encoding="utf-8"))
        assert raw["current"] == "WARN"
        assert raw["last_transition"]["from"] == "NORMAL"
