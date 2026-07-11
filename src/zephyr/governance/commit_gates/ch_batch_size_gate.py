# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.ch_batch_size_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.commit_gates._diff_helpers; zephyr.governance.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py added 行含 write_result 在 for/async for 循环体内直接调用时阻断 commit(passed=False); tests/豁免; ch_writer.py/buffered_writer.py 自身豁免; AST 精确检测(parent map 遍历); git diff 不可达 fail-open; 检出违规则 fail-closed
# [MODIFY-GUARD] gate_id="CH-BATCH-SIZE"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；ast.parse 失败 fail-open；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_ch_batch_size_gate.py
# [A_module] module_id=MOD-GOV-ch_batch_size_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ch_batch_size_gate.py — CH 批量写入防回退门禁（CH-BATCH-SIZE，§18.4 防复发）

检测 staged .py 文件中 write_result 在 for/async for 循环内直接调用
（无 BufferedWriter 中间层）。
违反裁定 #ARCH-CH-004：100% AI 开发模式需蓝图约束运行时门禁。

病根（第一性原理）
-----------------
阶段1-3 治本已完成 BufferedWriter 批量聚合层（裁定 #ARCH-CH-003），
将 5204 次 INSERT 降为 1-3 次。但新 AI 在写下载循环时，最直观模式是
``for result in fetch(): write_result(result)``——逐个处理，不会主动
设计缓冲区攒批，导致 CH data parts 爆炸问题复发。

100% AI 开发模式的放大效应（裁定 #ARCH-CH-004）：
- AI 写下载循环时不会主动回查蓝图约束
- 蓝图设计 vs 实际实现的鸿沟在 AI 开发模式下被系统性放大
- 缓解措施被遗漏是必然趋势，需运行时门禁强制

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified .py 文件
  2. 过滤 tests/ 豁免 + ch_writer.py/buffered_writer.py 自身豁免
  3. AST 解析检测 write_result 调用是否在 for/async for 循环体内
  4. 只检测 added 行（新增违规）——存量违规由人工排查
  5. 命中 -> 硬阻断

设计权衡
--------
1. **AST 精确检测**：用 ast.walk + parent map 判断 Call 节点是否在
   For/AsyncFor 体内，比正则更准确（不会误报注释中的 for/write_result）。
2. **只检测 added 行**：存量违规由人工排查，gate 只防新增（与
   bare_sql_gate 一致的检测模式）。
3. **ch_writer.py/buffered_writer.py 豁免**：ch_writer.py 是 write_result
   定义处；buffered_writer.py 是 BufferedWriter 中间层（内部用 write_tsv
   而非 write_result，但豁免以防误报）。
4. **priority=36**：蓝图 §18.4 原定 priority=34，但 34 已被
   datetime_now_forbidden_gate 占用，调整至 36（空闲编号）。

Usage::

    from zephyr.governance.commit_gates.ch_batch_size_gate import make_ch_batch_size_gate

    registry.register(make_ch_batch_size_gate())
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

__all__ = ["make_ch_batch_size_gate"]

# 豁免文件：write_result 定义处 + BufferedWriter 中间层
_EXEMPT_FILES = {"ch_writer.py", "buffered_writer.py"}


def _is_exempt_file(py_file: str) -> bool:
    """文件级豁免：ch_writer.py / buffered_writer.py 自身。"""
    return any(py_file.replace("\\", "/").endswith(f"/{name}") or py_file == name
               for name in _EXEMPT_FILES)


def _build_parent_map(tree: ast.AST) -> dict[int, ast.AST]:
    """构建 AST parent map：{id(child_node): parent_node}。

    用于从 Call 节点向上遍历祖先链，判断是否在 For/AsyncFor 体内。
    """
    parent_map: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parent_map[id(child)] = node
    return parent_map


def _find_enclosing_for(
    call_node: ast.Call, parent_map: dict[int, ast.AST]
) -> ast.For | ast.AsyncFor | None:
    """从 Call 节点向上遍历祖先链，返回最近的 For/AsyncFor 祖先。

    Returns:
        For/AsyncFor 节点，或 None（不在任何 for 循环体内）。
    """
    current = parent_map.get(id(call_node))
    while current is not None:
        if isinstance(current, (ast.For, ast.AsyncFor)):
            return current
        current = parent_map.get(id(current))
    return None


def _is_write_result_call(node: ast.AST) -> bool:
    """判断 AST 节点是否是 write_result 函数调用。

    覆盖：
    - ``write_result(...)`` — ast.Name(id='write_result')
    - ``ch_writer.write_result(...)`` — ast.Attribute(attr='write_result')
    - ``cw.write_result(...)`` — 任意对象.write_result
    """
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Name) and func.id == "write_result":
        return True
    if isinstance(func, ast.Attribute) and func.attr == "write_result":
        return True
    return False


def make_ch_batch_size_gate() -> GateSpec:
    """构造 CH 批量写入防回退 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="CH-BATCH-SIZE", priority=36)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = [
            f for f in _get_staged_py_files(gateway, "CH-BATCH-SIZE")
            if not is_test_exempt(f) and not _is_exempt_file(f)
        ]
        if not py_files:
            return True, ""

        violations: list[str] = []
        for py_file in py_files:
            file_content = _read_staged_file(gateway, py_file)
            if not file_content:
                continue
            # 获取 added 行号集合
            added_lines = {ln for ln, _ in _get_added_lines(gateway, py_file, "CH-BATCH-SIZE")}
            if not added_lines:
                continue

            # AST 解析（fail-open：语法错误跳过该文件）
            try:
                tree = ast.parse(file_content)
            except SyntaxError:
                logger.warning(
                    "CH-BATCH-SIZE: ast.parse 失败 %s（语法错误），fail-open 跳过",
                    py_file, exc_info=True,
                )
                continue

            parent_map = _build_parent_map(tree)

            # 遍历所有 Call 节点，找 write_result 调用
            for node in ast.walk(tree):
                if not _is_write_result_call(node):
                    continue
                for_node = _find_enclosing_for(node, parent_map)
                if for_node is None:
                    continue  # 不在 for 循环内，放行
                # 检测 added 行：
                # 1. write_result 调用行是 added 行（新增的循环内调用）
                # 2. for 循环头是 added 行（新增循环包裹已有调用）
                call_line = node.lineno
                for_line = for_node.lineno
                if call_line in added_lines or for_line in added_lines:
                    violations.append(
                        f"  {py_file}:{call_line}: write_result 在 for 循环内直接调用"
                        f"（for 循环头在第 {for_line} 行）"
                    )

        if violations:
            detail = (
                "CH-BATCH-SIZE：检测到 write_result 在 for 循环内直接调用，\n"
                "  违反裁定 #ARCH-CH-003/#ARCH-CH-004——必须使用 BufferedWriter 中间层。\n"
                "  病根：逐个 write_result 导致 CH data parts 爆炸（5204 次 INSERT → parts 堆积）。\n"
                + "\n".join(violations)
                + "\n-> 改用 BufferedWriter：writer = BufferedWriter(table); "
                "for r in fetch(): writer.add(r); writer.flush()"
            )
            logger.error("CH-BATCH-SIZE gate block:\n%s", detail)
            return False, detail
        return True, ""

    return GateSpec(gate_id="CH-BATCH-SIZE", check=_check, priority=36)
