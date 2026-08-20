# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.lifecycle.test_retirement_workflow
# [DOMAIN] D_GOVERNANCE
# [A_module] module_id=MOD-TEST-GOV-RETWF | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""退役 5 步工作流编排单元测试（61 号 §3.9）。

覆盖:
  - Step1 触发：无告警/未达持续阈值 → MONITORING；持续告警 → OBSERVING + 状态端口调用
  - Step2 诊断：端口供给三元组；oos_sharpe NaN → 抛错
  - Step3 决策矩阵：REOPTIMIZE / PAUSE_CUT_SIZE / RETIRE 三分支 + 边界值（0 / -0.2）
  - Step4 评审制铁律：RETIRE+human_approved → 顺序执行四动作+ARCHIVED；
    RETIRE 未批准 → 零执行 + escalation_required；PAUSE/REOPTIMIZE 批准也不执行
  - 可选端口 None → skipped_ports 留痕不抛
  - Step5 五骑士归因：默认规则（mismatch→REGIME_CHANGE，否则 OVERFITTING）+ 显式指定 + record_methodology
  - 输入非法：空 strategy_id / 阈值 <1 → RetirementWorkflowError
"""
from __future__ import annotations

import pytest

from zephyr.governance.lifecycle_governance.retirement_workflow import (
    DecayAlert,
    DecayKnight,
    RetirementDecision,
    RetirementDiagnosis,
    RetirementPorts,
    RetirementWorkflowError,
    classify_decay_knight,
    decide_retirement,
    run_retirement_workflow,
)


def _ports(
    *,
    alerts=(),
    oos_sharpe=0.5,
    peers=False,
    mismatch=False,
    with_execution=True,
    with_state=True,
    with_methodology=True,
):
    """构造 stub 端口；calls 列表记录全部执行动作（顺序断言用）。"""
    calls: list[tuple] = []
    return RetirementPorts(
        get_decay_alerts=lambda sid: alerts,
        run_backtest=lambda sid, days: oos_sharpe,
        check_peers=lambda sid: peers,
        get_regime_mismatch=lambda sid: mismatch,
        scale_position=(lambda sid, r: calls.append(("scale", r))) if with_execution else None,
        disable_new_entries=(lambda sid: calls.append(("disable",))) if with_execution else None,
        flatten_positions=(lambda sid: calls.append(("flatten",))) if with_execution else None,
        archive=(lambda sid: calls.append(("archive",))) if with_execution else None,
        set_lifecycle_state=(lambda sid, st: calls.append(("state", st))) if with_state else None,
        record_methodology=(lambda sid, k, d: calls.append(("methodology", k))) if with_methodology else None,
    ), calls


SUSTAINED = (DecayAlert("rolling_sharpe", consecutive_days=12),)
NOT_SUSTAINED = (DecayAlert("rolling_sharpe", consecutive_days=3),)


class TestTrigger:
    def test_no_alerts_monitoring(self):
        ports, calls = _ports(alerts=())
        result = run_retirement_workflow("s1", ports)
        assert result.state == "MONITORING"
        assert result.decision is None
        assert calls == []  # 未触发 → 零端口调用

    def test_below_sustained_threshold(self):
        ports, calls = _ports(alerts=NOT_SUSTAINED)
        result = run_retirement_workflow("s1", ports)
        assert result.state == "MONITORING"
        assert calls == []

    def test_sustained_alert_observing(self):
        ports, calls = _ports(alerts=SUSTAINED)
        result = run_retirement_workflow("s1", ports)
        assert result.state == "OBSERVING"
        assert result.sustained_alerts == ("rolling_sharpe",)
        assert ("state", "OBSERVING") in calls

    def test_boundary_exactly_10_days(self):
        """边界：consecutive_days == sustained_min_days（>=）→ 触发。"""
        ports, _ = _ports(alerts=(DecayAlert("m1", consecutive_days=10),))
        result = run_retirement_workflow("s1", ports, sustained_min_days=10)
        assert result.state == "OBSERVING"


class TestDiagnosis:
    def test_nan_oos_sharpe_raises(self):
        ports, _ = _ports(alerts=SUSTAINED, oos_sharpe=float("nan"))
        with pytest.raises(RetirementWorkflowError):
            run_retirement_workflow("s1", ports)

    def test_diagnosis_supplied_by_ports(self):
        ports, _ = _ports(alerts=SUSTAINED, oos_sharpe=-0.5, peers=True, mismatch=True)
        result = run_retirement_workflow("s1", ports)
        assert result.diagnosis == RetirementDiagnosis(
            oos_sharpe=-0.5, is_regime_wide=True, regime_mismatch=True
        )


class TestDecisionMatrix:
    """三选一矩阵全分支 + 边界（61 号 §3.9）。"""

    @pytest.mark.parametrize(
        "oos,wide,mismatch,expected",
        [
            (0.5, False, True, RetirementDecision.REOPTIMIZE),   # oos>0 & mismatch
            (0.5, False, False, RetirementDecision.PAUSE_CUT_SIZE),  # oos>0 非 mismatch → pause
            (0.0, False, False, RetirementDecision.PAUSE_CUT_SIZE),  # 边界 oos=0 > -0.2
            (-0.2, False, False, RetirementDecision.RETIRE),     # 边界 oos=-0.2 不> -0.2
            (-0.1, True, False, RetirementDecision.RETIRE),      # 全策略坏 → retire
            (0.5, True, False, RetirementDecision.RETIRE),       # oos>0 但全策略坏且非 mismatch → retire
            (-0.5, False, True, RetirementDecision.RETIRE),      # oos<0 mismatch 也非 reoptimize
        ],
    )
    def test_matrix(self, oos, wide, mismatch, expected):
        d = RetirementDiagnosis(oos_sharpe=oos, is_regime_wide=wide, regime_mismatch=mismatch)
        assert decide_retirement(d) is expected


class TestRetireExecution:
    def test_retire_approved_executes_in_order(self):
        ports, calls = _ports(alerts=SUSTAINED, oos_sharpe=-0.5)
        result = run_retirement_workflow("s1", ports, human_approved=True)
        assert result.decision is RetirementDecision.RETIRE
        # 执行顺序固定：仓位减半→暂停新建仓→平掉存量→归档→ARCHIVED
        assert calls == [
            ("state", "OBSERVING"),
            ("scale", 0.5),
            ("disable",),
            ("flatten",),
            ("archive",),
            ("state", "ARCHIVED"),
            ("methodology", DecayKnight.OVERFITTING),
        ]
        assert result.executed_actions[:5] == (
            "scale_position_0.5", "disable_new_entries", "flatten_positions",
            "archive", "set_state_archived",
        )
        assert result.escalation_required is False

    def test_retire_not_approved_no_execution(self):
        """评审制铁律：未批准 → 零执行 + escalation_required。"""
        ports, calls = _ports(alerts=SUSTAINED, oos_sharpe=-0.5)
        result = run_retirement_workflow("s1", ports, human_approved=False)
        assert result.decision is RetirementDecision.RETIRE
        assert result.escalation_required is True
        assert ("scale", 0.5) not in calls
        assert ("state", "ARCHIVED") not in calls
        # 复盘仍沉淀（评审材料）
        assert ("methodology", DecayKnight.OVERFITTING) in calls

    def test_pause_approved_no_execution(self):
        """PAUSE_CUT_SIZE 即使批准也不走 Step 4（Step 4 仅 RETIRE）。"""
        ports, calls = _ports(alerts=SUSTAINED, oos_sharpe=0.0)
        result = run_retirement_workflow("s1", ports, human_approved=True)
        assert result.decision is RetirementDecision.PAUSE_CUT_SIZE
        assert ("scale", 0.5) not in calls
        assert result.executed_actions == ("record_methodology",)

    def test_optional_ports_none_skipped(self):
        """可选执行端口 None → skipped_ports 留痕，不抛。"""
        ports, calls = _ports(alerts=SUSTAINED, oos_sharpe=-0.5, with_execution=False, with_state=False)
        result = run_retirement_workflow("s1", ports, human_approved=True)
        assert result.decision is RetirementDecision.RETIRE
        assert set(result.skipped_ports) == {
            "scale_position_0.5", "disable_new_entries", "flatten_positions", "archive",
        }
        assert ("state", "ARCHIVED") not in calls


class TestKnight:
    def test_default_regime_change(self):
        d = RetirementDiagnosis(oos_sharpe=-0.5, is_regime_wide=False, regime_mismatch=True)
        assert classify_decay_knight(d) is DecayKnight.REGIME_CHANGE

    def test_default_overfitting(self):
        d = RetirementDiagnosis(oos_sharpe=-0.5, is_regime_wide=False, regime_mismatch=False)
        assert classify_decay_knight(d) is DecayKnight.OVERFITTING

    def test_explicit_knight_overrides(self):
        ports, calls = _ports(alerts=SUSTAINED, oos_sharpe=-0.5)
        result = run_retirement_workflow(
            "s1", ports, human_approved=True, knight=DecayKnight.REGULATORY_CHANGE
        )
        assert result.knight is DecayKnight.REGULATORY_CHANGE
        assert ("methodology", DecayKnight.REGULATORY_CHANGE) in calls


class TestInvalidInput:
    def test_empty_strategy_id(self):
        ports, _ = _ports()
        with pytest.raises(RetirementWorkflowError):
            run_retirement_workflow("  ", ports)

    @pytest.mark.parametrize("kw", [{"sustained_min_days": 0}, {"lookback_days": 0}])
    def test_invalid_thresholds(self, kw):
        ports, _ = _ports()
        with pytest.raises(RetirementWorkflowError):
            run_retirement_workflow("s1", ports, **kw)
