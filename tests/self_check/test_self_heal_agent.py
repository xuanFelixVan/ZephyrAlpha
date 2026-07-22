# [A_test] module_id: MOD-GOV_self_heal_agent | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_self_heal_agent
# [INVARIANTS] OODA最大5轮;熔断器3次连续失败触发;不自动修复行为审计RED
# [MODIFY-GUARD] blueprint.md §3;_fixer-registry.yaml self_heal_agent段
# [CONSUMERS] CI/CD;pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.AssertionError
# [TESTS] tests/test_self_heal_agent.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock

# 治本：auto_fix_engine_03 已迁移到 zephyr.infrastructure.auto_fix_engine（ARCH 迁移）。
# 旧路径 zephyr.security.access_control.auto_fix_engine_03 已删除。
from zephyr.infrastructure.auto_fix_engine.models import (
    FixAction,
    FixConfidence,
    FixStatus,
    ValidationResult,
)
from zephyr.infrastructure.auto_fix_engine.self_heal_agent import SelfHealAgent


class TestSelfHealAgentInstantiation:
    def test_default_max_rounds(self):
        agent = SelfHealAgent()
        assert agent._max_rounds == 5

    def test_default_circuit_threshold(self):
        agent = SelfHealAgent()
        assert agent._circuit_threshold == 3

    def test_custom_max_rounds(self):
        agent = SelfHealAgent(max_rounds=10)
        assert agent._max_rounds == 10

    def test_custom_circuit_threshold(self):
        agent = SelfHealAgent(circuit_threshold=5)
        assert agent._circuit_threshold == 5

    def test_circuit_starts_closed(self):
        agent = SelfHealAgent()
        assert agent.circuit_open is False


class TestSelfHealAgentHeal:
    def test_heal_succeeds_on_first_round_when_no_issues(self):
        agent = SelfHealAgent()
        diagnose_fn = MagicMock(return_value={"issues": []})
        fix_fn = MagicMock()
        validate_fn = MagicMock()
        action = agent.heal("target.py", diagnose_fn, fix_fn, validate_fn)
        assert action.status == FixStatus.COMPLETED
        assert action.confidence == FixConfidence.HIGH
        assert action.metadata.get("rounds") == 1

    def test_heal_succeeds_after_fix_and_validation(self):
        agent = SelfHealAgent()
        call_count = [0]

        def diagnose_fn(target):
            call_count[0] += 1
            if call_count[0] <= 1:
                return {"issues": [{"type": "drift"}]}
            return {"issues": []}

        fix_fn = MagicMock(return_value=FixAction(action_type="test", target="target.py", status=FixStatus.COMPLETED))
        validate_fn = MagicMock(return_value=ValidationResult(valid=True, check_name="test"))
        action = agent.heal("target.py", diagnose_fn, fix_fn, validate_fn)
        assert action.status == FixStatus.COMPLETED

    def test_heal_opens_circuit_after_consecutive_failures(self):
        agent = SelfHealAgent(max_rounds=10, circuit_threshold=3)
        diagnose_fn = MagicMock(return_value={"issues": [{"type": "drift"}]})
        fix_fn = MagicMock(return_value=FixAction(action_type="test", target="target.py", status=FixStatus.COMPLETED))
        validate_fn = MagicMock(return_value=ValidationResult(valid=False, check_name="test", error="still broken"))
        action = agent.heal("target.py", diagnose_fn, fix_fn, validate_fn)
        assert action.status == FixStatus.FAILED
        assert agent.circuit_open is True
        assert "Circuit breaker" in action.metadata.get("error", "")

    def test_heal_returns_failed_when_circuit_is_open(self):
        agent = SelfHealAgent()
        agent._circuit_open = True
        action = agent.heal("target.py", MagicMock(), MagicMock(), MagicMock())
        assert action.status == FixStatus.FAILED
        assert "Circuit breaker open" in action.metadata.get("error", "")

    def test_heal_exceeds_max_rounds(self):
        agent = SelfHealAgent(max_rounds=2, circuit_threshold=100)
        diagnose_fn = MagicMock(return_value={"issues": [{"type": "drift"}]})
        fix_fn = MagicMock(return_value=FixAction(action_type="test", target="target.py", status=FixStatus.COMPLETED))
        validate_fn = MagicMock(return_value=ValidationResult(valid=False, check_name="test", error="still broken"))
        action = agent.heal("target.py", diagnose_fn, fix_fn, validate_fn)
        assert action.status == FixStatus.FAILED
        assert "Max rounds" in action.metadata.get("error", "")

    def test_heal_handles_diagnose_fn_exception(self):
        agent = SelfHealAgent()
        diagnose_fn = MagicMock(side_effect=RuntimeError("diagnose failed"))
        fix_fn = MagicMock()
        validate_fn = MagicMock()
        action = agent.heal("target.py", diagnose_fn, fix_fn, validate_fn)
        assert isinstance(action, FixAction)

    def test_heal_handles_fix_fn_exception(self):
        agent = SelfHealAgent()
        diagnose_fn = MagicMock(return_value={"issues": [{"type": "config"}]})
        fix_fn = MagicMock(side_effect=RuntimeError("fix crashed"))
        validate_fn = MagicMock(return_value=ValidationResult(valid=False, check_name="test"))
        action = agent.heal("target.py", diagnose_fn, fix_fn, validate_fn)
        assert isinstance(action, FixAction)

    def test_heal_escalates_high_severity(self):
        agent = SelfHealAgent()
        diagnose_fn = MagicMock(return_value={"issues": [{"type": "security_vulnerability"}]})
        fix_fn = MagicMock()
        validate_fn = MagicMock(return_value=ValidationResult(valid=True, check_name="test"))
        action = agent.heal("target.py", diagnose_fn, fix_fn, validate_fn)
        assert isinstance(action, FixAction)


