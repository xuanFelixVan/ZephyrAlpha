# [BLUEPRINT] MOD-FEEDBACK_LOOP | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TTL] permanent
"""DailyAuditor 单元测试 (MOD-RK-20)。"""

from __future__ import annotations

import math
from datetime import date, datetime, timezone

import numpy as np
import pytest

from zephyr.risk.core.daily_auditor import (
    AttributionStatus,
    AuditConfig,
    AuditPositionSnapshot,
    AuditRequest,
    AuditRiskMetricsReport,
    AuditStatus,
    CheckStatus,
    DailyAuditor,
    DailyAuditReport,
    FillRecord,
    InvalidAuditInputError,
    IssueSeverity,
    LimitConsumption,
    ReconciliationStatus,
)
from zephyr.risk.core.risk_decomposition import DecompositionResult, RiskDecomposer

T0 = datetime(2026, 8, 1, 15, 30, tzinfo=timezone.utc)
D0 = date(2026, 8, 1)


@pytest.fixture(autouse=True)
def _seed():
    np.random.seed(42)


# ── 辅助构造 ──────────────────────────────────────────────────────────────────


def pos(symbol, qty, entry, close):
    return AuditPositionSnapshot(symbol, qty, entry, close)


def fill(symbol, qty, price, realized=0.0, cost=0.0):
    return FillRecord(symbol, qty, price, realized, cost)


def consumption(lt, value, consumed):
    return LimitConsumption(lt, value, consumed)


def _do_audit(auditor, **kwargs):
    """Helper: 构造 AuditRequest 并执行 audit (参数对象模式, §5.150)。"""
    return auditor.audit(AuditRequest(**kwargs))


# ── 配置校验 ──────────────────────────────────────────────────────────────────


def test_config_negative_tolerance_rejected():
    with pytest.raises(InvalidAuditInputError):
        AuditConfig(pnl_tolerance=0)


def test_config_warn_ratio_out_of_range():
    with pytest.raises(InvalidAuditInputError):
        AuditConfig(warn_ratio=1.5)
    with pytest.raises(InvalidAuditInputError):
        AuditConfig(warn_ratio=0)


def test_config_bias_threshold_must_be_positive():
    with pytest.raises(InvalidAuditInputError):
        AuditConfig(bias_threshold=-0.1)


def test_config_defaults_valid():
    cfg = AuditConfig()
    assert cfg.pnl_tolerance == 0.001
    assert cfg.warn_ratio == 0.8
    assert cfg.bias_threshold == 0.1


# ── PnL 对账 ──────────────────────────────────────────────────────────────────


def test_pnl_reconciliation_match_no_change():
    """无成交无价格变动 → 全零, MATCH。"""
    auditor = DailyAuditor()
    prev = [pos("600000", 100, 10.0, 10.0)]
    now = [pos("600000", 100, 10.0, 10.0)]
    recon = auditor.reconcile_pnl(prev, now, [], nav=1_000_000.0, now=T0)
    assert recon.expected_pnl == pytest.approx(0.0)
    assert recon.realized_pnl == 0.0
    assert recon.unrealized_pnl == pytest.approx(0.0)
    assert recon.total_pnl == 0.0
    assert recon.gap == pytest.approx(0.0)
    assert recon.status == ReconciliationStatus.MATCH


def test_pnl_reconciliation_price_up_only_holding():
    """纯持仓价格上涨: expected = unrealized = qty*(close-prev_close)。"""
    auditor = DailyAuditor()
    prev = [pos("600000", 100, 10.0, 10.0)]
    now = [pos("600000", 100, 10.0, 11.0)]  # 涨到 11
    recon = auditor.reconcile_pnl(prev, now, [], nav=1_000_000.0, now=T0)
    # expected = 100*(11-10) = 100 ; unrealized = 100*(11-10)=100 ; realized=0
    assert recon.expected_pnl == pytest.approx(100.0)
    assert recon.unrealized_pnl == pytest.approx(100.0)
    assert recon.realized_pnl == 0.0
    assert recon.total_pnl == pytest.approx(100.0)
    assert recon.gap == pytest.approx(0.0)
    assert recon.status == ReconciliationStatus.MATCH


