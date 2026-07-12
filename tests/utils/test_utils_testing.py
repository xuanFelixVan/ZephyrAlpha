# [A_test] module_id: SRC-TST-1776 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_utils_testing

# [INVARIANTS] make_valid_task返回合法Task;make_p0_task优先级P0;make_completed_task状态COMPLETED

# [MODIFY-GUARD] testing.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 无

# [TESTS] pytest tests/test_utils_testing.py -q
# [TTL] task_bound

from zephyr.gov_enforcement.rule_enforcement.task_types import TaskStatus
from zephyr.integration.shared.schema.schemas import AuditReport, FailurePattern, HandoffPackage, KnowledgeEntry, Task
from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
from zephyr.shared.utils.testing import (
    make_completed_task,
    make_p0_task,
    make_valid_audit_report,
    make_valid_failure_pattern,
    make_valid_handoff_package,
    make_valid_knowledge_entry,
    make_valid_task,
)


class TestMakeValidTask:
    def test_returns_task_instance(self):
        task = make_valid_task()
        assert isinstance(task, Task)

    def test_default_values(self):
        task = make_valid_task()
        assert task.title == "Factory-generated test task"
        assert task.phase == 0
        assert task.safety_level == SafetyLevel.M
        assert task.status == TaskStatus.PENDING
        assert task.priority == Priority.P2

    def test_custom_overrides(self):
        task = make_valid_task(title="Custom title", phase=3)
        assert task.title == "Custom title"
        assert task.phase == 3

    def test_custom_task_id(self):
        task = make_valid_task(task_id="DW-9999")
        assert task.task_id == "DW-9999"

    def test_auto_generates_task_id(self):
        task = make_valid_task()
        assert task.task_id != ""


class TestMakeP0Task:
    def test_p0_priority(self):
        task = make_p0_task()
        assert task.priority == Priority.P0
        assert task.safety_level == SafetyLevel.H

    def test_overrides(self):
        task = make_p0_task(phase=2)
        assert task.phase == 2
        assert task.priority == Priority.P0


class TestMakeCompletedTask:
    def test_completed_status(self):
        task = make_completed_task()
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None


class TestMakeValidAuditReport:
    def test_returns_audit_report(self):
        report = make_valid_audit_report()
        assert isinstance(report, AuditReport)
        assert report.scanner == "factory-scanner"
        assert len(report.findings) >= 1

    def test_custom_scanner(self):
        report = make_valid_audit_report(scanner="custom-scanner")
        assert report.scanner == "custom-scanner"


class TestMakeValidKnowledgeEntry:
    def test_returns_knowledge_entry(self):
        ke = make_valid_knowledge_entry()
        assert isinstance(ke, KnowledgeEntry)
        assert ke.ke_id.startswith("KE-")

    def test_custom_ke_id(self):
        ke = make_valid_knowledge_entry(ke_id="KE-042")
        assert ke.ke_id == "KE-042"


class TestMakeValidFailurePattern:
    def test_returns_failure_pattern(self):
        fp = make_valid_failure_pattern()
        assert isinstance(fp, FailurePattern)
        assert fp.pattern_id.startswith("F-")

    def test_custom_failure_type(self):
        from zephyr.integration.shared.schema.schemas import FailureType

        fp = make_valid_failure_pattern(failure_type=FailureType.TIMEOUT)
        assert fp.failure_type == FailureType.TIMEOUT


class TestMakeValidHandoffPackage:
    def test_returns_handoff_package(self):
        hp = make_valid_handoff_package()
        assert isinstance(hp, HandoffPackage)
        assert hp.session_id == "factory-session-001"
        assert len(hp.completed_tasks) > 0
        assert len(hp.next_actions) > 0

    def test_custom_session_id(self):
        hp = make_valid_handoff_package(session_id="session-abc")
        assert hp.session_id == "session-abc"
