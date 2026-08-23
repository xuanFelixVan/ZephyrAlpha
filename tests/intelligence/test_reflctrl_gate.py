# [BLUEPRINT] MOD-REFLEXION_AGENT | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/12_reflexion_multi_agent.md | §4.3-P1-1
# [MODULE] tests.intelligence.test_reflctrl_gate
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/intelligence/test_reflctrl_gate.py -q
# [TTL] permanent
"""test_reflctrl_gate.py — ReflCtrl 频率闸门（12号文 §3.4/§4.3 P1-1）单元测试.

覆盖 P1-1 验收口径：
①规则外触发请求被拒（执行层无异常/战术层未到频次 → DENIED，留痕可追溯）。
②每次放行可追溯到触发规则（matched_rules 恒非空，规则 ID 对齐 §3.4 显式规则集：
L1 强制三条件 / Agent-R 四场景阈值 / HITL 低置信 / 分层频率 / L2 累积 N=5 /
频率控制决策矩阵 / 单任务反思轮次上限）。
③token 消耗统计落盘（放行才计 token，全量裁决写审计 jsonl）。
④规则可配置（ReflCtrlConfig 注入覆盖阈值生效）。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.intelligence.reflexion.reflctrl_gate import (
    DENIED_EXCELLENT_STREAK,
    DENIED_MAX_ROUNDS,
    DENIED_NO_RULE,
    DENIED_NORMAL_STREAK,
    RULE_AGENT_R_REGIME,
    RULE_AGENT_R_RISK_PARAM,
    RULE_AGENT_R_SIGNAL_SIGMA,
    RULE_AGENT_R_SLIPPAGE,
    RULE_HITL_CONFIDENCE_L1,
    RULE_HITL_CONFIDENCE_L2,
    RULE_L1_FORCE_DEVIATION,
    RULE_L1_FORCE_EXECUTION_FAILURE,
    RULE_L1_FORCE_RISK_VETO,
    RULE_L2_ACCUMULATED,
    RULE_LAYER_STRATEGIC_ALWAYS,
    RULE_LAYER_TACTICAL_NTH,
    ReflCtrlConfig,
    ReflCtrlGate,
    ReflectionRequest,
)


@pytest.fixture
def gate(tmp_path):
    return ReflCtrlGate(stats_root=tmp_path)


def _req(**overrides) -> ReflectionRequest:
    base = {
        "task_id": "task-1",
        "layer": "execution",
        "requested_level": "L1",
    }
    base.update(overrides)
    return ReflectionRequest(**base)


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class TestL1ForceRules:
    """L1 强制触发三条件：执行结果与预期偏差>20% / 风控否决 / 执行失败."""

    def test_deviation_over_20pct_forces_l1(self, gate):
        decision = gate.decide(_req(deviation_pct=25.0))
        assert decision.allowed is True
        assert RULE_L1_FORCE_DEVIATION in decision.matched_rules
        assert "L1" in decision.granted_levels

    def test_deviation_below_threshold_no_force(self, gate):
        decision = gate.decide(_req(deviation_pct=20.0))
        assert decision.allowed is False
        assert RULE_L1_FORCE_DEVIATION not in decision.matched_rules

    def test_risk_veto_forces_l1(self, gate):
        decision = gate.decide(_req(risk_vetoed=True))
        assert decision.allowed is True
        assert RULE_L1_FORCE_RISK_VETO in decision.matched_rules

    def test_execution_failure_forces_l1_and_matrix_l2(self, gate):
        decision = gate.decide(_req(outcome="failure"))
        assert decision.allowed is True
        assert RULE_L1_FORCE_EXECUTION_FAILURE in decision.matched_rules
        # 决策矩阵：失败→执行 L1+立即 L2+触发 L3
        assert "L1" in decision.granted_levels
        assert "L2" in decision.granted_levels
        assert "L3" in decision.granted_levels


class TestAgentRRules:
    """Agent-R 轨迹内异常四场景阈值（盘后轨迹复盘异常检测规则）."""

    def test_signal_sigma_deviation(self, gate):
        decision = gate.decide(_req(signal_sigma_deviation=2.5))
        assert decision.allowed is True
        assert RULE_AGENT_R_SIGNAL_SIGMA in decision.matched_rules

    def test_slippage_ratio(self, gate):
        decision = gate.decide(_req(slippage_ratio=2.1))
        assert decision.allowed is True
        assert RULE_AGENT_R_SLIPPAGE in decision.matched_rules

    def test_risk_param_deviation(self, gate):
        decision = gate.decide(_req(risk_param_deviation_pct=11.0))
        assert decision.allowed is True
        assert RULE_AGENT_R_RISK_PARAM in decision.matched_rules

    def test_regime_transition_untriggered(self, gate):
        decision = gate.decide(_req(regime_transition_prob_pct=95.0, regime_triggered=False))
        assert decision.allowed is True
        assert RULE_AGENT_R_REGIME in decision.matched_rules

    def test_regime_transition_triggered_no_rule(self, gate):
        decision = gate.decide(_req(regime_transition_prob_pct=95.0, regime_triggered=True))
        assert decision.allowed is False
        assert RULE_AGENT_R_REGIME not in decision.matched_rules


class TestHitlConfidenceRules:
    """HITL 低置信触发：50-69%→L1；<50%→L1+L2."""

    def test_confidence_50_to_69_triggers_l1(self, gate):
        decision = gate.decide(_req(eval_confidence=0.6))
        assert decision.allowed is True
        assert RULE_HITL_CONFIDENCE_L1 in decision.matched_rules
        assert "L2" not in decision.granted_levels

    def test_confidence_below_50_triggers_l1_l2(self, gate):
        decision = gate.decide(_req(eval_confidence=0.4))
        assert decision.allowed is True
        assert RULE_HITL_CONFIDENCE_L2 in decision.matched_rules
        assert "L2" in decision.granted_levels


class TestLayerFrequency:
    """分层频率：执行层仅异常 / 战术层每 5 次同类 L1 / 战略层每次任务 L1."""

    def test_execution_layer_no_anomaly_denied(self, gate):
        decision = gate.decide(_req(layer="execution"))
        assert decision.allowed is False
        assert decision.denied_by == DENIED_NO_RULE

    def test_tactical_layer_nth_task_allowed(self, gate):
        decision = gate.decide(_req(layer="tactical", similar_task_count=5))
        assert decision.allowed is True
        assert RULE_LAYER_TACTICAL_NTH in decision.matched_rules

    def test_tactical_layer_non_nth_denied(self, gate):
        decision = gate.decide(_req(layer="tactical", similar_task_count=3))
        assert decision.allowed is False
        assert decision.denied_by == DENIED_NO_RULE

    def test_strategic_layer_every_task_allowed(self, gate):
        decision = gate.decide(_req(layer="strategic"))
        assert decision.allowed is True
        assert RULE_LAYER_STRATEGIC_ALWAYS in decision.matched_rules

    def test_l2_accumulated_count(self, gate):
        decision = gate.decide(
            _req(layer="tactical", requested_level="L2", similar_task_count=5)
        )
        assert decision.allowed is True
        assert RULE_L2_ACCUMULATED in decision.matched_rules
        assert "L2" in decision.granted_levels


class TestDecisionMatrix:
    """频率控制决策矩阵：连续优秀≥5 跳过 L1 / 正常≥3 仅 L2 聚合 / 严重偏差 L1+L2."""

    def test_excellent_streak_skips_l1(self, gate):
        decision = gate.decide(_req(outcome="success", excellent_streak=5))
        assert decision.allowed is False
        assert decision.denied_by == DENIED_EXCELLENT_STREAK

    def test_forced_rule_beats_excellent_streak(self, gate):
        decision = gate.decide(_req(outcome="success", excellent_streak=6, risk_vetoed=True))
        assert decision.allowed is True
        assert RULE_L1_FORCE_RISK_VETO in decision.matched_rules

    def test_normal_streak_l2_only(self, gate):
        decision = gate.decide(_req(outcome="success", normal_streak=3))
        assert decision.allowed is False
        assert decision.denied_by == DENIED_NORMAL_STREAK

    def test_severe_deviation_grants_l1_l2(self, gate):
        decision = gate.decide(_req(severity="severe", deviation_pct=25.0))
        assert decision.allowed is True
        assert "L1" in decision.granted_levels
        assert "L2" in decision.granted_levels


class TestMaxRounds:
    """单任务反思轮次上限（可配置）."""

    def test_max_rounds_denies_even_with_forced_rule(self, gate):
        decision = gate.decide(_req(risk_vetoed=True, reflection_round=3))
        assert decision.allowed is False
        assert decision.denied_by == DENIED_MAX_ROUNDS

    def test_max_rounds_configurable(self, tmp_path):
        gate = ReflCtrlGate(
            config=ReflCtrlConfig(max_rounds_per_task=5), stats_root=tmp_path
        )
        decision = gate.decide(_req(risk_vetoed=True, reflection_round=3))
        assert decision.allowed is True


class TestConfigurability:
    """规则可配置：注入阈值覆盖生效."""

    def test_custom_deviation_threshold(self, tmp_path):
        gate = ReflCtrlGate(
            config=ReflCtrlConfig(deviation_force_pct=50.0), stats_root=tmp_path
        )
        decision = gate.decide(_req(deviation_pct=25.0))
        assert decision.allowed is False
        decision = gate.decide(_req(deviation_pct=55.0))
        assert decision.allowed is True
        assert RULE_L1_FORCE_DEVIATION in decision.matched_rules


class TestAuditAndTokenStats:
    """可审计：放行可追溯触发规则；token 消耗统计落盘."""

    def test_every_allowed_decision_traceable(self, gate):
        decision = gate.decide(_req(risk_vetoed=True))
        assert decision.allowed is True
        assert len(decision.matched_rules) >= 1

    def test_decision_audit_written_for_allow_and_deny(self, gate, tmp_path):
        gate.decide(_req(risk_vetoed=True))
        gate.decide(_req())
        records = _read_jsonl(tmp_path / "reflctrl_decisions.jsonl")
        assert len(records) == 2
        assert records[0]["allowed"] is True
        assert records[0]["matched_rules"]
        assert records[1]["allowed"] is False
        assert records[1]["denied_by"] == DENIED_NO_RULE

    def test_token_stats_only_on_allow(self, gate, tmp_path):
        gate.decide(_req(risk_vetoed=True, estimated_tokens=800))
        gate.decide(_req())  # 拒绝不计 token
        stats = _read_jsonl(tmp_path / "reflctrl_token_stats.jsonl")
        assert len(stats) == 1
        assert stats[0]["estimated_tokens"] == 800
        assert stats[0]["task_id"] == "task-1"
        assert gate.total_estimated_tokens() == 800


class TestInputValidation:
    """非法输入 fail-closed."""

    def test_invalid_layer_raises(self, gate):
        with pytest.raises(ValueError, match="layer"):
            gate.decide(_req(layer="mid-layer"))

    def test_invalid_level_raises(self, gate):
        with pytest.raises(ValueError, match="requested_level"):
            gate.decide(_req(requested_level="L9"))
