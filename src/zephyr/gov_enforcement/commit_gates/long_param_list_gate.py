# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.long_param_list_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py 新增函数定义参数数>7(排除self/cls)时阻断commit(passed=False); tests/豁免; AST解析失败fail-open; git diff不可达fail-open; 检出违规则fail-closed
# [MODIFY-GUARD] gate_id="NO-LONG-PARAM-LIST"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_long_param_list_gate.py
# [A_module] module_id=MOD-GOV-long_param_list_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""long_param_list_gate.py — 长参数列表阻断门禁（NO-LONG-PARAM-LIST，§5.150 防复发）

检测 staged .py 文件中**新增**函数的参数数 > 7（排除 self/cls）。
违反 §5.150 Long Parameter List 反模式。

病根（第一性原理）
-----------------
architecture_debt §5.150：5 处 Long Parameter List（16/9/9 参数），
源于 Data Class 反模式 + factories.py 工厂函数。修复需引入参数对象。
但新 AI 仍可能写新的长参数函数——本 gate 在 commit 阶段硬阻断。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified .py 文件
  2. 过滤 tests/ 豁免
  3. 对每个文件解析 diff，获取 added 行号集合
  4. AST 解析 staged 文件，找到所有 FunctionDef/AsyncFunctionDef
  5. 仅检测 lineno 在 added 行号集合中的函数（新增函数）
  6. 参数数（排除 self/cls）> 7 -> 硬阻断

设计权衡
--------
1. **只检测新增函数**：存量长参数由人工排查，gate 只防新增。
2. **AST-based**：准确处理跨行参数列表、posonly/kwonly/vararg/kwarg。
3. **排除 self/cls**：方法第一个参数是 self/cls，不计入业务参数。
4. **阈值=7**：与 §5.150 裁定一致（>7 即反模式）。
5. **priority=88**：在 DOC-REF-BROKEN(88) 同级，orphan_module_gate(86) 之前。

Usage::

    from zephyr.gov_enforcement.commit_gates.long_param_list_gate import make_long_param_list_gate

    registry.register(make_long_param_list_gate())
"""

from __future__ import annotations

import ast
import logging

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _get_added_lines,
    _get_staged_py_files,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_long_param_list_gate"]

_MAX_PARAMS = 7


def _count_params(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """计算函数参数数（排除 self/cls）。

    包含 posonlyargs + regular args + kwonlyargs + vararg + kwarg。
    如果 regular args 第一个参数是 self/cls，排除之。
    """
    args = node.args
    posonly = len(getattr(args, "posonlyargs", []) or [])
    regular = list(args.args or [])
    if regular and regular[0].arg in ("self", "cls"):
        regular = regular[1:]
    kwonly = len(args.kwonlyargs or [])
    vararg = 1 if args.vararg else 0
    kwarg = 1 if args.kwarg else 0
    return posonly + len(regular) + kwonly + vararg + kwarg


def make_long_param_list_gate() -> GateSpec:
    """构造长参数列表阻断 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="NO-LONG-PARAM-LIST", priority=88)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = [f for f in _get_staged_py_files(gateway, "NO-LONG-PARAM-LIST") if not is_test_exempt(f)]
        violations: list[str] = []
        for py_file in py_files:
            file_content = _read_staged_file(gateway, py_file)
            if not file_content:
                continue
            added_lines = {ln for ln, _ in _get_added_lines(gateway, py_file, "NO-LONG-PARAM-LIST")}
            if not added_lines:
                continue
            try:
                tree = ast.parse(file_content, filename=py_file)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.lineno in added_lines:
                    count = _count_params(node)
                    if count > _MAX_PARAMS:
                        violations.append(
                            f"  {py_file}:{node.lineno}: {node.name}({count} params > {_MAX_PARAMS})"
                        )
        if violations:
            detail = (
                "NO-LONG-PARAM-LIST：检测到长参数列表（>7参数），\n"
                "  违反 §5.150 Long Parameter List 反模式。\n"
                + "\n".join(violations)
                + "\n-> 考虑引入参数对象/Builder模式/dataclass 封装参数"
            )
            logger.error("NO-LONG-PARAM-LIST gate block:\n%s", detail)
            return False, detail
        return True, ""

    return GateSpec(gate_id="NO-LONG-PARAM-LIST", check=_check, priority=88)
