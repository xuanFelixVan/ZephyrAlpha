# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.manual_only_permanent_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged 新增 .py 文件含 [TTL] permanent 头标且使用 manual 触发模式（argparse.ArgumentParser / input() / __main__ + sys.argv 解析）但无事件订阅/自动触发注册时阻断 commit；tests/ 豁免；只检测新增文件（diff-filter=A）；in-process AST 分析无 subprocess；AST 解析失败/文件读取失败 fail-open；本 gate 自身文件豁免（含检测模式字符串）；与 PERM-TRIGGER 互补——PERM-TRIGGER 检测时间触发，本 gate 检测 manual 触发
# [MODIFY-GUARD] gate_id="MANUAL-ONLY-PERMANENT"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——AST/IO 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_manual_only_permanent_gate_noqa.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m02-manual-trigger  M02豁免: 本文件是MANUAL-ONLY-PERMANENT检测器自身,源码含检测模式字符串(argparse/input/sys.argv)用于AST匹配,非实际manual触发
# noqa: m11-perm-manual-legitimate  M11豁免: 本文件是 MANUAL-ONLY-PERMANENT 检测器自身（GitCommitGateway in-process 事件触发），源码含检测模式字符串用于 AST 匹配非真实 manual 触发
"""manual_only_permanent_gate.py — 永久系统脚本 manual 触发无事件订阅阻断门禁（MANUAL-ONLY-PERMANENT，#ARCH-GOV-CONVERGENCE-META Phase 3.6 补齐 rc4 enforceability）

病根（裁定#221，原 ai_first_governance_principles.md §二，文档已删 2026-07-30，git 历史可查）
------------------------------------------------
rc4_manual_exception_permissive: manual 例外开口过大
M02 metric warn-only 追踪 manual-only 永久脚本，无 commit gate 硬阻断含常驻服务特征的
manual-only permanent 脚本。本 gate 在 GitCommitGateway pre-commit 阶段
（in-process，``--no-verify`` 绕不过）注册，AST 分析 staged 新增 .py 文件。

治本方案
--------
检测 staged 新增 .py 文件中 [TTL] permanent 头标的脚本是否使用 manual 触发模式
（argparse / input / __main__ + sys.argv 解析）但未注册任何事件订阅/自动触发——
违反"永久系统必须全自动（事件触发）"铁律。

与 PERM-TRIGGER 的关系
----------------------
- PERM-TRIGGER (priority=82): 检测时间触发模式（while True / time.sleep / schedule）
- MANUAL-ONLY-PERMANENT (priority=36): 检测 manual 触发模式（argparse / input / __main__）
两者互补，共同覆盖"永久系统触发方式"的两大违规模式。

设计权衡
--------
1. **只检测新增文件**：存量违规由后续清理。本 gate 防止新增违规。
2. **in-process AST**：无 subprocess 调用，纯 ast.parse + ast.walk，自包含。
3. **fail-open on AST error**：语法错误文件不阻断。
4. **gate 自豁免**：本 gate 源码含检测模式字符串，需自豁免。
5. **priority=36**：在 R5-DIGIT-SUFFIX(35) 之后、CH-BATCH-SIZE(36 冲突)→调整为 36 与 CH-BATCH-SIZE 不冲突（CH-BATCH-SIZE 实际 priority=36，本 gate 用 36 会冲突，改为 43）。

实际 priority=43（避开 CH-BATCH-SIZE=36 / CH-FINAL=37 / CH-VERSION-COL=38 / RENAME-DEPGRAPH-SYNC=39 / FILE-PLACEMENT-TTL=33-40 区间）。
"""

from __future__ import annotations

import ast
import logging
import os
import re

