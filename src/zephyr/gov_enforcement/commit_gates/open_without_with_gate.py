# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.open_without_with_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——检测 src/zephyr/ 全量代码(.py)新增行中 open() 调用不在 with 语句内时阻断（5.144 资源清理顺序防复发，文件句柄泄漏）；with open(...) as f 的 open 是 with item context_expr 不报；tests/ 豁免；import/注释/docstring 豁免；# noqa: r144-open 豁免；ast.parse/git diff 不可达 fail-open（logger.warning 检测器失效）；检出违规则 fail-closed 阻断（passed=False）
# [MODIFY-GUARD] gate_id="OPEN-WITHOUT-WITH"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——ast.parse/git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_open_without_with_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""open_without_with_gate.py — open() 未在 with 内硬阻断门禁（OPEN-WITHOUT-WITH）

检测 staged 代码（src/zephyr/ 全量 .py）新增行中 ``open()`` 调用不在 ``with`` 语句内
—— 文件句柄泄漏风险（5.144 资源清理顺序防复发）。

病根（5.144 资源清理顺序）
--------------------------
- 核心关闭路径无异常隔离 + sqlite 清理缺 finally + 子进程管道关闭顺序错
- open() 未在 with 内 → 文件句柄泄漏（fd 泄漏）
- 治本：``with open(path) as f:`` 上下文管理器自动关闭

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified .py 文件
  2. 过滤到 src/zephyr/ 文件 + tests/ 豁免
  3. 对每个文件：``_read_staged_file`` 读全文 → ``ast.parse``
  4. 自定义 ``ast.NodeVisitor``，维护 ``with_depth`` 计数器：
     - visit ``ast.With``/``ast.AsyncWith``：先 ``with_depth += 1`` 再 ``generic_visit`` 再 ``-= 1``
     - visit ``ast.Call``：若 ``func`` 是 ``ast.Name(id="open")`` 且 ``with_depth == 0``
       → 潜在违规（open 调用不在 with 内）
  5. ``node.lineno`` 命中 added 行号集 + 非 noqa → 违规
  6. 命中 -> 硬阻断（passed=False）

设计权衡
--------
1. **with-context 栈**：``visit_With`` 先递增 ``with_depth`` 再 ``generic_visit``，
   确保 ``with open(...) as f:`` 中的 open（位于 With.items[].context_expr）
   在 ``with_depth=1`` 时被 visit，不误报。
2. **只检测 ast.Name(id="open")**：内置 ``open()``。不检测 ``ast.Attribute(attr="open")``
   （如 ``os.open()`` 是系统调用，语义不同，不应检测）。
3. **只检测 added 行**：存量违规由仪表盘 M27 监控，gate 只防新增。
4. **fail-open on ast.parse/git error**：解析失败时不阻断。
5. **priority=124**：在 MUTABLE-CONST-WITHOUT-FINAL(123) 之后、ZEPHYR-ENV-DIRECT-ACCESS(125) 之前。
6. **noqa 豁免**：合法场景（如需要在 with 外管理生命周期的低层封装）可用 noqa:r144-open。

Usage::

    from zephyr.gov_enforcement.commit_gates.open_without_with_gate import make_open_without_with_gate

    registry.register(make_open_without_with_gate())
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

