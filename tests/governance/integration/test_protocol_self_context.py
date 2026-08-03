# [A_test] module_id: MOD-GOV_protocol_self_context | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_protocol_self_context
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_protocol_self_context.py -q
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from zephyr.governance.context_governance.protocol_self_context import ProtocolSelfContext


class TestProtocolSelfContextInstantiation:
    def test_creates_instance(self):
        ctx = ProtocolSelfContext()
        assert isinstance(ctx, ProtocolSelfContext)

    def test_has_update_metrics_method(self):
        ctx = ProtocolSelfContext()
        assert callable(getattr(ctx, "update_metrics", None))

    def test_has_snapshot_method(self):
        ctx = ProtocolSelfContext()
        assert callable(getattr(ctx, "snapshot", None))

    def test_default_context_values(self):
        ctx = ProtocolSelfContext()
        snap = ctx.snapshot()
        assert snap["version"] == "v0.10.0"
        assert snap["active_rules"] == 0
        assert snap["last_reconcile"] is None


class TestUpdateMetrics:
    def test_update_active_rules(self):
        ctx = ProtocolSelfContext()
        ctx.update_metrics(active_rules=5)
        snap = ctx.snapshot()
        assert snap["active_rules"] == 5

    def test_update_active_rules_zero(self):
        ctx = ProtocolSelfContext()
        ctx.update_metrics(active_rules=10)
        ctx.update_metrics(active_rules=0)
        snap = ctx.snapshot()
        assert snap["active_rules"] == 0

    def test_update_active_rules_large_value(self):
        ctx = ProtocolSelfContext()
        ctx.update_metrics(active_rules=9999)
        snap = ctx.snapshot()
        assert snap["active_rules"] == 9999

    def test_update_overwrites_previous(self):
        ctx = ProtocolSelfContext()
        ctx.update_metrics(active_rules=3)
        ctx.update_metrics(active_rules=7)
        snap = ctx.snapshot()
        assert snap["active_rules"] == 7

    def test_update_does_not_affect_version(self):
        ctx = ProtocolSelfContext()
        ctx.update_metrics(active_rules=5)
        snap = ctx.snapshot()
        assert snap["version"] == "v0.10.0"


class TestSnapshot:
    def test_snapshot_returns_dict(self):
        ctx = ProtocolSelfContext()
        snap = ctx.snapshot()
        assert isinstance(snap, dict)

    def test_snapshot_is_copy(self):
        ctx = ProtocolSelfContext()
        snap1 = ctx.snapshot()
        snap1["active_rules"] = 999
        snap2 = ctx.snapshot()
        assert snap2["active_rules"] == 0

    def test_snapshot_contains_expected_keys(self):
        ctx = ProtocolSelfContext()
        snap = ctx.snapshot()
        assert "version" in snap
        assert "active_rules" in snap
        assert "last_reconcile" in snap

    def test_snapshot_reflects_update(self):
        ctx = ProtocolSelfContext()
        ctx.update_metrics(active_rules=42)
        snap = ctx.snapshot()
        assert snap["active_rules"] == 42

    def test_multiple_snapshots_independent(self):
        ctx = ProtocolSelfContext()
        ctx.update_metrics(active_rules=1)
        snap_a = ctx.snapshot()
        ctx.update_metrics(active_rules=2)
        snap_b = ctx.snapshot()
        assert snap_a["active_rules"] == 1
        assert snap_b["active_rules"] == 2


class TestBoundaryConditions:
    def test_update_with_negative_value(self):
        ctx = ProtocolSelfContext()
        ctx.update_metrics(active_rules=-1)
        snap = ctx.snapshot()
        assert snap["active_rules"] == -1

    def test_snapshot_before_any_update(self):
        ctx = ProtocolSelfContext()
        snap = ctx.snapshot()
        assert snap["active_rules"] == 0
        assert snap["version"] == "v0.10.0"
        assert snap["last_reconcile"] is None

    def test_repeated_updates(self):
        ctx = ProtocolSelfContext()
        for i in range(100):
            ctx.update_metrics(active_rules=i)
        snap = ctx.snapshot()
        assert snap["active_rules"] == 99

    def test_snapshot_does_not_modify_internal_state(self):
        ctx = ProtocolSelfContext()
        ctx.update_metrics(active_rules=10)
        for _ in range(50):
            ctx.snapshot()
        snap = ctx.snapshot()
        assert snap["active_rules"] == 10
