# [BLUEPRINT] MOD-SIG-128 | docs/03_modules/_domain_signal/tcp_rm_conformal/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-128 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_tcp_rm_conformal
# [TESTS] src/zephyr/signal_ashare/tcp_rm_conformal.py
"""MOD-SIG-128 单元测试：tcp_rm_conformal TCP-RM 时序保形预测增强器。

蓝图验收（B10-01854/CAND-TESTB-050，A1 §29.16-5）：
Robbins-Monro 在线校准（分位数误差反馈，步长按 1/n 衰减）+ DDCI 双反馈
（欠覆盖阈值外扩/过宽阈值内收，min_margin 护栏）+ CP-VaR 回测（注入回测
序列，下轨破位统计）+ 覆盖率统计报告（目标 vs 实际）。纯内存确定性重放。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.tcp_rm_conformal",
    reason="tcp_rm_conformal not importable",
)

from zephyr.signal_ashare.tcp_rm_conformal import (  # noqa: E402
    TcpRmConformal,
    TcpRmConfig,
    TcpRmError,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _engine(config: TcpRmConfig | None = None) -> TcpRmConformal:
    return TcpRmConformal(config=config, clock=lambda: _T0)


def _plain(**overrides) -> TcpRmConfig:
    """RM-only 基线配置（DDCI 关闭，min_margin=0 便于精确推导）。"""
    base = {"target_coverage": 0.8, "step0": 0.1, "ddci_gain": 0.0, "min_margin": 0.0}
    base.update(overrides)
    return TcpRmConfig(**base)


# ──────────────────────────────────────────────────────────────────────────────
# 构造期 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_target_coverage_out_of_range_raises(self) -> None:
        for bad in (0.0, 1.0, 1.5, float("nan")):
            with pytest.raises(TcpRmError):
                _engine(TcpRmConfig(target_coverage=bad))

    def test_step0_nonpositive_raises(self) -> None:
        for bad in (0.0, -0.1, float("nan")):
            with pytest.raises(TcpRmError):
                _engine(TcpRmConfig(step0=bad))

    def test_ddci_gain_negative_raises(self) -> None:
        with pytest.raises(TcpRmError):
            _engine(TcpRmConfig(ddci_gain=-0.01))

    def test_ddci_tolerance_out_of_range_raises(self) -> None:
        for bad in (1.0, -0.1, float("nan")):
            with pytest.raises(TcpRmError):
                _engine(TcpRmConfig(ddci_tolerance=bad))

    def test_min_margin_negative_raises(self) -> None:
        with pytest.raises(TcpRmError):
            _engine(TcpRmConfig(min_margin=-1e-6))


# ──────────────────────────────────────────────────────────────────────────────
# 在线校准（Robbins-Monro）
# ──────────────────────────────────────────────────────────────────────────────


class TestUpdate:
    def test_first_interval_uses_min_margin(self) -> None:
        eng = _engine(_plain(min_margin=1e-6))
        iv = eng.update(0.0, 0.5)
        assert iv.margin == pytest.approx(1e-6)
        assert iv.lower == pytest.approx(-1e-6)
        assert iv.upper == pytest.approx(1e-6)
        assert iv.n_step == 0
        assert iv.covered is False
        assert iv.at == _T0
        assert iv.target_coverage == pytest.approx(0.8)

    def test_no_lookahead(self) -> None:
        eng = _engine(_plain())
        eng.update(0.0, 5.0)  # miss → 阈值抬升
        m_before = eng.current_margin
        iv = eng.update(0.0, 0.0)
        assert iv.margin == m_before  # 区间用更新前阈值（无未来函数）
        assert iv.n_step == 1
        assert iv.covered is True  # 判定也用更新前阈值

    def test_miss_widens(self) -> None:
        eng = _engine(_plain())
        m0 = eng.current_margin
        eng.update(0.0, 5.0)  # 未覆盖 → 外扩
        assert eng.current_margin > m0

    def test_covered_narrows_slightly(self) -> None:
        eng = _engine(_plain())
        eng.update(0.0, 5.0)  # miss：margin = 0.1/1×0.8 = 0.08
        m_after_miss = eng.current_margin
        assert m_after_miss == pytest.approx(0.08)
        eng.update(0.0, 0.0)  # covered：margin += 0.1/2×(0.8−1) → 微内收
        assert eng.current_margin == pytest.approx(0.07)
        assert eng.current_margin < m_after_miss

    def test_step_decays_1_over_n(self) -> None:
        eng = _engine(_plain())
        expected = 0.0
        margins_seen: list[float] = []
        for k in range(1, 5):
            iv = eng.update(0.0, 100.0)  # 恒 miss：margin += (step0/k)×τ
            margins_seen.append(iv.margin)
            expected += (0.1 / k) * 0.8
            assert eng.current_margin == expected  # 同序累加，逐位一致
        # 区间载荷阈值=更新前：0, m1, m2, m3
        assert margins_seen[0] == 0.0
        assert margins_seen[1] == pytest.approx(0.08)
        assert margins_seen[2] == pytest.approx(0.08 + 0.04)

    def test_non_finite_raises(self) -> None:
        eng = _engine(_plain())
        with pytest.raises(TcpRmError):
            eng.update(float("nan"), 0.0)
        with pytest.raises(TcpRmError):
            eng.update(0.0, float("inf"))
        with pytest.raises(TcpRmError):
            eng.update("bad", 0.0)  # type: ignore[arg-type]
        with pytest.raises(TcpRmError):
            eng.predict_interval(float("nan"))

    def test_predict_does_not_mutate(self) -> None:
        eng = _engine(_plain())
        eng.update(0.0, 5.0)
        m = eng.current_margin
        iv1 = eng.predict_interval(1.0)
        iv2 = eng.predict_interval(1.0)
        assert iv1 == iv2
        assert iv1.covered is None
        assert eng.current_margin == m
        assert eng.coverage_report().n == 1  # predict 不计步


# ──────────────────────────────────────────────────────────────────────────────
# DDCI 双反馈
# ──────────────────────────────────────────────────────────────────────────────


class TestDdci:
    def test_undercoverage_ddci_widens(self) -> None:
        cfg_on = _plain(target_coverage=0.9, step0=0.05, ddci_gain=0.1)
        cfg_off = _plain(target_coverage=0.9, step0=0.05, ddci_gain=0.0)
        eng_on, eng_off = _engine(cfg_on), _engine(cfg_off)
        for _ in range(5):
            eng_on.update(0.0, 10.0)   # 恒 miss → 欠覆盖
            eng_off.update(0.0, 10.0)
        assert eng_on.current_margin > eng_off.current_margin  # DDCI 额外外扩
        rep = eng_on.coverage_report()
        assert rep.ddci_widen_count == 5
        assert rep.ddci_narrow_count == 0

    def test_overcoverage_ddci_narrows(self) -> None:
        cfg_on = _plain(target_coverage=0.5, step0=0.05, ddci_gain=0.1)
        cfg_off = _plain(target_coverage=0.5, step0=0.05, ddci_gain=0.0)
        eng_on, eng_off = _engine(cfg_on), _engine(cfg_off)
        for _ in range(4):
            eng_on.update(0.0, 0.0)    # 恒 covered → 超覆盖（过宽）
            eng_off.update(0.0, 0.0)
        rep = eng_on.coverage_report()
        assert rep.ddci_narrow_count == 4
        assert rep.ddci_widen_count == 0
        assert eng_off.coverage_report().ddci_narrow_count == 0
        assert rep.current_margin == 0.0  # min_margin=0 护栏兜底不转负

    def test_ddci_bidirectional(self) -> None:
        eng = _engine(_plain(target_coverage=0.5, step0=0.05, ddci_gain=0.1))
        peak = 0.0
        for _ in range(3):
            eng.update(0.0, 10.0)  # miss 段 → 欠覆盖外扩
            peak = max(peak, eng.current_margin)
        for _ in range(20):
            eng.update(0.0, 0.0)   # covered 段 → 覆盖率爬升过目标后内收
        rep = eng.coverage_report()
        assert rep.ddci_widen_count > 0
        assert rep.ddci_narrow_count > 0
        assert eng.current_margin < peak  # 内收段把阈值拉回

    def test_tolerance_blocks_ddci(self) -> None:
        eng = _engine(_plain(target_coverage=0.9, ddci_gain=0.1, ddci_tolerance=0.95))
        for _ in range(3):
            eng.update(0.0, 10.0)  # gap=0.9 < 容差0.95 → DDCI 不动作
        rep = eng.coverage_report()
        assert rep.ddci_widen_count == 0
        assert rep.ddci_narrow_count == 0

    def test_min_margin_floor(self) -> None:
        eng = _engine(_plain(target_coverage=0.5, step0=0.5, ddci_gain=1.0, min_margin=0.01))
        margins: list[float] = []
        for _ in range(10):
            iv = eng.update(0.0, 0.0)  # 恒 covered + 巨增益 → 死压阈值
            margins.append(iv.margin)
        assert all(m >= 0.01 for m in margins)
        assert eng.current_margin == 0.01  # 恒≥护栏


# ──────────────────────────────────────────────────────────────────────────────
# CP-VaR 回测（注入回测序列）
# ──────────────────────────────────────────────────────────────────────────────


class TestBacktestCpVar:
    def test_backtest_breach_stats(self) -> None:
        eng = _engine(_plain(target_coverage=0.8, step0=0.001))
        rep = eng.backtest_cp_var([0.0, 0.0, 0.0, 0.0], [-0.5, 0.3, -0.2, 0.0])
        assert rep.n == 4
        assert rep.breach_indices == (0, 2)  # 下轨破位：-0.5 与 -0.2
        assert rep.n_breaches == 2
        assert rep.breach_rate == pytest.approx(0.5)
        assert rep.target_breach_rate == pytest.approx(0.2)
        assert rep.breach_gap == pytest.approx(0.3)
        assert rep.ran_at == _T0

    def test_backtest_length_mismatch_raises(self) -> None:
        eng = _engine(_plain())
        with pytest.raises(TcpRmError):
            eng.backtest_cp_var([0.0], [0.0, 0.1])
        with pytest.raises(TcpRmError):
            eng.backtest_cp_var([], [])

    def test_backtest_non_finite_raises(self) -> None:
        eng = _engine(_plain())
        with pytest.raises(TcpRmError):
            eng.backtest_cp_var([0.0, 0.0], [0.1, float("nan")])

    def test_backtest_continues_state(self) -> None:
        eng = _engine(_plain(target_coverage=0.8, step0=0.001))
        eng.update(0.0, 1.0)  # 1 步在线
        eng.backtest_cp_var([0.0, 0.0], [0.2, -0.3])  # 续跑 2 步
        assert eng.coverage_report().n == 3
        # reset 后同序列重放 = 全新引擎（确定性）
        seq_p, seq_a = [0.0, 0.0], [0.2, -0.3]
        eng.reset()
        eng.update(0.0, 1.0)
        r1 = eng.backtest_cp_var(seq_p, seq_a)
        eng2 = _engine(_plain(target_coverage=0.8, step0=0.001))
        eng2.update(0.0, 1.0)
        r2 = eng2.backtest_cp_var(seq_p, seq_a)
        assert r1 == r2


# ──────────────────────────────────────────────────────────────────────────────
# 覆盖率统计报告（目标 vs 实际）
# ──────────────────────────────────────────────────────────────────────────────


class TestCoverageReport:
    def test_empty_report(self) -> None:
        rep = _engine(_plain(min_margin=0.01)).coverage_report()
        assert rep.n == 0
        assert rep.n_covered == 0
        assert rep.n_missed == 0
        assert rep.empirical_coverage is None
        assert rep.coverage_gap is None
        assert rep.mean_margin is None
        assert rep.current_margin == pytest.approx(0.01)
        assert rep.ddci_widen_count == 0
        assert rep.ddci_narrow_count == 0

    def test_report_counts(self) -> None:
        eng = _engine(_plain(target_coverage=0.8, step0=0.001))
        eng.update(0.0, -0.5)  # miss（margin 0）
        eng.update(0.0, 0.3)   # miss（margin 0.0008）
        eng.update(0.0, 0.0)   # covered（margin 0.0012）
        rep = eng.coverage_report()
        assert rep.n == 3
        assert rep.n_covered == 1
        assert rep.n_missed == 2
        assert rep.target_coverage == pytest.approx(0.8)
        assert rep.empirical_coverage == pytest.approx(1.0 / 3.0)
        assert rep.coverage_gap == pytest.approx(1.0 / 3.0 - 0.8)
        assert rep.mean_margin == pytest.approx((0.0 + 0.0008 + 0.0012) / 3.0)
        assert rep.current_margin == pytest.approx(0.0012 + 0.001 / 3.0 * (0.8 - 1.0))

    def test_determinism_two_engines(self) -> None:
        cfg = _plain(target_coverage=0.9, step0=0.05, ddci_gain=0.1)
        seq = [(0.0, 1.0), (0.0, 0.0), (0.1, -0.2), (0.0, 0.05), (0.0, 3.0)]
        eng1, eng2 = _engine(cfg), _engine(cfg)
        for p, a in seq:
            i1 = eng1.update(p, a)
            i2 = eng2.update(p, a)
            assert i1 == i2
        assert eng1.coverage_report() == eng2.coverage_report()
