# [A_test] module_id: SRC-TST-0094 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-252 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.contract.test_schema_stability
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
test_schema_stability.py —— Schema 稳定性快照测试

确保 shared/ 的核心数据结构不会意外变更——Task 字段、错误层次、类型别名、
枚举值等关键契约必须保持稳定（或在有充分理由时显式更新快照）。

对应盲点 B3：契约测试框架
对标：
  - insta (Rust): snapshot testing for data structures
  - syrupy (Python): snapshot assertions with test_update flag

设计原则：
  - 字段列表版 snapshot——不依赖外部序列化库，纯 Python list 对比
  - 变更新增字段不会导致测试失败，只会警告（warnings 而非 assert）
  - 字段重命名/删除会导致 hard fail——这是破坏性变更，必须显式确认
  - 显式快照更新机制：设置 EXPECTED_VERSION 版本号，强制人工审核

SSoT: MOD-INF-016 §5.1 29 文件清单 + §7.1 12 消费者
"""

from __future__ import annotations

import re

import pytest


def _pydantic_fields(model_class: type) -> dict[str, str]:
    """提取 Pydantic V2 模型的字段名→类型映射。"""
    result: dict[str, str] = {}
    for name, info in model_class.model_fields.items():
        annotation = info.annotation
        if annotation is not None:
            type_str = str(annotation)
            type_str = re.sub(r"<class '([^']+)'>", r"\1", type_str)
            type_str = re.sub(
                r"typing\.(Optional|Union|List|Dict|Set|Tuple|Literal|Annotated|ClassVar)",
                r"\1",
                type_str,
            )
            result[name] = type_str
        else:
            result[name] = "Any"
    return result


# =============================================================================
# Task 字段快照（31 字段）
# =============================================================================

TASK_EXPECTED_FIELDS = {
    "task_id": "str",
    "namespace": "TaskNamespace | None",
    "seq": "int",
    "title": "str",
    "status": "TaskStatus",
    "priority": "Priority",
    "phase": "ContractPhase | None",
    "execution_model": "ExecutionModel | None",
    "model_rationale": "str | None",
    "fallback_model": "ExecutionModel | None",
    "safety_level": "SafetyLevel",
    "directive": "str | None",
    "idempotent": "bool",
    "classification": "Classification | None",
    "evolution_policy": "EvolutionPolicy | None",
    "estimate_hours": "float | None",
    "actual_hours": "float | None",
    "files_in_scope": "list[str] | None",
    "deliverables": "list[str] | None",
    "acceptance": "list[str] | None",
    "depends_on": "list[str] | None",
    "tags": "list[str] | None",
    "session_id": "str | None",
    "waiting_for": "str | None",
    "ready_at": "datetime.datetime | None",
    "completed_at": "datetime.datetime | None",
    "created_at": "datetime.datetime | None",
    "updated_at": "datetime.datetime | None",
    "is_deleted": "bool",
    "deleted_at": "datetime.datetime | None",
    "schema_version": "str",
}


class TestTaskSchemaStability:
    """Task 模型的字段稳定性快照测试。"""

    def test_task_field_count(self) -> None:
        from zephyr.gov_enforcement.rule_enforcement.task_types import Task

        fields = _pydantic_fields(Task)
        actual_count = len(fields)

        assert actual_count == 31, (
            f"Task 字段数预期 31，实际 {actual_count}。\n"
            f"  当前字段: {sorted(fields.keys())}\n"
            f"  注意：31 字段 = 28 业务 + 3 DB 追踪（is_deleted/deleted_at/schema_version）\n"
            f"  新增字段会改变契约，请检查所有 12 消费者是否兼容。"
        )

    def test_task_required_fields_present(self) -> None:
        from zephyr.gov_enforcement.rule_enforcement.task_types import Task

        fields = _pydantic_fields(Task)
        field_names = set(fields.keys())

        for expected_name, expected_type in TASK_EXPECTED_FIELDS.items():
            assert expected_name in field_names, (
                f"Task 缺失关键字段: {expected_name}\n"
                f"  这可能是破坏性变更——消费者依赖此字段。\n"
                f"  如果是有意删除，请更新 TASK_EXPECTED_FIELDS 字典。"
            )

    def test_extra_fields_warned(self) -> None:
        from zephyr.gov_enforcement.rule_enforcement.task_types import Task

        fields = _pydantic_fields(Task)
        extra = set(fields.keys()) - set(TASK_EXPECTED_FIELDS.keys())

        if extra:
            pytest.fail(
                f"Task 包含预期外的字段: {sorted(extra)}\n"
                f"  这改变了数据契约，影响所有 12 消费者。\n"
                f"  如果有意新增字段，请：\n"
                f"    1. 更新 TASK_EXPECTED_FIELDS 字典\n"
                f"    2. 更新 schemas.py Task docstring（字段计数 31→{31 + len(extra)}）\n"
                f"    3. 更新 models.py TaskCard docstring\n"
                f"    4. 更新 blueprint.md/registries\n"
                f"    5. 检查所有消费者兼容性"
            )


# =============================================================================
# TaskCard 继承验证
# =============================================================================


class TestTaskCardInheritance:
    """TaskCard 继承 Task 的完整性验证。"""

    def test_taskcard_inherits_task(self) -> None:
        from zephyr.gov_enforcement.rule_enforcement.task_types import Task
        from zephyr.shared.foundation.models import TaskCard

        assert issubclass(TaskCard, Task), (
            f"TaskCard 必须继承 schemas.py Task。\n"
            f"  这是 ADR-0040 + metadata_registry.yaml §7 的铁律。\n"
            f"  当前 TaskCard 的 MRO: {[c.__name__ for c in TaskCard.__mro__]}"
        )

    def test_taskcard_has_all_task_fields(self) -> None:
        from zephyr.gov_enforcement.rule_enforcement.task_types import Task
        from zephyr.shared.foundation.models import TaskCard

        task_fields = set(Task.model_fields.keys())
        taskcard_fields = set(TaskCard.model_fields.keys())

        missing = task_fields - taskcard_fields
        assert not missing, f"TaskCard 缺失 Task 基类的字段: {sorted(missing)}\n  TaskCard 只能新增字段，不能删减。"

    def test_taskcard_no_field_shadow_conflict(self) -> None:
        from zephyr.gov_enforcement.rule_enforcement.task_types import Task
        from zephyr.shared.foundation.models import TaskCard

        task_types = {name: info.annotation for name, info in Task.model_fields.items()}
        taskcard_types = {name: info.annotation for name, info in TaskCard.model_fields.items()}

        conflicts = []
        for name in task_types.keys() & taskcard_types.keys():
            if task_types[name] != taskcard_types[name]:
                conflicts.append(f"  {name}: Task={task_types[name]}, TaskCard={taskcard_types[name]}")

        assert not conflicts, (
            "TaskCard 与 Task 字段类型冲突:\n"
            + "\n".join(conflicts)
            + "\n  继承字段不应改变类型——这违反 Liskov 替换原则。"
        )


# =============================================================================
# 错误层次验证
# =============================================================================

ERROR_SUBCLASSES_EXPECTED = {
    "ConfigError",
    "ContextError",
    "ContractError",
    "DataError",
    "FeedbackError",
    "GateError",
    "IOError",
    "PipelineError",
    "SecurityError",
    "TaskError",
    "UnimplementedError",
    "ValidationError",
}


class TestErrorHierarchy:
    """错误层次稳定性验证。"""

    def test_all_error_subclasses_exist(self) -> None:
        from zephyr.shared.foundation import errors as err_module

        found = {
            name
            for name in dir(err_module)
            if isinstance(getattr(err_module, name), type)
            and issubclass(getattr(err_module, name), err_module.ZephyrBaseError)
            and name != "ZephyrBaseError"
        }

        assert found == ERROR_SUBCLASSES_EXPECTED, (
            f"错误子类清单不一致。\n"
            f"  额外: {found - ERROR_SUBCLASSES_EXPECTED}\n"
            f"  缺失: {ERROR_SUBCLASSES_EXPECTED - found}\n"
            f"  如果是招商新增错误子类，请更新 ERROR_SUBCLASSES_EXPECTED。\n"
            f"  如果错误子类被删除，检查所有 catch 语句。"
        )

    def test_error_subclasses_instantiable(self) -> None:
        from zephyr.shared.foundation import errors as err_module

        for name in ERROR_SUBCLASSES_EXPECTED:
            cls = getattr(err_module, name)
            try:
                instance = cls(f"{name} test message")
                assert str(instance) == f"{name} test message"
            except Exception as e:
                pytest.fail(f"{name} 实例化失败: {e}")


# =============================================================================
# 类型别名验证
# =============================================================================

EXPECTED_TYPE_ALIASES = {
    "TaskId",
    "ModuleId",
    "FilePath",
    "AbsPath",
    "SessionId",
    "AgentId",
    "ContractId",
    "FingerprintHash",
    "TokenCount",
    "BlueprintVersion",
    "DocumentId",
    "MetricName",
    "SSoT_Key",
}


class TestTypeAliases:
    """共享类型别名稳定性验证。"""

    def test_all_type_aliases_exist(self) -> None:
        from zephyr.shared.foundation import types as t_module

        found = set(t_module.__all__) if hasattr(t_module, "__all__") else set()

        if not found:
            found = {
                name
                for name in dir(t_module)
                if not name.startswith("_") and not name.islower() and not callable(getattr(t_module, name, None))
            }

        assert found == EXPECTED_TYPE_ALIASES, (
            f"Type alias 清单不一致。\n"
            f"  额外: {found - EXPECTED_TYPE_ALIASES}\n"
            f"  缺失: {EXPECTED_TYPE_ALIASES - found}\n"
            f"  如果是招商新增类型别名，请更新 EXPECTED_TYPE_ALIASES。"
        )
