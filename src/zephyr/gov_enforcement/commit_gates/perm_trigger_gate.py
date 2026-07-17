# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.perm_trigger_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 硬阻断——staged 新增 .py 文件含 [TTL] permanent 头标且使用时间触发模式（while True / time.sleep / schedule. / APScheduler）但未注册事件订阅时阻断 commit；tests/ 豁免（真源：commit_gate_registry.is_test_exempt）；只检测新增文件（diff-filter=A）；in-process AST 分析无 subprocess；AST 解析失败/文件读取失败 fail-open（logger.warning）
# [MODIFY-GUARD] gate_id="PERM-TRIGGER"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——AST/IO 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_perm_trigger_gate.py
# [A_module] module_id=MOD-GOV-perm_trigger_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 本文件是PERM-TRIGGER检测器自身,源码含检测模式字符串(while True/time.sleep/APScheduler等)用于AST匹配,非实际时间触发
"""perm_trigger_gate.py — 永久系统脚本时间触发模式无事件订阅阻断门禁（PERM-TRIGGER）

检测 staged 新增 .py 文件中 [TTL] permanent 头标的脚本是否使用时间触发模式
（``while True`` / ``time.sleep`` / ``schedule.`` / APScheduler）但未注册任何
事件订阅——违反"永久系统必须全自动（事件触发）"铁律。

病根（第一性原理）
-----------------
永久系统脚本若用 ``while True: time.sleep(N)`` 轮询而非事件订阅，会出现：
  1. 进程崩溃后无自愈（无事件触发重启）
  2. 多实例并发时无协调（无事件总线仲裁）
  3. 资源浪费（空转 sleep 占用进程槽）
铁律要求永久系统必须通过事件订阅（``event_bus.subscribe`` / ``@subscriber``）
驱动，而非时间轮询。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process，``--no-verify`` 绕不过）注册
门禁，AST 分析 staged 新增 .py 文件：
  1. 文件头标含 ``[TTL] permanent``（case-insensitive）才检测
  2. 时间触发模式：``while True`` / ``time.sleep()`` / ``schedule.`` 属性访问 /
     ``APScheduler`` / ``BackgroundScheduler`` / ``BlockingScheduler`` 标识符
  3. 事件订阅：``.subscribe(`` 调用 / ``@subscriber`` 装饰器 /
     ``@event_handler`` 装饰器 / ``register_handler(`` 调用 / ``event_bus.`` 属性访问
  4. 时间触发存在但事件订阅缺失 -> 违规

设计权衡
--------
1. **只检测新增文件**：存量违规由后续清理。本 gate 防止新增违规。
2. **in-process AST**：无 subprocess 调用，纯 ast.parse + ast.walk，自包含。
3. **fail-open on AST error**：语法错误文件（可能正在编辑）不阻断，由其他 gate
   （如 syntax check）负责。本 gate 关注架构违规而非语法。
4. **priority=82**：在 VOCAB-HARDCODE(80) 之后、EMPTY-HANDLER(84) 之前。

Usage::

    from zephyr.gov_enforcement.commit_gates.perm_trigger_gate import make_perm_trigger_gate

    registry.register(make_perm_trigger_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import ast
import logging
import os

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_perm_trigger_gate"]

# 时间触发模式标识符（APScheduler 类名 + 标识符）
_TIME_TRIGGER_IDENTIFIERS = frozenset({
    "APScheduler",
    "BackgroundScheduler",
    "BlockingScheduler",
    "AsyncIOScheduler",
})

# 事件订阅相关属性名/方法名
_EVENT_REGISTRATION_ATTRS = frozenset({"subscribe", "register_handler"})
_EVENT_BUS_ATTR = "event_bus"
_EVENT_DECORATORS = frozenset({"subscriber", "event_handler"})


def _has_permanent_ttl(content: str) -> bool:
    """检查文件头部注释是否含 [TTL] permanent 标记（case-insensitive）。

    Args:
        content: 文件文本。

    Returns:
        True 表示文件头标声明为 permanent。
    """
    # 只看前 40 行（头标在文件开头）
    head_lines = content.splitlines()[:40]
    head = "\n".join(head_lines).lower()
    return "[ttl] permanent" in head


def _is_time_trigger_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Attribute) and func.attr == "sleep":
        return True
    if isinstance(func, ast.Attribute):
        root = func
        while isinstance(root, ast.Attribute):
            root = root.value
        if isinstance(root, ast.Name) and root.id == "schedule":
            return True
    return False


def _detect_time_trigger(tree: ast.AST) -> bool:
    """AST 中是否存在时间触发模式。

    检测：
      - ``ast.While`` 且 test 为 ``ast.Constant(True)``（while True）
      - ``time.sleep(...)`` 调用
      - ``schedule.`` 属性访问
      - 标识符 APScheduler / BackgroundScheduler / BlockingScheduler / AsyncIOScheduler
    """
    for node in ast.walk(tree):
        # while True
        if isinstance(node, ast.While) and isinstance(node.test, ast.Constant) and node.test.value is True:
            return True
        # time.sleep(...) / xxx.sleep(...)
        if _is_time_trigger_call(node):
            return True
        # schedule.xxx 属性访问（非调用）
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == "schedule":
                return True
        # APScheduler / BackgroundScheduler 等标识符（Name 节点）
        if isinstance(node, ast.Name) and node.id in _TIME_TRIGGER_IDENTIFIERS:
            return True
    return False


def _detect_time_trigger_in_text(text: str) -> bool:
    """文本模式检测时间触发（用于 diff 新增行，AST 无法解析片段）。

    检测：
      - ``time.sleep(`` / ``.sleep(`` 调用
      - ``while True`` / ``while 1``
      - ``schedule.`` 属性访问
      - APScheduler / BackgroundScheduler / BlockingScheduler / AsyncIOScheduler 标识符
      - ``.wait(timeout=`` 事件超时轮询模式
    """
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "time.sleep(" in line or ".sleep(" in line:
            return True
        if "while True" in line or "while 1:" in line:
            return True
        if "schedule." in line:
            return True
        for ident in _TIME_TRIGGER_IDENTIFIERS:
            if ident in line:
                return True
        if ".wait(timeout=" in line:
            return True
    return False


def _detect_event_registration(tree: ast.AST) -> bool:
    """AST 中是否存在事件订阅/注册模式。

    检测：
      - ``.subscribe(...)`` / ``.register_handler(...)`` 调用
      - ``@subscriber`` / ``@event_handler`` 装饰器
      - ``event_bus.xxx`` 属性访问或调用
    """
    for node in ast.walk(tree):
        # .subscribe(...) / .register_handler(...) 调用
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in _EVENT_REGISTRATION_ATTRS:
                return True
            # event_bus.xxx(...)
            if isinstance(node.func.value, ast.Name) and node.func.value.id == _EVENT_BUS_ATTR:
                return True
        # event_bus.xxx 属性访问（非调用）
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == _EVENT_BUS_ATTR:
                return True
        # @subscriber / @event_handler 装饰器
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for dec in node.decorator_list:
                dec_name = _decorator_name(dec)
                if dec_name in _EVENT_DECORATORS:
                    return True
    return False


def _decorator_name(dec: ast.AST) -> str:
    """提取装饰器名称（支持 @foo / @foo.bar / @foo(...) 三种形式）。"""
    if isinstance(dec, ast.Name):
        return dec.id
    if isinstance(dec, ast.Attribute):
        return dec.attr
    if isinstance(dec, ast.Call):
        return _decorator_name(dec.func)
    return ""


def _get_staged_py_files(gateway) -> tuple[list[str], str]:
    """获取 staged 新增+修改的 .py 文件列表和 worktree root。

    Returns: (py_files, wt_root) — py_files 为空时表示无文件或 fail-open。
    """
    try:
        diff_result = gateway._run_git(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"]
        )
        if diff_result.returncode != 0:
            logger.warning(
                "PERM-TRIGGER gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                diff_result.returncode,
            )
            return [], ""
        staged_files = diff_result.stdout.strip().splitlines()
    except Exception as e:
        logger.warning(
            "PERM-TRIGGER gate fail-open: git diff 异常(%s: %s)，检测器失效。",
            type(e).__name__, e, exc_info=True
        )
        return [], ""

    py_files = [
        f.replace("\\", "/") for f in staged_files
        if f.endswith(".py") and not is_test_exempt(f)
    ]
    if not py_files:
        return [], ""

    try:
        toplevel_result = gateway._run_git(
            ["git", "rev-parse", "--show-toplevel"]
        )
        wt_root = toplevel_result.stdout.strip() if toplevel_result.returncode == 0 else str(gateway.project_root)
    except Exception:
        wt_root = str(gateway.project_root)

    return py_files, wt_root


def _get_added_set(gateway) -> set[str]:
    """获取 staged 新增(A)文件集合。"""
    try:
        result = gateway._run_git(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=A"]
        )
        return set(result.stdout.strip().splitlines()) if result.returncode == 0 else set()
    except Exception:
        return set()


def _check_permanent_trigger_new(abs_path: str, content: str) -> bool:
    """检测新增 permanent 文件是否含时间触发但无事件订阅。"""
    try:
        tree = ast.parse(content, filename=abs_path)
    except SyntaxError as e:
        logger.warning(
            "PERM-TRIGGER gate skip file %s: AST 解析失败(%s: %s)，检测器失效。",
            abs_path, type(e).__name__, e,
        )
        return False
    has_trigger = _detect_time_trigger(tree)
    has_event = _detect_event_registration(tree)
    return has_trigger and not has_event


def _check_permanent_trigger_modified(gateway, rel_path: str, abs_path: str, content: str) -> bool:
    """检测修改文件的 staged 新增行是否含时间触发且全文件无事件订阅。"""
    try:
        diff_content = gateway._run_git(
            ["git", "diff", "--cached", "--unified=0", "--", rel_path]
        )
        if diff_content.returncode != 0:
            return False
        added_lines = [
            line[1:] for line in diff_content.stdout.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        ]
    except Exception:
        return False

    if not added_lines:
        return False

    added_text = "\n".join(added_lines)
    if not _detect_time_trigger_in_text(added_text):
        return False

    # 检查修改后全文件是否有事件订阅
    try:
        tree = ast.parse(content, filename=abs_path)
        return not _detect_event_registration(tree)
    except SyntaxError:
        return True  # AST 解析失败，认为无事件订阅


def make_perm_trigger_gate() -> GateSpec:
    """构造永久系统脚本时间触发无事件订阅阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="PERM-TRIGGER", priority=82)。
        priority=82——在 VOCAB-HARDCODE(80) 之后、EMPTY-HANDLER(84) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged .py 文件 + worktree root
        py_files, wt_root = _get_staged_py_files(gateway)
        if not py_files:
            return True, ""

        # 2. 获取新增文件集合（区分 A/M）
        added_set = _get_added_set(gateway)

        # 3. AST 检测：permanent 文件含时间触发但无事件订阅
        violations: list[str] = []
        for rel_path in py_files:
            abs_path = rel_path if os.path.isabs(rel_path) else os.path.join(wt_root, rel_path.replace("/", os.sep))
            if not os.path.isfile(abs_path):
                continue

            try:
                with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except OSError as e:
                logger.warning(
                    "PERM-TRIGGER gate skip file %s: 读取失败(%s: %s)。",
                    abs_path, type(e).__name__, e,
                )
                continue

            if not _has_permanent_ttl(content):
                continue  # 非 permanent 文件，跳过

            # 门禁文件自豁免：检测器本身含 pattern 字符串（非真实时间触发）
            if "governance/commit_gates/" in rel_path or "governance\\commit_gates\\" in rel_path:
                continue

            if rel_path in added_set:
                # 新增文件：全文件 AST 检测
                if _check_permanent_trigger_new(abs_path, content):
                    violations.append(rel_path)
            else:
                # 修改文件：只检测 staged diff 新增行中的时间触发模式
                if _check_permanent_trigger_modified(gateway, rel_path, abs_path, content):
                    violations.append(rel_path + " (modified)")

        if violations:
            detail = "; ".join(violations[:5])
            return False, (
                f"永久系统脚本使用时间触发模式但未注册事件订阅"
                f"（违反'永久系统必须全自动事件触发'铁律）: {detail}"
            )
        return True, ""

    return GateSpec(gate_id="PERM-TRIGGER", check=_check, priority=82)
