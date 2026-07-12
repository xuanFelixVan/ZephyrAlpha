# [A_test] module_id: SRC-TST-0382 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
import os
import sys
import tempfile
import warnings
from datetime import UTC, datetime

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from zephyr.governance.persistence.task_repo import TaskNotFoundError, TaskRepository
from zephyr.gov_enforcement.rule_enforcement.task_types import Task, TaskNamespace, TaskStatus
from zephyr.integration.shared.schema.execution_model import ExecutionModel
from zephyr.integration.shared.schema.severity_types import SafetyLevel
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

_NOW = datetime.now(UTC)


def _make_task(**overrides):
    defaults = dict(
        task_id="OPS-1",
        namespace=TaskNamespace.OPS,
        seq=1,
        title="测试任务",
        safety_level=SafetyLevel.L,
        phase=1,
        execution_model=ExecutionModel.deepseek,
        source_blueprint="MOD-INF-039",
        source_section="§3.2.1",
        description="根因：测试 auto_split 功能。治根：验证任务卡拆分机制，确保超粒度任务卡能被自动拆分为合规的原子卡。施工步骤：(1) 构造超粒度任务卡并调用 auto_split 方法验证拆分结果。验收标准：拆分后每张子卡通过粒度门禁且幻觉风险为零。",
        files_in_scope=[str(REPO_ROOT / "src" / "zephyr" / "db" / "task_repo.py")],
        deliverables=["task_repo.py 修复完成"],
        acceptance=["拆分后子卡通过粒度门禁"],
        allowed_touch=[str(REPO_ROOT / "src" / "zephyr" / "db" / "task_repo.py")],
        applicable_rules=[{"module_id": "MOD-INF-039", "section": "§3.2.1", "reason": "测试"}],
        rollback_instructions="git checkout -- .",
        post_sync_standard=["echo ok"],
        dependency_type="soft",
        created_at=_NOW,
        updated_at=_NOW,
    )
    defaults.update(overrides)
    return Task(**defaults)


def _create_repo():
    tmp = tempfile.mkdtemp(prefix="zephyr_split_test_")
    db_path = os.path.join(tmp, "test_data/databases/governance.db")
    return TaskRepository(db_path=db_path)


class TestAutoSplitNoViolation:
    def test_no_split_when_granularity_ok(self):
        repo = _create_repo()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            task = _make_task(task_id="OPS-1", seq=1)
        sub_cards = repo.auto_split_task(task)
        assert sub_cards == []


class TestAutoSplitByDeliverable:
    def test_split_by_deliverable(self):
        repo = _create_repo()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            task = _make_task(
                task_id="OPS-1",
                seq=1,
                deliverables=["产出A", "产出B"],
            )
        sub_cards = repo.auto_split_task(task)
        assert len(sub_cards) == 2
        for card in sub_cards:
            assert len(card.deliverables) == 1

    def test_sub_cards_have_dependency_chain(self):
        repo = _create_repo()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            task = _make_task(
                task_id="OPS-1",
                seq=1,
                deliverables=["产出A", "产出B"],
            )
        sub_cards = repo.auto_split_task(task)
        assert len(sub_cards) == 2
        assert sub_cards[1].depends_on == [sub_cards[0].task_id]
        assert sub_cards[1].dependency_type == "hard"


class TestAutoSplitByFile:
    def test_split_by_file(self):
        repo = _create_repo()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            task = _make_task(
                task_id="OPS-1",
                seq=1,
                deliverables=["产出A"],
                files_in_scope=[
                    str(REPO_ROOT / "src" / "zephyr" / "db" / "task_repo.py"),
                    str(REPO_ROOT / "src" / "zephyr" / "core" / "models.py"),
                    str(REPO_ROOT / "src" / "zephyr" / "gates" / "task_types.py"),
                    str(REPO_ROOT / "tests" / "test_task_types.py"),
                ],
                allowed_touch=[
                    str(REPO_ROOT / "src" / "zephyr" / "db" / "task_repo.py"),
                    str(REPO_ROOT / "src" / "zephyr" / "core" / "models.py"),
                    str(REPO_ROOT / "src" / "zephyr" / "gates" / "task_types.py"),
                    str(REPO_ROOT / "tests" / "test_task_types.py"),
                ],
            )
        sub_cards = repo.auto_split_task(task)
        assert len(sub_cards) >= 2
        for card in sub_cards:
            assert len(card.files_in_scope) <= 3


class TestAutoSplitByAcceptance:
    def test_split_by_acceptance(self):
        repo = _create_repo()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            task = _make_task(
                task_id="OPS-1",
                seq=1,
                deliverables=["产出A"],
                acceptance=["验收点A", "验收点B"],
            )
        sub_cards = repo.auto_split_task(task, split_strategy="by_acceptance")
        assert len(sub_cards) == 2
        for card in sub_cards:
            assert len(card.acceptance) == 1


