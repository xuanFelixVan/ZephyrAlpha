# [BLUEPRINT] MOD-GOV-045 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""rollback_state_machine 五态降级状态机单元测试（#ARCH-QUANT-003，53 号 §3.8）。

覆盖：五态迁移矩阵全路径 / 单向更保守（无自动恢复）/ Hysteresis trip≠recover /
≥30 笔样本地板（29 不触发 + 30 触发边界）/ P0 绕过地板 / recover 权限三件套
（PermissionError/ValueError）/ fail-closed 畸形持久化 / 持久化 roundtrip /
T+1 UNWINDING 仅 T-1 持仓语义 / 晋级耦合点 check_promotion_allowed。
"""

from __future__ import annotations

import pytest

from zephyr.governance.lifecycle_governance.paper_live_transition import (
    check_promotion_allowed,
)
from zephyr.governance.lifecycle_governance.rollback_state_machine import (
    _AUTO_TRANSITIONS,
    _HYSTERESIS,
    _MIN_SAMPLE_TRADES,
    RollbackState,
    evaluate_rollback,
    load_persisted_state,
    persist_state,
    recover,
    safe_read_state,
)
from zephyr.shared.state_store import JsonStateStore

S = RollbackState


class TestFiveStateEnum:
    def test_five_states_exact(self):
        assert [s.value for s in S] == [
            "NORMAL", "THROTTLED", "SOFT_HALT", "HARD_HALT", "UNWINDING",
        ]

    def test_enum_order_is_conservatism_order(self):
        # recover() 的方向判定依赖枚举序=保守程度序
        assert list(S).index(S.NORMAL) < list(S).index(S.UNWINDING)

    def test_auto_transitions_only_more_conservative(self):
        for (frm, to) in _AUTO_TRANSITIONS:
            assert list(S).index(to) > list(S).index(frm)

    def test_hard_halt_to_unwinding_not_auto(self):
        assert (S.HARD_HALT, S.UNWINDING) not in _AUTO_TRANSITIONS


class TestHysteresis:
    def test_trip_recover_asymmetric(self):
        # Hysteresis 防抖动：recover 阈值必须严格小于 trip（daily_loss recover=0
        # 表示当日亏损触发后当日不可自动恢复）
        for key, h in _HYSTERESIS.items():
            assert h["recover"] < h["trip"], key

    def test_threshold_values(self):
        assert _HYSTERESIS["intraday_dd"] == {"trip": 0.01, "recover": 0.003}
        assert _HYSTERESIS["daily_loss"] == {"trip": 0.03, "recover": 0.00}
        assert _HYSTERESIS["reject_rate"] == {"trip": 0.01, "recover": 0.005}

    def test_min_sample_trades(self):
        assert _MIN_SAMPLE_TRADES == 30


class TestEvaluateRollbackMatrix:
    """五态迁移矩阵全路径（每 tick 单步，只向更保守）。"""

    def test_normal_no_breach_stays(self):
        assert evaluate_rollback({}, S.NORMAL, 100) == S.NORMAL

    def test_normal_soft_breach_dd_to_throttled(self):
        m = {"intraday_dd": 0.011}  # > 1% trip
        assert evaluate_rollback(m, S.NORMAL, 100) == S.THROTTLED

    def test_normal_soft_breach_reject_to_throttled(self):
        m = {"reject_rate": 0.011}
        assert evaluate_rollback(m, S.NORMAL, 100) == S.THROTTLED

    def test_normal_at_threshold_not_triggered(self):
        # trip 是严格大于：恰好 1% 不触发
        assert evaluate_rollback({"intraday_dd": 0.01}, S.NORMAL, 100) == S.NORMAL

    def test_throttled_hard_breach_dd_to_soft_halt(self):
        m = {"intraday_dd": 0.021}  # > 1% × 2.0
        assert evaluate_rollback(m, S.THROTTLED, 100) == S.SOFT_HALT

    def test_throttled_hard_breach_reject_to_soft_halt(self):
        m = {"reject_rate": 0.051}  # > 1% × 5.0
        assert evaluate_rollback(m, S.THROTTLED, 100) == S.SOFT_HALT

    def test_throttled_persistent_reject_to_soft_halt(self):
        m = {"reject_rate_duration_s": 60}  # 持续 60s
        assert evaluate_rollback(m, S.THROTTLED, 100) == S.SOFT_HALT

    def test_throttled_daily_loss_near_3pct_to_soft_halt(self):
        # v1.7.9（AI-R5）：daily_loss > 2.5%（3%×5/6，"接近 3%"数值化）触发爬梯
        m = {"daily_loss": 0.026}
        assert evaluate_rollback(m, S.THROTTLED, 100) == S.SOFT_HALT

    def test_throttled_daily_loss_below_2_5pct_stays(self):
        # daily_loss 恰 2.5%（严格大于口径）不触发——Hysteresis 区间停留
        assert evaluate_rollback({"daily_loss": 0.025}, S.THROTTLED, 100) == S.THROTTLED
        assert evaluate_rollback({"daily_loss": 0.024}, S.THROTTLED, 100) == S.THROTTLED

    def test_throttled_soft_breach_only_stays(self):
        # THROTTLED 态 1.5% DD（超 soft 未超 hard 2%）停留——Hysteresis 区间
        assert evaluate_rollback({"intraday_dd": 0.015}, S.THROTTLED, 100) == S.THROTTLED

    def test_soft_halt_daily_loss_to_hard_halt(self):
        m = {"daily_loss": 0.031}  # > 3% trip
        assert evaluate_rollback(m, S.SOFT_HALT, 100) == S.HARD_HALT

    def test_soft_halt_circuit_breaker_to_hard_halt(self):
        m = {"circuit_breaker": True}
        assert evaluate_rollback(m, S.SOFT_HALT, 100) == S.HARD_HALT

    def test_soft_halt_p0_to_hard_halt(self):
        m = {"p0_event": True}
        assert evaluate_rollback(m, S.SOFT_HALT, 100) == S.HARD_HALT

    def test_hard_halt_never_auto_unwinding(self):
        # HARD_HALT → UNWINDING 须人工 + 双人复核，任何 metrics 不自动迁移
        m = {"daily_loss": 0.5, "circuit_breaker": True, "p0_event": True}
        assert evaluate_rollback(m, S.HARD_HALT, 100) == S.HARD_HALT

    def test_unwinding_never_auto(self):
        m = {"daily_loss": 0.5, "p0_event": True}
        assert evaluate_rollback(m, S.UNWINDING, 100) == S.UNWINDING

    def test_no_auto_recovery_throttled(self):
        # 指标全部回落到 recover 阈值以下：不自动恢复（恢复须人工 recover()）
        m = {"intraday_dd": 0.001, "reject_rate": 0.001, "daily_loss": 0.0}
        assert evaluate_rollback(m, S.THROTTLED, 100) == S.THROTTLED

    def test_no_auto_recovery_hard_halt(self):
        assert evaluate_rollback({}, S.HARD_HALT, 100) == S.HARD_HALT

    def test_one_step_per_tick(self):
        # 阶梯单步：NORMAL 遇灾难性 daily_loss 本 tick 不直接跳 HARD_HALT
        m = {"daily_loss": 0.10}
        assert evaluate_rollback(m, S.NORMAL, 100) == S.NORMAL

    def test_full_ladder_three_ticks(self):
        # 连续恶化：NORMAL → THROTTLED → SOFT_HALT → HARD_HALT 三 tick 走满梯子
        s = evaluate_rollback({"intraday_dd": 0.02}, S.NORMAL, 100)
        assert s == S.THROTTLED
        s = evaluate_rollback({"intraday_dd": 0.025}, s, 100)
        assert s == S.SOFT_HALT
        s = evaluate_rollback({"daily_loss": 0.04}, s, 100)
        assert s == S.HARD_HALT


class TestSampleFloor:
    def test_29_trades_not_triggered(self):
        m = {"intraday_dd": 0.05}
        assert evaluate_rollback(m, S.NORMAL, 29) == S.NORMAL

    def test_30_trades_triggered(self):
        m = {"intraday_dd": 0.02}
        assert evaluate_rollback(m, S.NORMAL, 30) == S.THROTTLED

    def test_zero_trades_not_triggered(self):
        assert evaluate_rollback({"intraday_dd": 0.05}, S.NORMAL, 0) == S.NORMAL

    def test_p0_bypasses_floor(self):
        # P0 事件绕过样本地板：SOFT_HALT + P0 + 0 笔 → HARD_HALT
        assert evaluate_rollback({"p0_event": True}, S.SOFT_HALT, 0) == S.HARD_HALT

    def test_p0_bypasses_floor_at_normal_with_breach(self):
        m = {"p0_event": True, "intraday_dd": 0.02}
        assert evaluate_rollback(m, S.NORMAL, 0) == S.THROTTLED

    def test_p0_alone_at_normal_no_jump(self):
        # 伪代码语义：NORMAL 态 P0 无超限时本 tick 不跳变（梯子单步制）
        assert evaluate_rollback({"p0_event": True}, S.NORMAL, 0) == S.NORMAL


class TestRecover:
    def test_no_rca_permission_error(self):
        with pytest.raises(PermissionError):
            recover(S.HARD_HALT, S.SOFT_HALT,
                    rca_written=False, dual_approval=True, position_flat=True)

    def test_no_dual_approval_permission_error(self):
        with pytest.raises(PermissionError):
            recover(S.HARD_HALT, S.SOFT_HALT,
                    rca_written=True, dual_approval=False, position_flat=True)

    def test_neither_rca_nor_approval_permission_error(self):
        with pytest.raises(PermissionError):
            recover(S.HARD_HALT, S.NORMAL,
                    rca_written=False, dual_approval=False, position_flat=True)

    def test_permission_check_precedes_direction_check(self):
        # 先权限后方向：无 RCA 即使方向合法也 PermissionError
        with pytest.raises(PermissionError):
            recover(S.NORMAL, S.HARD_HALT,
                    rca_written=False, dual_approval=False, position_flat=True)

    def test_reverse_direction_value_error(self):
        # 恢复只能向更宽松态：向更保守态 = ValueError
        with pytest.raises(ValueError):
            recover(S.THROTTLED, S.HARD_HALT,
                    rca_written=True, dual_approval=True, position_flat=True)

    def test_same_state_value_error(self):
        with pytest.raises(ValueError):
            recover(S.THROTTLED, S.THROTTLED,
                    rca_written=True, dual_approval=True, position_flat=True)

    def test_unwinding_position_not_flat_value_error(self):
        # T+1：T-1 持仓未平禁止回 NORMAL
        with pytest.raises(ValueError):
            recover(S.UNWINDING, S.NORMAL,
                    rca_written=True, dual_approval=True, position_flat=False)

    def test_unwinding_to_normal_success(self):
        got = recover(S.UNWINDING, S.NORMAL,
                      rca_written=True, dual_approval=True, position_flat=True)
        assert got == S.NORMAL

    def test_hard_halt_to_throttled_success(self):
        # 恢复可跨级向更宽松（人工裁决）
        got = recover(S.HARD_HALT, S.THROTTLED,
                      rca_written=True, dual_approval=True, position_flat=False)
        assert got == S.THROTTLED

    def test_throttled_to_normal_success(self):
        got = recover(S.THROTTLED, S.NORMAL,
                      rca_written=True, dual_approval=True, position_flat=True)
        assert got == S.NORMAL


class TestFailClosed:
    def test_none_persisted_soft_halt(self):
        assert safe_read_state(None) == S.SOFT_HALT

    def test_empty_dict_soft_halt(self):
        assert safe_read_state({}) == S.SOFT_HALT

    def test_garbage_state_value_soft_halt(self):
        assert safe_read_state({"state": "GARBAGE"}) == S.SOFT_HALT

    def test_wrong_type_soft_halt(self):
        assert safe_read_state({"state": 123}) == S.SOFT_HALT

    def test_non_dict_persisted_soft_halt(self):
        assert safe_read_state("NORMAL") == S.SOFT_HALT  # type: ignore[arg-type]

    def test_valid_persisted_roundtrip(self):
        assert safe_read_state({"state": "THROTTLED"}) == S.THROTTLED


class TestPersistence:
    def test_persist_load_roundtrip(self, tmp_path):
        store = JsonStateStore(tmp_path)
        persist_state(store, S.THROTTLED, reason="intraday_dd>1%", trade_count=42)
        assert load_persisted_state(store) == S.THROTTLED

    def test_load_missing_soft_halt(self, tmp_path):
        store = JsonStateStore(tmp_path)
        assert load_persisted_state(store) == S.SOFT_HALT

    def test_load_corrupt_soft_halt(self, tmp_path):
        store = JsonStateStore(tmp_path)
        (tmp_path / "rollback_state.json").write_bytes(b"{corrupt!!")
        assert load_persisted_state(store) == S.SOFT_HALT

    def test_load_garbage_state_soft_halt(self, tmp_path):
        store = JsonStateStore(tmp_path)
        persist_state(store, S.NORMAL)
        (tmp_path / "rollback_state.json").write_text(
            '{"state": "NOT_A_STATE"}', encoding="utf-8")
        assert load_persisted_state(store) == S.SOFT_HALT

    def test_crash_restart_posture_survives(self, tmp_path):
        # Crash-only：熔断姿态重启存活（kill switch 不因为进程重启而解除）
        persist_state(JsonStateStore(tmp_path), S.HARD_HALT, reason="daily_loss>=3%")
        store2 = JsonStateStore(tmp_path)  # 模拟重启后新实例
        assert load_persisted_state(store2) == S.HARD_HALT


class TestPromotionCoupling:
    """两机唯一耦合点：阶段晋级前置当前降级姿态=NORMAL。"""

    def test_normal_allows_promotion(self):
        check_promotion_allowed(S.NORMAL)  # 不抛异常

    @pytest.mark.parametrize("posture", [
        S.THROTTLED, S.SOFT_HALT, S.HARD_HALT, S.UNWINDING,
    ])
    def test_non_normal_blocks_promotion(self, posture):
        with pytest.raises(PermissionError):
            check_promotion_allowed(posture)

    def test_fail_closed_read_blocks_promotion(self, tmp_path):
        # fail-closed 链路实证：畸形持久化 → SOFT_HALT → 禁止晋级
        store = JsonStateStore(tmp_path)
        (tmp_path / "rollback_state.json").write_bytes(b"###not-json###")
        posture = load_persisted_state(store)
        assert posture == S.SOFT_HALT
        with pytest.raises(PermissionError):
            check_promotion_allowed(posture)