# 复用 perm_trigger_gate 的辅助函数（SSoT，避免 FUNCTION-DUP 重复定义）
from zephyr.gov_enforcement.commit_gates.perm_trigger_gate import (
    _decorator_name,
    _has_permanent_ttl,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_manual_only_permanent_gate"]

# manual 触发模式标识符（argparse 类名 + 相关函数名）
_MANUAL_TRIGGER_IDENTIFIERS = frozenset(
    {
        "ArgumentParser",
        "argparse",
    }
)

# m11-perm-manual-legitimate noqa 标记正则（#ARCH-P3-FOLLOWUP-TODOS-001 裁定 B / C，P3-1.2 治本）
# 格式：`# noqa: m11-perm-manual-legitimate` + 2+ 空格 + reason（>=10 字符）
# reason 末尾的尾随空白会被 rstrip 去除后再计数
_M11_NOQA_PATTERN = re.compile(
    r"#\s*noqa:\s*m11-perm-manual-legitimate\s{2,}(\S.*)$",
    re.MULTILINE,
)

# 事件订阅/自动触发相关属性名/方法名（与 PERM-TRIGGER 共享语义）
_EVENT_REGISTRATION_ATTRS = frozenset({"subscribe", "register_handler"})
_EVENT_BUS_ATTR = "event_bus"
_EVENT_DECORATORS = frozenset({"subscriber", "event_handler"})
# 自动触发注册方法（reconciler / scheduler 注册）
_AUTO_TRIGGER_METHODS = frozenset(
    {
        "register_reconciler",
        "register_scheduler",
        "register_daemon",
        "register_auto_trigger",
        "add_reconciler",
        "add_scheduler",
    }
)


def _is_manual_trigger_call(node: ast.AST) -> bool:
    """检测 argparse 相关调用。"""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    # ArgumentParser(...) 直接调用
    if isinstance(func, ast.Name) and func.id in _MANUAL_TRIGGER_IDENTIFIERS:
        return True
    # argparse.ArgumentParser(...) 属性调用
    if isinstance(func, ast.Attribute):
        if func.attr == "ArgumentParser":
            return True
        if isinstance(func.value, ast.Name) and func.value.id == "argparse":
            return True
    return False


def _is_input_call(node: ast.AST) -> bool:
    """检测 input() 调用（手动输入触发）。"""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Name) and func.id == "input":
        return True
    return False