def test_pnl_reconciliation_with_realized_trade():
    """部分卖出产生已实现盈亏, 持仓守恒时缺口为零 (资产负债表恒等式)。"""
    auditor = DailyAuditor()
    prev = [pos("600000", 100, 10.0, 10.0)]
    # 现持仓 60 股, 卖出 40 股 @ 11, realized=40*(11-10)=40, cost=5
    now = [pos("600000", 60, 10.0, 11.0)]
    fills = [fill("600000", -40, 11.0, realized=40.0, cost=5.0)]
    recon = auditor.reconcile_pnl(prev, now, fills, nav=10_000.0, now=T0)
    # MV_prev=1000, MV_now=660, trade_cash=(-40)*11=-440
    # expected = (660-1000) - (-440) = 100
    assert recon.expected_pnl == pytest.approx(100.0)
    # realized = 40 (gross) ; unrealized = 60*(11-10)=60 ; total = 100
    assert recon.realized_pnl == pytest.approx(40.0)
    assert recon.unrealized_pnl == pytest.approx(60.0)
    assert recon.total_pnl == pytest.approx(100.0)
    # gap = 100 - 100 = 0 (持仓守恒, 已实现与成交一致)
    assert recon.gap == pytest.approx(0.0)
    assert recon.total_cost == pytest.approx(5.0)
    assert recon.status == ReconciliationStatus.MATCH


def test_pnl_reconciliation_mismatch_missing_fill():
    """持仓数量增加但无对应成交 (缺失 fill) → 缺口超容差 → MISMATCH。"""
    auditor = DailyAuditor(AuditConfig(pnl_tolerance=0.0001))
    prev = [pos("600000", 100, 10.0, 10.0)]
    # 持仓从 100 增至 110, 但 fills 为空 (10 股来源不明 = 缺失成交)
    now = [pos("600000", 110, 10.0, 12.0)]
    recon = auditor.reconcile_pnl(prev, now, [], nav=1_000.0, now=T0)
    # MV_prev=1000, MV_now=110*12=1320, trade_cash=0
    # expected = (1320-1000) - 0 = 320
    # unrealized = 110*(12-10)=220, realized=0, total=220
    # gap = 320 - 220 = 100 ; gap_pct = 100/1000 = 0.1 > 0.0001 → MISMATCH
    assert recon.expected_pnl == pytest.approx(320.0)
    assert recon.gap == pytest.approx(100.0)
    assert recon.gap_pct == pytest.approx(0.1)
    assert recon.status == ReconciliationStatus.MISMATCH


def test_pnl_reconciliation_new_position_with_entry_fill():
    """新持仓无前日快照, prev_close=avg_entry; 含买入成交 → 缺口为零。"""
    auditor = DailyAuditor()
    now = [pos("600000", 100, 10.0, 11.0)]  # 无前日快照
    # 新持仓必有买入成交: 买入 100 @ 10
    fills = [fill("600000", 100, 10.0)]
    recon = auditor.reconcile_pnl([], now, fills, nav=10_000.0, now=T0)
    # MV_prev=0, MV_now=1100, trade_cash=100*10=1000
    # expected = (1100-0) - 1000 = 100
    assert recon.expected_pnl == pytest.approx(100.0)
    # prev_close=avg_entry=10 → unrealized = 100*(11-10)=100
    assert recon.unrealized_pnl == pytest.approx(100.0)
    assert recon.gap == pytest.approx(0.0)
    assert recon.status == ReconciliationStatus.MATCH


def test_pnl_reconciliation_new_position_missing_fill_mismatch():
    """新持仓但无买入成交 (缺失 fill) → MISMATCH。"""
    auditor = DailyAuditor(AuditConfig(pnl_tolerance=0.0001))
    now = [pos("600000", 100, 10.0, 11.0)]  # 无前日快照, 无成交
    recon = auditor.reconcile_pnl([], now, [], nav=1_000.0, now=T0)
    # MV_prev=0, MV_now=1100, trade_cash=0 → expected=1100
    # unrealized=100*(11-10)=100, total=100, gap=1000 → MISMATCH
    assert recon.expected_pnl == pytest.approx(1100.0)
    assert recon.gap == pytest.approx(1000.0)
    assert recon.status == ReconciliationStatus.MISMATCH


def test_pnl_reconciliation_zero_nav_gap_pct_zero():
    """nav=0 时 gap_pct=0 (避免除零)。"""
    auditor = DailyAuditor()
    prev = [pos("600000", 100, 10.0, 10.0)]
    now = [pos("600000", 100, 8.0, 12.0)]
    recon = auditor.reconcile_pnl(prev, now, [], nav=0.0, now=T0)
    assert recon.gap_pct == 0.0
    assert recon.status == ReconciliationStatus.MATCH


