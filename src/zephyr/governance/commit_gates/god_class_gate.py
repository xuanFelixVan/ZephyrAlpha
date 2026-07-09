# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.god_class_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.commit_gates._diff_helpers; zephyr.governance.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py 新增类定义方法数>20时阻断commit(passed=False); tests/豁免; AST解析失败fail-open; git diff不可达fail-open; 检出违规则fail-closed
# [MODIFY-GUARD] gate_id="NO-GOD-CLASS"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_god_class_gate.py
# [A_module] module_id=MOD-GOV-god_class_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""god_class_gate.py — God Class 阻断门禁（NO-GOD-CLASS，§5.150 防复发）

检测 staged .py 文件中**新增**类的方法数 > 20。
违反 §5.150 God Class 反模式。

病根（第一性原理）
-----------------
architecture_debt §5.150：3 处 God Class（resource_optimization 39方法 /
auto_runtime_core 42方法 / action_dispatcher 22方法），职责过多。
修复需职责拆分+回归测试。但新 AI 仍可能写新的 God Class——本 gate 硬阻断。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified .py 文件
  2. 过滤 tests/ 豁免
  3. 对每个文件解析 diff，获取 added 行号集合
  4. AST 解析 staged 文件，找到所有 ClassDef
  5. 仅检测 lineno 在 added 行号集合中的类（新增类）
  6. 方法数 > 20 -> 硬阻断

设计权衡
--------
1. **只检测新增类**：存量 God Class 由人工排查，gate 只防新增。
2. **AST-based**：准确统计类体内的方法数。
3. **阈值=20**：与 §5.150 裁定一致（>20 即反模式）。
4. **priority=86**：在 NO-BARE-SQL(87) 之后，ID-UNIQUENESS(86)/ORPHAN-MODULE(86) 同级。

Usage::

    from zephyr.governance.commit_gates.god_class_gate import make_god_class_gate

    registry.register(make_god_class_gate())
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

__all__ = ["make_god_class_gate"]

_MAX_METHODS = 20


def _count_methods(node: ast.ClassDef) -> int:
    """统计类中的方法数（直接 body 内的 FunctionDef/AsyncFunctionDef）。"""
    return sum(
        1 for child in node.body
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
    )


def make_god_class_gate() -> GateSpec:
    """构造 God Class 阻断 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="NO-GOD-CLASS", priority=86)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = [f for f in _get_staged_py_files(gateway, "NO-GOD-CLASS") if not is_test_exempt(f)]
        violations: list[str] = []
        for py_file in py_files:
            file_content = _read_staged_file(gateway, py_file)
            if not file_content:
                continue
            added_lines = {ln for ln, _ in _get_added_lines(gateway, py_file, "NO-GOD-CLASS")}
            if not added_lines:
                continue
            try:
                tree = ast.parse(file_content, filename=py_file)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.lineno in added_lines:
                    method_count = _count_methods(node)
                    if method_count > _MAX_METHODS:
                        violations.append(
                            f"  {py_file}:{node.lineno}: class {node.name}({method_count} methods > {_MAX_METHODS})"
                        )
        if violations:
            detail = (
                "NO-GOD-CLASS：检测到 God Class（方法数>20），\n"
                "  违反 §5.150 God Class 反模式。\n"
                + "\n".join(violations)
                + "\n-> 考虑按职责拆分类（单一职责原则）"
            )
            logger.error("NO-GOD-CLASS gate block:\n%s", detail)
            return False, detail
        return True, ""

    return GateSpec(gate_id="NO-GOD-CLASS", check=_check, priority=86)
