# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.empty_handler_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 硬阻断——staged 新增 .py 文件中含事件订阅 handler 函数但函数体仅含 logger/pass/return/docstring（无实际逻辑）时阻断 commit；tests/ 豁免（真源：commit_gate_registry.is_test_exempt）；只检测新增文件（diff-filter=A）；in-process AST 分析无 subprocess；AST 解析失败/文件读取失败 fail-open（logger.warning）
# [MODIFY-GUARD] gate_id="EMPTY-HANDLER"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——AST/IO 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_empty_handler_gate.py
# [A_module] module_id=MOD-GOV-empty_handler_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""empty_handler_gate.py — 空事件 handler 函数阻断门禁（EMPTY-HANDLER）

检测 staged 新增 .py 文件中的事件订阅 handler 函数是否为空壳（函数体仅含
logger/pass/return/docstring，无实际业务逻辑）——空 handler 是死代码，注册了
事件订阅但什么都不做，违反"事件订阅必须有效"原则。

病根（第一性原理）
-----------------
新 AI 添加事件订阅时常写空 handler 占位：
  1. ``@subscriber`` 装饰 ``def on_xxx(event): pass`` —— 注册了但无逻辑
  2. ``def handle_xxx(event): logger.info("got event")`` —— 仅日志无业务
  3. ``def on_event(event): return`` —— 空返回
空 handler 让事件总线以为有处理者，实际无人处理，事件丢失静默失败。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁，AST 分析
staged 新增 .py 文件中的 handler 函数：
  1. 识别 handler：函数装饰器名含 ``subscriber`` / ``event_handler`` / ``handler``
     / ``listener``，或函数名以 ``handle_`` / ``on_`` 开头
  2. 检查函数体（排除 docstring）：若全部为 ``pass`` / ``logger.xxx()`` 调用 /
     ``return`` (None/常量) 则为空 handler
  3. 收集文件内所有空 handler，返回前 5 个

设计权衡
--------
1. **只检测新增文件**：存量违规由后续清理。本 gate 防止新增违规。
2. **in-process AST**：纯 ast.walk，无 subprocess，自包含。
3. **fail-open on AST error**：语法错误文件不阻断。
4. **handler 识别宽松**：装饰器名或函数名匹配即认为是 handler——宁可误判也不漏检。
5. **priority=84**：在 PERM-TRIGGER(82) 之后、ORPHAN-MODULE(86) 之前。

