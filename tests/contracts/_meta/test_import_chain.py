# [A_test] module_id: SRC-TST-0093 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-251 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.contract.test_import_chain
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
test_import_chain.py —— 消费者导入链路验证

验证 shared/ 和 core/ 的所有外部消费者能正常导入——shared/ 变更后的第一道安全网。

对应盲点 B3：契约测试框架
对标：Google "Live at Head" 模式——每次 shared/ 变更后所有消费者必须能编译

设计原则：
  - 不测试 shared 内部互导入（那是 shared/ 自己的单元测试职责）
  - 只测试外部跨模块导入——这反映真实的消费者兼容性
  - 失败 = shared/ 破坏性变更，需要检查 ADR-0040 extra=forbid 等约束

SSoT: MOD-INF-016 §7.1 12 消费者模块
"""

from __future__ import annotations

import importlib
import pathlib
import re
from typing import NamedTuple

import pytest
from zephyr.shared.io.paths import REPO_ROOT


class Consumer(NamedTuple):
    module: str
    path: str
    description: str
    is_package: bool = False


SRC_DIR = REPO_ROOT / "src" / "zephyr"

CONSUMERS: list[Consumer] = [
    Consumer("gates.gate_engine", "src/zephyr/governance/rule_enforcement/gate_engine/gate_engine.py", "G7 门禁引擎"),
    Consumer("db.task_repo", "src/zephyr/db/task_repo.py", "Task 持久化仓库"),
    Consumer("db.sqlite_schema", "src/zephyr/db/sqlite_schema.py", "SQLite Schema 管理"),
    Consumer("mcp.task_manager_server", "src/zephyr/mcp/task_manager_server.py", "MCP Task 管理服务端"),
    Consumer("mcp.blueprint_search_server", "src/zephyr/mcp/blueprint_search_server.py", "MCP 蓝图搜索服务端"),
    Consumer("orchestrator.trigger_router", "src/zephyr/orchestrator/trigger_router.py", "管线触发路由器"),
    Consumer("feedback-loop", "src/zephyr/feedback-loop/__init__.py", "Feedback Loop MOD-FEEDBACK_LOOP", is_package=True),
    Consumer("kb", "src/zephyr/knowledge/kb/__init__.py", "Knowledge Base MOD-KB-001", is_package=True),
]


def _extract_shared_imports(file_path: pathlib.Path) -> list[str]:
    """从源文件中提取所有 zephyr.shared / zephyr.orchestrator.core 导入语句。

    如果是 package 消费者（is_package=True），递归扫描整个包目录。
    """
    pattern = re.compile(
        r"^\s*(?:from\s+(zephyr\.(?:shared|core)[^\s]+)\s+import|import\s+(zephyr\.(?:shared|core)[^\s]+))",
        re.MULTILINE,
    )

    if file_path.is_dir() or (file_path.name == "__init__.py" and file_path.parent.is_dir()):
        pkg_dir = file_path if file_path.is_dir() else file_path.parent
        all_imports: list[str] = []
        for py_file in pkg_dir.rglob("*.py"):
            if py_file.exists():
                content = py_file.read_text(encoding="utf-8")
                all_imports.extend([m.group(1) or m.group(2) for m in pattern.finditer(content)])
        return list(dict.fromkeys(all_imports))

    if not file_path.exists():
        return []

    content = file_path.read_text(encoding="utf-8")
    return [m.group(1) or m.group(2) for m in pattern.finditer(content)]


class TestConsumerImports:
    """验证所有消费者模块能正常导入。"""

    @pytest.mark.parametrize(
        "consumer",
        CONSUMERS,
        ids=[c.module for c in CONSUMERS],
    )
    def test_consumer_imports_without_error(self, consumer: Consumer) -> None:
        """每个外部消费者必须能完整导入，不抛出 ImportError / AttributeError。"""
        full_module = f"zephyr.{consumer.module}"
        try:
            importlib.import_module(full_module)
        except ImportError as e:
            pytest.fail(
                f"消费者 {consumer.module} ({consumer.description}) 导入失败:\n"
                f"  {e}\n"
                f"  这意味着 shared/ 的变更破坏了这个消费者。\n"
                f"  检查最近对 shared/ 的修改。"
            )
        except Exception as e:
            pytest.fail(f"消费者 {consumer.module} 导入时抛出运行时异常:\n  {type(e).__name__}: {e}")

    @pytest.mark.parametrize(
        "consumer",
        CONSUMERS,
        ids=[c.module for c in CONSUMERS],
    )
    def test_consumer_has_shared_imports(self, consumer: Consumer) -> None:
        """每个消费者应确实引用了 shared/ 或 core/（否则不是消费者）。"""
        file_path = REPO_ROOT / consumer.path
        imports = _extract_shared_imports(file_path)
        assert imports, (
            f"消费者 {consumer.module} ({consumer.path}) 没有从 shared/ 或 core/ 导入任何符号。\n"
            f"  要么这个文件不是消费者，要么导入被重构掉了。\n"
            f"  如果是后者，请从 CONSUMERS 列表中移除。"
        )


class TestAllConsumerFilesExist:
    """验证消费者文件确实存在。"""

    @pytest.mark.parametrize(
        "consumer",
        CONSUMERS,
        ids=[c.module for c in CONSUMERS],
    )
    def test_consumer_file_exists(self, consumer: Consumer) -> None:
        """每个消费者的源文件必须存在。"""
        file_path = REPO_ROOT / consumer.path
        assert file_path.exists(), (
            f"消费者 {consumer.module} 的源文件不存在: {consumer.path}\n"
            f"  可能文件已被移动或删除。请更新 CONSUMERS 列表。"
        )


def test_consumer_list_not_empty() -> None:
    """消费者列表不能为空——否则契约测试失去意义。"""
    assert len(CONSUMERS) >= 8, f"消费者列表只有 {len(CONSUMERS)} 个条目。\n  契约测试需要足够多的消费者覆盖才能有效。"


def test_no_duplicate_consumers() -> None:
    """消费者列表中不应有重复条目。"""
    seen: set[str] = set()
    for c in CONSUMERS:
        assert c.module not in seen, f"重复的消费者: {c.module}"
        seen.add(c.module)
