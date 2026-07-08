# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.high_complexity_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.commit_gates._diff_helpers; zephyr.governance.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
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
  5. 仅检测 lineno 在 added 行号集合中的函数（新增函数）
  6. 循环复杂度 > 15 -> 硬阻断

设计权衡
--------
1. **只检测新增函数**：存量高复杂度由人工排查，gate 只防新增。
2. **AST-based McCabe**：统计 If/For/While/ExceptHandler/BoolOp/comprehension-if。
3. **阈值=15**：与 §5.158 裁定一致（>15 即反模式）。
4. **priority=85**：在 god_class_gate(86) 之前。

Usage::

    from zephyr.governance.commit_gates.high_complexity_gate import make_high_complexity_gate

    registry.register(make_high_complexity_gate())
"""

from __future__ import annotations

import ast
import logging

from zephyr.governance.commit_gates._diff_helpers import (
    _get_added_lines,
    _get_staged_py_files,
    _read_staged_file,
)
from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_high_complexity_gate"]

_MAX_COMPLEXITY = 15


def _cyclomatic_complexity(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """计算函数的循环复杂度（McCabe）。

    基础复杂度=1，每个决策点+1：
    - If / IfExp
    - For / AsyncFor / While
    - ExceptHandler
    - BoolOp(And/Or) 每个操作数（len(values)-1）
    - comprehension 的 if 子句
    """
    complexity = 1
    for child in ast.walk(node):
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
        GateSpec(gate_id="NO-HIGH-COMPLEXITY", priority=89)。
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
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.lineno in added_lines:
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