def _has_main_guard_with_argv(tree: ast.AST) -> bool:
    """检测 if __name__ == "__main__": 块内是否使用 sys.argv 解析。

    这是典型的 manual 命令行触发模式。
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        # 检测 __name__ == "__main__"
        test = node.test
        if not _is_main_guard_test(test):
            continue
        # 在 if 块内查找 sys.argv 引用
        for child in ast.walk(node):
            if isinstance(child, ast.Attribute):
                if isinstance(child.value, ast.Name) and child.value.id == "sys":
                    if child.attr == "argv":
                        return True
            if isinstance(child, ast.Subscript):
                # sys.argv[1] 之类的下标访问
                if isinstance(child.value, ast.Attribute):
                    if isinstance(child.value.value, ast.Name) and child.value.value.id == "sys":
                        if child.value.attr == "argv":
                            return True
    return False


def _is_name_main_compare(test: ast.AST, left_is_name: bool) -> bool:
    """检测 __name__ == "__main__" 或 "__main__" == __name__ 条件。

    Args:
        left_is_name: True 检测形式 1（左侧 __name__），False 检测形式 2（左侧 "__main__"）。
    """
    if not isinstance(test, ast.Compare):
        return False
    if len(test.ops) != 1 or not isinstance(test.ops[0], ast.Eq):
        return False
    if left_is_name:
        if not (isinstance(test.left, ast.Name) and test.left.id == "__name__"):
            return False
        return any(isinstance(c, ast.Constant) and c.value == "__main__" for c in test.comparators)
    if not (isinstance(test.left, ast.Constant) and test.left.value == "__main__"):
        return False
    return any(isinstance(c, ast.Name) and c.id == "__name__" for c in test.comparators)


def _is_main_guard_test(test: ast.AST) -> bool:
    """检测 __name__ == "__main__" 条件（两种形式）。"""
    if _is_name_main_compare(test, left_is_name=True):
        return True
    return _is_name_main_compare(test, left_is_name=False)


def _detect_manual_trigger(tree: ast.AST) -> bool:
    """AST 中是否存在 manual 触发模式。"""
    for node in ast.walk(tree):
        # argparse.ArgumentParser(...) 调用
        if _is_manual_trigger_call(node):
            return True
        # input() 调用
        if _is_input_call(node):
            return True
    # if __name__ == "__main__": 块内使用 sys.argv
    if _has_main_guard_with_argv(tree):
        return True
    return False


def _detect_event_or_auto_trigger(tree: ast.AST) -> bool:
    """AST 中是否存在事件订阅或自动触发注册。

    检测：
      - ``.subscribe(...)`` / ``.register_handler(...)`` 调用
      - ``@subscriber`` / ``@event_handler`` 装饰器
      - ``event_bus.xxx`` 属性访问或调用
      - ``register_reconciler(...)`` / ``register_scheduler(...)`` 等自动触发注册
    """
    for node in ast.walk(tree):
        # .subscribe(...) / .register_handler(...) / .register_reconciler(...) 调用
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in _EVENT_REGISTRATION_ATTRS:
                return True
            if node.func.attr in _AUTO_TRIGGER_METHODS:
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


def _get_staged_py_files(gateway) -> tuple[list[str], str]:
    """获取 staged 新增+修改的 .py 文件列表和 worktree root。"""
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
        if diff_result.returncode != 0:
            logger.warning(
                "MANUAL-ONLY-PERMANENT gate fail-open: git diff 失败(rc=%d)。",
                diff_result.returncode,
            )
            return [], ""
        staged_files = diff_result.stdout.strip().splitlines()
    except Exception as e:  # noqa: BLE001 — broad exception catch for fail-open
        logger.warning(
            "MANUAL-ONLY-PERMANENT gate fail-open: git diff 异常(%s: %s)。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return [], ""

    py_files = [f.replace("\\", "/") for f in staged_files if f.endswith(".py") and not is_test_exempt(f)]
    if not py_files:
        return [], ""

    try:
        toplevel = gateway.run_git(["git", "rev-parse", "--show-toplevel"])
        wt_root = toplevel.stdout.strip() if toplevel.returncode == 0 else str(gateway.project_root)
    except Exception:  # noqa: BLE001 — broad exception catch for fail-open
        wt_root = str(gateway.project_root)

    return py_files, wt_root


def _get_added_set(gateway) -> set[str]:
    """获取 staged 新增(A)文件集合。"""
    try:
        result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=A"])
        return set(result.stdout.strip().splitlines()) if result.returncode == 0 else set()
    except Exception:  # noqa: BLE001 — broad exception catch for fail-open
        return set()


def _check_manual_only_permanent_new(abs_path: str, content: str) -> bool:
    """检测新增 permanent 文件是否含 manual 触发但无事件/自动触发订阅。

    P3-1.2 治本（#ARCH-P3-FOLLOWUP-TODOS-001 裁定 B / C，2026-07-20）：
    若文件含合规 m11-perm-manual-legitimate noqa 标记，视为合法豁免，返回 False（放行）。
    """
    try:
        tree = ast.parse(content, filename=abs_path)
    except SyntaxError as e:
        logger.warning(
            "MANUAL-ONLY-PERMANENT gate skip file %s: AST 解析失败(%s: %s)。",
            abs_path,
            type(e).__name__,
            e,
        )
        return False
    has_manual = _detect_manual_trigger(tree)
    has_event = _detect_event_or_auto_trigger(tree)
    if has_manual and not has_event:
        # 检查 m11 合规豁免（P3-1.2 治本：合法 manual 触发 permanent 脚本）
        if _has_m11_exemption(content):
            return False  # 合规豁免，放行
        return True  # 违规：manual 触发 + 无事件订阅 + 无合规豁免
    return False


def _has_m11_exemption(content: str) -> bool:
    """检测内容是否含合规的 m11-perm-manual-legitimate noqa 标记（P3-1.2 治本）。

    合规条件（与 noqa_exempt_registry.yaml 的 m11 条目一致）：
      1. 含 ``m11-perm-manual-legitimate`` noqa 标记（``#`` 引导，``noqa:`` 前缀）
      2. 标记后跟 2+ 空格分隔的 reason
      3. reason 长度 >= 10 字符（rstrip 后计数）

    用途：MANUAL-ONLY-PERMANENT gate 的合法豁免路径——
    AI/CI 按需调用的 permanent runner（非 cron / 非 daemon / 非常驻服务）
    可通过 ``m11-perm-manual-legitimate`` noqa 标记 + ``M11豁免: <理由>`` 格式豁免。

    Args:
        content: 文件全文内容。

    Returns:
        True = 含合规 m11 豁免标记（gate 应放行）；
        False = 无 m11 标记 / reason 不足 10 字符 / 其他 noqa 标记。
    """
    for match in _M11_NOQA_PATTERN.finditer(content):
        reason = match.group(1).rstrip()
        if len(reason) >= 10:
            return True
    return False


def _check_manual_only_permanent_modified(gateway, rel_path: str, abs_path: str, content: str) -> bool:
    """检测修改文件的 staged 新增行是否含 manual 触发且全文件无事件订阅。

    P3-1.2 治本对齐（2026-08-02）：modified 文件同样适用 m11 合规豁免——
    合法 manual 触发 permanent 脚本（如 apply_depgraph.py / apply_dataflowgraph.py
    等 CLI 写入工具）在新增命令/参数时不应被误判，与 new 文件豁免逻辑一致。
    """
    if _has_m11_exemption(content):
        return False  # 合规豁免，放行（与 _check_manual_only_permanent_new 一致）
    try:
        # --ignore-cr-at-eol：EOL 规范化提交全文件行伪"added"，会把存量 manual 触发
        # 模式误报为新增——按内容判定 added，行尾差异不计（2026-08-16 EOL 批实证）
        diff_content = gateway.run_git(["git", "diff", "--cached", "--unified=0", "--ignore-cr-at-eol", "--", rel_path])
        if diff_content.returncode != 0:
            return False
        added_lines = [
            line[1:] for line in diff_content.stdout.splitlines() if line.startswith("+") and not line.startswith("+++")
        ]
    except Exception:  # noqa: BLE001 — broad exception catch for fail-open
        return False

    if not added_lines:
        return False

    # 文本模式快速检测 manual 触发模式
    added_text = "\n".join(added_lines)
    quick_hit = False
    for line in added_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "ArgumentParser" in line or "argparse." in line:
            quick_hit = True
            break
        if "input(" in line:
            quick_hit = True
            break
        if "__name__" in line and "__main__" in line:
            quick_hit = True
            break
    if not quick_hit:
        return False

    # 检查修改后全文件是否有事件订阅
    try:
        tree = ast.parse(content, filename=abs_path)
        return not _detect_event_or_auto_trigger(tree)
    except SyntaxError:
        return True  # AST 解析失败，认为无事件订阅


def make_manual_only_permanent_gate() -> GateSpec:
    """构造永久系统脚本 manual 触发无事件订阅阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="MANUAL-ONLY-PERMANENT", priority=43)。
        priority=43——避开 33-42 区间（FILE-PLACEMENT-TTL/CH-* / RENAME-DEPGRAPH-SYNC），
        在 ENCODING(42) 之后、FOREIGN-CHANGE(45) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged .py 文件 + worktree root
        py_files, wt_root = _get_staged_py_files(gateway)
        if not py_files:
            return True, ""

        # 2. 获取新增文件集合（区分 A/M）
        added_set = _get_added_set(gateway)

        # 3. AST 检测：permanent 文件含 manual 触发但无事件/自动触发订阅
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
                    "MANUAL-ONLY-PERMANENT gate skip file %s: 读取失败(%s: %s)。",
                    abs_path,
                    type(e).__name__,
                    e,
                )
                continue

            if not _has_permanent_ttl(content):
                continue  # 非 permanent 文件，跳过

            # 门禁文件自豁免：检测器本身含 pattern 字符串（非真实 manual 触发）
            # 2026-08-20 修 governance→gov_enforcement 迁移漂移：原匹配 governance/commit_gates/ 已失配
            if "commit_gates/" in rel_path.replace("\\", "/"):
                continue

            if rel_path in added_set:
                # 新增文件：全文件 AST 检测
                if _check_manual_only_permanent_new(abs_path, content):
                    violations.append(rel_path)
            else:
                # 修改文件：只检测 staged diff 新增行中的 manual 触发模式
                if _check_manual_only_permanent_modified(gateway, rel_path, abs_path, content):
                    violations.append(rel_path + " (modified)")

        if violations:
            detail = "; ".join(violations[:5])
            return False, (
                f"永久系统脚本使用 manual 触发模式（argparse/input/__main__+argv）但未注册"
                f"事件订阅/自动触发（违反'永久系统必须全自动事件触发'铁律）: {detail}"
            )
        return True, ""

    return GateSpec(gate_id="MANUAL-ONLY-PERMANENT", check=_check, priority=43)
