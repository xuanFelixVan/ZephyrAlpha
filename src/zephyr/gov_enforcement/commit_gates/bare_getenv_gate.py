# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.bare_getenv_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.shared.security.secrets (SECRET_INDICATOR_PATTERNS)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged 新增+修改 .py 文件含裸 os.getenv/os.environ.get/os.environ["KEY"] 读取密钥类变量时阻断 commit（passed=False）；tests/ 豁免（真源：commit_gate_registry.is_test_exempt）；新增文件（diff-filter=A）全文件 AST 扫描；修改文件（diff-filter=M）只检测 git diff 新增行中的违规（diff-aware，不触碰存量基线）；检测模式真源=SECRET_INDICATOR_PATTERNS（zephyr.shared.security.secrets SSoT），不硬编码；只检测字符串字面量参数（变量参数不检测，因 secrets.py SSoT 自身用 os.environ.get(key) 变量参数）；AST/subprocess/git diff 异常 fail-open（logger.warning）
# [MODIFY-GUARD] gate_id="NO-BARE-GETENV"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——AST/git 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_bare_getenv_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
bare_getenv_gate.py — 裸 os.getenv 读密钥阻断门禁（NO-BARE-GETENV，§5.17.10 治本）

检测 staged 新增 .py 文件中是否用裸 os.getenv / os.environ.get / os.environ["KEY"]
读取密钥类变量——违反 SecretProvider SSoT 原则，应改用 get_secret / get_secret_or_default。

病根（第一性原理）
-----------------
architecture_debt §5.17.10：AI 在 10 个模块里写 10 种 os.getenv("API_KEY")，
绕过 SecretProvider 真源——不可审计、不可切换 backend、无 sanitization。
迁移完成后存量已清零，但新 AI 仍可能写新的裸 getenv——本 gate 在 commit
阶段硬阻断，防止债务复发。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. AST 解析 staged 新增 .py 文件
  2. 遍历 Call 节点，检测 os.getenv("...") / os.environ.get("...") 调用
  3. 遍历 Subscript 节点，检测 os.environ["..."] 访问
  4. 提取字符串字面量参数，检查是否含 SECRET_INDICATOR_PATTERNS 中的模式
  5. 匹配 -> 违规（应改用 get_secret / get_secret_or_default）

设计权衡
--------
1. **只检测字符串字面量参数**：secrets.py SSoT 自身用 os.environ.get(key)
   变量参数读取，不检测变量参数避免误伤 SSoT 实现。
2. **检测模式真源=SECRET_INDICATOR_PATTERNS**：从 secrets.py import，不硬编码，
   模式变更（如新增 "CREDENTIAL"）自动同步到本 gate。
3. **diff-aware 修改文件检测**（#ARCH-SECRETS-GOV-001 Phase 2-S3 增强）：
   新增文件（A）全文件 AST 扫描；修改文件（M）只检测 git diff 新增行中的违规
   （不触碰存量基线）。原只检测新增文件（diff-filter=A），AI 在现有文件中添加
   裸 getenv 无法被发现。增强为 diff-filter=AM + 新增行过滤，既防止存量违规
   逍遥法外，又避免对修改文件全文件扫描的误阻断。
4. **fail-open on AST error**：语法错误文件不阻断（由其他 gate 管语法）。
5. **priority=81**：在 VOCAB-HARDCODE(80) 之后、PERM-TRIGGER(82) 之前。

