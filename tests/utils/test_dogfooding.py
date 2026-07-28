# [A_test] module_id: MOD-GOV_dogfooding | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-379 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_dogfooding
# [INVARIANTS] DogfoodReport.self_consistent=True iff tasks_passed==tasks_tested
# [MODIFY-GUARD] 仅当dogfooding公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_dogfooding.py -q
# [TTL] task_bound

import json

from zephyr.shared.maintenance.dogfooding import (
    DOGFOOD_TASKS,
    Dogfooding,
    DogfoodReport,
    DogfoodTask,
)


class TestDogfoodingInstantiation:
    def test_default_instantiation(self):
        df = Dogfooding()
        assert df is not None

    def test_instantiation_with_data_dir(self, tmp_path):
        df = Dogfooding(data_dir=tmp_path / "dogfood")
        assert df is not None

    def test_instantiation_with_none_data_dir(self):
        df = Dogfooding(data_dir=None)
        assert df is not None

    def test_default_tasks_loaded(self):
        df = Dogfooding()
        assert len(df.tasks) == len(DOGFOOD_TASKS)


class TestDogfoodingRegisterTask:
    def test_register_custom_task(self):
        df = Dogfooding()
        initial_count = len(df.tasks)
        task = DogfoodTask("CUSTOM-001", "Custom test", "MOD-TEST", "P2")
        df.register_dogfood_task(task)
        assert len(df.tasks) == initial_count + 1

    def test_register_multiple_tasks(self):
        df = Dogfooding()
        initial_count = len(df.tasks)
        for i in range(3):
            df.register_dogfood_task(DogfoodTask(f"CUSTOM-{i}", f"Test {i}", "MOD", "P2"))
        assert len(df.tasks) == initial_count + 3

    def test_register_task_with_self_test_false(self):
        df = Dogfooding()
        task = DogfoodTask("CUSTOM-NOSELF", "No self test", "MOD", "P3", self_test=False)
        df.register_dogfood_task(task)
        assert df.tasks[-1].self_test is False


class TestDogfoodingRunCycle:
    def test_run_cycle_returns_report(self, tmp_path):
        df = Dogfooding(data_dir=tmp_path / "dogfood")
        report = df.run_dogfood_cycle()
        assert isinstance(report, DogfoodReport)

    def test_run_cycle_self_consistent(self, tmp_path):
        df = Dogfooding(data_dir=tmp_path / "dogfood")
        report = df.run_dogfood_cycle()
        assert report.self_consistent is True
        assert report.tasks_passed == report.tasks_tested

    def test_run_cycle_tasks_tested_count(self, tmp_path):
        df = Dogfooding(data_dir=tmp_path / "dogfood")
        report = df.run_dogfood_cycle()
        assert report.tasks_tested == len(DOGFOOD_TASKS)

    def test_run_cycle_report_id_format(self, tmp_path):
        df = Dogfooding(data_dir=tmp_path / "dogfood")
        report = df.run_dogfood_cycle()
        assert report.report_id.startswith("DOGFOOD-")

    def test_run_cycle_timestamp(self, tmp_path):
        df = Dogfooding(data_dir=tmp_path / "dogfood")
        report = df.run_dogfood_cycle()
        assert len(report.timestamp_utc) > 0

    def test_run_cycle_saves_report_file(self, tmp_path):
        data_dir = tmp_path / "dogfood"
        df = Dogfooding(data_dir=data_dir)
        report = df.run_dogfood_cycle()
        report_path = data_dir / f"{report.report_id}.json"
        assert report_path.exists()
        data = json.loads(report_path.read_text(encoding="utf-8"))
        assert data["report_id"] == report.report_id
        assert data["tasks_tested"] == report.tasks_tested

    def test_run_cycle_with_custom_task(self, tmp_path):
        df = Dogfooding(data_dir=tmp_path / "dogfood")
        df.register_dogfood_task(DogfoodTask("CUSTOM-001", "Extra", "MOD", "P2"))
        report = df.run_dogfood_cycle()
        assert report.tasks_tested == len(DOGFOOD_TASKS) + 1

    def test_run_cycle_empty_findings_on_success(self, tmp_path):
        df = Dogfooding(data_dir=tmp_path / "dogfood")
        report = df.run_dogfood_cycle()
        assert report.findings == []


class TestDogfoodTask:
    def test_task_construction(self):
        task = DogfoodTask("T-001", "Test task", "MOD-001", "P0")
        assert task.task_id == "T-001"
        assert task.description == "Test task"
        assert task.module == "MOD-001"
        assert task.priority == "P0"
        assert task.self_test is True

    def test_task_self_test_default(self):
        task = DogfoodTask("T-002", "Desc", "MOD", "P1")
        assert task.self_test is True


class TestDogfoodReport:
    def test_report_construction(self):
        report = DogfoodReport(
            report_id="R-001",
            tasks_tested=5,
            tasks_passed=5,
            self_consistent=True,
            findings=[],
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        assert report.report_id == "R-001"
        assert report.tasks_tested == 5
        assert report.tasks_passed == 5
        assert report.self_consistent is True
