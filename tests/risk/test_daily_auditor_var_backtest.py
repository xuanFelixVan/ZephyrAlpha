# [BLUEPRINT] MOD-FEEDBACK_LOOP | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] tests.risk.test_daily_auditor_var_backtest
# [DOMAIN] D_RISK
# [TESTS] zephyr.risk.core.daily_auditor(run_var_backtest/log_entry_var/log_baseline/log_recalibration/compute_clean_pnl/compute_dirty_pnl)
# [COVERAGE] 36号 §3.11 综合定级(样本门控/三档矩阵/low_power) + §3.11 三审计日志 + §3.13 clean/dirty P&L 双轨
# [MATURITY] evolving
# [TTL] task_bound

"""DailyAuditor VaR 集成包装层测试 (36号 §3.11 + §3.13)。

实证目标:
    1. run_var_backtest 样本门控: n<30 强制 PASS(INSUFFICIENT_SAMPLE_SKIP);
       30≤n<60 仅 E-backtesting 参与定级(LOW_POWER_WARNING, 传统 3 法排除);
       n≥60 全 4 法 + Basel 参与
    2. 三档定级矩阵: PASS / RECALIBRATE(单信号 reject/basel yellow/ebt yellow|red)
       / REBUILD(basel red/ebt black)
    3. log_entry_var/log_baseline/log_recalibration 审计记录载荷 + 日志级别
    4. compute_clean_pnl/compute_dirty_pnl (§3.13 T+1 口径: 锁仓 MtM 剔除/成本扣减)
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta

import pytest

from zephyr.risk.core.daily_auditor import (
    AuditPositionSnapshot,
    DailyAuditor,
    FillRecord,
    VAR_BACKTEST_LOW_POWER_SAMPLES,
    VAR_BACKTEST_MIN_SAMPLES,
)
from zephyr.risk.core.var_backtester import BacktestObservation, VarBacktester

D0 = date(2026, 8, 20)
BASE = datetime(2024, 1, 1)


# ── 数据集构造 ────────────────────────────────────────────────────────────────


def _make_obs(n: int, violations: set[int], var: float = 0.02, es: float = 0.025):
    """合成回测观测: 超限日 realized=-0.025 (|r|>var 且 r/es=-1, Z2 不拒绝)。"""
    return [
        BacktestObservation(
            date=BASE + timedelta(days=i),
            var_forecast=var,
            es_forecast=es,
            realized_return=(-0.025 if i in violations else -0.005),
        )
        for i in range(n)
    ]


@pytest.fixture()
def auditor() -> DailyAuditor:
    return DailyAuditor()


# ── 样本门控 ──────────────────────────────────────────────────────────────────


class TestSampleGating:
    def test_below_min_samples_forced_pass_skip(self, auditor: DailyAuditor) -> None:
        obs = _make_obs(VAR_BACKTEST_MIN_SAMPLES - 1, set(range(10)))  # n=29 重度超限
        rep = auditor.run_var_backtest(D0, obs)
        assert rep.action == "PASS"
        assert "INSUFFICIENT_SAMPLE_SKIP" in rep.flags
        assert rep.n_obs == VAR_BACKTEST_MIN_SAMPLES - 1
        assert rep.report is None  # 跳过回测, 不跑 full_report

    def test_empty_observations_forced_pass(self, auditor: DailyAuditor) -> None:
        rep = auditor.run_var_backtest(D0, [])
        assert rep.action == "PASS"
        assert "INSUFFICIENT_SAMPLE_SKIP" in rep.flags
        assert rep.report is None

    def test_low_power_excludes_traditional_tests(self, auditor: DailyAuditor) -> None:
        """30≤n<60: kupiec reject (n=45 全_clean 超限率 0 vs 名义 5%) 被排除,
        仅 E-backtesting(green) 参与 → PASS + LOW_POWER_WARNING。"""
        obs = _make_obs(45, set())
        # 实证前置: kupiec 确实 reject (证明排除生效, 否则结果应为 RECALIBRATE)
        raw = VarBacktester().full_report(obs)
        assert raw["kupiec_pof"]["reject"] is True
        assert raw["e_backtesting"]["alert_level"] == "green"
        rep = auditor.run_var_backtest(D0, obs)
        assert rep.action == "PASS"
        assert "LOW_POWER_WARNING" in rep.flags
        assert rep.report is not None

    def test_low_power_basel_red_excluded_ebt_red_recalibrate(self, auditor: DailyAuditor) -> None:
        """30≤n<60: basel red 同被排除 (45 日前 8 日连续超限→basel red/ebt red),
        仅 ebt red 参与 → RECALIBRATE (若 basel 参与则 REBUILD)。"""
        obs = _make_obs(45, set(range(8)))
        raw = VarBacktester().full_report(obs)
        assert raw["basel_traffic_light"]["zone"] == "red"
        assert raw["e_backtesting"]["alert_level"] == "red"
        rep = auditor.run_var_backtest(D0, obs)
        assert rep.action == "RECALIBRATE"
        assert "LOW_POWER_WARNING" in rep.flags

    def test_low_power_ebt_black_rebuild(self, auditor: DailyAuditor) -> None:
        obs = _make_obs(45, set(range(10)))
        raw = VarBacktester().full_report(obs)
        assert raw["e_backtesting"]["alert_level"] == "black"
        rep = auditor.run_var_backtest(D0, obs)
        assert rep.action == "REBUILD"
        assert "LOW_POWER_WARNING" in rep.flags

    def test_boundary_n60_full_grading(self, auditor: DailyAuditor) -> None:
        """n=60 出 low_power 窗口: basel red 恢复参与定级。"""
        obs = _make_obs(VAR_BACKTEST_LOW_POWER_SAMPLES, set(range(10)))
        rep = auditor.run_var_backtest(D0, obs)
        assert "LOW_POWER_WARNING" not in rep.flags
        assert rep.action == "REBUILD"  # basel red


# ── 三档定级矩阵 (n≥60, 真实 full_report) ─────────────────────────────────────


class TestGradingMatrix:
    def test_pass_well_calibrated(self, auditor: DailyAuditor) -> None:
        obs = _make_obs(250, set(range(0, 250, 25)))  # 10 次分散超限
        rep = auditor.run_var_backtest(D0, obs)
        assert rep.action == "PASS"
        assert rep.flags == ()
        assert rep.report is not None
        assert rep.report["overall_reject"] is False

    def test_recalibrate_basel_yellow_ebt_yellow(self, auditor: DailyAuditor) -> None:
        obs = _make_obs(250, set(int(i * 250 / 17) for i in range(17)))  # 17 次分散超限
        rep = auditor.run_var_backtest(D0, obs)
        assert rep.action == "RECALIBRATE"
        assert "basel_yellow" in rep.reason

    def test_recalibrate_single_test_rejects(self, auditor: DailyAuditor) -> None:
        """单信号 reject (kupiec+christoffersen) 归 RECALIBRATE (§3.10 触发映射),
        不升级为 REBUILD。"""
        obs = _make_obs(250, set(int(i * 250 / 20) for i in range(20)))  # 20 次分散超限
        raw = VarBacktester().full_report(obs)
        assert raw["kupiec_pof"]["reject"] is True
        rep = auditor.run_var_backtest(D0, obs)
        assert rep.action == "RECALIBRATE"
        assert "kupiec_reject" in rep.reason

    def test_rebuild_basel_red(self, auditor: DailyAuditor) -> None:
        obs = _make_obs(300, set(range(0, 300, 10)))  # 30 次超限 → basel red
        rep = auditor.run_var_backtest(D0, obs)
        assert rep.action == "REBUILD"

    def test_injected_backtester_used(self, auditor: DailyAuditor) -> None:
        """backtester 依赖注入: 99% 置信度口径生效。"""
        bt = VarBacktester(confidence_level=0.99)
        obs = _make_obs(250, set(range(0, 250, 25)))
        rep = auditor.run_var_backtest(D0, obs, backtester=bt)
        assert rep.report is not None
        assert rep.report["confidence_level"] == 0.99


# ── 定级矩阵单元覆盖 (合成报告字典, 含 error 容错) ────────────────────────────


class TestGradeVarBacktestUnit:
    @staticmethod
    def _report(basel="green", ebt="green", kupiec=False, christ=False, z2=False):
        return {
            "basel_traffic_light": {"zone": basel},
            "e_backtesting": {"alert_level": ebt},
            "kupiec_pof": {"reject": kupiec},
            "christoffersen": {"reject": christ},
            "acerbi_szekely_z2": {"reject": z2},
        }

    @pytest.mark.parametrize(
        ("report", "expected"),
        [
            (_report(), "PASS"),
            (_report(basel="yellow"), "RECALIBRATE"),
            (_report(kupiec=True), "RECALIBRATE"),
            (_report(christ=True), "RECALIBRATE"),
            (_report(z2=True), "RECALIBRATE"),
            (_report(ebt="yellow"), "RECALIBRATE"),
            (_report(ebt="red"), "RECALIBRATE"),
            (_report(basel="red"), "REBUILD"),
            (_report(ebt="black"), "REBUILD"),
            (_report(basel="red", ebt="black"), "REBUILD"),
            # 严重信号优先: basel red + 单信号 reject → REBUILD
            (_report(basel="red", kupiec=True), "REBUILD"),
        ],
    )
    def test_matrix(self, report: dict, expected: str) -> None:
        action, _ = DailyAuditor._grade_var_backtest(report, low_power=False)
        assert action == expected

    def test_error_subdicts_tolerated(self) -> None:
        """单项检验 error 字典 (样本不足降级) 按不拒绝处理。"""
        report = {
            "basel_traffic_light": {"error": "样本不足"},
            "e_backtesting": {"error": "样本不足"},
            "kupiec_pof": {"error": "样本不足"},
            "christoffersen": {"error": "样本不足"},
            "acerbi_szekely_z2": {"error": "无超限"},
        }
        action, _ = DailyAuditor._grade_var_backtest(report, low_power=False)
        assert action == "PASS"


# ── 审计日志三方法 ────────────────────────────────────────────────────────────


class TestVarAuditLogs:
    def test_log_entry_var_payload(self, auditor: DailyAuditor, caplog) -> None:
        with caplog.at_level(logging.INFO):
            rec = auditor.log_entry_var(D0, 0.023, entry_es=0.031)
        assert rec["event"] == "entry_var"
        assert rec["trade_date"] == D0.isoformat()
        assert rec["entry_var"] == 0.023
        assert rec["entry_es"] == 0.031
        assert "logged_at" in rec
        assert "VAR_AUDIT entry_var" in caplog.text

    def test_log_entry_var_es_optional(self, auditor: DailyAuditor) -> None:
        rec = auditor.log_entry_var(D0, 0.02)
        assert rec["entry_es"] is None

    def test_log_baseline_payload(self, auditor: DailyAuditor, caplog) -> None:
        with caplog.at_level(logging.INFO):
            rec = auditor.log_baseline(D0, 0.021, 0.028)
        assert rec["event"] == "baseline"
        assert rec["var_95"] == 0.021
        assert rec["es_95"] == 0.028
        assert "VAR_AUDIT baseline" in caplog.text

    def test_log_recalibration_levels(self, auditor: DailyAuditor, caplog) -> None:
        with caplog.at_level(logging.DEBUG):
            auditor.log_recalibration(D0, "REBUILD", "basel red")
            auditor.log_recalibration(D0, "RECALIBRATE", "kupiec reject")
            auditor.log_recalibration(D0, "RECOVERED_FROM_REBUILD", "业主确认")
        levels = [r.levelname for r in caplog.records if "VAR_AUDIT recalibration" in r.message]
        assert levels == ["CRITICAL", "WARNING", "INFO"]

    def test_log_recalibration_payload_normalized(self, auditor: DailyAuditor) -> None:
        rec = auditor.log_recalibration(D0, "recalibrate", "kupiec reject")
        assert rec["action"] == "RECALIBRATE"
        assert rec["reason"] == "kupiec reject"
        assert rec["event"] == "recalibration"


# ── clean/dirty P&L 双轨 (§3.13) ──────────────────────────────────────────────


def _pos(symbol: str, qty: float, entry: float, close: float) -> AuditPositionSnapshot:
    return AuditPositionSnapshot(symbol, qty, entry, close)


class TestPnlDual:
    def test_clean_excludes_locked_mtm_and_cost(self, auditor: DailyAuditor) -> None:
        """T+1 口径: 当日新建仓 (NEW) 未实现 MtM 剔除出 clean; 成本不进 clean。"""
        prev = [_pos("OLD", 100, 10.0, 10.0)]
        now = [_pos("OLD", 100, 10.0, 11.0), _pos("NEW", 100, 20.0, 22.0)]
        fills = [FillRecord("NEW", 100, 20.0, realized_pnl=0.0, cost=50.0)]
        clean = auditor.compute_clean_pnl(prev, now, fills, new_position_symbols={"NEW"})
        # gross = OLD MtM 100×(11−10)=100 + NEW MtM 100×(22−20)=200 = 300
        # clean = 300 − 200(锁仓) = 100 (成本 50 不扣)
        assert clean == pytest.approx(100.0)

    def test_dirty_includes_all_mtm_minus_cost(self, auditor: DailyAuditor) -> None:
        prev = [_pos("OLD", 100, 10.0, 10.0)]
        now = [_pos("OLD", 100, 10.0, 11.0), _pos("NEW", 100, 20.0, 22.0)]
        fills = [FillRecord("NEW", 100, 20.0, realized_pnl=0.0, cost=50.0)]
        dirty = auditor.compute_dirty_pnl(prev, now, fills)
        # dirty = 300(全部 MtM) − 50(成本) = 250
        assert dirty == pytest.approx(250.0)

    def test_clean_equals_gross_when_no_new_positions(self, auditor: DailyAuditor) -> None:
        prev = [_pos("OLD", 100, 10.0, 10.0)]
        now = [_pos("OLD", 100, 10.0, 11.0)]
        clean = auditor.compute_clean_pnl(prev, now, [], new_position_symbols=None)
        assert clean == pytest.approx(100.0)

    def test_clean_first_entry_day_zero(self, auditor: DailyAuditor) -> None:
        """冷启动边界 (§3.13): 首次建仓日全部头寸 T+1 不可平仓 → clean=0。"""
        now = [_pos("NEW", 100, 20.0, 22.0)]
        clean = auditor.compute_clean_pnl([], now, [], new_position_symbols={"NEW"})
        assert clean == pytest.approx(0.0)

    def test_clean_realized_pnl_kept(self, auditor: DailyAuditor) -> None:
        """可平仓头寸已实现盈亏保留在 clean (fills 已实现天然属可平仓)。"""
        prev = [_pos("OLD", 100, 10.0, 10.0)]
        now = [_pos("OLD", 50, 10.0, 11.0)]
        fills = [FillRecord("OLD", -50, 11.0, realized_pnl=50.0, cost=5.0)]
        clean = auditor.compute_clean_pnl(prev, now, fills)
        # realized 50 + 剩余 MtM 50×(11−10)=50 = 100
        assert clean == pytest.approx(100.0)
        dirty = auditor.compute_dirty_pnl(prev, now, fills)
        assert dirty == pytest.approx(95.0)  # 100 − 5 成本
