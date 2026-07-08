# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.msg_style_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 硬阻断——staged 新增/修改 .py 文件的 raise 语句异常消息含 Unicode 箭头 ->（U+2192）或以中文句号 。（U+3002）结尾时阻断 commit；tests/ 豁免（真源：commit_gate_registry.is_test_exempt）；in-process AST 分析无 subprocess；AST 解析失败/文件读取失败 fail-open（logger.warning）；行尾含 `# noqa: MSG-STYLE` 注释的单行豁免
# [MODIFY-GUARD] gate_id="MSG-STYLE"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——AST/IO 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_msg_style_gate.py
# [A_module] module_id=MOD-GOV-msg_style_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""msg_style_gate.py — 错误消息标点/箭头风格阻断门禁（MSG-STYLE）

检测 staged .py 文件中 ``raise XxxError(...)`` 模式——异常消息含 Unicode
箭头 ``->``（U+2192）或以中文句号 ``。``（U+3002）结尾，违反"错误消息标点风格
统一"原则（5.99.22 治本防复发）。

病根（第一性原理）
-----------------
100% AI 开发场景下，AI 生成异常消息时标点风格不一致（训练数据混用 Unicode/ASCII
箭头、有/无句号结尾）。这些不一致导致日志聚合/告警匹配困难、用户阅读体验差。

铁律：错误消息统一使用 ASCII ``->``（非 Unicode ``->``）+ 无句号结尾。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process，``--no-verify`` 绕不过）注册
门禁，AST 分析 staged .py 文件中所有 ``ast.Raise`` 节点：

  1. raise 的 exc 是 ``ast.Call``（构造异常实例）
  2. 构造函数名以 ``Error`` 或 ``Exception`` 结尾（自定义异常类）
  3. 第一个参数是 ``ast.JoinedStr``（f-string）或 ``ast.Constant``（普通字符串）
  4. 字符串字面量部分含 ``->``（U+2192）或以 ``。``（U+3002）结尾

设计权衡
--------
1. **只查 staged diff 新增行**：存量违规由 5.99.22 已修复，本 gate 防止新增违规。
   与 MSG-EXPOSURE 一致，新增文件(A)查全文件 AST，修改文件(M)只查 diff 新增行。
2. **in-process AST**：纯 ast.parse + ast.walk，自包含无 subprocess。
3. **fail-open on AST error**：语法错误文件不阻断，由其他 gate 负责。
4. **行级豁免**：单行可用 ``# noqa: MSG-STYLE`` 注释豁免（用于误报或合规的特殊情况）。
5. **priority=92**：在 DOC-REF-BROKEN(91) 之后，作为最新门禁。

Usage::

    from zephyr.governance.commit_gates.msg_style_gate import make_msg_style_gate

    registry.register(make_msg_style_gate())
"""

from __future__ import annotations

import ast
import logging
import os

from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_msg_style_gate"]

# 违规字符常量
_UNICODE_ARROW = "\u2192"  # ->
_CN_PERIOD = "\u3002"      # 。

# 行级豁免标记（与 MSG-EXPOSURE 一致的 noqa 风格）
_NOQA_MARKER = "noqa: MSG-STYLE"


def _is_exception_constructor(call: ast.Call) -> bool:
    """判断 Call 节点是否在构造异常实例（函数名以 Error/Exception 结尾）。

    豁免：Exception()/BaseException() 内建无参构造不算（无消息参数）。
    """
    func = call.func
    name: str | None = None
    if isinstance(func, ast.Name):
        name = func.id
    elif isinstance(func, ast.Attribute):
        name = func.attr
    if name is None:
        return False
    if not (name.endswith("Error") or name.endswith("Exception")):
        return False
    # 内建 Exception()/BaseException() 无参不算
    if name in ("Exception", "BaseException") and not call.args:
        return False
    return True


def _get_exc_name(call: ast.Call) -> str:
    """从 Call 节点提取异常类名。"""
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return ""


def _extract_string_parts(node: ast.expr) -> list[str]:
    """从消息节点提取所有静态字符串部分。

    - ast.Constant(str)：返回 [value]
    - ast.JoinedStr（f-string）：返回所有 Constant(str) 部分
    - 其他：返回 []
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
        return parts
    return []


