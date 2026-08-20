# [BLUEPRINT] MOD-FEEDBACK_LOOP | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] tests.risk.test_var_breach_state_machine
# [DOMAIN] D_RISK
# [TESTS] zephyr.risk.core.var_breach_state_machine; zephyr.position.core.drawdown_controller(var_breach_state 折扣)
# [COVERAGE] 36号 §3.15 状态机迁移/反弹重置/复燃/边界相等 + 跨重启持久化 + ×0.8/×0.9 乘性折扣接入 evaluate
# [MATURITY] evolving
# [TTL] task_bound

"""VarBreachStateMachine + drawdown_controller 乘性折扣测试 (36号 §3.15)。

实证目标:
    1. 迁移规则: NORMAL→BREACHED(>breach) / BREACHED→RECOVERY(连续3日<recovery)
       / RECOVERY→NORMAL(连续5日,同一计数器续计) / RECOVERY复燃→BREACHED(清零)
    2. 中间带 (recovery≤var≤breach): 停留原态 + 计数重置
    3. 边界相等: var==breach 不进入 BREACHED; var==recovery 不计数
    4. 持久化: save/load 往返一致 / 缺失→冷启动 NORMAL / 损坏→StateCorruptError
    5. evaluate(var_breach_state=): BREACHED×0.8 / RECOVERY×0.9 / NORMAL×1.0 /
       None 零回归 / 未知值抛错 / 与黑天鹅取 min / 下限 max(0.0)
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from zephyr.position.core.drawdown_controller import (
    BlackSwanMode,
    BlackSwanSignal,
    DrawdownController,
    DrawdownInfo,
    InvalidDrawdownControlError,
    VarCvarMetrics,
)
from zephyr.risk.core.var_breach_state_machine import (
    InvalidVarBreachConfigError,
    VarBreachConfig,
    VarBreachState,
    VarBreachStateMachine,
    VarBreachStateSnapshot,
)
from zephyr.shared.state_store import JsonStateStore, StateCorruptError

D0 = date(2026, 8, 20)
# 默认配置: breach=0.02, recovery=0.016, 3日→RECOVERY, 5日→NORMAL
BREACH = 0.02
RECOVERY = 0.016


def _days(n: int) -> list[date]:
    return [D0 + timedelta(days=i) for i in range(n)]


# ── 配置校验 ──────────────────────────────────────────────────────────────────


class TestConfig:
    def test_default_thresholds(self) -> None:
        cfg = VarBreachConfig()
        assert cfg.recovery_threshold == pytest.approx(0.016)

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"breach_threshold": 0.0},
            {"breach_threshold": -0.01},
            {"recovery_threshold_ratio": 0.0},
            {"recovery_threshold_ratio": 1.0},
            {"days_to_recovery": 0},
            {"days_to_recovery": 4, "days_to_normal": 3},  # normal < recovery 非法(续计口径)
        ],
    )
    def test_invalid_config_rejected(self, kwargs: dict) -> None:
        with pytest.raises(InvalidVarBreachConfigError):
            VarBreachConfig(**kwargs)

    def test_negative_var_rejected(self) -> None:
        m = VarBreachStateMachine()
        with pytest.raises(InvalidVarBreachConfigError):
            m.transition(-0.001)


# ── 迁移规则 ──────────────────────────────────────────────────────────────────


class TestTransitions:
    def test_normal_stays_below_breach(self) -> None:
        m = VarBreachStateMachine()
        assert m.transition(BREACH, D0) is VarBreachState.NORMAL  # 边界相等不进入
        assert m.transition(0.019, D0) is VarBreachState.NORMAL

    def test_normal_to_breached_records_date(self) -> None:
        m = VarBreachStateMachine()
        assert m.transition(0.021, D0) is VarBreachState.BREACHED
        assert m.breach_date == D0.isoformat()
        assert m.consecutive_days_below_recovery == 0

    def test_breached_to_recovery_needs_3_consecutive(self) -> None:
        m = VarBreachStateMachine()
        d = _days(5)
        m.transition(0.021, d[0])
        assert m.transition(0.010, d[1]) is VarBreachState.BREACHED  # 1日
        assert m.transition(0.010, d[2]) is VarBreachState.BREACHED  # 2日
        assert m.transition(0.010, d[3]) is VarBreachState.RECOVERY  # 3日 → RECOVERY
        assert m.consecutive_days_below_recovery == 3

    def test_rebound_resets_counter(self) -> None:
        """期间反弹 (中间带或再超 breach) 计数重置 (§3.15)。"""
        m = VarBreachStateMachine()
        d = _days(8)
        m.transition(0.021, d[0])
        m.transition(0.010, d[1])  # 1日
        m.transition(0.010, d[2])  # 2日
        assert m.transition(0.018, d[3]) is VarBreachState.BREACHED  # 中间带反弹 → 重置
        assert m.consecutive_days_below_recovery == 0
        m.transition(0.010, d[4])  # 重新 1日
        m.transition(0.025, d[5])  # 再超 breach → 重置 (仍 BREACHED)
        assert m.consecutive_days_below_recovery == 0
        m.transition(0.010, d[6])
        m.transition(0.010, d[7])
        assert m.state is VarBreachState.BREACHED  # 仅 2 日, 未到 3

    def test_recovery_to_normal_needs_5_continuous(self) -> None:
        """RECOVERY→NORMAL 同一计数器续计 ≥5 (3日进 RECOVERY 后再 2 日)。"""
        m = VarBreachStateMachine()
        d = _days(6)
        m.transition(0.021, d[0])
        for i in range(1, 4):
            m.transition(0.010, d[i])  # 3日 → RECOVERY
        assert m.state is VarBreachState.RECOVERY
        assert m.transition(0.010, d[4]) is VarBreachState.RECOVERY  # 4日
        assert m.transition(0.010, d[5]) is VarBreachState.NORMAL  # 5日 → NORMAL
        assert m.breach_date is None
        assert m.consecutive_days_below_recovery == 0

    def test_recovery_relapse_back_to_breached(self) -> None:
        """RECOVERY 中 VaR 再超 breach_threshold → 回 BREACHED (复燃, 计数清零)。"""
        m = VarBreachStateMachine()
        d = _days(6)
        m.transition(0.021, d[0])
        for i in range(1, 4):
            m.transition(0.010, d[i])
        assert m.state is VarBreachState.RECOVERY
        assert m.transition(0.025, d[4]) is VarBreachState.BREACHED
        assert m.breach_date == d[4].isoformat()
        assert m.consecutive_days_below_recovery == 0

    def test_recovery_middle_band_stays(self) -> None:
        """RECOVERY 中中间带停留 + 计数重置。"""
        m = VarBreachStateMachine()
        d = _days(8)
        m.transition(0.021, d[0])
        for i in range(1, 4):
            m.transition(0.010, d[i])
        assert m.transition(0.018, d[4]) is VarBreachState.RECOVERY  # 中间带停留
        assert m.consecutive_days_below_recovery == 0
        # 重新计满 5 日才回 NORMAL
        for i in range(5, 8):
            m.transition(0.010, d[i])
        assert m.state is VarBreachState.RECOVERY  # 仅 3 日

    def test_recovery_boundary_equality_no_count(self) -> None:
        """var == recovery_threshold 边界相等不计数 (严格 < 口径)。"""
        m = VarBreachStateMachine()
        d = _days(5)
        m.transition(0.021, d[0])
        for i in range(1, 5):
            m.transition(RECOVERY, d[i])
        assert m.state is VarBreachState.BREACHED
        assert m.consecutive_days_below_recovery == 0


# ── 乘数 ──────────────────────────────────────────────────────────────────────


class TestMultiplier:
    def test_state_multipliers(self) -> None:
        assert VarBreachState.NORMAL.position_cap_multiplier == 1.0
        assert VarBreachState.BREACHED.position_cap_multiplier == 0.8
        assert VarBreachState.RECOVERY.position_cap_multiplier == 0.9

    def test_machine_multiplier_follows_state(self) -> None:
        m = VarBreachStateMachine()
        assert m.position_cap_multiplier == 1.0
        m.transition(0.021, D0)
        assert m.position_cap_multiplier == 0.8


# ── 持久化 ────────────────────────────────────────────────────────────────────


class TestPersistence:
    def test_save_load_roundtrip(self, tmp_path) -> None:
        store = JsonStateStore(tmp_path)
        m = VarBreachStateMachine()
        d = _days(3)
        m.transition(0.021, d[0])
        m.transition(0.010, d[1])
        m.save(store)
        loaded = VarBreachStateMachine.load(store)
        assert loaded.state is VarBreachState.BREACHED
        assert loaded.breach_date == d[0].isoformat()
        assert loaded.consecutive_days_below_recovery == 1

    def test_load_missing_cold_start_normal(self, tmp_path) -> None:
        store = JsonStateStore(tmp_path)
        loaded = VarBreachStateMachine.load(store)
        assert loaded.state is VarBreachState.NORMAL  # 不假设上次在 BREACHED
        assert loaded.breach_date is None

    def test_load_corrupt_raises(self, tmp_path) -> None:
        store = JsonStateStore(tmp_path)
        (tmp_path / "var_breach_state.json").write_text("{not json", encoding="utf-8")
        with pytest.raises(StateCorruptError):
            VarBreachStateMachine.load(store)

    def test_load_semantic_corrupt_raises(self, tmp_path) -> None:
        """语义畸形 (非法状态值/负计数) → StateCorruptError。"""
        store = JsonStateStore(tmp_path)
        store.save("var_breach_state", {"state": "BOGUS", "consecutive_days_below_recovery": 0})
        with pytest.raises(StateCorruptError):
            VarBreachStateMachine.load(store)
        store.save(
            "var_breach_state",
            {"state": "BREACHED", "consecutive_days_below_recovery": -1},
        )
        with pytest.raises(StateCorruptError):
            VarBreachStateMachine.load(store)

    def test_snapshot_roundtrip_preserves_recovery_counter(self) -> None:
        snap = VarBreachStateSnapshot(VarBreachState.RECOVERY, "2026-08-19", 4, "2026-08-20")
        restored = VarBreachStateSnapshot.from_dict(snap.to_dict())
        assert restored == snap

    def test_resume_after_restart_continues_count(self, tmp_path) -> None:
        """跨重启续计: 重启后连续天数不丢 (转换守卫依赖, §3.18/§3.19 配对)。"""
        store = JsonStateStore(tmp_path)
        d = _days(4)
        m = VarBreachStateMachine()
        m.transition(0.021, d[0])
        m.transition(0.010, d[1])
        m.transition(0.010, d[2])
        m.save(store)
        m2 = VarBreachStateMachine.load(store)
        assert m2.transition(0.010, d[3]) is VarBreachState.RECOVERY  # 第 3 日达成


# ── drawdown_controller.evaluate 乘性折扣接入 ─────────────────────────────────


def _dd_info() -> DrawdownInfo:
    return DrawdownInfo(drawdown_pct=0.0, peak_nav=1.0, current_nav=1.0, recovered_pct=0.0)


class TestControllerDiscount:
    def test_none_zero_regression(self) -> None:
        """未接线 (None) 与既有行为一致 (GREEN cap=1.0)。"""
        ctl = DrawdownController()
        resp = ctl.evaluate(_dd_info(), VarCvarMetrics(0.01, 0.015))
        assert resp.position_cap == 1.0

    def test_breached_discount_0_8(self) -> None:
        """GREEN(1.0) × BREACHED(0.8) = 0.8 (VaR breach 额外保守)。"""
        ctl = DrawdownController()
        resp = ctl.evaluate(_dd_info(), VarCvarMetrics(0.01, 0.015), var_breach_state="BREACHED")
        assert resp.position_cap == pytest.approx(0.8)
        assert any("×0.80" in a for a in resp.actions)

    def test_recovery_discount_0_9(self) -> None:
        ctl = DrawdownController()
        resp = ctl.evaluate(_dd_info(), VarCvarMetrics(0.01, 0.015), var_breach_state="RECOVERY")
        assert resp.position_cap == pytest.approx(0.9)

    def test_normal_no_discount(self) -> None:
        ctl = DrawdownController()
        resp = ctl.evaluate(_dd_info(), VarCvarMetrics(0.01, 0.015), var_breach_state="NORMAL")
        assert resp.position_cap == 1.0

    def test_enum_accepted(self) -> None:
        """VarBreachState 枚举 (str mixin) 直接传入可用。"""
        ctl = DrawdownController()
        resp = ctl.evaluate(_dd_info(), VarCvarMetrics(0.01, 0.015), var_breach_state=VarBreachState.BREACHED)
        assert resp.position_cap == pytest.approx(0.8)

    def test_discount_stacks_on_risk_level_cap(self) -> None:
        """YELLOW(0.5) × BREACHED(0.8) = 0.4 (与风险级 cap 乘性叠加)。"""
        ctl = DrawdownController()
        resp = ctl.evaluate(_dd_info(), VarCvarMetrics(0.03, 0.04), var_breach_state="BREACHED")
        assert resp.position_cap == pytest.approx(0.4)

    def test_black_swan_min_wins(self) -> None:
        """黑天鹅 cap 与折扣后 base 取 min (BS003 0.5 < GREEN×0.8=0.8)。"""
        ctl = DrawdownController()
        resp = ctl.evaluate(
            _dd_info(),
            VarCvarMetrics(0.01, 0.015),
            black_swan=BlackSwanSignal(frozenset({BlackSwanMode.BS003_VOLATILITY})),
            var_breach_state="BREACHED",
        )
        assert resp.position_cap == pytest.approx(0.5)

    def test_lower_bound_zero(self) -> None:
        """下限保护 max(0.0): BLACK(0.0) × 0.8 = 0.0 不为负。"""
        ctl = DrawdownController()
        resp = ctl.evaluate(_dd_info(), VarCvarMetrics(0.09, 0.11), var_breach_state="BREACHED")
        assert resp.position_cap == 0.0

    def test_unknown_state_rejected(self) -> None:
        ctl = DrawdownController()
        with pytest.raises(InvalidDrawdownControlError):
            ctl.evaluate(_dd_info(), VarCvarMetrics(0.01, 0.015), var_breach_state="BOGUS")

    def test_case_insensitive(self) -> None:
        ctl = DrawdownController()
        resp = ctl.evaluate(_dd_info(), VarCvarMetrics(0.01, 0.015), var_breach_state="breached")
        assert resp.position_cap == pytest.approx(0.8)

    def test_dual_recovery_stacks(self) -> None:
        """双 RECOVERY 叠加 (§3.15 E3): 回撤阶梯 0.5 × VaR RECOVERY 0.9 = 0.45。"""
        ctl = DrawdownController()
        info = DrawdownInfo(drawdown_pct=-0.05, peak_nav=1.0, current_nav=0.975, recovered_pct=0.5)
        resp = ctl.evaluate(info, VarCvarMetrics(0.01, 0.015), var_breach_state="RECOVERY")
        assert resp.position_cap == pytest.approx(0.5 * 0.9)
