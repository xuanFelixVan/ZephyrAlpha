# [A_test] module_id: SRC-TST-0268 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_action_selector
# [INVARIANTS] ActionSelector requires FeedbackProtocolAdapter; select_action returns ActionType|None
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from zephyr.feedback_loop.actors.action_selector import ActionRecord, ActionSelector
from zephyr.feedback_loop.protocols import ActionType


@dataclass
class StubAdapter:
    result: bool = True

    def dispatch_action(self, action_type: ActionType, payload: dict[str, Any]) -> bool:
        return self.result


class TestActionRecord:
    def test_instantiation(self):
        rec = ActionRecord(action_type=ActionType.NOTIFY_OWNER, timestamp=1.0, success=True)
        assert rec.action_type == ActionType.NOTIFY_OWNER
        assert rec.timestamp == 1.0
        assert rec.success is True

    def test_failure_record(self):
        rec = ActionRecord(action_type=ActionType.REPAIR, timestamp=2.0, success=False)
        assert rec.success is False


class TestActionSelectorInstantiation:
    def test_default_construction(self):
        adapter = StubAdapter()
        sel = ActionSelector(protocol_adapter=adapter)
        assert sel.protocol_adapter is adapter
        assert len(sel.action_priority) == 6
        assert sel.history == []
        assert sel.retired_actions == {}
        assert sel.consecutive_failures == {}
        assert sel.RETIRE_SECONDS == 7 * 24 * 3600
        assert sel.MAX_CONSECUTIVE_FAILURES == 3

    def test_custom_priority(self):
        adapter = StubAdapter()
        custom = [ActionType.REPAIR, ActionType.DEPLOY]
        sel = ActionSelector(protocol_adapter=adapter, action_priority=custom)
        assert sel.action_priority == custom


class TestSelectAction:
    def test_returns_first_available(self):
        adapter = StubAdapter()
        sel = ActionSelector(protocol_adapter=adapter)
        result = sel.select_action(diagnosis=None)
        assert result == ActionType.NOTIFY_OWNER

    def test_skips_retired_actions(self):
        adapter = StubAdapter()
        sel = ActionSelector(protocol_adapter=adapter)
        sel.retired_actions[ActionType.NOTIFY_OWNER.value] = time.time()
        result = sel.select_action(diagnosis=None)
        assert result == ActionType.ADJUST_THRESHOLD

    def test_returns_none_when_all_retired(self):
        adapter = StubAdapter()
        sel = ActionSelector(protocol_adapter=adapter)
        now = time.time()
        for at in sel.action_priority:
            sel.retired_actions[at.value] = now
        result = sel.select_action(diagnosis=None)
        assert result is None

    def test_retired_action_revived_after_ttl(self):
        adapter = StubAdapter()
        sel = ActionSelector(protocol_adapter=adapter)
        expired = time.time() - sel.RETIRE_SECONDS - 1
        sel.retired_actions[ActionType.NOTIFY_OWNER.value] = expired
        result = sel.select_action(diagnosis=None)
        assert result == ActionType.NOTIFY_OWNER
        assert ActionType.NOTIFY_OWNER.value not in sel.retired_actions


class TestRecordResult:
    def test_success_resets_failures(self):
        adapter = StubAdapter()
        sel = ActionSelector(protocol_adapter=adapter)
        sel.consecutive_failures[ActionType.REPAIR.value] = 2
        sel.record_result(ActionType.REPAIR, success=True)
        assert sel.consecutive_failures[ActionType.REPAIR.value] == 0
        assert len(sel.history) == 1
        assert sel.history[0].success is True

    def test_failure_increments_counter(self):
        adapter = StubAdapter()
        sel = ActionSelector(protocol_adapter=adapter)
        sel.record_result(ActionType.REPAIR, success=False)
        assert sel.consecutive_failures[ActionType.REPAIR.value] == 1

    def test_retires_after_max_consecutive_failures(self):
        adapter = StubAdapter()
        sel = ActionSelector(protocol_adapter=adapter)
        for _ in range(sel.MAX_CONSECUTIVE_FAILURES):
            sel.record_result(ActionType.REPAIR, success=False)
        assert ActionType.REPAIR.value in sel.retired_actions
        assert sel.consecutive_failures[ActionType.REPAIR.value] == 0

    def test_failure_does_not_retire_before_threshold(self):
        adapter = StubAdapter()
        sel = ActionSelector(protocol_adapter=adapter)
        sel.record_result(ActionType.REPAIR, success=False)
        sel.record_result(ActionType.REPAIR, success=False)
        assert ActionType.REPAIR.value not in sel.retired_actions


class TestExecuteAction:
    def test_dispatch_delegates_to_adapter(self):
        adapter = StubAdapter(result=True)
        sel = ActionSelector(protocol_adapter=adapter)
        assert sel.execute_action(ActionType.NOTIFY_OWNER, {}) is True

    def test_dispatch_returns_false_on_adapter_failure(self):
        adapter = StubAdapter(result=False)
        sel = ActionSelector(protocol_adapter=adapter)
        assert sel.execute_action(ActionType.NOTIFY_OWNER, {}) is False