class TestAutoSplitByTarget:
    def test_split_by_target(self):
        repo = _create_repo()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            task = _make_task(
                task_id="OPS-1",
                seq=1,
                deliverables=["产出A"],
                description="根因：测试 R4 门禁。治根：验证施工目标上限。施工步骤：(1) 修改 _validate_template_fields() 增加空字符串判断 (2) 修改 _validate_granularity() 增加空列表判断。影响范围：task_repo.py。验收标准：空字符串和空列表均被校验拦截。",
            )
        sub_cards = repo.auto_split_task(task, split_strategy="by_target")
        assert len(sub_cards) >= 2
        for card in sub_cards:
            assert len(card.deliverables) <= 1
            assert len(card.acceptance) <= 1


class TestAutoSplitG1Vague:
    def test_split_g1_vague(self):
        repo = _create_repo()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            task = _make_task(
                task_id="OPS-1",
                seq=1,
                description="根因：系统质量差。治根：改进系统。施工步骤：修复所有问题，让系统变好。影响范围：整个项目。验收标准：系统正常运行。",
                files_in_scope=[
                    str(REPO_ROOT / "src" / "zephyr" / "db" / "task_repo.py"),
                    str(REPO_ROOT / "src" / "zephyr" / "autopilot" / "autopilot.py"),
                    str(REPO_ROOT / "tests" / "test_task_types.py"),
                    str(REPO_ROOT / "docs" / "03_modules" / "_domain-infra_ops" / "task-system" / "blueprint.md"),
                    str(REPO_ROOT / "src" / "zephyr" / "core" / "blueprint_decomposer.py"),
                ],
                deliverables=["系统改进完成", "测试通过", "文档更新"],
                acceptance=["系统正常运行", "测试通过", "文档更新"],
                allowed_touch=[
                    str(REPO_ROOT / "src" / "zephyr" / "db" / "task_repo.py"),
                    str(REPO_ROOT / "src" / "zephyr" / "autopilot" / "autopilot.py"),
                    str(REPO_ROOT / "tests" / "test_task_types.py"),
                    str(REPO_ROOT / "docs" / "03_modules" / "_domain-infra_ops" / "task-system" / "blueprint.md"),
                    str(REPO_ROOT / "src" / "zephyr" / "core" / "blueprint_decomposer.py"),
                ],
            )
        sub_cards = repo.auto_split_task(task)
        assert len(sub_cards) >= 3
        for card in sub_cards:
            assert len(card.deliverables) <= 1
            assert len(card.files_in_scope) <= 3
            assert len(card.acceptance) <= 1


class TestAutoSplitWithTaskId:
    def test_split_existing_task_cancels_original(self):
        repo = _create_repo()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            task = _make_task(task_id="OPS-1", seq=1)
        repo.create(task, allow_direct_create=True)
        repo._conn.execute(
            "UPDATE tasks SET deliverables=? WHERE task_id=?",
            ('["产出A", "产出B"]', "OPS-1"),
        )
        repo._conn.commit()
        sub_cards = repo.auto_split_task("OPS-1")
        assert len(sub_cards) >= 2
        original = repo.get("OPS-1")
        assert original.status == TaskStatus.CANCELLED


class TestAutoSplitNonexistent:
    def test_split_nonexistent_raises(self):
        repo = _create_repo()
        with pytest.raises(TaskNotFoundError):
            repo.auto_split_task("OPS-999")


class TestAutoSplitSubCardQuality:
    def test_sub_cards_pass_granularity_gate(self):
        repo = _create_repo()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            task = _make_task(
                task_id="OPS-1",
                seq=1,
                deliverables=["产出A", "产出B", "产出C"],
            )
        sub_cards = repo.auto_split_task(task)
        for card in sub_cards:
            violations = repo._validate_granularity(card)
            assert violations == [], f"子卡 {card.task_id} 粒度违规: {violations}"

    def test_sub_cards_have_auto_split_tag(self):
        repo = _create_repo()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            task = _make_task(
                task_id="OPS-1",
                seq=1,
                deliverables=["产出A", "产出B"],
            )
        sub_cards = repo.auto_split_task(task)
        for card in sub_cards:
            assert "auto-split" in card.tags
            assert "parent:OPS-1" in card.tags

    def test_sub_cards_description_has_structure(self):
        repo = _create_repo()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            task = _make_task(
                task_id="OPS-1",
                seq=1,
                deliverables=["产出A", "产出B"],
            )
        sub_cards = repo.auto_split_task(task)
        for card in sub_cards:
            assert "根因" in card.description
            assert "治根" in card.description
            assert "施工步骤" in card.description
            assert "验收标准" in card.description
            assert len(card.description) >= 100


class TestDetermineSplitStrategy:
    def test_strategy_by_deliverable(self):
        repo = _create_repo()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            task = _make_task(deliverables=["A", "B"])
        violations = repo._validate_granularity(task)
        strategy = TaskRepository._determine_split_strategy(task, violations)
        assert strategy == "by_deliverable"

    def test_strategy_by_file(self):
        repo = _create_repo()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            task = _make_task(
                deliverables=["A"],
                files_in_scope=["f1", "f2", "f3", "f4"],
            )
        violations = repo._validate_granularity(task)
        strategy = TaskRepository._determine_split_strategy(task, violations)
        assert strategy == "by_file"