def test_pnl_reconciliation_nan_nav_rejected():
    auditor = DailyAuditor()
    with pytest.raises(InvalidAuditInputError):
        auditor.reconcile_pnl([], [], [], nav=float("nan"), now=T0)


def test_pnl_reconciliation_nan_qty_rejected():
    auditor = DailyAuditor()
    bad = [pos("600000", float("nan"), 10.0, 10.0)]
    with pytest.raises(InvalidAuditInputError):
        auditor.reconcile_pnl([], bad, [], nav=1_000.0, now=T0)


def test_pnl_reconciliation_multi_symbol():
    auditor = DailyAuditor()
    prev = [pos("A", 100, 10.0, 10.0), pos("B", 50, 20.0, 20.0)]
    now = [pos("A", 100, 10.0, 11.0), pos("B", 50, 20.0, 19.0)]
    recon = auditor.reconcile_pnl(prev, now, [], nav=10_000.0, now=T0)
    # expected = 100*(11-10) + 50*(19-20) = 100 - 50 = 50
    assert recon.expected_pnl == pytest.approx(50.0)


# ── 归因偏差检测 ──────────────────────────────────────────────────────────────


def _make_decomp(factor_var, total_var):
    """构造一个有因子模型的 DecompositionResult。"""
    cov = np.array([[total_var]])
    w = np.array([1.0])
    return DecompositionResult(
        total_risk=float(np.sqrt(total_var)),
        total_variance=total_var,
        mcr=np.array([np.sqrt(total_var)]),
        ccr=np.array([np.sqrt(total_var)]),
        pct_contribution=np.array([1.0]),
        weights=w,
        timestamp=T0,
        factor_variance=factor_var,
        factor_risk=float(np.sqrt(factor_var)),
        residual_variance=total_var - factor_var,
        residual_risk=float(np.sqrt(max(total_var - factor_var, 0.0))),
    )


def test_attribution_no_decomposition_not_applicable():
    auditor = DailyAuditor()
    result = auditor.detect_attribution_bias(None, 100.0, 50.0, now=T0)
    assert result.status == AttributionStatus.NOT_APPLICABLE
    assert result.predicted_factor_pct is None
    assert result.bias == 0.0


def test_attribution_decomp_without_factor_model_not_applicable():
    """DecompositionResult 无 factor_variance → NOT_APPLICABLE。"""
    auditor = DailyAuditor()
    decomp = RiskDecomposer().decompose(np.eye(2), np.array([0.5, 0.5]), now=T0)
    result = auditor.detect_attribution_bias(decomp, 100.0, 50.0, now=T0)
    assert result.status == AttributionStatus.NOT_APPLICABLE


def test_attribution_aligned():
    """预测=实际 → ALIGNED。"""
    auditor = DailyAuditor()
    # factor_var=40, total_var=100 → predicted=0.4
    decomp = _make_decomp(40.0, 100.0)
    # actual: factor=40, residual=60 → actual=40/100=0.4
    result = auditor.detect_attribution_bias(decomp, 40.0, 60.0, now=T0)
    assert result.predicted_factor_pct == pytest.approx(0.4)
    assert result.actual_factor_pct == pytest.approx(0.4)
    assert result.bias == pytest.approx(0.0)
    assert result.status == AttributionStatus.ALIGNED


def test_attribution_biased():
    """偏差超阈值 → BIASED。"""
    auditor = DailyAuditor(AuditConfig(bias_threshold=0.1))
    # predicted=0.6, actual=0.4 → bias=0.2 > 0.1
    decomp = _make_decomp(60.0, 100.0)
    result = auditor.detect_attribution_bias(decomp, 40.0, 60.0, now=T0)
    assert result.bias == pytest.approx(0.2)
    assert result.status == AttributionStatus.BIASED


def test_attribution_zero_pnl_aligned():
    """实际 PnL 全零 → 偏差=0, ALIGNED。"""
    auditor = DailyAuditor()
    decomp = _make_decomp(40.0, 100.0)
    result = auditor.detect_attribution_bias(decomp, 0.0, 0.0, now=T0)
    assert result.actual_factor_pct == 0.0
    assert result.bias == 0.0
    assert result.status == AttributionStatus.ALIGNED


