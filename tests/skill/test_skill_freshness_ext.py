# [A_test] module_id: MOD-GOV_skill_freshness_ext | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §3.2
# [MODULE] tests.test_skill_freshness_ext
# [INVARIANTS] must mock FreshnessDecayModel and SkillLifecycle; no real file I/O
# [MODIFY-GUARD] skill_freshness_ext.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] all tests must pass independently; no shared mutable state across tests
# [TESTS] pytest tests/test_skill_freshness_ext.py -q
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock, patch

from zephyr.autonomy_core.skills.skill_freshness_ext import (
    auto_deprecate_skill,
    increment_round,
    scan_all_freshness,
    should_load_onboarding,
)
from zephyr.autonomy_core.skills.skill_model import SkillStatus


class TestScanAllFreshness:
    def test_scan_with_default_model(self):
        mock_model = MagicMock()
        mock_model.WARNING_THRESHOLD = 30.0
        mock_model.CRITICAL_THRESHOLD = 10.0
        mock_model._load.return_value = {
            "skill-a": {"last_validated": "2026-05-22T00:00:00+00:00"},
            "skill-b": {"last_validated": "2026-01-01T00:00:00+00:00"},
        }
        mock_model.compute.side_effect = lambda v: 80.0 if "05-22" in v else 5.0
        result = scan_all_freshness(model=mock_model)
        assert result["total_scanned"] == 2
        assert result["healthy"] == 1
        assert result["criticals"] == 1

    def test_scan_empty_data(self):
        mock_model = MagicMock()
        mock_model.WARNING_THRESHOLD = 30.0
        mock_model.CRITICAL_THRESHOLD = 10.0
        mock_model._load.return_value = {}
        result = scan_all_freshness(model=mock_model)
        assert result["total_scanned"] == 0
        assert result["healthy"] == 0
        assert result["warnings"] == 0
        assert result["criticals"] == 0

    def test_scan_classifies_warnings(self):
        mock_model = MagicMock()
        mock_model.WARNING_THRESHOLD = 30.0
        mock_model.CRITICAL_THRESHOLD = 10.0
        mock_model._load.return_value = {"skill-w": {"last_validated": "x"}}
        mock_model.compute.return_value = 20.0
        result = scan_all_freshness(model=mock_model)
        assert result["warnings"] == 1
        assert result["healthy"] == 0
        assert result["criticals"] == 0

    def test_scan_none_model_creates_default(self):
        with patch("zephyr.autonomy_core.skills.skill_freshness_ext.FreshnessDecayModel") as MockCls:
            instance = MagicMock()
            instance.WARNING_THRESHOLD = 30.0
            instance.CRITICAL_THRESHOLD = 10.0
            instance._load.return_value = {}
            MockCls.return_value = instance
            result = scan_all_freshness(model=None)
            MockCls.assert_called_once()
            assert result["total_scanned"] == 0


class TestAutoDeprecateSkill:
    def test_deprecate_critical_score(self):
        lifecycle = MagicMock()
        lifecycle.current_status.return_value = SkillStatus.ACTIVE.value
        lifecycle.transition.return_value = {
            "skill_id": "sk-1",
            "from": "active",
            "to": "deprecated",
            "allowed": True,
            "reason": "",
        }
        result = auto_deprecate_skill(lifecycle, "sk-1", 5.0)
        assert result["allowed"] is True
        lifecycle.transition.assert_called_once()

    def test_warning_score_issues_warning(self):
        lifecycle = MagicMock()
        lifecycle.current_status.return_value = SkillStatus.ACTIVE.value
        result = auto_deprecate_skill(lifecycle, "sk-2", 25.0)
        assert result["action"] == "warning_issued"
        lifecycle.transition.assert_not_called()

    def test_healthy_score_no_action(self):
        lifecycle = MagicMock()
        lifecycle.current_status.return_value = SkillStatus.ACTIVE.value
        result = auto_deprecate_skill(lifecycle, "sk-3", 80.0)
        assert result["action"] == "no_action"

    def test_non_active_skill_skipped(self):
        lifecycle = MagicMock()
        lifecycle.current_status.return_value = SkillStatus.DRAFT.value
        result = auto_deprecate_skill(lifecycle, "sk-4", 5.0)
        assert result["action"] == "skipped"
        lifecycle.transition.assert_not_called()

    def test_deprecate_with_custom_reason(self):
        lifecycle = MagicMock()
        lifecycle.current_status.return_value = SkillStatus.ACTIVE.value
        lifecycle.transition.return_value = {
            "skill_id": "sk-5",
            "from": "active",
            "to": "deprecated",
            "allowed": True,
            "reason": "custom",
        }
        result = auto_deprecate_skill(lifecycle, "sk-5", 3.0, reason="custom reason")
        assert result["allowed"] is True
        call_args = lifecycle.transition.call_args
        assert call_args[1]["reason"] == "custom reason"


class TestShouldLoadOnboarding:
    def test_below_max_rounds(self):
        loader = MagicMock()
        loader._conversation_round = {"sess-1": 1}
        assert should_load_onboarding(loader, "sess-1", max_rounds=3) is True

    def test_at_max_rounds(self):
        loader = MagicMock()
        loader._conversation_round = {"sess-1": 3}
        assert should_load_onboarding(loader, "sess-1", max_rounds=3) is False

    def test_unknown_session(self):
        loader = MagicMock()
        loader._conversation_round = {}
        assert should_load_onboarding(loader, "new-sess", max_rounds=3) is True

    def test_none_conversation_round_attr(self):
        loader = MagicMock(spec=[])
        assert should_load_onboarding(loader, "sess-x", max_rounds=3) is True


class TestIncrementRound:
    def test_increment_new_session(self):
        loader = MagicMock()
        loader._conversation_round = {}
        result = increment_round(loader, "sess-a")
        assert result == 1
        assert loader._conversation_round["sess-a"] == 1

    def test_increment_existing_session(self):
        loader = MagicMock()
        loader._conversation_round = {"sess-b": 2}
        result = increment_round(loader, "sess-b")
        assert result == 3
        assert loader._conversation_round["sess-b"] == 3

    def test_increment_creates_dict_if_missing(self):
        loader = MagicMock(spec=[])
        result = increment_round(loader, "sess-c")
        assert result == 1
        assert loader._conversation_round["sess-c"] == 1
