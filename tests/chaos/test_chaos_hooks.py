# [A_test] module_id: SRC-TST-0512 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_chaos_hooks
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from zephyr.orchestrator.fault_tolerance.chaos_engine import ChaosEngine
from zephyr.orchestrator.fault_tolerance.chaos_hooks import (
    ChaosHook,
    ChaosHookPolicy,
    HookContext,
)


class TestChaosHookPolicy:
    def test_add_step_fault(self):
        policy = ChaosHookPolicy()
        policy.add_step_fault("step_1", "latency", "api", {"delay_ms": 100})
        assert "step_1" in policy.step_faults
        assert len(policy.step_faults["step_1"]) == 1
        assert policy.step_faults["step_1"][0]["fault_type"] == "latency"

    def test_add_multiple_faults_to_step(self):
        policy = ChaosHookPolicy()
        policy.add_step_fault("step_1", "latency", "api")
        policy.add_step_fault("step_1", "exception", "db")
        assert len(policy.step_faults["step_1"]) == 2

    def test_default_enabled(self):
        policy = ChaosHookPolicy()
        assert policy.enabled is True

    def test_disabled_policy(self):
        policy = ChaosHookPolicy(enabled=False)
        assert policy.enabled is False


class TestChaosHookPreStep:
    def test_pre_step_injects_fault(self):
        engine = ChaosEngine()
        hook = ChaosHook(engine=engine)
        policy = ChaosHookPolicy()
        policy.add_step_fault("step_1", "latency", "api", {"delay_ms": 10})
        hook.configure(policy)

        ctx = HookContext(step_name="step_1")
        result = hook.pre_step_hook(ctx)
        assert len(result.fault_records) == 1
        assert result.fault_records[0].fault_type == "latency"
        assert result.fault_records[0].target == "api"

    def test_pre_step_no_faults_for_step(self):
        engine = ChaosEngine()
        hook = ChaosHook(engine=engine)
        policy = ChaosHookPolicy()
        hook.configure(policy)

        ctx = HookContext(step_name="step_1")
        result = hook.pre_step_hook(ctx)
        assert result.fault_records == []

    def test_pre_step_disabled_policy(self):
        engine = ChaosEngine()
        hook = ChaosHook(engine=engine)
        policy = ChaosHookPolicy(enabled=False)
        policy.add_step_fault("step_1", "latency", "api")
        hook.configure(policy)

        ctx = HookContext(step_name="step_1")
        result = hook.pre_step_hook(ctx)
        assert result.fault_records == []


class TestChaosHookPostStep:
    def test_post_step_recovers_faults(self):
        engine = ChaosEngine()
        hook = ChaosHook(engine=engine)
        policy = ChaosHookPolicy()
        policy.add_step_fault("step_1", "latency", "api", {"delay_ms": 10})
        hook.configure(policy)

        ctx = hook.pre_step_hook(HookContext(step_name="step_1"))
        assert not engine.is_healthy()

        ctx = hook.post_step_hook(ctx)
        assert engine.is_healthy()
        assert ctx.fault_records == []

    def test_post_step_no_active_faults(self):
        engine = ChaosEngine()
        hook = ChaosHook(engine=engine)
        hook.configure(ChaosHookPolicy())

        ctx = HookContext(step_name="step_1")
        result = hook.post_step_hook(ctx)
        assert result.fault_records == []


class TestChaosHookConfigure:
    def test_configure_sets_policy(self):
        hook = ChaosHook()
        policy = ChaosHookPolicy()
        policy.add_step_fault("step_1", "latency", "api")
        hook.configure(policy)
        ctx = hook.pre_step_hook(HookContext(step_name="step_1"))
        assert len(ctx.fault_records) == 1


class TestChaosHookIntegration:
    def test_full_pre_post_cycle(self):
        engine = ChaosEngine()
        hook = ChaosHook(engine=engine)
        policy = ChaosHookPolicy()
        policy.add_step_fault("step_1", "latency", "svc_a", {"delay_ms": 10})
        policy.add_step_fault("step_1", "error", "svc_b")
        hook.configure(policy)

        ctx = hook.pre_step_hook(HookContext(step_name="step_1"))
        assert len(ctx.fault_records) == 2
        assert not engine.is_healthy()

        ctx = hook.post_step_hook(ctx)
        assert engine.is_healthy()

    def test_get_engine(self):
        engine = ChaosEngine()
        hook = ChaosHook(engine=engine)
        assert hook.get_engine() is engine