def test_attribution_negative_pnl():
    """负 PnL (亏损): 占比用绝对值计算。"""
    auditor = DailyAuditor()
    decomp = _make_decomp(50.0, 100.0)  # predicted=0.5
    # factor=-30, residual=-70 → actual=-30/100=-0.3, bias=0.5-(-0.3)=0.8
    result = auditor.detect_attribution_bias(decomp, -30.0, -70.0, now=T0)
    assert result.actual_factor_pct == pytest.approx(-0.3)
    assert result.bias == pytest.approx(0.8)
    assert result.status == AttributionStatus.BIASED


# ── 合规检查 ──────────────────────────────────────────────────────────────────


def test_compliance_all_ok():
    auditor = DailyAuditor()
    consumptions = [
        consumption("VAR_95", 1_000_000.0, 500_000.0),  # 50%
        consumption("SECTOR", 0.3, 0.1),  # 33%
    ]
    report = auditor.run_compliance_check(consumptions, now=T0)
    assert report.overall_status == AuditStatus.PASS
    assert all(c.status == CheckStatus.OK for c in report.checks)


def test_compliance_warning():
    auditor = DailyAuditor(AuditConfig(warn_ratio=0.8))
    consumptions = [consumption("VAR_95", 1_000_000.0, 850_000.0)]  # 85% > 0.8
    report = auditor.run_compliance_check(consumptions, now=T0)
    assert report.overall_status == AuditStatus.PASS_WITH_WARNINGS
    assert report.checks[0].status == CheckStatus.WARNING


def test_compliance_breached():
    auditor = DailyAuditor()
    consumptions = [consumption("VAR_95", 1_000_000.0, 1_200_000.0)]  # 120%
    report = auditor.run_compliance_check(consumptions, now=T0)
    assert report.overall_status == AuditStatus.FAIL
    assert report.checks[0].status == CheckStatus.BREACHED
    assert report.checks[0].utilization == pytest.approx(1.2)


def test_compliance_mixed_breach_dominates():
    """有 BREACHED + WARNING → overall=FAIL。"""
    auditor = DailyAuditor(AuditConfig(warn_ratio=0.8))
    consumptions = [
        consumption("VAR_95", 1_000_000.0, 850_000.0),  # WARNING
        consumption("GROSS", 5_000_000.0, 6_000_000.0),  # BREACHED
    ]
    report = auditor.run_compliance_check(consumptions, now=T0)
    assert report.overall_status == AuditStatus.FAIL


def test_compliance_zero_value_no_consumption_ok():
    auditor = DailyAuditor()
    consumptions = [consumption("UNUSED", 0.0, 0.0)]
    report = auditor.run_compliance_check(consumptions, now=T0)
    assert report.checks[0].status == CheckStatus.OK
    assert report.overall_status == AuditStatus.PASS


def test_compliance_zero_value_with_consumption_breached():
    """value=0 但有消耗 → BREACHED (不应有消耗)。"""
    auditor = DailyAuditor()
    consumptions = [consumption("FORBIDDEN", 0.0, 100.0)]
    report = auditor.run_compliance_check(consumptions, now=T0)
    assert report.checks[0].status == CheckStatus.BREACHED
    assert math.isinf(report.checks[0].utilization)


def test_compliance_nan_rejected():
    auditor = DailyAuditor()
    with pytest.raises(InvalidAuditInputError):
        auditor.run_compliance_check([consumption("VAR_95", float("nan"), 100.0)], now=T0)


def test_compliance_negative_consumed_rejected():
    auditor = DailyAuditor()
    with pytest.raises(InvalidAuditInputError):
        auditor.run_compliance_check([consumption("VAR_95", 1_000.0, -50.0)], now=T0)


def test_compliance_empty_list_pass():
    auditor = DailyAuditor()
    report = auditor.run_compliance_check([], now=T0)
    assert report.overall_status == AuditStatus.PASS
    assert report.checks == []


# ── 日终检查清单 ──────────────────────────────────────────────────────────────


def _good_recon():
    auditor = DailyAuditor()
    prev = [pos("A", 100, 10.0, 10.0)]
    now = [pos("A", 100, 10.0, 11.0)]
    return auditor.reconcile_pnl(prev, now, [], nav=10_000.0, now=T0)