def _detect_msg_style(tree: ast.AST) -> list[tuple[int, str, str]]:
    """AST 中检测 raise 语句标点/箭头风格违规。

    Returns:
        违规列表 [(lineno, exception_name, violation_type), ...]
        violation_type: "unicode_arrow" 或 "cn_period_end"
    """
    violations: list[tuple[int, str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Raise):
            continue
        if node.exc is None:
            continue  # bare `raise`（re-raise）
        # raise XxxError(...) — exc 是 Call
        if not isinstance(node.exc, ast.Call):
            continue  # raise some_var（变量引用，非构造）— 不检测
        call = node.exc
        if not _is_exception_constructor(call):
            continue
        # 第一个参数是消息（约定俗成）
        if not call.args:
            continue  # 无参数构造（如 raise RuntimeError()）
        first_arg = call.args[0]
        parts = _extract_string_parts(first_arg)
        if not parts:
            continue  # 非字符串消息（如 raise Foo(variable)）

        exc_name = _get_exc_name(call)

        # 检查 Unicode 箭头 ->（任一字面量部分含即违规）
        for part in parts:
            if _UNICODE_ARROW in part:
                violations.append((node.lineno, exc_name, "unicode_arrow"))
                break

        # 检查中文句号 。 结尾（只看最后一个字面量部分）
        last_part = parts[-1]
        if last_part.endswith(_CN_PERIOD):
            violations.append((node.lineno, exc_name, "cn_period_end"))

    return violations


def _is_line_noqa(content: str, lineno: int) -> bool:
    """检查指定行号是否含 noqa 豁免标记。"""
    lines = content.splitlines()
    if lineno < 1 or lineno > len(lines):
        return False
    return _NOQA_MARKER in lines[lineno - 1]


def _filter_noqa_violations(
    content: str,
    violations: list[tuple[int, str, str]],
) -> list[tuple[int, str, str]]:
    """过滤掉带 noqa 标记的违规行。"""
    return [v for v in violations if not _is_line_noqa(content, v[0])]


def make_msg_style_gate() -> GateSpec:
    """构造错误消息标点/箭头风格阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="MSG-STYLE", priority=92)。
        priority=92——在 DOC-REF-BROKEN(91) 之后，作为最新门禁。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged 新增(A) + 修改(M) .py 文件
        try:
            diff_result = gateway._run_git(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"]
            )
            if diff_result.returncode != 0:
                logger.warning(
                    "MSG-STYLE gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                    diff_result.returncode,
                )
                return True, ""
            staged_files = diff_result.stdout.strip().splitlines()
        except Exception as e:
            logger.warning(
                "MSG-STYLE gate fail-open: git diff 异常(%s: %s)，检测器失效。",
                type(e).__name__, e, exc_info=True,
            )
            return True, ""

        # 2. 过滤 .py 文件 + tests/ 豁免
        py_files = [
            f.replace("\\", "/") for f in staged_files
            if f.endswith(".py") and not is_test_exempt(f)
        ]
        if not py_files:
            return True, ""

        # 3. 获取 worktree root
        try:
            toplevel_result = gateway._run_git(["git", "rev-parse", "--show-toplevel"])
            if toplevel_result.returncode == 0:
                wt_root = toplevel_result.stdout.strip()
            else:
                wt_root = str(gateway.project_root)
        except Exception:
            wt_root = str(gateway.project_root)

        # 4. 区分新增(A)和修改(M)
        try:
            added_result = gateway._run_git(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=A"]
            )
            added_set = set(added_result.stdout.strip().splitlines()) if added_result.returncode == 0 else set()
        except Exception:
            added_set = set()

        # 5. 门禁文件自豁免：检测器本身含违规字符（文档字符串中的 -> 和 。）
        violations_all: list[str] = []
        for rel_path in py_files:
            if os.path.isabs(rel_path):
                abs_path = rel_path
            else:
                abs_path = os.path.join(wt_root, rel_path.replace("/", os.sep))
            if not os.path.isfile(abs_path):
                continue

            # 门禁文件自豁免
            rel_normalized = rel_path.replace("\\", "/")
            if "governance/commit_gates/" in rel_normalized:
                continue

            try:
                with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except OSError as e:
                logger.warning(
                    "MSG-STYLE gate skip file %s: 读取失败(%s: %s)。",
                    abs_path, type(e).__name__, e,
                )
                continue

            is_new = rel_path in added_set
            if is_new:
                # 新增文件：全文件 AST 检测
                try:
                    tree = ast.parse(content, filename=abs_path)
                except SyntaxError as e:
                    logger.warning(
                        "MSG-STYLE gate skip file %s: AST 解析失败(%s: %s)，检测器失效。",
                        abs_path, type(e).__name__, e,
                    )
                    continue
                violations = _detect_msg_style(tree)
                violations = _filter_noqa_violations(content, violations)
                for lineno, exc_name, vtype in violations:
                    desc = "Unicode 箭头 ->" if vtype == "unicode_arrow" else "中文句号 。 结尾"
                    violations_all.append(
                        f"{rel_path}:{lineno} raise {exc_name}(...) [{vtype}: {desc}]"
                    )
            else:
                # 修改文件：只检测 diff 新增行范围内的违规
                try:
                    diff_content = gateway._run_git(
                        ["git", "diff", "--cached", "--unified=0", "--", rel_path]
                    )
                    if diff_content.returncode != 0:
                        continue
                    added_lines_meta: list[tuple[int, str]] = []  # (lineno, line_content)
                    cur_lineno = 0
                    for line in diff_content.stdout.splitlines():
                        if line.startswith("@@"):
                            # @@ -a,b +c,d @@ -> c 是新增行起始行号
                            try:
                                plus_part = line.split("+")[1].split("@@")[0].strip()
                                cur_lineno = int(plus_part.split(",")[0])
                            except (IndexError, ValueError):
                                cur_lineno = 0
                        elif line.startswith("+") and not line.startswith("+++"):
                            if cur_lineno > 0:
                                added_lines_meta.append((cur_lineno, line[1:]))
                            cur_lineno += 1
                        elif line.startswith("-"):
                            pass  # 删除行不影响行号计数
                        else:
                            cur_lineno += 1
                except Exception:
                    continue

                if not added_lines_meta:
                    continue

                added_line_nos = {ln for ln, _ in added_lines_meta}
                added_content_map = {ln: lc for ln, lc in added_lines_meta}

                try:
                    tree = ast.parse(content, filename=abs_path)
                except SyntaxError:
                    continue

                violations = _detect_msg_style(tree)
                for lineno, exc_name, vtype in violations:
                    if lineno not in added_line_nos:
                        continue  # 只关心 diff 新增行
                    # 行级 noqa 豁免
                    line_content = added_content_map.get(lineno, "")
                    if _NOQA_MARKER in line_content:
                        continue
                    desc = "Unicode 箭头 ->" if vtype == "unicode_arrow" else "中文句号 。 结尾"
                    violations_all.append(
                        f"{rel_path}:{lineno} raise {exc_name}(...) [{vtype}: {desc}] (modified)"
                    )

        if violations_all:
            detail = "; ".join(violations_all[:5])
            return False, (
                f"错误消息标点/箭头风格违规（统一 ASCII -> + 无句号结尾，"
                f"5.99.22 治本防复发）: {detail}"
            )
        return True, ""

    return GateSpec(gate_id="MSG-STYLE", check=_check, priority=92)
