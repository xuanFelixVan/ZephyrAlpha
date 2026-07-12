# [A_test] module_id: SRC-TST-0927 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_action_selector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.actors.action_selector
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_action_selector.py
# [TTL] task_bound

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from zephyr.feedback_loop.actors.action_selector import ActionSelector
from zephyr.feedback_loop.protocols import ActionType


@dataclass
class StubAdapter:
    dispatched: list[tuple[ActionType, dict[str, Any]]] = None

    def __post_init__(self):
        if self.dispatched is None:
            self.dispatched = []

    def dispatch_action(self, action_type: ActionType, payload: dict[str, Any]) -> bool:
        self.dispatched.append((action_type, payload))
        return True


class TestActionSelectorInstantiation:
    def test_creates_with_defaults(self):
        adapter = StubAdapter()
        selector = ActionSelector(protocol_adapter=adapter)
        assert selector.protocol_adapter is adapter
        assert selector.history == []
        assert selector.retired_actions == {}
        assert selector.consecutive_failures == {}

    def test_creates_with_custom_params(self):
        adapter = StubAdapter()
        selector = ActionSelector(
            protocol_adapter=adapter,
            RETIRE_SECONDS=100,
            MAX_CONSECUTIVE_FAILURES=5,
            learning_rate=0.2,
            discount_factor=0.8,
        )
        assert selector.RETIRE_SECONDS == 100
        assert selector.MAX_CONSECUTIVE_FAILURES == 5


class TestSelectAction:
    def test_returns_highest_priority_action(self):
        adapter = StubAdapter()
        selector = ActionSelector(protocol_adapter=adapter)
        result = selector.select_action(diagnosis=None)
        assert result == ActionType.NOTIFY_OWNER

    def test_skips_retired_actions(self):
        adapter = StubAdapter()
        selector = ActionSelector(protocol_adapter=adapter)
        selector.retired_actions[ActionType.NOTIFY_OWNER.value] = time.time()
        result = selector.select_action(diagnosis=None)
        assert result == ActionType.ADJUST_THRESHOLD

    def test_returns_none_when_all_retired(self):
        adapter = StubAdapter()
        selector = ActionSelector(protocol_adapter=adapter)
        now = time.time()
        for at in ActionType:
            selector.retired_actions[at.value] = now
        result = selector.select_action(diagnosis=None)
        assert result is None

    def test_revives_retired_action_after_expiry(self):
        adapter = StubAdapter()
        selector = ActionSelector(protocol_adapter=adapter, RETIRE_SECONDS=0)
        selector.retired_actions[ActionType.NOTIFY_OWNER.value] = time.time() - 1
        result = selector.select_action(diagnosis=None)
        assert result == ActionType.NOTIFY_OWNER


class TestRecordResult:
    def test_records_success(self):
        adapter = StubAdapter()
        selector = ActionSelector(protocol_adapter=adapter)
        selector.record_result(ActionType.REPAIR, True)
        assert len(selector.history) == 1
        assert selector.history[0].success is True
        assert selector.consecutive_failures.get(ActionType.REPAIR.value, 0) == 0

    def test_records_failure_and_tracks_consecutive(self):
        adapter = StubAdapter()
        selector = ActionSelector(protocol_adapter=adapter, MAX_CONSECUTIVE_FAILURES=2)
        selector.record_result(ActionType.REPAIR, False)
        selector.record_result(ActionType.REPAIR, False)
        assert ActionType.REPAIR.value in selector.retired_actions

    def test_resets_consecutive_on_success(self):
        adapter = StubAdapter()
        selector = ActionSelector(protocol_adapter=adapter)
        selector.record_result(ActionType.REPAIR, False)
        selector.record_result(ActionType.REPAIR, True)
        assert selector.consecutive_failures[ActionType.REPAIR.value] == 0


class TestExecuteAction:
    def test_dispatches_via_adapter(self):
        adapter = StubAdapter()
        selector = ActionSelector(protocol_adapter=adapter)
        result = selector.execute_action(ActionType.REPAIR, {"key": "val"})
        assert result is True
        assert len(adapter.dispatched) == 1
        assert adapter.dispatched[0][0] == ActionType.REPAIR

    def test_boundary_empty_payload(self):
        adapter = StubAdapter()
        selector = ActionSelector(protocol_adapter=adapter)
        result = selector.execute_action(ActionType.NOTIFY_OWNER, {})
        assert result is True