def test_checklist_all_pass():
    auditor = DailyAuditor()
    recon = _good_recon()
    compliance = auditor.run_compliance_check([consumption("VAR_95", 1_000_000.0, 500_000.0)], now=T0)
    checklist = auditor.run_daily_checklist(
        [pos("A", 100, 10.0, 10.0)],
        [pos("A", 100, 10.0, 11.0)],
        recon,
        compliance,
        kill_switch_state="CLOSED",
        data_completeness=True,
        now=T0,
    )
    assert len(checklist) == 5
    assert all(c.status == CheckStatus.PASS for c in checklist)


def test_checklist_kill_switch_open_fails():
    auditor = DailyAuditor()
    recon = _good_recon()
    compliance = auditor.run_compliance_check([], now=T0)
    checklist = auditor.run_daily_checklist(
        [],
        [],
        recon,
        compliance,
        kill_switch_state="OPEN",
        data_completeness=True,
        now=T0,
    )
    ks = [c for c in checklist if c.name == "Kill Switch状态"][0]
    assert ks.status == CheckStatus.FAIL


def test_checklist_data_incomplete_fails():
    auditor = DailyAuditor()
    recon = _good_recon()
    compliance = auditor.run_compliance_check([], now=T0)
    checklist = auditor.run_daily_checklist(
        [],
        [],
        recon,
        compliance,
        kill_switch_state="CLOSED",
        data_completeness=False,
        now=T0,
    )
    di = [c for c in checklist if c.name == "数据完整性"][0]
    assert di.status == CheckStatus.FAIL


def test_checklist_pnl_mismatch_fails():
    auditor = DailyAuditor(AuditConfig(pnl_tolerance=0.0001))
    # 缺失成交: 持仓 100→110 但无 fill
    prev = [pos("A", 100, 10.0, 10.0)]
    now = [pos("A", 110, 10.0, 12.0)]
    recon = auditor.reconcile_pnl(prev, now, [], nav=1_000.0, now=T0)
    assert recon.status == ReconciliationStatus.MISMATCH
    compliance = auditor.run_compliance_check([], now=T0)
    checklist = auditor.run_daily_checklist(
        prev,
        now,
        recon,
        compliance,
        kill_switch_state="CLOSED",
        data_completeness=True,
        now=T0,
    )
    pnl_item = [c for c in checklist if c.name == "PnL对账"][0]
    assert pnl_item.status == CheckStatus.FAIL


def test_checklist_limit_warning_warns():
    auditor = DailyAuditor(AuditConfig(warn_ratio=0.8))
    recon = _good_recon()
    compliance = auditor.run_compliance_check([consumption("VAR_95", 1_000_000.0, 850_000.0)], now=T0)
    checklist = auditor.run_daily_checklist(
        [],
        [],
        recon,
        compliance,
        kill_switch_state="CLOSED",
        data_completeness=True,
        now=T0,
    )
    lim = [c for c in checklist if c.name == "限额合规"][0]
    assert lim.status == CheckStatus.WARNING


# ── 完整审计 audit() ──────────────────────────────────────────────────────────


def test_audit_clean_pass():
    auditor = DailyAuditor()
    prev = [pos("A", 100, 10.0, 10.0)]
    now = [pos("A", 100, 10.0, 11.0)]
    report = _do_audit(
        auditor,
        trading_date=D0,
        portfolio_id="PF-001",
        positions_prev=prev,
        positions_now=now,
        fills=[],
        nav=10_000.0,
        consumptions=[consumption("VAR_95", 1_000_000.0, 500_000.0)],
        kill_switch_state="CLOSED",
        data_completeness=True,
        now=T0,
    )
    assert isinstance(report, DailyAuditReport)
    assert report.overall_status == AuditStatus.PASS
    assert report.issues == []
    assert report.trading_date == D0
    assert report.portfolio_id == "PF-001"
    assert len(report.checklist) == 5


def test_audit_with_failures():
    auditor = DailyAuditor(AuditConfig(pnl_tolerance=0.0001))
    prev = [pos("A", 100, 10.0, 10.0)]
    now = [pos("A", 110, 10.0, 12.0)]  # 缺失成交 → PnL MISMATCH
    report = _do_audit(
        auditor,
        trading_date=D0,
        portfolio_id="PF-002",
        positions_prev=prev,
        positions_now=now,
        fills=[],
        nav=1_000.0,
        consumptions=[consumption("VAR_95", 1_000.0, 1_500.0)],  # BREACHED
        kill_switch_state="OPEN",
        data_completeness=False,
        now=T0,
    )
    assert report.overall_status == AuditStatus.FAIL
    # 应有多个 issue: PnL mismatch + limit breach + kill switch + data integrity
    categories = {i.category for i in report.issues}
    assert "PNL_RECONCILIATION" in categories
    assert "LIMIT_BREACH" in categories
    assert "KILL_SWITCH" in categories
    assert "DATA_INTEGRITY" in categories
    assert all(i.status.value == "OPEN" for i in report.issues)