Usage::

    from zephyr.gov_enforcement.commit_gates.bare_getenv_gate import make_bare_getenv_gate

    registry.register(make_bare_getenv_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: bare_getenv_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① make_bare_getenv_gate
#   name_en: make_bare_getenv_gate
#   intro: 构造裸 os.getenv 读密钥阻断门禁 GateSpec（硬阻断型）。
#   desc: 构造裸 os.getenv 读密钥阻断门禁 GateSpec（硬阻断型）。 Returns: GateSpec(gate_id="NO-BARE-GETENV", priorit…；源码 L345-L394
#   inputs: 无参数
#   outputs: GateSpec
# 层: 输出
# - id: O1
#   name_zh: GateSpec
#   name_en: GateSpec
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import ast
import logging
import os
import re

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt
from zephyr.shared.security.secrets import SECRET_INDICATOR_PATTERNS

logger = logging.getLogger(__name__)

__all__ = ["make_bare_getenv_gate"]


class _BareGetenvVisitor(ast.NodeVisitor):
    """AST visitor——检测裸 os.getenv/os.environ.get/os.environ["KEY"] 读密钥。

    只检测字符串字面量参数（变量参数不检测，因 SSoT 实现用变量参数）。
    """

    def __init__(self) -> None:
        self.violations: list[tuple[int, str, str]] = []  # (lineno, call_pattern, key)

    def _is_secret_key(self, key: str) -> bool:
        """检查 key 是否匹配 SECRET_INDICATOR_PATTERNS（大小写不敏感）。"""
        key_upper = key.upper()
        return any(pattern in key_upper for pattern in SECRET_INDICATOR_PATTERNS)

    def _extract_string_arg(self, call: ast.Call) -> str | None:
        """提取 Call 的第一个参数（仅当是字符串字面量）。"""
        if not call.args:
            return None
        first = call.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value
        return None

    def _is_os_getenv(self, call: ast.Call) -> bool:
        """检测 os.getenv(...) 调用。"""
        func = call.func
        # os.getenv(...)
        if isinstance(func, ast.Attribute) and func.attr == "getenv":
            if isinstance(func.value, ast.Name) and func.value.id == "os":
                return True
        return False

    def _is_os_environ_get(self, call: ast.Call) -> bool:
        """检测 os.environ.get(...) 调用。"""
        func = call.func
        if isinstance(func, ast.Attribute) and func.attr == "get":
            # os.environ.get(...)
            if isinstance(func.value, ast.Attribute) and func.value.attr == "environ":
                if isinstance(func.value.value, ast.Name) and func.value.value.id == "os":
                    return True
        return False

    def visit_Call(self, node: ast.Call) -> None:
        # 检测 os.getenv("KEY") 和 os.environ.get("KEY")
        if self._is_os_getenv(node) or self._is_os_environ_get(node):
            key = self._extract_string_arg(node)
            if key is not None and self._is_secret_key(key):
                pattern = "os.getenv" if self._is_os_getenv(node) else "os.environ.get"
                self.violations.append((node.lineno, pattern, key))
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        """检测 os.environ["KEY"] 访问。"""
        # os.environ[...]
        value = node.value
        if isinstance(value, ast.Attribute) and value.attr == "environ":
            if isinstance(value.value, ast.Name) and value.value.id == "os":
                # 提取下标
                slice_node = node.slice
                # Python 3.9+ 直接是表达式；3.8 是 ast.Index
                if isinstance(slice_node, ast.Index):  # pragma: no cover
                    slice_node = slice_node.value
                if isinstance(slice_node, ast.Constant) and isinstance(slice_node.value, str):
                    key = slice_node.value
                    if self._is_secret_key(key):
                        self.violations.append((node.lineno, 'os.environ["..."]', key))
        self.generic_visit(node)


def _get_staged_py_files(gateway) -> tuple[list[str], list[str]] | None:
    """获取 staged 新增+修改的 .py 文件列表（git diff --cached --diff-filter=AM）。

    diff-aware 增强（#ARCH-SECRETS-GOV-001 Phase 2-S3）：原只获取新增文件
    （--diff-filter=A），现扩展为新增+修改（--diff-filter=AM），修改文件
    只检测新增行中的违规（由 _get_added_line_numbers + _collect_violations 过滤）。

    Returns:
        (added_py_files, modified_py_files) 或 None（fail-open）。
        列表中的路径已归一化为正斜杠，已过滤 tests/ 豁免。
    """
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-status", "--diff-filter=AM"])
        if diff_result.returncode != 0:
            logger.warning(
                "NO-BARE-GETENV gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                diff_result.returncode,
            )
            return None
        added: list[str] = []
        modified: list[str] = []
        for line in diff_result.stdout.strip().splitlines():
            if not line:
                continue
            parts = line.split("\t", 1)
            if len(parts) != 2:
                continue
            status, path = parts
            path = path.replace("\\", "/").strip()
            if not path.endswith(".py"):
                continue
            if is_test_exempt(path):
                continue
            if status == "A":
                added.append(path)
            elif status == "M":
                modified.append(path)
        return added, modified
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "NO-BARE-GETENV gate fail-open: git diff 异常(%s: %s)，检测器失效。", type(e).__name__, e, exc_info=True
        )
        return None


def _get_added_line_numbers(gateway, file_path: str) -> set[int] | None:
    """获取修改文件的新增行号集合（git diff --cached -U0）。

    解析 ``@@ -old_start,old_count +new_start,new_count @@`` 行，遍历 diff
    内容行，收集 ``+`` 开头的新增行在文件中的行号。

    用于 diff-aware 检测：修改文件 AST 扫描后，只保留行号在此集合中的违规，
    避免对存量代码的误报。

    Returns:
        新增行号集合；None 表示 fail-open（git 失败/异常，该文件跳过检测）。
    """
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "-U0", "--", file_path])
        if diff_result.returncode != 0:
            logger.warning(
                "NO-BARE-GETENV gate: git diff -U0 失败 for %s(rc=%d)，该修改文件跳过 diff-aware 检测（fail-open）。",
                file_path,
                diff_result.returncode,
            )
            return None
        added_lines: set[int] = set()
        new_line = 0
        for line in diff_result.stdout.splitlines():
            if line.startswith("@@"):
                m = re.search(r"\+(\d+)(?:,(\d+))?", line)
                if m:
                    new_line = int(m.group(1))
                continue
            if line.startswith("+++") or line.startswith("---"):
                continue
            if line.startswith("+"):
                if new_line > 0:
                    added_lines.add(new_line)
                    new_line += 1
            elif line.startswith("-"):
                pass  # 删除行，new_line 不变
            else:
                new_line += 1  # context 行
        return added_lines
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "NO-BARE-GETENV gate: git diff -U0 异常 for %s(%s: %s)，该修改文件跳过 diff-aware 检测（fail-open）。",
            file_path,
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None


