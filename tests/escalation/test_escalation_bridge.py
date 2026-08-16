# [A_test] module_id: MOD-GOV_escalation_bridge | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_escalation_bridge
# [INVARIANTS] 测试覆盖escalate/escalate_dead_letter/get_escalation_history;边界:空输入/None/异常
# [MODIFY-GUARD] blueprint.md §3
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import sys

from zephyr.infrastructure.auto_fix_engine.escalation_bridge import EscalationBridge
from zephyr.infrastructure.auto_fix_engine.models import FixAction, FixLevel, FixStatus


def _make_action(status: FixStatus = FixStatus.PENDING) -> FixAction:
    return FixAction(
        action_type="drift_fix",
        target="t.py",
        level=FixLevel.L1_RULE,
        status=status,
    )


def _block_escalation_engine():
    saved = {}
    for key in list(sys.modules.keys()):
        if key.startswith("zephyr.infrastructure.escalation"):
            saved[key] = sys.modules.pop(key)
    sys.modules["zephyr.governance.services.adapter"] = None
    return saved


def _restore_escalation_engine(saved):
    for key in list(sys.modules.keys()):
        if key.startswith("zephyr.infrastructure.escalation"):
            del sys.modules[key]
    # 清除 _block 注入的 None 占位，防止同进程后续 import 触发 "import halted"
    sys.modules.pop("zephyr.governance.services.adapter", None)
    sys.modules.update(saved)


class TestEscalationBridgeInstantiation:
    def test_default_config(self):
        eb = EscalationBridge()
        assert eb.enabled is True

    def test_custom_config(self):
        eb = EscalationBridge(config={"bridge_enabled": False, "auto_escalate_dead_letter": False})
        assert eb.enabled is False

    def test_none_config(self):
        eb = EscalationBridge(config=None)
        assert eb.enabled is True


class TestEscalate:
    def test_escalate_disabled(self):
        eb = EscalationBridge(config={"bridge_enabled": False})
        action = _make_action()
        result = eb.escalate(action, "test reason")
        assert result.metadata.get("escalation_skipped") is True
        assert result.metadata.get("skip_reason") == "Escalation bridge disabled"

    def test_escalate_fallback_on_import_error(self):
        eb = EscalationBridge()
        action = _make_action()
        saved = _block_escalation_engine()
        try:
            result = eb.escalate(action, "test")
        finally:
            _restore_escalation_engine(saved)
        assert result.escalated is True
        assert result.status == FixStatus.APPROVAL_PENDING
        assert result.metadata.get("escalation_fallback") is True

    def test_escalate_records_history(self):
        eb = EscalationBridge()
        action = _make_action()
        saved = _block_escalation_engine()
        try:
            eb.escalate(action, "test reason")
        finally:
            _restore_escalation_engine(saved)
        history = eb.get_escalation_history()
        assert len(history) == 1
        assert history[0]["action_id"] == action.action_id
        assert history[0]["reason"] == "test reason"

    def test_escalate_with_reason(self):
        eb = EscalationBridge()
        action = _make_action()
        saved = _block_escalation_engine()
        try:
            result = eb.escalate(action, "custom reason")
        finally:
            _restore_escalation_engine(saved)
        assert result.metadata.get("escalation_reason") == "custom reason"

    def test_escalate_empty_reason(self):
        eb = EscalationBridge()
        action = _make_action()
        saved = _block_escalation_engine()
        try:
            result = eb.escalate(action, "")
        finally:
            _restore_escalation_engine(saved)
        assert result.escalated is True


class TestEscalateDeadLetter:
    def test_escalate_dead_letter_enabled(self):
        eb = EscalationBridge(config={"auto_escalate_dead_letter": True})
        action = _make_action()
        saved = _block_escalation_engine()
        try:
            result = eb.escalate_dead_letter(action, "max retries")
        finally:
            _restore_escalation_engine(saved)
        assert result.escalated is True

    def test_escalate_dead_letter_disabled(self):
        eb = EscalationBridge(config={"auto_escalate_dead_letter": False})
        action = _make_action()
        result = eb.escalate_dead_letter(action, "max retries")
        assert not result.escalated

    def test_escalate_dead_letter_reason_prefix(self):
        eb = EscalationBridge()
        action = _make_action()
        saved = _block_escalation_engine()
        try:
            eb.escalate_dead_letter(action, "timeout")
        finally:
            _restore_escalation_engine(saved)
        history = eb.get_escalation_history()
        assert "Dead letter: timeout" in history[0]["reason"]


class TestGetEscalationHistory:
    def test_empty_history(self):
        eb = EscalationBridge()
        assert eb.get_escalation_history() == []

    def test_history_limit(self):
        eb = EscalationBridge()
        saved = _block_escalation_engine()
        try:
            for i in range(60):
                action = _make_action()
                eb.escalate(action, f"reason {i}")
        finally:
            _restore_escalation_engine(saved)
        history = eb.get_escalation_history(limit=10)
        assert len(history) == 10

    def test_history_order(self):
        eb = EscalationBridge()
        saved = _block_escalation_engine()
        try:
            a1 = _make_action()
            a2 = _make_action()
            eb.escalate(a1, "first")
            eb.escalate(a2, "second")
        finally:
            _restore_escalation_engine(saved)
        history = eb.get_escalation_history()
        assert history[0]["reason"] == "first"
        assert history[1]["reason"] == "second"
