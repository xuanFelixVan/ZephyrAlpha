# [A_test] module_id: MOD-GOV_daily_ops | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_daily_ops
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_daily_ops.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.ops_governance.daily_ops import (
    QUICK_COMMANDS,
    OpsPhase,
    QuickCommand,
)


class TestOpsPhase:
    def test_all_phases_exist(self):
        assert OpsPhase.P1_PRE_OPEN.value == "08:00-09:30 盘前"
        assert OpsPhase.P2_CORE.value == "09:30-16:00 主交易"
        assert OpsPhase.P3_CLOSE.value == "16:00-16:30 收市核实"
        assert OpsPhase.P4_MAINTENANCE.value == "16:30-17:30 盘后维护"
        assert OpsPhase.P5_SUMMARY.value == "17:30-18:00 日终总结"

    def test_five_phases(self):
        assert len(OpsPhase) == 5

    def test_enum_is_str(self):
        for member in OpsPhase:
            assert isinstance(member, str)

    def test_phase_ordering(self):
        names = [m.name for m in OpsPhase]
        assert names == ["P1_PRE_OPEN", "P2_CORE", "P3_CLOSE", "P4_MAINTENANCE", "P5_SUMMARY"]


class TestQuickCommand:
    def test_all_commands_exist(self):
        assert QuickCommand.CRISIS.value == "/crisis"
        assert QuickCommand.STATUS.value == "/status"
        assert QuickCommand.NOTES.value == "/notes"
        assert QuickCommand.PUBLISH.value == "/publish"

    def test_four_commands(self):
        assert len(QuickCommand) == 4

    def test_enum_is_str(self):
        for member in QuickCommand:
            assert isinstance(member, str)

    def test_command_format(self):
        for member in QuickCommand:
            assert member.value.startswith("/")


class TestQuickCommandsDict:
    def test_all_keys_are_enum_members(self):
        for key in QUICK_COMMANDS:
            assert isinstance(key, QuickCommand)

    def test_all_values_are_strings(self):
        for value in QUICK_COMMANDS.values():
            assert isinstance(value, str)
            assert len(value) > 0

    def test_crisis_description(self):
        assert "Pause" in QUICK_COMMANDS[QuickCommand.CRISIS] or "Emergency" in QUICK_COMMANDS[QuickCommand.CRISIS]

    def test_status_description(self):
        assert (
            "指标" in QUICK_COMMANDS[QuickCommand.STATUS] or "dashboard" in QUICK_COMMANDS[QuickCommand.STATUS].lower()
        )

    def test_notes_description(self):
        assert "markdown" in QUICK_COMMANDS[QuickCommand.NOTES].lower() or "事件" in QUICK_COMMANDS[QuickCommand.NOTES]

    def test_publish_description(self):
        assert "发布" in QUICK_COMMANDS[QuickCommand.PUBLISH] or "bump" in QUICK_COMMANDS[QuickCommand.PUBLISH].lower()
