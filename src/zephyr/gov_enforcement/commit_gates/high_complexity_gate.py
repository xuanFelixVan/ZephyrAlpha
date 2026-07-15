# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.high_complexity_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py 新增函数循环复杂度>15时阻断commit(passed=False); tests/豁免; AST解析失败fail-open; git diff不可达fail-open; 检出违规则fail-closed
# [MODIFY-GUARD] gate_id="NO-HIGH-COMPLEXITY"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_high_complexity_gate.py
# [A_module] module_id=MOD-GOV-high_complexity_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""high_complexity_gate.py — 高循环复杂度阻断门禁（NO-HIGH-COMPLEXITY，§5.158 防复发）

检测 staged .py 文件中**新增**函数的循环复杂度（McCabe）> 15。
违反 §5.158 循环复杂度反模式。

病根（第一性原理）
-----------------
architecture_debt §5.158：10 处长函数（复杂度 30+/17/16 等），
需拆分为短函数+回归测试。但新 AI 仍可能写新的高复杂度函数——本 gate 硬阻断。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified .py 文件
  2. 过滤 tests/ 豁免
  3. 对每个文件解析 diff，获取 added 行号集合
  4. AST 解析 staged 文件，找到所有 FunctionDef/AsyncFunctionDef
  5. 读取 HEAD 版本，收集已有函数名集合
  6. 仅检测 lineno 在 added 行号集合 **且** 不在 HEAD 函数名集合中的函数（真正新增的函数）
  7. 循环复杂度 > 15 -> 硬阻断

裁定#214 修复（2026-07-15）
---------------------------
原实现 ``node.lineno in added_lines`` 捕获了**修改签名的已有函数**（如 Any→object 类型注解修复），
与 docstring 声明的"只检测新增函数"不一致。修复：读取 HEAD 版本函数名集合，
仅对 HEAD 中不存在的函数名检测复杂度。已有函数的复杂度增加由全量扫描脚本补充监控。

设计权衡
--------
1. **只检测新增函数**：存量高复杂度由人工排查+全量扫描脚本补充，gate 只防新增。
2. **AST-based McCabe**：统计 If/For/While/ExceptHandler/BoolOp/comprehension-if。
3. **阈值=15**：与 §5.158 裁定一致（>15 即反模式）。
4. **priority=85**：在 NO-GOD-CLASS(86) 之前，FILE-COPY(85) 同级。

Usage::

    from zephyr.gov_enforcement.commit_gates.high_complexity_gate import make_high_complexity_gate

    registry.register(make_high_complexity_gate())
"""

from __future__ import annotations

import ast
import logging

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _collect_function_names,
    _get_added_lines,
    _get_staged_py_files,
    _read_head_file,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_high_complexity_gate"]

_MAX_COMPLEXITY = 15


def _walk_excluding_nested_funcs(node):
    """遍历 AST 节点的所有后代，但不递归进入嵌套函数定义。

    McCabe 复杂度应只计算函数自身的决策点，不包含嵌套函数体内的决策点。
    嵌套函数由调用方（gate）独立检查，不计入父函数复杂度。

    裁定#215 修复（2026-07-15）：原实现用 ast.walk(node) 递归进入嵌套函数体，
    将嵌套函数的决策点计入父函数，导致复杂度虚高（如 make_create_guard wrapper
    报告 105 实际 1，_read_config_file 报告 81 实际 3）。
    """
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue  # 不递归进入嵌套函数
        yield child
        yield from _walk_excluding_nested_funcs(child)


def _cyclomatic_complexity(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """计算函数的循环复杂度（McCabe），不递归进入嵌套函数。

    基础复杂度=1，每个决策点+1：
    - If / IfExp
    - For / AsyncFor / While
    - ExceptHandler
    - BoolOp(And/Or) 每个操作数（len(values)-1）
    - comprehension 的 if 子句

    裁定#215：不递归进入嵌套函数体（嵌套函数由 gate 独立检查）。
    """
    complexity = 1
    for child in _walk_excluding_nested_funcs(node):
        if isinstance(child, (ast.If, ast.IfExp)):
            complexity += 1
        elif isinstance(child, (ast.For, ast.AsyncFor, ast.While)):
            complexity += 1
        elif isinstance(child, ast.ExceptHandler):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        elif isinstance(child, ast.comprehension):
            complexity += len(child.ifs)
    return complexity


def make_high_complexity_gate() -> GateSpec:
    """构造高循环复杂度阻断 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="NO-HIGH-COMPLEXITY", priority=85)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = [f for f in _get_staged_py_files(gateway, "NO-HIGH-COMPLEXITY") if not is_test_exempt(f)]
        violations: list[str] = []
        for py_file in py_files:
            file_content = _read_staged_file(gateway, py_file)
            if not file_content:
                continue
            added_lines = {ln for ln, _ in _get_added_lines(gateway, py_file, "NO-HIGH-COMPLEXITY")}
            if not added_lines:
                continue
            try:
                tree = ast.parse(file_content, filename=py_file)
            except SyntaxError:
                continue
            # 裁定#214：读取 HEAD 版本函数名集合，区分"新增函数"与"修改函数"
            # 只对 HEAD 中不存在的函数名检测复杂度（gate 设计意图："只检测新增函数"）
            head_content = _read_head_file(gateway, py_file)
            head_func_names: set[str] = set()
            if head_content is not None:
                head_func_names = _collect_function_names(head_content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.lineno in added_lines:
                    # 跳过已存在于 HEAD 的函数（修改函数，非新增函数）
                    if node.name in head_func_names:
                        continue
                    complexity = _cyclomatic_complexity(node)
                    if complexity > _MAX_COMPLEXITY:
                        violations.append(
                            f"  {py_file}:{node.lineno}: {node.name}(complexity={complexity} > {_MAX_COMPLEXITY})"
                        )
        if violations:
            detail = (
                "NO-HIGH-COMPLEXITY：检测到高循环复杂度函数（>15），\n"
                "  违反 §5.158 循环复杂度反模式。\n"
                + "\n".join(violations)
                + "\n-> 考虑拆分为短函数/策略模式/查表法"
            )
            logger.error("NO-HIGH-COMPLEXITY gate block:\n%s", detail)
            return False, detail
        return True, ""

    return GateSpec(gate_id="NO-HIGH-COMPLEXITY", check=_check, priority=85)
