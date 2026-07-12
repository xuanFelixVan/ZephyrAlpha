# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.test_source_consistency_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.commit_gates._diff_helpers; zephyr.governance.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged tests/ .py 文件 from zephyr.* import 的符号在源码中不存在时阻断 commit（passed=False）；tests/ 专属 gate（只检测测试文件，不检测源码）；module-level pytest.skip/importorskip 豁免（已标记漂移的测试文件不重复检测）；检查所有顶层符号（class/def/assign/annassign），不依赖 __all__（Python 允许显式 import 任何顶层符号）；源码文件不存在/解析失败 fail-open（passed=True，其他 gate 处理）；git diff 不可达 fail-open（logger.warning）
# [MODIFY-GUARD] gate_id="TEST-SOURCE-CONSISTENCY"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff/AST 解析异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_test_source_consistency_gate.py
# [A_module] module_id=MOD-GOV-test_source_consistency_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_source_consistency_gate.py — 测试-源码符号一致性门禁（TEST-SOURCE-CONSISTENCY，§5.178 防复发）

检测 staged tests/ .py 文件中 ``from zephyr.xxx import yyy`` 的 ``yyy`` 符号
在源码中是否存在——不存在则硬阻断 commit。

病根（第一性原理）
-----------------
architecture_debt §5.178：源码进化后测试未同步更新（名称漂移），导致
``pytest --collect-only`` 报 ImportError。本次修复 14 个符号漂移 + 25 个
模块删除后，需 commit-time gate 防止未来复发。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified tests/ .py 文件
  2. 解析 AST，提取 ``from zephyr.* import yyy`` 语句
  3. 跳过含 module-level ``pytest.skip``/``pytest.importorskip`` 的文件（已标记漂移）
  4. 对每个 import，解析源码 AST 提取符号表（class/def/顶层赋值）
  5. 符号不在源码表 -> 硬阻断

设计权衡
--------
1. **只检测 tests/ 文件**：gate 专防测试漂移，不检测源码内部一致性。
2. **只检测 zephyr.* import**：第三方包由 pytest.importorskip 处理。
3. **module-level skip 豁免**：已用 ``pytest.skip(allow_module_level=True)``
   或 ``pytest.importorskip`` 标记的文件不重复检测。
4. **检查所有顶层符号**：Python 允许显式 import 任何顶层符号（不受 __all__
   限制），故检查 class/def/assign/annassign 而非仅 __all__。
5. **priority=96**：在 TESTS-COVERAGE(95) 之后，作为最高优先级 gate。

Usage::

    from zephyr.governance.commit_gates.test_source_consistency_gate import make_test_source_consistency_gate

    registry.register(make_test_source_consistency_gate())
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

from zephyr.governance.commit_gates._diff_helpers import (
    _get_added_lines,
    _get_staged_py_files,
    _read_staged_file,
)
from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

__all__ = ["make_test_source_consistency_gate"]

# 源码根目录
_SRC_ROOT = REPO_ROOT / "src"


def _has_module_level_skip(tree: ast.Module) -> bool:
    """检查 AST 是否含 module-level pytest.skip/importorskip 调用。

    检测模式（在 Module body 顶层，非函数/类内部）：
    - ``pytest.skip("...", allow_module_level=True)``
    - ``pytest.importorskip("...")``

    Args:
        tree: 已解析的 Module AST。

    Returns:
        True 表示该文件已标记跳过（漂移已知），gate 应豁免。
    """
    for node in tree.body:
        # 只检查顶层表达式语句（Expr -> Call）
        if not isinstance(node, ast.Expr):
            # 也检查赋值语句中的 skip（如 _ = pytest.skip(...)）
            if isinstance(node, ast.Assign):
                if not isinstance(node.value, ast.Call):
                    continue
                call = node.value
            else:
                continue
        elif not isinstance(node.value, ast.Call):
            continue
        else:
            call = node.value

        # 检查 call.func 是否为 pytest.skip / pytest.importorskip
        func = call.func
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            if func.value.id == "pytest" and func.attr in ("skip", "importorskip"):
                return True
    return False


def _module_to_path(module_path: str) -> Path | None:
    """将 Python 模块路径转换为源码文件路径。

    ``zephyr.governance.audit_trail.feedback_bridge`` ->
    ``src/zephyr/governance/audit_trail/feedback_bridge.py``

    ``zephyr.governance`` ->
    ``src/zephyr/governance/__init__.py``

    Args:
        module_path: 点分隔的模块路径（如 ``zephyr.xxx.yyy``）。

    Returns:
        对应的 .py 文件路径，不存在则 None。
    """
    parts = module_path.split(".")
    # zephyr.xxx -> src/zephyr/xxx
    rel_path = Path(*parts)
    py_file = _SRC_ROOT / rel_path.with_suffix(".py")
    if py_file.exists():
        return py_file
    # 尝试包 __init__.py
    init_file = _SRC_ROOT / rel_path / "__init__.py"
    if init_file.exists():
        return init_file
    return None