def test_audit_idempotent_same_input_same_report():
    """幂等: 相同输入产生等价报告 (除 timestamp 外字段相等)。"""
    auditor = DailyAuditor()
    prev = [pos("A", 100, 10.0, 10.0)]
    now = [pos("A", 100, 10.0, 11.0)]
    args = dict(
        trading_date=D0,
        portfolio_id="PF-001",
        positions_prev=prev,
        positions_now=now,
        fills=[],
        nav=10_000.0,
        consumptions=[consumption("VAR_95", 1_000_000.0, 500_000.0)],
        kill_switch_state="CLOSED",
        data_completeness=True,
        now=T0,
    )
    r1 = _do_audit(auditor, **args)
    r2 = _do_audit(auditor, **args)
    assert r1.overall_status == r2.overall_status
    assert r1.pnl_reconciliation.total_pnl == r2.pnl_reconciliation.total_pnl
    assert r1.issues == r2.issues
    assert len(r1.checklist) == len(r2.checklist)


def test_audit_with_attribution_bias_issue():
    auditor = DailyAuditor(AuditConfig(bias_threshold=0.1))
    decomp = _make_decomp(60.0, 100.0)  # predicted=0.6
    prev = [pos("A", 100, 10.0, 10.0)]
    now = [pos("A", 100, 10.0, 11.0)]
    report = _do_audit(
        auditor,
        trading_date=D0,
        portfolio_id="PF-003",
        positions_prev=prev,
        positions_now=now,
        fills=[],
        nav=10_000.0,
        consumptions=[],
        decomposition=decomp,
        actual_factor_pnl=40.0,
        actual_residual_pnl=60.0,  # actual=0.4, bias=0.2
        kill_switch_state="CLOSED",
        data_completeness=True,
        now=T0,
    )
    # 归因偏差不直接影响 checklist (5项不含归因), 但会登记 issue
    assert report.attribution_bias.status == AttributionStatus.BIASED
    cats = {i.category for i in report.issues}
    assert "ATTRIBUTION_BIAS" in cats


def test_audit_no_decomposition_attribution_none():
    auditor = DailyAuditor()
    prev = [pos("A", 100, 10.0, 10.0)]
    now = [pos("A", 100, 10.0, 11.0)]
    report = _do_audit(
        auditor,
        trading_date=D0,
        portfolio_id="PF-004",
        positions_prev=prev,
        positions_now=now,
        fills=[],
        nav=10_000.0,
        consumptions=[],
        decomposition=None,
        kill_switch_state="CLOSED",
        data_completeness=True,
        now=T0,
    )
    assert report.attribution_bias is not None
    assert report.attribution_bias.status == AttributionStatus.NOT_APPLICABLE


def test_audit_status_pass_with_warnings():
    """有 WARNING 无 FAIL → PASS_WITH_WARNINGS。"""
    auditor = DailyAuditor(AuditConfig(warn_ratio=0.8))
    prev = [pos("A", 100, 10.0, 10.0)]
    now = [pos("A", 100, 10.0, 11.0)]
    report = _do_audit(
        auditor,
        trading_date=D0,
        portfolio_id="PF-005",
        positions_prev=prev,
        positions_now=now,
        fills=[],
        nav=10_000.0,
        consumptions=[consumption("VAR_95", 1_000_000.0, 850_000.0)],  # WARNING
        kill_switch_state="CLOSED",
        data_completeness=True,
        now=T0,
    )
    assert report.overall_status == AuditStatus.PASS_WITH_WARNINGS


# ── AuditRiskMetricsReport ─────────────────────────────────────────────────────────


