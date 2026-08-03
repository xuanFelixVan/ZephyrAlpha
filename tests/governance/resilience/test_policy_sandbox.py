# [A_test] module_id: MOD-GOV_policy_sandbox | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_policy_sandbox
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_policy_sandbox.py
# [TTL] task_bound

from __future__ import annotations

import pytest
import yaml

from zephyr.governance.resilience_governance.policy_sandbox import PolicySandbox, SandboxTrial


class TestSandboxTrial:
    def test_fields(self):
        trial = SandboxTrial(
            policy_changes={"key": "value"},
            simulated_impact={"metric": 0.5},
            safe=True,
            rollback_available=True,
            trial_id="trial-0001",
        )
        assert trial.policy_changes == {"key": "value"}
        assert trial.safe is True
        assert trial.trial_id == "trial-0001"
        assert isinstance(trial.timestamp, float)


def _write_sample_policy(path, data=None):
    if data is None:
        data = {
            "policy_version": "0.1.0",
            "budget_levels": {
                "normal": {"hard_limit": 1000, "soft_limit": 700},
                "economy": {"hard_limit": 500, "soft_limit": 350},
            },
        }
    path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")


class TestPolicySandbox:
    def test_init_default_path(self):
        sb = PolicySandbox()
        assert sb.policy_path.name == "budget_policy.yaml"
        assert "config" in str(sb.policy_path)

    def test_init_custom_path(self, tmp_path):
        policy_file = tmp_path / "policy.yaml"
        _write_sample_policy(policy_file)
        sb = PolicySandbox(policy_path=str(policy_file))
        assert sb.policy_path == policy_file

    def test_load_current(self, tmp_path):
        policy_file = tmp_path / "policy.yaml"
        _write_sample_policy(policy_file)
        sb = PolicySandbox(policy_path=str(policy_file))
        data = sb.load_current()
        assert "budget_levels" in data

    def test_load_current_missing_file(self, tmp_path):
        sb = PolicySandbox(policy_path=str(tmp_path / "nonexistent.yaml"))
        with pytest.raises(FileNotFoundError):
            sb.load_current()

    def test_start_sandbox(self, tmp_path):
        policy_file = tmp_path / "policy.yaml"
        _write_sample_policy(policy_file)
        sb = PolicySandbox(policy_path=str(policy_file))
        sb.start_sandbox()
        assert sb.sandbox_policy is not None

    def test_propose_change(self, tmp_path):
        policy_file = tmp_path / "policy.yaml"
        _write_sample_policy(policy_file)
        sb = PolicySandbox(policy_path=str(policy_file))
        sb.start_sandbox()
        sb.propose_change("budget_levels.normal.hard_limit", 2000)
        assert "budget_levels.normal.hard_limit" in sb.changes

    def test_propose_change_auto_starts_sandbox(self, tmp_path):
        policy_file = tmp_path / "policy.yaml"
        _write_sample_policy(policy_file)
        sb = PolicySandbox(policy_path=str(policy_file))
        sb.propose_change("key", "value")
        assert sb.sandbox_policy is not None

    def test_simulate(self, tmp_path):
        policy_file = tmp_path / "policy.yaml"
        _write_sample_policy(policy_file)
        sb = PolicySandbox(policy_path=str(policy_file))
        sb.start_sandbox()
        sb.propose_change("budget_levels.normal.hard_limit", 2000)
        trial = sb.simulate()
        assert isinstance(trial, SandboxTrial)
        assert trial.trial_id.startswith("trial-")
        assert trial.rollback_available is True

    def test_simulate_safe_impact(self, tmp_path):
        policy_file = tmp_path / "policy.yaml"
        _write_sample_policy(policy_file)
        sb = PolicySandbox(policy_path=str(policy_file))
        sb.start_sandbox()
        sb.propose_change("budget_levels.normal.hard_limit", 2000)
        trial = sb.simulate()
        assert isinstance(trial.safe, bool)

    def test_simulate_auto_starts_sandbox(self, tmp_path):
        policy_file = tmp_path / "policy.yaml"
        _write_sample_policy(policy_file)
        sb = PolicySandbox(policy_path=str(policy_file))
        trial = sb.simulate()
        assert isinstance(trial, SandboxTrial)

    def test_commit(self, tmp_path):
        policy_file = tmp_path / "policy.yaml"
        _write_sample_policy(policy_file)
        sb = PolicySandbox(policy_path=str(policy_file))
        sb.start_sandbox()
        sb.propose_change("budget_levels.normal.hard_limit", 2000)
        sb.commit()
        updated = yaml.safe_load(policy_file.read_text(encoding="utf-8"))
        assert updated["budget_levels"]["normal"]["hard_limit"] == 2000

    def test_commit_without_sandbox(self, tmp_path):
        policy_file = tmp_path / "policy.yaml"
        _write_sample_policy(policy_file)
        sb = PolicySandbox(policy_path=str(policy_file))
        sb.commit()

    def test_rollback(self, tmp_path):
        policy_file = tmp_path / "policy.yaml"
        _write_sample_policy(policy_file)
        sb = PolicySandbox(policy_path=str(policy_file))
        sb.start_sandbox()
        sb.propose_change("key", "value")
        sb.rollback()
        assert sb.sandbox_policy is None
        assert sb.changes == {}

    def test_recent_trials(self, tmp_path):
        policy_file = tmp_path / "policy.yaml"
        _write_sample_policy(policy_file)
        sb = PolicySandbox(policy_path=str(policy_file))
        sb.start_sandbox()
        sb.propose_change("key1", "val1")
        sb.simulate()
        sb.propose_change("key2", "val2")
        sb.simulate()
        trials = sb.recent_trials()
        assert len(trials) == 2

    def test_recent_trials_limit(self, tmp_path):
        policy_file = tmp_path / "policy.yaml"
        _write_sample_policy(policy_file)
        sb = PolicySandbox(policy_path=str(policy_file))
        sb.start_sandbox()
        for i in range(15):
            sb.propose_change(f"key{i}", f"val{i}")
            sb.simulate()
        trials = sb.recent_trials(n=5)
        assert len(trials) == 5

    def test_trial_counter_increments(self, tmp_path):
        policy_file = tmp_path / "policy.yaml"
        _write_sample_policy(policy_file)
        sb = PolicySandbox(policy_path=str(policy_file))
        sb.start_sandbox()
        sb.propose_change("key", "val")
        t1 = sb.simulate()
        t2 = sb.simulate()
        assert t2.trial_id != t1.trial_id

    def test_assess_impact_with_valid_levels(self, tmp_path):
        policy_file = tmp_path / "policy.yaml"
        _write_sample_policy(policy_file)
        sb = PolicySandbox(policy_path=str(policy_file))
        policy = {
            "budget_levels": {
                "normal": {"hard_limit": 1000, "soft_limit": 700},
            },
        }
        impact = sb.assess_impact(policy)
        assert "normal_strictness" in impact
        assert impact["normal_strictness"] == 700 / 1000

    def test_assess_impact_with_zero_limits(self, tmp_path):
        policy_file = tmp_path / "policy.yaml"
        _write_sample_policy(policy_file)
        sb = PolicySandbox(policy_path=str(policy_file))
        policy = {
            "budget_levels": {
                "broken": {"hard_limit": 0, "soft_limit": 0},
            },
        }
        impact = sb.assess_impact(policy)
        assert impact["broken_strictness"] == 0.5

    def test_set_nested(self, tmp_path):
        d = {"a": {"b": {}}}
        PolicySandbox.set_nested(d, "a.b.c", 42)
        assert d["a"]["b"]["c"] == 42

    def test_set_nested_creates_intermediate(self, tmp_path):
        d = {}
        PolicySandbox.set_nested(d, "x.y.z", "deep")
        assert d["x"]["y"]["z"] == "deep"
