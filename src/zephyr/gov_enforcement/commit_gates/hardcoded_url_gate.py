# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.hardcoded_url_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py 文件 added 行含 http://localhost: 字面量时阻断 commit（passed=False）；shared/foundation/constants.py 豁免（SSoT 定义位置）；tests/ 豁免；import/注释/docstring 豁免；git diff 不可达 fail-open（logger.warning）；检出违规则 fail-closed（passed=False）
# [MODIFY-GUARD] gate_id="NO-HARDCODED-URL"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_hardcoded_url_gate.py
# [A_module] module_id=MOD-GOV-hardcoded_url_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""hardcoded_url_gate.py — 硬编码 localhost URL 阻断门禁（NO-HARDCODED-URL，§5.160.9 防复发）

检测 staged .py 文件 added 行中的 ``http://localhost:`` / ``https://localhost:``
字面量——违反 DEFAULT_OLLAMA_URL SSoT 原则（§5.160.9），应改用
``from zephyr.shared.foundation.constants import DEFAULT_OLLAMA_URL``。

病根（第一性原理）
-----------------
architecture_debt §5.160.9：DEFAULT_OLLAMA_URL 原在 3 处重复定义，6 文件硬编码
``http://localhost:11434``。修复方式是集中到 shared/foundation/constants.py SSoT。
但新 AI 仍可能写新的硬编码 URL——本 gate 在 commit 阶段硬阻断。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified .py 文件
  2. 过滤 tests/ 豁免
  3. 对每个文件解析 diff，检查 added 行是否含 ``http://localhost:``
  4. 豁免 import/注释/docstring 行
  5. 豁免 shared/foundation/constants.py（SSoT 定义位置）
  6. 命中 -> 硬阻断

设计权衡
--------
1. **只检测 added 行**：存量硬编码由人工排查，gate 只防新增。
2. **豁免 constants.py**：SSoT 定义位置必须有 ``http://localhost:11434``
   作为 default value，这是合法的。
3. **正则匹配**：``https?://localhost:`` 同时覆盖 http 和 https。
4. **diff-based 检测**：使用 _diff_helpers 共享工具，与
   datetime_now_forbidden_gate 一致的检测模式。
5. **priority=94**：在 NO-UPWARD-IMPORT(93) 之后。

Usage::

    from zephyr.gov_enforcement.commit_gates.hardcoded_url_gate import make_hardcoded_url_gate

    registry.register(make_hardcoded_url_gate())
"""

from __future__ import annotations

import logging
import re

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _extract_docstring_lines,
    _is_exempt_line,
    _parse_diff_with_line_numbers,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_hardcoded_url_gate"]

# SSoT 定义文件豁免（DEFAULT_OLLAMA_URL 的 default value 必须有硬编码 URL）
_SSoT_EXEMPT_FILE = "src/zephyr/shared/foundation/constants.py"

# 匹配 http://localhost: 或 https://localhost:
_HARDCODED_LOCALHOST_RE = re.compile(r"https?://localhost:")


def _collect_staged_py_files(gateway):
    # 1. 获取 staged added/modified .py 文件
    try:
        diff_result = gateway._run_git(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"]
        )
        if diff_result.returncode != 0:
            logger.warning(
                "NO-HARDCODED-URL gate fail-open: git diff 失败(rc=%d)。",
                diff_result.returncode,
            )
            return None
        staged = [f.replace("\\", "/") for f in diff_result.stdout.strip().splitlines() if f]
    except Exception as e:
        logger.warning(
            "NO-HARDCODED-URL gate fail-open: git diff 异常(%s: %s)。",
            type(e).__name__, e, exc_info=True,
        )
        return None

    # 2. 过滤 .py 文件 + tests/ 豁免 + SSoT 豁免
    py_files = [
        f for f in staged
        if f.endswith(".py")
        and not is_test_exempt(f)
        and f != _SSoT_EXEMPT_FILE
    ]
    return py_files


def _scan_file_violations(gateway, py_file):
    # 3a. 读取 staged 完整文件，预计算 docstring 行号集合
    file_content = _read_staged_file(gateway, py_file)
    docstring_lines = _extract_docstring_lines(file_content) if file_content else set()

    # 3b. 解析 diff，获取 added 行及行号
    try:
        file_diff = gateway._run_git(
            ["git", "diff", "--cached", "--unified=0", "--", py_file]
        )
    except Exception as e:
        logger.warning("NO-HARDCODED-URL gate: git diff 失败 file=%s, %s", py_file, e)
        return []
    if file_diff.returncode != 0:
        return []

    added_lines = _parse_diff_with_line_numbers(file_diff.stdout)
    violations = []
    for line_no, content in added_lines:
        # 豁免：docstring 内的行
        if line_no in docstring_lines:
            continue
        # 豁免：注释 / import
        if _is_exempt_line(content):
            continue
        if _HARDCODED_LOCALHOST_RE.search(content):
            violations.append(
                f"  {py_file}:{line_no}: {content.strip()}"
            )
    return violations


def make_hardcoded_url_gate() -> GateSpec:
    """构造硬编码 localhost URL 阻断 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="NO-HARDCODED-URL", priority=94)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = _collect_staged_py_files(gateway)
        if not py_files:
            return True, ""

        # 3. 检测每个文件的 added 行
        violations: list[str] = []
        for py_file in py_files:
            violations.extend(_scan_file_violations(gateway, py_file))

        # 4. 硬阻断
        if violations:
            detail = (
                "NO-HARDCODED-URL：检测到硬编码 localhost URL，\n"
                "  违反 §5.160.9 DEFAULT_OLLAMA_URL SSoT 原则。\n"
                + "\n".join(violations)
                + "\n-> 改用 from zephyr.shared.foundation.constants import DEFAULT_OLLAMA_URL"
            )
            logger.error("NO-HARDCODED-URL gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(gate_id="NO-HARDCODED-URL", check=_check, priority=94)