__all__ = ["make_open_without_with_gate"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注

# src/zephyr/ 全量检测面前缀
_SRC_ZEPHYR_PREFIX = "src/zephyr/"

# noqa 豁免标记（MUST 在 noqa_exempt_registry.yaml 登记）
_NOQA_MARKER = "r144-open"


def _is_src_zephyr_file(py_file: str) -> bool:
    """判定 .py 文件是否在 src/zephyr/ 目录下。"""
    return py_file.replace("\\", "/").startswith(_SRC_ZEPHYR_PREFIX)


def _has_noqa_exempt(content: str) -> bool:
    """检查行是否含 ``# noqa: r144-open`` 豁免标记。"""
    return f"# noqa: {_NOQA_MARKER}" in content


class _OpenCallVisitor(ast.NodeVisitor):
    """AST 访问器：收集不在 with 语句内的 open() 调用节点。

    维护 ``with_depth`` 计数器：进入 With/AsyncWith 时 +1，离开时 -1。
    ``visit_With`` 先递增再 ``generic_visit``（遍历 items + body），
    确保 with item context_expr 内的 open 在 with_depth>0 时被 visit。
    """

    def __init__(self) -> None:
        self.with_depth: int = 0
        # 不在 with 内的 open() 调用节点列表
        self.bare_open_calls: list[ast.Call] = []

    def visit_With(self, node: ast.With) -> None:
        self.with_depth += 1
        self.generic_visit(node)
        self.with_depth -= 1

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        self.with_depth += 1
        self.generic_visit(node)
        self.with_depth -= 1

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        # 只检测内置 open()：ast.Name(id="open")
        # 不检测 ast.Attribute(attr="open")（如 os.open() 是系统调用，语义不同）
        if isinstance(func, ast.Name) and func.id == "open":
            if self.with_depth == 0:
                self.bare_open_calls.append(node)
        self.generic_visit(node)


def _scan_file_for_violations(gateway, py_file: str) -> list[str]:
    """检测单个文件的 added 行，返回违规列表。

    检测 open() 调用不在 with 内 + lineno 命中 added 行。
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
            "OPEN-WITHOUT-WITH gate: ast.parse 失败 file=%s（语法错误），fail-open 跳过该文件。",
            py_file,
            exc_info=True,
        )
        return violations

    # 3. 遍历 AST，收集不在 with 内的 open() 调用
    visitor = _OpenCallVisitor()
    visitor.visit(tree)

    if not visitor.bare_open_calls:
        return violations

    # 4. 获取 added 行号集 + 内容映射
    added_lines = _get_added_lines(gateway, py_file, gate_name="OPEN-WITHOUT-WITH")
    added_line_numbers = {ln for ln, _ in added_lines}
    added_line_contents = {ln: content for ln, content in added_lines}

    # 5. 交叉验证：open 调用的 lineno 命中 added 行 + 非 noqa
    for call_node in visitor.bare_open_calls:
        lineno = call_node.lineno
        if lineno not in added_line_numbers:
            continue  # 存量违规（非 added 行），由 M27 监控
        if lineno in docstring_lines:
            continue  # docstring 豁免
        content = added_line_contents.get(lineno, "")
        if _has_noqa_exempt(content):
            continue  # noqa 豁免
        violations.append(
            f"  {py_file}:{lineno}: open() 调用未在 with 语句内（文件句柄泄漏风险）"
            f"-> {content.strip()}"
            f"\n     应改: with open(...) as f:（上下文管理器自动关闭）"
        )
    return violations


def _format_violation_detail(violations: list[str]) -> str:
    return (
        "OPEN-WITHOUT-WITH：检测到 open() 未在 with 语句内（5.144 资源清理顺序防复发），\n"
        "  src/zephyr/ 全量禁止 open() 调用不在 with 上下文管理器内。\n"
        + "\n".join(violations)
        + "\n-> 改用 with open(...) as f:（自动关闭文件句柄）；"
        "合法场景（低层封装需手动管理生命周期）用 # noqa: r144-open 豁免并附理由说明文本。"
    )


def make_open_without_with_gate() -> GateSpec:
    """构造 open() 未在 with 内硬阻断 GateSpec。

    Returns:
        GateSpec(gate_id="OPEN-WITHOUT-WITH", priority=124)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged added/modified .py 文件
        staged = _get_staged_py_files(gateway, gate_name="OPEN-WITHOUT-WITH")
        if not staged:
            return True, ""

        # 2. 过滤到 src/zephyr/ 文件 + tests/ 豁免
        target_files = [f for f in staged if _is_src_zephyr_file(f) and not is_test_exempt(f)]
        if not target_files:
            return True, ""

        # 3. 检测每个目标文件
        violations: list[str] = []
        for py_file in target_files:
            violations.extend(_scan_file_for_violations(gateway, py_file))

        # 4. 硬阻断：检出违规则 fail-closed
        if violations:
            detail = _format_violation_detail(violations)
            logger.error("OPEN-WITHOUT-WITH gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(gate_id="OPEN-WITHOUT-WITH", check=_check, priority=124)