def _resolve_worktree_root(gateway) -> str:
    """解析 worktree 根目录（git rev-parse --show-toplevel），失败回退 project_root。"""
    try:
        toplevel_result = gateway.run_git(["git", "rev-parse", "--show-toplevel"])
        if toplevel_result.returncode == 0:
            return toplevel_result.stdout.strip()
        return str(gateway.project_root)
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return str(gateway.project_root)


def _resolve_abs_paths(new_py_files: list[str], wt_root: str) -> list[str]:
    """将相对路径解析为绝对路径，并过滤出实际存在的文件。"""
    abs_files: list[str] = []
    for rel in new_py_files:
        if os.path.isabs(rel):
            abs_files.append(rel)
        else:
            abs_files.append(os.path.join(wt_root, rel.replace("/", os.sep)))
    return [f for f in abs_files if os.path.isfile(f)]


def _collect_violations(
    abs_paths: list[str],
    wt_root: str,
    added_lines_map: dict[str, set[int]] | None = None,
) -> list[str]:
    """AST 扫描所有文件，收集裸 getenv/os.environ 读密钥违规描述列表。

    Args:
        abs_paths: 文件绝对路径列表。
        wt_root: worktree 根目录。
        added_lines_map: 修改文件的新增行号映射 {rel_path: {line_numbers}}。
            None 表示新增文件（报告所有违规）。
            非 None 时，只报告行号在对应集合中的违规（diff-aware 过滤）。
    """
    all_violations: list[str] = []
    for abs_path in abs_paths:
        try:
            with open(abs_path, encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError as e:
            logger.warning(
                "NO-BARE-GETENV gate skip file %s: 读取失败(%s: %s)。",
                abs_path,
                type(e).__name__,
                e,
            )
            continue

        try:
            tree = ast.parse(content, filename=abs_path)
        except SyntaxError as e:
            logger.warning(
                "NO-BARE-GETENV gate skip file %s: AST 解析失败(%s: %s)，检测器失效。",
                abs_path,
                type(e).__name__,
                e,
            )
            continue

        visitor = _BareGetenvVisitor()
        visitor.visit(tree)

        if visitor.violations:
            rel_name = os.path.relpath(abs_path, wt_root).replace("\\", "/")
            added_lines = added_lines_map.get(rel_name) if added_lines_map else None
            for lineno, pattern, key in visitor.violations:
                # diff-aware 过滤：修改文件只报告新增行中的违规
                if added_lines is not None and lineno not in added_lines:
                    continue
                all_violations.append(
                    f'{rel_name}:{lineno} {pattern}("{key}") '
                    f"—— 应改用 get_secret/get_secret_or_default（SecretProvider SSoT）"
                )
    return all_violations


def make_bare_getenv_gate() -> GateSpec:
    """构造裸 os.getenv 读密钥阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="NO-BARE-GETENV", priority=81)。
        priority=81——在 VOCAB-HARDCODE(80) 之后、PERM-TRIGGER(82) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged 新增+修改 .py 文件（fail-open on git 错误）
        result = _get_staged_py_files(gateway)
        if result is None:
            return True, ""
        added_files, modified_files = result
        if not added_files and not modified_files:
            return True, ""

        # 2. 获取 worktree root
        wt_root = _resolve_worktree_root(gateway)

        all_violations: list[str] = []

        # 3. 新增文件（A）：全文件 AST 扫描
        if added_files:
            added_abs = _resolve_abs_paths(added_files, wt_root)
            if added_abs:
                all_violations.extend(_collect_violations(added_abs, wt_root))

        # 4. 修改文件（M）：diff-aware 检测（只报告新增行中的违规）
        if modified_files:
            added_lines_map: dict[str, set[int]] = {}
            scannable_modified: list[str] = []
            for rel in modified_files:
                lines = _get_added_line_numbers(gateway, rel)
                if lines is not None:
                    added_lines_map[rel] = lines
                    scannable_modified.append(rel)
                # lines is None → fail-open，跳过该文件检测
            if scannable_modified:
                modified_abs = _resolve_abs_paths(scannable_modified, wt_root)
                if modified_abs:
                    all_violations.extend(_collect_violations(modified_abs, wt_root, added_lines_map))

        # 5. 汇总违规
        if all_violations:
            detail = "; ".join(all_violations[:5])
            return False, f"裸 os.getenv/os.environ 读密钥（§5.17.10）: {detail}"
        return True, ""

    return GateSpec(gate_id="NO-BARE-GETENV", check=_check, priority=81)
