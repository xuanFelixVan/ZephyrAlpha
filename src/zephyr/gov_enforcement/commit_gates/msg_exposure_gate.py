# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.msg_exposure_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 硬阻断——staged 新增/修改 .py 文件的 raise 语句异常消息 f-string 中含敏感变量名（tx_id/path/file_path/password/secret/token 等）时阻断 commit；tests/ 豁免（真源：commit_gate_registry.is_test_exempt）；in-process AST 分析无 subprocess；AST 解析失败/文件读取失败 fail-open（logger.warning）；行尾含 `# noqa: MSG-EXPOSURE` 注释的单行豁免
# [MODIFY-GUARD] gate_id="MSG-EXPOSURE"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——AST/IO 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_msg_exposure_gate.py
# [A_module] module_id=MOD-GOV-msg_exposure_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""msg_exposure_gate.py — 错误消息暴露敏感信息阻断门禁（MSG-EXPOSURE）

检测 staged .py 文件中 ``raise XxxError(f"...{sensitive_var}...")`` 模式——
异常消息 f-string 中插值了路径/tx_id/密钥/连接串等敏感变量，违反"敏感信息
应放入 details 字段而非消息文本"原则（5.99.20 治本）。

病根（第一性原理）
-----------------
100% AI 开发场景下，AI 生成异常时默认把上下文信息拼进消息（"调试方便"），
但训练数据里这种模式暴露了内部实现细节（文件路径/事务ID/参数名/密码）。
这些消息可能被记录到日志、返回前端、进入审计报告——信息泄露。

铁律：敏感信息走结构化 ``details`` 字段（dict），消息文本只保留人类可读摘要。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process，``--no-verify`` 绕不过）注册
门禁，AST 分析 staged .py 文件中所有 ``ast.Raise`` 节点：

  1. raise 的 exc 是 ``ast.Call``（构造异常实例）
  2. 构造函数名以 ``Error`` 或 ``Exception`` 结尾（自定义异常类）
  3. 第一个参数是 ``ast.JoinedStr``（f-string）
  4. f-string 的 ``FormattedValue`` 中引用了敏感变量名/属性

敏感变量分类
------------
- **路径类**：path/file_path/file/dir/target/draft/baseline/tmp_path/bak_path
- **标识类**：tx_id/transaction_id/event_id/session_id/user_id/task_id
- **凭据类**：password/passwd/secret/token/api_key/private_key/credential
- **连接类**：conn_str/connection_string/dsn/url/host/port
- **数据类**：sql/query/stmt/payload/body

设计权衡
--------
1. **只查 staged diff 新增行**：存量违规由 5.99.20 已修复，本 gate 防止新增违规。
   与 PERM-TRIGGER 一致，新增文件(A)查全文件 AST，修改文件(M)只查 diff 新增行。
2. **in-process AST**：纯 ast.parse + ast.walk，自包含无 subprocess。
3. **fail-open on AST error**：语法错误文件不阻断，由其他 gate 负责。
4. **行级豁免**：单行可用 ``# noqa: MSG-EXPOSURE`` 注释豁免（用于误报或合规的特殊情况）。
5. **priority=83**：在 PERM-TRIGGER(82) 之后、EMPTY-HANDLER(84) 之前。

Usage::

    from zephyr.governance.commit_gates.msg_exposure_gate import make_msg_exposure_gate

    registry.register(make_msg_exposure_gate())
