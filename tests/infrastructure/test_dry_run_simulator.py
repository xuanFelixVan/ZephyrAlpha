# [A_test] module_id: MOD-GOV_dry_run_simulator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §dry_run_simulator
# [MODULE] tests.test_dry_run_simulator
# [INVARIANTS] DryRunSimulator.simulate必须返回SimulationResult; 危险操作必须BLOCKED
# [MODIFY-GUARD] 仅当dry_run_simulator公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_dry_run_simulator.py -q
# [TTL] task_bound

from zephyr.infrastructure.dry_run_simulator import (
    DryRunSimulator,
    SimulationResult,
    SimulationRisk,
    SimulationStatus,
)


class TestSimulationRisk:
    def test_values(self):
        assert SimulationRisk.NONE.value == "none"
        assert SimulationRisk.LOW.value == "low"
        assert SimulationRisk.MEDIUM.value == "medium"
        assert SimulationRisk.HIGH.value == "high"
        assert SimulationRisk.CRITICAL.value == "critical"


class TestSimulationStatus:
    def test_values(self):
        assert SimulationStatus.PASSED.value == "passed"
        assert SimulationStatus.PASSED_WITH_WARNINGS.value == "passed_with_warnings"
        assert SimulationStatus.BLOCKED.value == "blocked"
        assert SimulationStatus.ERROR.value == "error"


class TestSimulationResult:
    def test_default_construction(self):
        result = SimulationResult(simulation_id="SIM-0001")
        assert result.simulation_id == "SIM-0001"
        assert result.status == SimulationStatus.PASSED
        assert result.risk == SimulationRisk.NONE
        assert result.warnings == []
        assert result.errors == []
        assert result.affected_files == []
        assert result.is_safe is True

    def test_blocked_not_safe(self):
        result = SimulationResult(
            simulation_id="SIM-0002",
            status=SimulationStatus.BLOCKED,
        )
        assert result.is_safe is False


class TestDryRunSimulator:
    def test_instantiation(self, tmp_path):
        sim = DryRunSimulator(sandbox_root=str(tmp_path / "dry_runs"))
        assert sim is not None

    def test_simulate_safe_operation(self, tmp_path):
        sim = DryRunSimulator(sandbox_root=str(tmp_path / "dry_runs"))
        result = sim.simulate(
            {
                "type": "file_write",
                "target": str(tmp_path / "safe_file.py"),
                "content": "print('hello')",
            }
        )
        assert isinstance(result, SimulationResult)
        assert result.status in (SimulationStatus.PASSED, SimulationStatus.PASSED_WITH_WARNINGS)

    def test_simulate_dangerous_pattern(self, tmp_path):
        sim = DryRunSimulator(sandbox_root=str(tmp_path / "dry_runs"))
        result = sim.simulate(
            {
                "type": "file_write",
                "target": "/tmp/test.sh",
                "content": "rm -rf /",
            }
        )
        assert result.status == SimulationStatus.BLOCKED
        assert result.risk == SimulationRisk.CRITICAL
        assert any("危险操作模式" in w for w in result.warnings)

    def test_simulate_sensitive_path(self, tmp_path):
        sim = DryRunSimulator(sandbox_root=str(tmp_path / "dry_runs"))
        result = sim.simulate(
            {
                "type": "file_write",
                "target": "C:\\Windows\\System32\\test.py",
                "content": "safe content",
            }
        )
        assert result.risk in (SimulationRisk.HIGH, SimulationRisk.CRITICAL)
        assert any("敏感路径" in w for w in result.warnings)

    def test_simulate_drop_table(self, tmp_path):
        sim = DryRunSimulator(sandbox_root=str(tmp_path / "dry_runs"))
        result = sim.simulate(
            {
                "type": "sql",
                "target": "db.sqlite",
                "content": "DROP TABLE users;",
            }
        )
        assert result.status == SimulationStatus.BLOCKED
        assert result.risk == SimulationRisk.CRITICAL

    def test_simulate_file_operation_tracks_affected(self, tmp_path):
        sim = DryRunSimulator(sandbox_root=str(tmp_path / "dry_runs"))
        result = sim.simulate(
            {
                "type": "file_write",
                "target": "/tmp/output.txt",
                "content": "data",
            }
        )
        assert "/tmp/output.txt" in result.affected_files

    def test_simulate_rollback_plan(self, tmp_path):
        sim = DryRunSimulator(sandbox_root=str(tmp_path / "dry_runs"))
        result = sim.simulate(
            {
                "type": "file_delete",
                "target": "/tmp/old_file.txt",
                "content": "",
            }
        )
        assert result.rollback_plan != ""

    def test_simulate_batch(self, tmp_path):
        sim = DryRunSimulator(sandbox_root=str(tmp_path / "dry_runs"))
        ops = [
            {"type": "file_write", "target": "/tmp/a.py", "content": "pass"},
            {"type": "file_write", "target": "/tmp/b.py", "content": "rm -rf /"},
        ]
        results = sim.simulate_batch(ops)
        assert len(results) == 2
        assert results[0].status != SimulationStatus.BLOCKED or results[0].risk == SimulationRisk.NONE
        assert results[1].status == SimulationStatus.BLOCKED

    def test_simulate_unknown_type(self, tmp_path):
        sim = DryRunSimulator(sandbox_root=str(tmp_path / "dry_runs"))
        result = sim.simulate(
            {
                "type": "unknown",
                "target": "/tmp/test",
                "content": "data",
            }
        )
        assert isinstance(result, SimulationResult)

    def test_simulate_empty_operation(self, tmp_path):
        sim = DryRunSimulator(sandbox_root=str(tmp_path / "dry_runs"))
        result = sim.simulate({})
        assert isinstance(result, SimulationResult)
