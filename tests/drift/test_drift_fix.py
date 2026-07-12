# [A_test] module_id: SRC-TST-0775 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §

# [MODULE] tests.test_drift_fix

# [INVARIANTS] DriftFixHandler.on_drift_fix returns correct action for auto_fixable and manual events

# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] pytest raises on failure

# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

# ARCH-034 P3 / SRC-038 合并：governance/drift_fix.py 冗余副本已删除，改为从 canonical 真源 import
from zephyr.infrastructure.rollback.drift_fix import DriftFixHandler
from zephyr.gov_drift.events import ManagedDriftEvent, ManagedDriftState, DriftType


class TestDriftFixHandlerInit:
    def test_instantiation(self):
        handler = DriftFixHandler()
        assert handler is not None

    def test_has_on_drift_fix_method(self):
        handler = DriftFixHandler()
        assert callable(getattr(handler, "on_drift_fix", None))


class TestDriftFixHandlerOnDriftFix:
    def test_auto_fixable_event_returns_fixed(self):
        handler = DriftFixHandler()
        event = ManagedDriftEvent(
            drift_id="drift-001",
            target="src/module.py",
            drift_type=DriftType.CODE_DIVERGENCE,
            auto_fixable=True,
            fix_suggestion="Revert to baseline",
        )
        result = handler.on_drift_fix(event)
        assert result["fixed"] is True
        assert result["action"] == "AUTO_FIXED"
        assert result["drift_id"] == "drift-001"
        assert result["drift_type"] == "CODE_DIVERGENCE"
        assert result["target"] == "src/module.py"
        assert result["fix_suggestion"] == "Revert to baseline"

    def test_auto_fixable_marks_state_fixed(self):
        handler = DriftFixHandler()
        event = ManagedDriftEvent(
            drift_id="drift-002",
            target="src/other.py",
            auto_fixable=True,
        )
        handler.on_drift_fix(event)
        assert event.state == ManagedDriftState.FIXED

    def test_not_auto_fixable_returns_manual_required(self):
        handler = DriftFixHandler()
        event = ManagedDriftEvent(
            drift_id="drift-003",
            target="src/config.yaml",
            auto_fixable=False,
        )
        result = handler.on_drift_fix(event)
        assert result["fixed"] is False
        assert result["action"] == "MANUAL_REQUIRED"
        assert result["reason"] == "auto_fixable=False"

    def test_not_auto_fixable_marks_manual_required(self):
        handler = DriftFixHandler()
        event = ManagedDriftEvent(
            drift_id="drift-004",
            target="src/schema.py",
            auto_fixable=False,
        )
        handler.on_drift_fix(event)
        assert event.state == ManagedDriftState.MANUAL_REQUIRED

    def test_drift_type_preserved_in_result(self):
        handler = DriftFixHandler()
        for dt in DriftType:
            event = ManagedDriftEvent(
                drift_id=f"drift-{dt.value}",
                target="src/test.py",
                drift_type=dt,
                auto_fixable=True,
            )
            result = handler.on_drift_fix(event)
            assert result["drift_type"] == dt.value


class TestDriftFixHandlerBoundary:
    def test_event_with_empty_fix_suggestion(self):
        handler = DriftFixHandler()
        event = ManagedDriftEvent(
            drift_id="drift-empty",
            target="src/empty.py",
            auto_fixable=True,
            fix_suggestion="",
        )
        result = handler.on_drift_fix(event)
        assert result["fixed"] is True
        assert result["fix_suggestion"] == ""

    def test_event_with_empty_target(self):
        handler = DriftFixHandler()
        event = ManagedDriftEvent(
            drift_id="drift-notarget",
            target="",
            auto_fixable=True,
        )
        result = handler.on_drift_fix(event)
        assert result["target"] == ""

    def test_multiple_calls_independent(self):
        handler = DriftFixHandler()
        event1 = ManagedDriftEvent(drift_id="a", target="a.py", auto_fixable=True)
        event2 = ManagedDriftEvent(drift_id="b", target="b.py", auto_fixable=False)
        r1 = handler.on_drift_fix(event1)
        r2 = handler.on_drift_fix(event2)
        assert r1["fixed"] is True
        assert r2["fixed"] is False