"""

from __future__ import annotations

import ast
import logging
import os

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_msg_exposure_gate"]

# 敏感变量名清单（小写匹配，覆盖变量名 + 属性访问的 attr 名）
# 分类维护，便于后续扩展
_SENSITIVE_NAMES: frozenset[str] = frozenset({
    # 路径类
    "path", "file_path", "filepath", "file", "dir", "directory",
    "target", "draft", "baseline", "tmp_path", "bak_path", "backup_path",
    "src", "dst", "source", "destination", "filename", "fname",
    # 标识类
    "tx_id", "transaction_id", "event_id", "session_id", "user_id", "task_id",
    "request_id", "trace_id", "span_id",
    # 凭据类
    "password", "passwd", "pwd", "secret", "token", "api_key", "apikey",
    "private_key", "priv_key", "credential", "credentials", "auth_token",
    "access_token", "refresh_token",
    # 连接类
    "conn_str", "connection_string", "dsn", "url", "host", "port",
    "endpoint", "server", "database_url", "db_url",
    # 数据类
    "sql", "query", "stmt", "statement", "payload", "body", "content",
})

# 行级豁免标记（与 PERM-TRIGGER 一致的 noqa 风格）
_NOQA_MARKER = "noqa: MSG-EXPOSURE"


def _extract_name(node: ast.AST) -> str | None:
    """从 AST 节点提取标识符名称（Name.id / Attribute.attr / self.xxx 的 attr）。

    Returns:
        标识符名称（小写），无法提取时返回 None。
    """
    if isinstance(node, ast.Name):
        return node.id.lower()
    if isinstance(node, ast.Attribute):
        # self.path -> "path"；obj.file_path -> "file_path"
        return node.attr.lower()
    return None


def _f_string_has_sensitive_value(joined_str: ast.JoinedStr) -> tuple[bool, list[str]]:
    """检查 f-string 是否插值了敏感变量。

    Args:
        joined_str: ast.JoinedStr 节点（f-string）。

    Returns:
        (has_sensitive, sensitive_names) — 是否含敏感变量名 + 命中的变量名列表。
    """
    sensitive_hits: list[str] = []
    for value in joined_str.values:
        if not isinstance(value, ast.FormattedValue):
            continue
        # FormattedValue.value 可能是 Name / Attribute / Call / BinOp 等
        name = _extract_name(value.value)
        if name and name in _SENSITIVE_NAMES:
            sensitive_hits.append(name)
        # BinOp 处理：f"{a + b}" 这种少见情况，递归检查左右
        if isinstance(value.value, ast.BinOp):
            for sub in (value.value.left, value.value.right):
                sub_name = _extract_name(sub)
                if sub_name and sub_name in _SENSITIVE_NAMES:
                    sensitive_hits.append(sub_name)
        # Call 处理：f"{str(path)}" / f"{path!r}" 等
        if isinstance(value.value, ast.Call):
            call_name = _extract_name(value.value.func)
            if call_name == "str":
                inner_name = _extract_name(value.value.args[0]) if value.value.args else None
                if inner_name and inner_name in _SENSITIVE_NAMES:
                    sensitive_hits.append(inner_name)
    return (len(sensitive_hits) > 0, sensitive_hits)


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


def _detect_msg_exposure(tree: ast.AST) -> list[tuple[int, str, list[str]]]:
    """AST 中检测 raise 语句暴露敏感信息。

    Returns:
        违规列表 [(lineno, exception_name, [sensitive_var_names]), ...]
    """
    violations: list[tuple[int, str, list[str]]] = []
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
        # 第一个参数是消息（约定俗成），检查是否为 f-string
        if not call.args:
            continue  # 无参数构造（如 raise RuntimeError()）
        first_arg = call.args[0]
        if not isinstance(first_arg, ast.JoinedStr):
            continue  # 非 f-string（如 raise Foo("literal") 或 raise Foo(variable)）
        has_sensitive, hits = _f_string_has_sensitive_value(first_arg)
        if has_sensitive:
            exc_name = ""
            if isinstance(call.func, ast.Name):
                exc_name = call.func.id
            elif isinstance(call.func, ast.Attribute):
                exc_name = call.func.attr
            violations.append((node.lineno, exc_name, hits))
    return violations


def _is_line_noqa(content: str, lineno: int) -> bool:
    """检查指定行号是否含 noqa 豁免标记。

    Args:
        content: 文件完整文本。
        lineno: 1-based 行号。

    Returns:
        True 表示该行有 ``# noqa: MSG-EXPOSURE`` 标记。
    """
    lines = content.splitlines()
    if lineno < 1 or lineno > len(lines):
        return False
    return _NOQA_MARKER in lines[lineno - 1]


def _filter_noqa_violations(
    content: str,
    violations: list[tuple[int, str, list[str]]],
) -> list[tuple[int, str, list[str]]]:
    """过滤掉带 noqa 标记的违规行。"""
    return [v for v in violations if not _is_line_noqa(content, v[0])]


def make_msg_exposure_gate() -> GateSpec:
    """构造错误消息暴露敏感信息阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="MSG-EXPOSURE", priority=83)。
        priority=83——在 PERM-TRIGGER(82) 之后、EMPTY-HANDLER(84) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged 新增(A) + 修改(M) .py 文件
        try:
            diff_result = gateway._run_git(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"]
            )
            if diff_result.returncode != 0:
                logger.warning(
                    "MSG-EXPOSURE gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                    diff_result.returncode,
                )
                return True, ""
            staged_files = diff_result.stdout.strip().splitlines()
        except Exception as e:
            logger.warning(
                "MSG-EXPOSURE gate fail-open: git diff 异常(%s: %s)，检测器失效。",
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

        # 5. 门禁文件自豁免：检测器本身含敏感变量名字符串（非真实暴露）
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
                    "MSG-EXPOSURE gate skip file %s: 读取失败(%s: %s)。",
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
                        "MSG-EXPOSURE gate skip file %s: AST 解析失败(%s: %s)，检测器失效。",
                        abs_path, type(e).__name__, e,
                    )
                    continue
                violations = _detect_msg_exposure(tree)
                violations = _filter_noqa_violations(content, violations)
                for lineno, exc_name, hits in violations:
                    violations_all.append(
                        f"{rel_path}:{lineno} raise {exc_name}(f\"...{{{hits[0]}}}...\") "
                        f"[sensitive: {', '.join(hits)}]"
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
                # 检查新增行是否含 noqa 标记
                added_content_map = {ln: lc for ln, lc in added_lines_meta}

                try:
                    tree = ast.parse(content, filename=abs_path)
                except SyntaxError:
                    continue

                violations = _detect_msg_exposure(tree)
                for lineno, exc_name, hits in violations:
                    if lineno not in added_line_nos:
                        continue  # 只关心 diff 新增行
                    # 行级 noqa 豁免
                    line_content = added_content_map.get(lineno, "")
                    if _NOQA_MARKER in line_content:
                        continue
                    violations_all.append(
                        f"{rel_path}:{lineno} raise {exc_name}(f\"...{{{hits[0]}}}...\") "
                        f"[sensitive: {', '.join(hits)}] (modified)"
                    )

        if violations_all:
            detail = "; ".join(violations_all[:5])
            return False, (
                f"错误消息暴露敏感信息（路径/tx_id/凭据/连接串等应放入 details 字段而非消息文本，"
                f"5.99.20 治本）: {detail}"
            )
        return True, ""

    return GateSpec(gate_id="MSG-EXPOSURE", check=_check, priority=83)