class TestSelfHealAgentResetCircuit:
    def test_reset_circuit_closes_open_circuit(self):
        agent = SelfHealAgent()
        agent._circuit_open = True
        agent._consecutive_failures = 5
        agent.reset_circuit()
        assert agent.circuit_open is False
        assert agent._consecutive_failures == 0

    def test_reset_circuit_on_fresh_agent(self):
        agent = SelfHealAgent()
        agent.reset_circuit()
        assert agent.circuit_open is False


class TestSelfHealAgentObserve:
    def test_observe_returns_dict_from_diagnose_fn(self):
        agent = SelfHealAgent()
        result = agent._observe("target.py", lambda t: {"issues": ["a"]})
        assert result == {"issues": ["a"]}

    def test_observe_converts_list_to_dict(self):
        agent = SelfHealAgent()
        result = agent._observe("target.py", lambda t: ["issue1", "issue2"])
        assert result == {"issues": ["issue1", "issue2"]}

    def test_observe_handles_exception(self):
        agent = SelfHealAgent()
        result = agent._observe("target.py", MagicMock(side_effect=Exception("boom")))
        assert "error" in result


class TestSelfHealAgentOrient:
    def test_orient_no_issues(self):
        agent = SelfHealAgent()
        result = agent._orient({"issues": []})
        assert result["action"] == "none"

    def test_orient_security_issue_is_high_severity(self):
        agent = SelfHealAgent()
        result = agent._orient({"issues": [{"type": "security_breach"}]})
        assert result["severity"] == "high"

    def test_orient_drift_issue_is_medium_severity(self):
        agent = SelfHealAgent()
        result = agent._orient({"issues": [{"type": "drift_detected"}]})
        assert result["severity"] == "medium"


class TestSelfHealAgentDecide:
    def test_decide_skip_when_no_action(self):
        agent = SelfHealAgent()
        result = agent._decide({"action": "none", "reason": "clean"})
        assert result["plan"] == "skip"

    def test_decide_escalate_high_severity(self):
        agent = SelfHealAgent()
        result = agent._decide({"action": "fix", "severity": "high"})
        assert result["plan"] == "escalate"

    def test_decide_auto_fix_low_severity(self):
        agent = SelfHealAgent()
        result = agent._decide({"action": "fix", "severity": "low"})
        assert result["plan"] == "auto_fix"