def test_risk_metrics_report_fields():
    auditor = DailyAuditor()
    prev = [pos("A", 100, 10.0, 10.0)]
    now = [pos("A", 100, 10.0, 11.0)]
    report = _do_audit(
        auditor,
        trading_date=D0,
        portfolio_id="PF-001",
        positions_prev=prev,
        positions_now=now,
        fills=[],
        nav=10_000.0,
        consumptions=[consumption("VAR_95", 1_000_000.0, 500_000.0)],
        kill_switch_state="CLOSED",
        data_completeness=True,
        now=T0,
    )
    rmr = auditor.generate_risk_metrics_report(report, now=T0)
    assert isinstance(rmr, AuditRiskMetricsReport)
    assert rmr.portfolio_id == "PF-001"
    assert rmr.trading_date == D0
    assert rmr.total_pnl == pytest.approx(100.0)
    assert rmr.audit_status == AuditStatus.PASS
    assert rmr.compliance_status == AuditStatus.PASS
    assert rmr.issues_count == 0
    assert rmr.high_severity_count == 0
    assert rmr.report_id.startswith("RMR-PF-001-")


def test_risk_metrics_report_counts_high_severity():
    auditor = DailyAuditor(AuditConfig(pnl_tolerance=0.0001))
    prev = [pos("A", 100, 10.0, 10.0)]
    now = [pos("A", 110, 10.0, 12.0)]  # 缺失成交 → PnL MISMATCH (HIGH)
    report = _do_audit(
        auditor,
        trading_date=D0,
        portfolio_id="PF-002",
        positions_prev=prev,
        positions_now=now,
        fills=[],
        nav=1_000.0,
        consumptions=[consumption("VAR_95", 1_000.0, 1_500.0)],  # BREACHED (HIGH)
        kill_switch_state="CLOSED",
        data_completeness=False,  # HIGH
        now=T0,
    )
    rmr = auditor.generate_risk_metrics_report(report, now=T0)
    # PnL mismatch(HIGH) + limit breach(HIGH) + data integrity(HIGH) = 3 HIGH
    assert rmr.high_severity_count == 3
    assert rmr.issues_count >= 3
    assert rmr.audit_status == AuditStatus.FAIL


def test_risk_metrics_report_to_dict_serializable():
    auditor = DailyAuditor()
    report = _do_audit(
        auditor,
        trading_date=D0,
        portfolio_id="PF-X",
        positions_prev=[pos("A", 100, 10.0, 10.0)],
        positions_now=[pos("A", 100, 10.0, 11.0)],
        fills=[],
        nav=10_000.0,
        consumptions=[],
        kill_switch_state="CLOSED",
        data_completeness=True,
        now=T0,
    )
    rmr = auditor.generate_risk_metrics_report(report, now=T0)
    d = rmr.to_dict()
    assert d["portfolio_id"] == "PF-X"
    assert d["audit_status"] == "PASS"


def test_audit_report_to_dict_serializable():
    auditor = DailyAuditor()
    report = _do_audit(
        auditor,
        trading_date=D0,
        portfolio_id="PF-X",
        positions_prev=[pos("A", 100, 10.0, 10.0)],
        positions_now=[pos("A", 100, 10.0, 11.0)],
        fills=[],
        nav=10_000.0,
        consumptions=[],
        kill_switch_state="CLOSED",
        data_completeness=True,
        now=T0,
    )
    d = report.to_dict()
    assert d["portfolio_id"] == "PF-X"
    assert d["overall_status"] == "PASS"
    assert len(d["checklist"]) == 5


# ── IssueRecord ───────────────────────────────────────────────────────────────


def test_issue_record_defaults():
    from zephyr.risk.core.daily_auditor import IssueRecord, IssueStatus

    issue = IssueRecord(
        issue_id="ISS-001",
        category="PNL_RECONCILIATION",
        severity=IssueSeverity.HIGH,
        description="test",
    )
    assert issue.root_cause == "待分析"
    assert issue.correction == "待定"
    assert issue.status == IssueStatus.OPEN


def test_issue_severity_high_for_pnl_mismatch():
    auditor = DailyAuditor(AuditConfig(pnl_tolerance=0.0001))
    prev = [pos("A", 100, 10.0, 10.0)]
    now = [pos("A", 110, 10.0, 12.0)]  # 缺失成交 → PnL MISMATCH
    report = _do_audit(
        auditor,
        trading_date=D0,
        portfolio_id="PF-1",
        positions_prev=prev,
        positions_now=now,
        fills=[],
        nav=1_000.0,
        consumptions=[],
        kill_switch_state="CLOSED",
        data_completeness=True,
        now=T0,
    )
    pnl_issues = [i for i in report.issues if i.category == "PNL_RECONCILIATION"]
    assert len(pnl_issues) == 1
    assert pnl_issues[0].severity == IssueSeverity.HIGH
