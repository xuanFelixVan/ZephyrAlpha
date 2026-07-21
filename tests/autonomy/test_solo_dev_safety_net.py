# [A_test] module_id: MOD-GOV_solo_dev_safety_net | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_solo_dev_safety_net
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_solo_dev_safety_net.py -q
# [TTL] task_bound
import pytest

from zephyr.security.llm_defense.llm_security.solo_dev_safety_net import SafetyNetCheck, SoloDevSafetyNet


class TestSafetyNetCheckInstantiation:
    def test_all_fields_set(self):
        check = SafetyNetCheck(
            task_id="T-001",
            is_p0=True,
            confirmation_needed=True,
            context_summary="preview",
        )
        assert check.task_id == "T-001"
        assert check.is_p0 is True
        assert check.confirmation_needed is True
        assert check.context_summary == "preview"
        assert check.timeout_auto_proceed is False

    def test_timeout_auto_proceed_override(self):
        check = SafetyNetCheck(
            task_id="T-002",
            is_p0=False,
            confirmation_needed=False,
            context_summary="",
            timeout_auto_proceed=True,
        )
        assert check.timeout_auto_proceed is True

    def test_missing_required_field_raises(self):
        with pytest.raises(TypeError):
            SafetyNetCheck(task_id="T-003")

    def test_empty_string_fields(self):
        check = SafetyNetCheck(
            task_id="",
            is_p0=False,
            confirmation_needed=False,
            context_summary="",
        )
        assert check.task_id == ""
        assert check.context_summary == ""


class TestSoloDevSafetyNetInstantiation:
    def test_create_instance(self):
        net = SoloDevSafetyNet()
        assert net is not None

    def test_has_check_injection_method(self):
        net = SoloDevSafetyNet()
        assert callable(getattr(net, "check_injection", None))


class TestCheckInjectionP0:
    def test_p0_uppercase(self):
        net = SoloDevSafetyNet()
        result = net.check_injection("T-100", "P0", "urgent fix needed")
        assert result.is_p0 is True
        assert result.confirmation_needed is True
        assert result.task_id == "T-100"
        assert result.context_summary == "urgent fix needed"

    def test_p0_lowercase(self):
        net = SoloDevSafetyNet()
        result = net.check_injection("T-101", "p0", "lowercase priority")
        assert result.is_p0 is True
        assert result.confirmation_needed is True

    def test_p0_mixed_case(self):
        net = SoloDevSafetyNet()
        result = net.check_injection("T-102", "p0", "mixed case")
        assert result.is_p0 is True


class TestCheckInjectionNonP0:
    def test_p1(self):
        net = SoloDevSafetyNet()
        result = net.check_injection("T-200", "P1", "normal task")
        assert result.is_p0 is False
        assert result.confirmation_needed is False

    def test_p2(self):
        net = SoloDevSafetyNet()
        result = net.check_injection("T-201", "P2", "low priority")
        assert result.is_p0 is False
        assert result.confirmation_needed is False

    def test_empty_priority(self):
        net = SoloDevSafetyNet()
        result = net.check_injection("T-202", "", "no priority")
        assert result.is_p0 is False
        assert result.confirmation_needed is False


class TestCheckInjectionContextSummaryTruncation:
    def test_short_context_unchanged(self):
        net = SoloDevSafetyNet()
        short = "abc"
        result = net.check_injection("T-300", "P1", short)
        assert result.context_summary == short

    def test_exact_200_chars_unchanged(self):
        net = SoloDevSafetyNet()
        exact = "x" * 200
        result = net.check_injection("T-301", "P1", exact)
        assert result.context_summary == exact
        assert len(result.context_summary) == 200

    def test_over_200_chars_truncated(self):
        net = SoloDevSafetyNet()
        long_text = "y" * 300
        result = net.check_injection("T-302", "P1", long_text)
        assert len(result.context_summary) == 200
        assert result.context_summary == "y" * 200


class TestCheckInjectionBoundary:
    def test_none_task_id(self):
        net = SoloDevSafetyNet()
        result = net.check_injection(None, "P0", "ctx")
        assert result.task_id is None
        assert result.is_p0 is True

    def test_none_context_preview(self):
        net = SoloDevSafetyNet()
        with pytest.raises((TypeError, AttributeError)):
            net.check_injection("T-400", "P0", None)

    def test_none_priority(self):
        net = SoloDevSafetyNet()
        with pytest.raises((TypeError, AttributeError)):
            net.check_injection("T-401", None, "ctx")

    def test_empty_task_id(self):
        net = SoloDevSafetyNet()
        result = net.check_injection("", "P0", "ctx")
        assert result.task_id == ""
        assert result.is_p0 is True

    def test_timeout_auto_proceed_default(self):
        net = SoloDevSafetyNet()
        result = net.check_injection("T-500", "P0", "ctx")
        assert result.timeout_auto_proceed is False
