# [A_test] module_id: MOD-GOV_trading_kill_switch | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_trading_kill_switch
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from zephyr.trading.trading_contracts.risk.trading_kill_switch import (
    KILL_SWITCHES,
    KillSwitch,
    KillSwitchLevel,
    active_switches,
    evaluate,
    get_switch,
    reset,
    trigger,
)


@pytest.fixture(autouse=True)
def _reset_all_switches() -> None:
    for ks in KILL_SWITCHES.values():
        ks.active = False


class TestKillSwitchLevel:
    def test_all_levels_exist(self) -> None:
        expected = {
            "POSITION_LIMIT",
            "DAILY_LOSS",
            "CIRCUIT_BREAKER",
            "SECOND_LEVEL",
            "API_TIMEOUT",
        }
        actual = {level.value for level in KillSwitchLevel}
        assert actual == expected

    def test_invalid_level(self) -> None:
        with pytest.raises(ValueError):
            KillSwitchLevel("INVALID")


class TestKillSwitchModel:
    def test_create_kill_switch(self) -> None:
        ks = KillSwitch(
            level=KillSwitchLevel.POSITION_LIMIT,
            label="test",
            trigger_condition="x > 10",
            action="REDUCE_ONLY",
        )
        assert ks.level == KillSwitchLevel.POSITION_LIMIT
        assert ks.label == "test"
        assert ks.active is False
        assert ks.cooldown_seconds == 0
        assert ks.auto_reenable is False

    def test_kill_switch_with_options(self) -> None:
        ks = KillSwitch(
            level=KillSwitchLevel.DAILY_LOSS,
            label="daily loss",
            trigger_condition="pnl < -0.03",
            action="CANCEL_ALL",
            cooldown_seconds=300,
            auto_reenable=True,
            active=True,
        )
        assert ks.cooldown_seconds == 300
        assert ks.auto_reenable is True
        assert ks.active is True

    def test_kill_switch_missing_required_field(self) -> None:
        with pytest.raises(Exception):
            KillSwitch(level=KillSwitchLevel.POSITION_LIMIT)


class TestKillSwitchesRegistry:
    def test_all_levels_registered(self) -> None:
        for level in KillSwitchLevel:
            assert level in KILL_SWITCHES

    def test_all_start_inactive(self) -> None:
        for ks in KILL_SWITCHES.values():
            assert ks.active is False

    def test_each_has_different_action(self) -> None:
        actions = {ks.action for ks in KILL_SWITCHES.values()}
        assert len(actions) == len(KILL_SWITCHES)


class TestGetSwitch:
    def test_get_existing_switch(self) -> None:
        ks = get_switch(KillSwitchLevel.POSITION_LIMIT)
        assert ks is not None
        assert ks.level == KillSwitchLevel.POSITION_LIMIT

    def test_get_all_levels(self) -> None:
        for level in KillSwitchLevel:
            ks = get_switch(level)
            assert ks is not None

    def test_get_returns_none_for_absent(self) -> None:
        result = get_switch("NONEXISTENT")  # type: ignore[arg-type]
        assert result is None


class TestTrigger:
    def test_trigger_activates_switch(self) -> None:
        result = trigger(KillSwitchLevel.CIRCUIT_BREAKER)
        assert result is True
        assert KILL_SWITCHES[KillSwitchLevel.CIRCUIT_BREAKER].active is True

    def test_trigger_returns_false_for_invalid(self) -> None:
        result = trigger("NONEXISTENT")  # type: ignore[arg-type]
        assert result is False

    def test_trigger_idempotent(self) -> None:
        trigger(KillSwitchLevel.API_TIMEOUT)
        result = trigger(KillSwitchLevel.API_TIMEOUT)
        assert result is True
        assert KILL_SWITCHES[KillSwitchLevel.API_TIMEOUT].active is True


class TestReset:
    def test_reset_deactivates_switch(self) -> None:
        trigger(KillSwitchLevel.DAILY_LOSS)
        assert KILL_SWITCHES[KillSwitchLevel.DAILY_LOSS].active is True
        result = reset(KillSwitchLevel.DAILY_LOSS)
        assert result is True
        assert KILL_SWITCHES[KillSwitchLevel.DAILY_LOSS].active is False

    def test_reset_returns_false_for_invalid(self) -> None:
        result = reset("NONEXISTENT")  # type: ignore[arg-type]
        assert result is False

    def test_reset_inactive_switch(self) -> None:
        result = reset(KillSwitchLevel.POSITION_LIMIT)
        assert result is True
        assert KILL_SWITCHES[KillSwitchLevel.POSITION_LIMIT].active is False


class TestActiveSwitches:
    def test_none_active_initially(self) -> None:
        assert active_switches() == []

    def test_returns_only_active(self) -> None:
        trigger(KillSwitchLevel.POSITION_LIMIT)
        trigger(KillSwitchLevel.API_TIMEOUT)
        active = active_switches()
        assert len(active) == 2
        levels = {ks.level for ks in active}
        assert KillSwitchLevel.POSITION_LIMIT in levels
        assert KillSwitchLevel.API_TIMEOUT in levels

    def test_after_reset_empty(self) -> None:
        trigger(KillSwitchLevel.SECOND_LEVEL)
        reset(KillSwitchLevel.SECOND_LEVEL)
        assert active_switches() == []


class TestEvaluate:
    def test_evaluate_triggers_matching(self) -> None:
        evaluator = MagicMock(return_value=True)
        triggered = evaluate("test_condition", evaluator)
        assert len(triggered) == len(KILL_SWITCHES)
        for ks in triggered:
            assert ks.active is True

    def test_evaluate_no_match(self) -> None:
        evaluator = MagicMock(return_value=False)
        triggered = evaluate("test_condition", evaluator)
        assert triggered == []
        for ks in KILL_SWITCHES.values():
            assert ks.active is False

    def test_evaluate_exception_in_evaluator_skipped(self) -> None:
        call_count = 0

        def flaky_evaluator(cond: str) -> bool:
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise RuntimeError("evaluator error")
            return True

        triggered = evaluate("test_condition", flaky_evaluator)
        assert len(triggered) > 0

    def test_evaluate_does_not_retrigger_active(self) -> None:
        trigger(KillSwitchLevel.POSITION_LIMIT)
        evaluator = MagicMock(return_value=True)
        triggered = evaluate("test_condition", evaluator)
        already_active = [ks for ks in triggered if ks.level == KillSwitchLevel.POSITION_LIMIT]
        assert len(already_active) == 0

    def test_evaluate_with_empty_condition(self) -> None:
        evaluator = MagicMock(return_value=False)
        triggered = evaluate("", evaluator)
        assert triggered == []
