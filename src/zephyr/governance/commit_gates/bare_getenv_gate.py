# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.bare_getenv_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.shared.security.secrets (SECRET_INDICATOR_PATTERNS)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 硬阻断——staged 新增 .py 文件含裸 os.getenv/os.environ.get/os.environ["KEY"] 读取密钥类变量时阻断 commit（passed=False）；tests/ 豁免（真源：commit_gate_registry.is_test_exempt）；只检测新增文件（diff-filter=A），不触碰存量基线；检测模式真源=SECRET_INDICATOR_PATTERNS（zephyr.shared.security.secrets SSoT），不硬编码；只检测字符串字面量参数（变量参数不检测，因 secrets.py SSoT 自身用 os.environ.get(key) 变量参数）；AST/subprocess 异常 fail-open（logger.warning）
# [MODIFY-GUARD] gate_id="NO-BARE-GETENV"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——AST/git 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_bare_getenv_gate.py
# [A_module] module_id=MOD-GOV-bare_getenv_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""bare_getenv_gate.py — 裸 os.getenv 读密钥阻断门禁（NO-BARE-GETENV，§5.17.10 治本）

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
3. **只检测新增文件**：存量违规已清零（§5.17.10 FIXED），本 gate 防止新增违规。
   若检测修改文件，AI 改个注释也触发全文件扫描，增加误阻断风险。
4. **fail-open on AST error**：语法错误文件不阻断（由其他 gate 管语法）。
5. **priority=81**：在 VOCAB-HARDCODE(80) 之后、PERM-TRIGGER(82) 之前。

Usage::

    from zephyr.governance.commit_gates.bare_getenv_gate import make_bare_getenv_gate

    registry.register(make_bare_getenv_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import ast
import logging
import os

from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt
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


def make_bare_getenv_gate() -> GateSpec:
    """构造裸 os.getenv 读密钥阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="NO-BARE-GETENV", priority=81)。
        priority=81——在 VOCAB-HARDCODE(80) 之后、PERM-TRIGGER(82) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged 新增 .py 文件
        try:
            diff_result = gateway._run_git(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=A"]
            )
            if diff_result.returncode != 0:
                logger.warning(
                    "NO-BARE-GETENV gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                    diff_result.returncode,
                )
                return True, ""
            staged_new = diff_result.stdout.strip().splitlines()
        except Exception as e:
            logger.warning(
                "NO-BARE-GETENV gate fail-open: git diff 异常(%s: %s)，检测器失效。",
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

        # 5. AST 检测
        all_violations: list[str] = []
        for abs_path in abs_files:
            try:
                content = open(abs_path, "r", encoding="utf-8", errors="replace").read()
            except OSError as e:
                logger.warning(
                    "NO-BARE-GETENV gate skip file %s: 读取失败(%s: %s)。",
                    abs_path, type(e).__name__, e,
                )
                continue

            try:
                tree = ast.parse(content, filename=abs_path)
            except SyntaxError as e:
                logger.warning(
                    "NO-BARE-GETENV gate skip file %s: AST 解析失败(%s: %s)，检测器失效。",
                    abs_path, type(e).__name__, e,
                )
                continue

            visitor = _BareGetenvVisitor()
            visitor.visit(tree)

            if visitor.violations:
                rel_name = os.path.relpath(abs_path, wt_root).replace("\\", "/")
                for lineno, pattern, key in visitor.violations:
                    all_violations.append(
                        f"{rel_name}:{lineno} {pattern}(\"{key}\") "
                        f"—— 应改用 get_secret/get_secret_or_default（SecretProvider SSoT）"
                    )

        if all_violations:
            detail = "; ".join(all_violations[:5])
            return False, f"裸 os.getenv/os.environ 读密钥（§5.17.10）: {detail}"
        return True, ""

    return GateSpec(gate_id="NO-BARE-GETENV", check=_check, priority=81)
