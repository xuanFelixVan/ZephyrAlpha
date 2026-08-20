# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.mutable_const_without_final_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——检测 src/zephyr/ 全量代码(.py)新增行中模块级 ast.Assign（非 AnnAssign）且 value 为可变容器（List/Dict/Set 字面量或 list()/dict()/set() 调用）时阻断（5.114 Final/@final 强制防复发，缺 Final 标注的可变常量）；tests/ 豁免；import/注释/docstring 豁免；# noqa: n114-final 豁免；ast.parse/git diff 不可达 fail-open（logger.warning 检测器失效）；检出违规则 fail-closed 阻断（passed=False）
# [MODIFY-GUARD] gate_id="MUTABLE-CONST-WITHOUT-FINAL"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——ast.parse/git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_mutable_const_without_final_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""mutable_const_without_final_gate.py — 可变常量缺 Final 标注硬阻断门禁（MUTABLE-CONST-WITHOUT-FINAL）

检测 staged 代码（src/zephyr/ 全量 .py）新增行中**模块级** ``ast.Assign``（非 ``AnnAssign``），
且 value 为可变容器（``List``/``Dict``/``Set`` 字面量或 ``list()``/``dict()``/``set()`` 调用）
→ 缺 ``Final`` 标注的可变常量（5.114 Final/@final 强制防复发）。

病根（5.114 Final/@final 强制）
-------------------------------
- 可变 dict 常量无 Final + 375 处模块级常量未标 Final + @final 零使用
- 治本：``X: Final = [...]``（AnnAssign + Final 注解）使常量不可重新绑定

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified .py 文件
  2. 过滤到 src/zephyr/ 文件 + tests/ 豁免
  3. 对每个文件：``_read_staged_file`` 读全文 → ``ast.parse``
  4. ``ast.iter_child_nodes(tree)`` 只遍历模块级节点（非函数/类内部局部变量）
  5. 找 ``ast.Assign``（非 ``AnnAssign``——AnnAssign 可能带 Final 注解）+ value 可变容器
  6. ``node.lineno`` 命中 added 行号集 → 违规
  7. 豁免 import/注释/docstring 行 + noqa:n114-final 标记
  8. 命中 -> 硬阻断（passed=False）

设计权衡
--------
1. **只检测模块级**：用 ``ast.iter_child_nodes(tree)`` 而非 ``ast.walk``，
   只取 Module 直接子节点——函数内局部变量不检测（局部变量非"常量"）。
2. **只检测 ast.Assign**：``AnnAssign``（``X: Final = ...``）不检测，
   因为带类型注解的赋值可能已标 Final。
3. **可变容器判定**：``List``/``Dict``/``Set`` 字面量 + ``list()``/``dict()``/``set()`` 调用。
   不检测 tuple（``ast.Tuple``）——tuple 本身不可变，无需 Final。
4. **只检测 added 行**：存量违规由仪表盘 M25 监控，gate 只防新增。
5. **fail-open on ast.parse/git error**：解析失败时不阻断。
6. **priority=123**：在 ASYNCIO-RUN-IN-CONTEXT(122) 之后、OPEN-WITHOUT-WITH(124) 之前。
7. **noqa 豁免**：合法场景（如需运行时修改的注册表常量）可用 noqa:n114-final。

Usage::

    from zephyr.gov_enforcement.commit_gates.mutable_const_without_final_gate import make_mutable_const_without_final_gate

    registry.register(make_mutable_const_without_final_gate())
"""

from __future__ import annotations

import ast
import logging

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _extract_docstring_lines,
    _get_added_lines,
    _get_staged_py_files,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_mutable_const_without_final_gate"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注

# src/zephyr/ 全量检测面前缀
_SRC_ZEPHYR_PREFIX = "src/zephyr/"

# noqa 豁免标记（MUST 在 noqa_exempt_registry.yaml 登记）
_NOQA_MARKER = "n114-final"

# 可变容器构造函数名
_MUTABLE_CALL_FUNCS = {"list", "dict", "set"}  # noqa: n114-final  n114-final豁免: gate检测器自身常量，Final标注会改变语义（frozenset不可用于in操作性能）


def _is_src_zephyr_file(py_file: str) -> bool:
    """判定 .py 文件是否在 src/zephyr/ 目录下。"""
    return py_file.replace("\\", "/").startswith(_SRC_ZEPHYR_PREFIX)


def _has_noqa_exempt(content: str) -> bool:
    """检查行是否含 ``# noqa: n114-final`` 豁免标记。"""
    return f"# noqa: {_NOQA_MARKER}" in content