Usage::

    from zephyr.governance.commit_gates.empty_handler_gate import make_empty_handler_gate

    registry.register(make_empty_handler_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import ast
import logging
import os

from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_empty_handler_gate"]

# 装饰器名包含这些子串 -> handler
_HANDLER_DECORATOR_SUBSTRS = ("subscriber", "event_handler", "handler", "listener")

# 函数名前缀 -> handler
_HANDLER_FUNC_PREFIXES = ("handle_", "on_")

# logger 方法名（logger.info/debug/warning/error 等）
_LOGGER_METHODS = frozenset({"info", "debug", "warning", "error", "critical", "log", "exception"})


def _extract_decorator_name(dec: ast.AST) -> str:
    """提取装饰器名称（支持 @foo / @foo.bar / @foo(...) 三种形式）。"""
    if isinstance(dec, ast.Name):
        return dec.id
    if isinstance(dec, ast.Attribute):
        return dec.attr
    if isinstance(dec, ast.Call):
        return _extract_decorator_name(dec.func)
    return ""


def _is_handler(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """判断函数是否是事件 handler（装饰器名匹配或函数名前缀匹配）。"""
    # 装饰器匹配
    for dec in func.decorator_list:
        name = _extract_decorator_name(dec).lower()
        if any(s in name for s in _HANDLER_DECORATOR_SUBSTRS):
            return True
    # 函数名前缀匹配
    fname = func.name.lower()
    if fname.startswith(_HANDLER_FUNC_PREFIXES):
        return True
    return False


def _is_empty_logger_call(stmt: ast.stmt) -> bool:
    """语句是否是 logger.xxx() 调用。"""
    if not isinstance(stmt, ast.Expr):
        return False
    if not isinstance(stmt.value, ast.Call):
        return False
    func = stmt.value.func
    # logger.info(...) / log.info(...) 等
    if isinstance(func, ast.Attribute) and func.attr in _LOGGER_METHODS:
        if isinstance(func.value, ast.Name) and func.value.id in ("logger", "log", "logging"):
            return True
    return False


def _is_empty_return(stmt: ast.stmt) -> bool:
    """语句是否是空 return（无值或 None 常量）。"""
    if not isinstance(stmt, ast.Return):
        return False
    if stmt.value is None:
        return True
    if isinstance(stmt.value, ast.Constant) and stmt.value.value is None:
        return True
    return False


def _is_empty_handler_body(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """检查 handler 函数体是否仅含 docstring/pass/logger/return（无实际逻辑）。

    Args:
        func: ast.FunctionDef 或 ast.AsyncFunctionDef 节点。

    Returns:
        True 表示函数体是空壳（仅含 docstring/pass/logger/return）。
    """
    body = list(func.body)
    # 排除 docstring（第一个 ast.Expr 且 value 是 str 常量）
    real_stmts: list[ast.stmt] = []
    for stmt in body:
        if (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, str)):
            continue  # docstring
        real_stmts.append(stmt)

    if not real_stmts:
        return True  # 只有 docstring 的空函数体

    for stmt in real_stmts:
        if isinstance(stmt, ast.Pass):
            continue
        if _is_empty_logger_call(stmt):
            continue
        if _is_empty_return(stmt):
            continue
        # 其他语句 -> 有实际逻辑
        return False
    return True  # 全部都是空壳语句


def make_empty_handler_gate() -> GateSpec:
    """构造空事件 handler 函数阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="EMPTY-HANDLER", priority=84)。
        priority=84——在 PERM-TRIGGER(82) 之后、ORPHAN-MODULE(86) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged 新增 .py 文件
        try:
            diff_result = gateway._run_git(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=A"]
            )
            if diff_result.returncode != 0:
                logger.warning(
                    "EMPTY-HANDLER gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                    diff_result.returncode,
                )
                return True, ""
            staged_new = diff_result.stdout.strip().splitlines()
        except Exception as e:
            logger.warning(
                "EMPTY-HANDLER gate fail-open: git diff 异常(%s: %s)，检测器失效。",
                type(e).__name__, e, exc_info=True
            )
            return True, ""

        # 2. 过滤 .py 文件 + tests/ 豁免
        new_py_files = [
            f.replace("\\", "/") for f in staged_new
            if f.endswith(".py") and not is_test_exempt(f)
        ]
        if not new_py_files:
            return True, ""

        # 3. 获取 worktree root
        try:
            toplevel_result = gateway._run_git(
                ["git", "rev-parse", "--show-toplevel"]
            )
            if toplevel_result.returncode == 0:
                wt_root = toplevel_result.stdout.strip()
            else:
                wt_root = str(gateway.project_root)
        except Exception:
            wt_root = str(gateway.project_root)

        # 4. 解析为绝对路径
        abs_files = []
        for rel in new_py_files:
            if os.path.isabs(rel):
                abs_files.append(rel)
            else:
                abs_files.append(os.path.join(wt_root, rel.replace("/", os.sep)))
        abs_files = [f for f in abs_files if os.path.isfile(f)]
        if not abs_files:
            return True, ""

        # 5. AST 检测：handler 函数体空壳
        all_violations: list[str] = []
        for abs_path in abs_files:
            try:
                content = open(abs_path, "r", encoding="utf-8", errors="replace").read()
            except OSError as e:
                logger.warning(
                    "EMPTY-HANDLER gate skip file %s: 读取失败(%s: %s)。",
                    abs_path, type(e).__name__, e,
                )
                continue

            try:
                tree = ast.parse(content, filename=abs_path)
            except SyntaxError as e:
                logger.warning(
                    "EMPTY-HANDLER gate skip file %s: AST 解析失败(%s: %s)，检测器失效。",
                    abs_path, type(e).__name__, e,
                )
                continue

            rel_name = os.path.relpath(abs_path, wt_root).replace("\\", "/")
            file_violations: list[str] = []
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if not _is_handler(node):
                    continue
                if _is_empty_handler_body(node):
                    file_violations.append(
                        f"空 handler 函数 {node.name} 仅含 logger/pass/return 无实际逻辑（{rel_name}）"
                    )
            all_violations.extend(file_violations[:5])

        if all_violations:
            detail = "; ".join(all_violations[:5])
            return False, detail
        return True, ""

    return GateSpec(gate_id="EMPTY-HANDLER", check=_check, priority=84)
