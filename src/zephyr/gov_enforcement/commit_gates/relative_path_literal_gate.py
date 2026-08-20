# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.relative_path_literal_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.gov_enforcement.commit_gates._diff_helpers (_extract_docstring_lines, _is_exempt_line, _parse_diff_with_line_numbers, _read_staged_file)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py 文件 added 行含字符串字面量 "./" / "../" / "~/" 开头的相对路径时阻断 commit（豁免 Path(__file__) 上下文/import/注释/docstring）；tests/ 豁免；git diff 不可达 fail-open；检出违规则 fail-closed（passed=False）
# [MODIFY-GUARD] gate_id="RELATIVE-PATH-LITERAL"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
r"""relative_path_literal_gate.py — 相对路径字面量硬阻断门禁（RELATIVE-PATH-LITERAL）

补强 DIRECTORY-CONTRACT-GATE（目录区约束）和 HARDCODED-URL（URL 硬编码）的盲区——
代码内字符串字面量中的相对路径（"./" / "../" / "~/"）违反"所有路径必须使用绝对路径"
铁律（AGENTS.md 硬约束）。

病根（第一性原理）
-----------------
12 维度审计 §7.5"绝对路径"痛点：手工审反复发现代码内 ``open("./config.yaml")``
这类相对路径字面量。相对路径依赖 cwd，AI 在不同目录运行会解析到不同文件——
幻觉/漂移根源。AGENTS.md 硬约束要求"所有路径必须使用绝对路径"。

DIRECTORY-CONTRACT-GATE 管目录区，HARDCODED-URL 管 URL，但代码内相对路径字面量
无门禁覆盖。需要独立 gate。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified .py 文件
  2. 过滤 tests/ 豁免
  3. 对每个文件解析 diff，检查 added 行是否含字符串字面量中的相对路径
  4. 豁免 import/注释/docstring 行
  5. 豁免 Path(__file__) 上下文（合法的相对基准用法）
  6. 命中 -> 硬阻断

设计权衡
--------
1. **diff-based 检测**：与 HARDCODED-URL 一致的检测模式，复用 _diff_helpers。
2. **正则匹配引号后的相对路径**：``(["\'])(\.\./|\./|~/)`` 精确匹配字符串字面量。
3. **豁免 __file__ 上下文**：``Path(__file__).parent / "config.yaml"`` 是合法的
   相对基准用法，不阻断。检测当前行或前一行含 ``__file__`` 即豁免。
4. **priority=115**：在 DERIVATION-ANNOTATION(114) 之后。
5. **fail-open on diff error**：git diff 失败不阻断（避免误伤）。

Usage::

    from zephyr.gov_enforcement.commit_gates.relative_path_literal_gate import (
        make_relative_path_literal_gate,
    )

    registry.register(make_relative_path_literal_gate())
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
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    GateSpec,
    is_test_exempt,
)

logger = logging.getLogger(__name__)

__all__ = ["make_relative_path_literal_gate"]

# 匹配字符串字面量中的相对路径：引号后跟 ../  ./  ~/
# 捕获组1=引号，捕获组2=相对路径前缀
_RELATIVE_PATH_RE = re.compile(r'(["\'])(\.\./|\./|~/)')

# __file__ 上下文豁免标记——当前行含 __file__ 视为合法相对基准
_FILE_MARKER = "__file__"


def _collect_staged_py_files(gateway) -> list[str] | None:
    """获取 staged added/modified .py 文件列表（tests/ 豁免）。

    Returns:
        相对路径列表；git diff 失败/异常返回 None（fail-open）。
    """
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
        if diff_result.returncode != 0:
            logger.warning(
                "RELATIVE-PATH-LITERAL gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                diff_result.returncode,
            )
            return None
        result: list[str] = []
        for line in diff_result.stdout.strip().splitlines():
            if not line.strip():
                continue
            fp = line.strip().replace("\\", "/")
            if not fp.endswith(".py"):
                continue
            if is_test_exempt(fp):
                continue
            result.append(fp)
        return result
    except Exception as e:  # noqa: BLE001 — fail-open 不阻断
        logger.warning(
            "RELATIVE-PATH-LITERAL gate fail-open: git diff 异常(%s: %s)，检测器失效。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None


def _scan_file_violations(gateway, py_file: str) -> list[str]:
    """扫描单个文件的相对路径字面量违规。

    返回违规消息列表（每条违规一行）。
    """
    # 读取 staged 完整文件，预计算 docstring 行号集合
    file_content = _read_staged_file(gateway, py_file)
    docstring_lines = _extract_docstring_lines(file_content) if file_content else set()

    # 解析 diff，获取 added 行及行号
    try:
        file_diff = gateway.run_git(["git", "diff", "--cached", "--unified=0", "--ignore-cr-at-eol", "--", py_file])
    except Exception as e:  # noqa: BLE001 — fail-open 不阻断
        logger.warning("RELATIVE-PATH-LITERAL gate: git diff 失败 file=%s, %s", py_file, e)
        return []
    if file_diff.returncode != 0:
        return []

    added_lines = _parse_diff_with_line_numbers(file_diff.stdout)
    violations: list[str] = []
    for line_no, content in added_lines:
        # 豁免：docstring 内的行
        if line_no in docstring_lines:
            continue
        # 豁免：注释 / import
        if _is_exempt_line(content):
            continue
        # 豁免：__file__ 上下文（合法相对基准）
        if _FILE_MARKER in content:
            continue
        # 检测相对路径字面量
        if _RELATIVE_PATH_RE.search(content):
            violations.append(f"  {py_file}:{line_no}: {content.strip()}")

    return violations


def make_relative_path_literal_gate() -> GateSpec:
    """构造相对路径字面量硬阻断 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="RELATIVE-PATH-LITERAL", priority=115)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = _collect_staged_py_files(gateway)
        if not py_files:
            return True, ""

        violations: list[str] = []
        for py_file in py_files:
            violations.extend(_scan_file_violations(gateway, py_file))

        if violations:
            detail = (
                "RELATIVE-PATH-LITERAL：检测到代码内相对路径字面量，\n"
                "  违反 AGENTS.md 硬约束'所有路径必须使用绝对路径'。\n"
                + "\n".join(violations)
                + "\n-> 改用 REPO_ROOT / Path(__file__).resolve().parent 拼接绝对路径"
            )
            logger.error("RELATIVE-PATH-LITERAL gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(gate_id="RELATIVE-PATH-LITERAL", check=_check, priority=115)