def _is_mutable_value(value: ast.expr) -> bool:
    """判定 AST value 节点是否为可变容器字面量或可变容器构造调用。

    Args:
        value: ``ast.Assign`` 的 value 节点。

    Returns:
        True 如果是 ``List``/``Dict``/``Set`` 字面量或 ``list()``/``dict()``/``set()`` 调用。
    """
    if isinstance(value, (ast.List, ast.Dict, ast.Set)):
        return True
    if isinstance(value, ast.Call):
        func = value.func
        if isinstance(func, ast.Name) and func.id in _MUTABLE_CALL_FUNCS:
            return True
    return False


def _scan_file_for_violations(gateway, py_file: str) -> list[str]:
    """检测单个文件的 added 行，返回违规列表。

    检测模块级 ``ast.Assign``（非 AnnAssign）+ value 可变容器 + lineno 命中 added 行。
    """
    violations: list[str] = []

    # 1. 读取 staged 完整文件，预计算 docstring 行号集合（豁免 docstring）
    file_content = _read_staged_file(gateway, py_file)
    if not file_content:
        return violations
    docstring_lines = _extract_docstring_lines(file_content)

    # 2. AST 解析（fail-open on SyntaxError）
    try:
        tree = ast.parse(file_content)
    except SyntaxError:
        logger.warning(
            "MUTABLE-CONST-WITHOUT-FINAL gate: ast.parse 失败 file=%s（语法错误），fail-open 跳过该文件。",
            py_file,
            exc_info=True,
        )
        return violations

    # 3. 获取 added 行号集 + 内容映射
    added_lines = _get_added_lines(gateway, py_file, gate_name="MUTABLE-CONST-WITHOUT-FINAL")
    added_line_numbers = {ln for ln, _ in added_lines}
    added_line_contents = {ln: content for ln, content in added_lines}

    # 4. 遍历模块级 Assign（非 AnnAssign）+ value 可变容器
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.Assign):
            continue  # AnnAssign / AugAssign / 其他不检测
        if not _is_mutable_value(node.value):
            continue  # 非可变容器
        # node.lineno 命中 added 行？
        if node.lineno not in added_line_numbers:
            continue  # 存量违规（非 added 行），由 M25 监控
        # 豁免：docstring 内的行（理论上模块级 Assign 不在 docstring，保险处理）
        if node.lineno in docstring_lines:
            continue
        # 豁免：noqa 标记
        content = added_line_contents.get(node.lineno, "")
        if _has_noqa_exempt(content):
            continue
        # 提取目标变量名（首个 target）
        var_name = _extract_target_name(node)
        violations.append(
            f"  {py_file}:{node.lineno}: 模块级可变常量缺 Final 标注"
            f"（{var_name} = <可变容器>）-> {content.strip()}"
            f"\n     应改: {var_name}: Final = ...（AnnAssign + Final 注解）"
        )
    return violations


def _extract_target_name(node: ast.Assign) -> str:
    """提取 Assign 节点的首个目标变量名（用于违规消息）。"""
    if not node.targets:
        return "<unknown>"
    target = node.targets[0]
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Tuple) and target.elts:
        first = target.elts[0]
        if isinstance(first, ast.Name):
            return first.id
    return "<expr>"


def _format_violation_detail(violations: list[str]) -> str:
    return (
        "MUTABLE-CONST-WITHOUT-FINAL：检测到模块级可变常量缺 Final 标注（5.114 Final/@final 强制防复发），\n"
        "  src/zephyr/ 全量禁止模块级可变容器赋值（X = [...]）无 Final 标注。\n"
        + "\n".join(violations)
        + "\n-> 改用 X: Final = [...]（AnnAssign + Final 注解）；"
        "合法场景（需运行时修改的注册表）用 # noqa: n114-final 豁免并附理由说明文本。"
    )


def make_mutable_const_without_final_gate() -> GateSpec:
    """构造可变常量缺 Final 标注硬阻断 GateSpec。

    Returns:
        GateSpec(gate_id="MUTABLE-CONST-WITHOUT-FINAL", priority=123)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged added/modified .py 文件
        staged = _get_staged_py_files(gateway, gate_name="MUTABLE-CONST-WITHOUT-FINAL")
        if not staged:
            return True, ""

        # 2. 过滤到 src/zephyr/ 文件 + tests/ 豁免
        target_files = [f for f in staged if _is_src_zephyr_file(f) and not is_test_exempt(f)]
        if not target_files:
            return True, ""

        # 3. 检测每个目标文件的模块级 Assign
        violations: list[str] = []
        for py_file in target_files:
            violations.extend(_scan_file_for_violations(gateway, py_file))

        # 4. 硬阻断：检出违规则 fail-closed
        if violations:
            detail = _format_violation_detail(violations)
            logger.error("MUTABLE-CONST-WITHOUT-FINAL gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(gate_id="MUTABLE-CONST-WITHOUT-FINAL", check=_check, priority=123)