def _extract_source_symbols(file_path: Path) -> set[str] | None:
    """从源码文件 AST 提取所有顶层符号集合。

    提取所有顶层定义的符号（Python 允许显式 import 任何顶层符号，
    不受 __all__ 限制）：
    - class 名称
    - def/async def 名称
    - 顶层赋值目标名称（常量/变量）
    - 顶层带注解赋值目标名称

    Args:
        file_path: 源码 .py 文件路径。

    Returns:
        符号名称集合；文件不存在/解析失败返回 None（fail-open）。
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None

    symbols: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    symbols.add(target.id)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                symbols.add(node.target.id)
    return symbols


def _extract_all_list(value: ast.expr) -> set[str] | None:
    """从 __all__ 赋值值提取符号名集合（工具函数，保留供测试使用）。

    支持：
    - 列表：``__all__ = ["foo", "bar"]``
    - 元组：``__all__ = ("foo", "bar")``

    Args:
        value: __all__ 赋值的 value 节点。

    Returns:
        符号名集合；非列表/元组返回 None。
    """
    if not isinstance(value, (ast.List, ast.Tuple)):
        return None
    names: set[str] = set()
    for elt in value.elts:
        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
            names.add(elt.value)
    return names if names else None


def _check_import_node(node: ast.ImportFrom, test_file: str) -> list[str]:
    """检查单个 ImportFrom 节点的符号一致性，返回违规列表。

    Args:
        node: AST ImportFrom 节点。
        test_file: 测试文件路径（用于错误消息）。

    Returns:
        违规描述列表（空列表表示无违规）。
    """
    module_path = node.module
    if not module_path or not module_path.startswith("zephyr."):
        return []
    if node.level > 0:  # 跳过相对导入
        return []

    violations: list[str] = []
    source_file = _module_to_path(module_path)

    if source_file is None:
        # 源码模块不存在，可能是已删除模块
        for alias in node.names:
            if alias.name == "*":
                continue
            violations.append(
                f"  {test_file}:{node.lineno}: "
                f"from {module_path} import {alias.name} "
                f"-> 模块不存在（已删除/迁移？）"
            )
        return violations

    # 提取源码符号表
    source_symbols = _extract_source_symbols(source_file)
    if source_symbols is None:
        # 源码解析失败，fail-open
        return []

    # 检查每个 import 的符号
    for alias in node.names:
        if alias.name == "*":
            continue
        if alias.name not in source_symbols:
            violations.append(
                f"  {test_file}:{node.lineno}: "
                f"from {module_path} import {alias.name} "
                f"-> 符号不存在（源码 {source_file.name} 中未定义）"
            )
    return violations


def _check_test_file(content: str, test_file: str) -> list[str]:
    """检查单个测试文件的 import 符号一致性，返回违规列表。

    Args:
        content: 测试文件内容。
        test_file: 测试文件路径（用于错误消息）。

    Returns:
        违规描述列表（空列表表示无违规或跳过）。
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []  # 语法错误由其他 gate 处理

    # 跳过已标记 module-level skip 的文件
    if _has_module_level_skip(tree):
        return []

    # 检查每个 from zephyr.* import yyy
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            violations.extend(_check_import_node(node, test_file))
    return violations


def make_test_source_consistency_gate() -> GateSpec:
    """构造测试-源码符号一致性 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="TEST-SOURCE-CONSISTENCY", priority=96)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged added/modified .py 文件
        staged = _get_staged_py_files(gateway, gate_name="TEST-SOURCE-CONSISTENCY")
        if not staged:
            return True, ""

        # 2. 过滤 tests/ 文件（gate 专防测试漂移）
        test_files = [f for f in staged if is_test_exempt(f)]
        if not test_files:
            return True, ""

        # 3. 检测每个测试文件的 import 符号一致性
        violations: list[str] = []
        for test_file in test_files:
            content = _read_staged_file(gateway, test_file)
            if not content:
                continue
            violations.extend(_check_test_file(content, test_file))

        # 4. 硬阻断
        if violations:
            detail = (
                "TEST-SOURCE-CONSISTENCY (§5.178)：检测到测试-源码符号漂移\n"
                "  测试文件 import 的符号在源码中不存在（名称漂移）。\n"
                + "\n".join(violations)
                + "\n-> 检查源码是否已重命名/移除该符号，更新测试 import"
                + "\n   或在测试文件顶部添加 pytest.skip(allow_module_level=True) 标记"
            )
            logger.error("TEST-SOURCE-CONSISTENCY gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(
        gate_id="TEST-SOURCE-CONSISTENCY",
        check=_check,
        priority=96,
    )
