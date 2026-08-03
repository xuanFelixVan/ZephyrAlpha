# [A_test] module_id: MOD-GOV_process_isolator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_process_isolator
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_process_isolator.py -q
# [TTL] task_bound
from zephyr.governance.resilience_governance.process_isolator import ProcessIsolator


class TestProcessIsolatorInstantiation:
    def test_creates_instance(self):
        isolator = ProcessIsolator()
        assert isinstance(isolator, ProcessIsolator)

    def test_has_spawn_engine_method(self):
        isolator = ProcessIsolator()
        assert callable(getattr(isolator, "spawn_engine", None))

    def test_has_isolate_method(self):
        isolator = ProcessIsolator()
        assert callable(getattr(isolator, "isolate", None))

    def test_has_kill_engine_method(self):
        isolator = ProcessIsolator()
        assert callable(getattr(isolator, "kill_engine", None))


class TestSpawnEngine:
    def test_spawn_returns_true(self):
        isolator = ProcessIsolator()
        result = isolator.spawn_engine("eng-1")
        assert result is True

    def test_spawn_creates_process_entry(self):
        isolator = ProcessIsolator()
        isolator.spawn_engine("eng-1")
        assert "eng-1" in isolator.processes

    def test_spawn_status_is_running(self):
        isolator = ProcessIsolator()
        isolator.spawn_engine("eng-1")
        assert isolator.processes["eng-1"]["status"] == "running"

    def test_spawn_with_config(self):
        isolator = ProcessIsolator()
        config = {"mode": "strict", "timeout": 30}
        isolator.spawn_engine("eng-1", config=config)
        assert isolator.processes["eng-1"]["config"] == config

    def test_spawn_without_config_defaults_empty(self):
        isolator = ProcessIsolator()
        isolator.spawn_engine("eng-1")
        assert isolator.processes["eng-1"]["config"] == {}

    def test_spawn_multiple_engines(self):
        isolator = ProcessIsolator()
        isolator.spawn_engine("eng-1")
        isolator.spawn_engine("eng-2")
        assert "eng-1" in isolator.processes
        assert "eng-2" in isolator.processes


class TestIsolate:
    def test_isolate_existing_engine(self):
        isolator = ProcessIsolator()
        isolator.spawn_engine("eng-1")
        result = isolator.isolate("eng-1")
        assert result is True

    def test_isolate_nonexistent_engine(self):
        isolator = ProcessIsolator()
        result = isolator.isolate("nonexistent")
        assert result is False

    def test_isolate_with_resource_limits(self):
        isolator = ProcessIsolator()
        isolator.spawn_engine("eng-1")
        limits = {"cpu": 2, "memory_mb": 512}
        isolator.isolate("eng-1", resource_limits=limits)
        assert isolator.processes["eng-1"]["limits"] == limits

    def test_isolate_default_limits(self):
        isolator = ProcessIsolator()
        isolator.spawn_engine("eng-1")
        isolator.isolate("eng-1")
        assert isolator.processes["eng-1"]["limits"] == {"cpu": 1, "memory_mb": 256}

    def test_isolate_after_kill_returns_false(self):
        isolator = ProcessIsolator()
        isolator.spawn_engine("eng-1")
        isolator.kill_engine("eng-1")
        result = isolator.isolate("eng-1")
        assert result is False


class TestKillEngine:
    def test_kill_existing_engine(self):
        isolator = ProcessIsolator()
        isolator.spawn_engine("eng-1")
        result = isolator.kill_engine("eng-1")
        assert result is True

    def test_kill_removes_process(self):
        isolator = ProcessIsolator()
        isolator.spawn_engine("eng-1")
        isolator.kill_engine("eng-1")
        assert "eng-1" not in isolator.processes

    def test_kill_nonexistent_engine(self):
        isolator = ProcessIsolator()
        result = isolator.kill_engine("nonexistent")
        assert result is False

    def test_kill_same_engine_twice(self):
        isolator = ProcessIsolator()
        isolator.spawn_engine("eng-1")
        first = isolator.kill_engine("eng-1")
        second = isolator.kill_engine("eng-1")
        assert first is True
        assert second is False

    def test_kill_one_does_not_affect_other(self):
        isolator = ProcessIsolator()
        isolator.spawn_engine("eng-1")
        isolator.spawn_engine("eng-2")
        isolator.kill_engine("eng-1")
        assert "eng-1" not in isolator.processes
        assert "eng-2" in isolator.processes


class TestBoundaryConditions:
    def test_spawn_empty_engine_id(self):
        isolator = ProcessIsolator()
        result = isolator.spawn_engine("")
        assert result is True
        assert "" in isolator.processes

    def test_isolate_before_spawn(self):
        isolator = ProcessIsolator()
        result = isolator.isolate("never-spawned")
        assert result is False

    def test_kill_before_spawn(self):
        isolator = ProcessIsolator()
        result = isolator.kill_engine("never-spawned")
        assert result is False

    def test_spawn_overwrites_existing(self):
        isolator = ProcessIsolator()
        isolator.spawn_engine("eng-1", config={"v": 1})
        isolator.spawn_engine("eng-1", config={"v": 2})
        assert isolator.processes["eng-1"]["config"] == {"v": 2}

    def test_isolate_with_empty_limits_uses_default(self):
        isolator = ProcessIsolator()
        isolator.spawn_engine("eng-1")
        isolator.isolate("eng-1", resource_limits={})
        assert isolator.processes["eng-1"]["limits"] == {"cpu": 1, "memory_mb": 256}

    def test_isolate_with_custom_cpu_and_memory(self):
        isolator = ProcessIsolator()
        isolator.spawn_engine("eng-1")
        limits = {"cpu": 4, "memory_mb": 1024}
        isolator.isolate("eng-1", resource_limits=limits)
        assert isolator.processes["eng-1"]["limits"]["cpu"] == 4
        assert isolator.processes["eng-1"]["limits"]["memory_mb"] == 1024
