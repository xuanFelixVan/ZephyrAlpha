# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.datetime_now_forbidden_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged 生成器代码(.py)新增行含 datetime.now() 调用时阻断 commit（passed=False）；生成器判定：路径含 /generators/ 或文件名以 generate_ 开头；tests/ 豁免；import/注释/docstring 豁免；非生成器文件豁免；YAML/git diff 不可达 fail-open（logger.warning 检测器失效）；检出违规则 fail-closed 阻断（passed=False）
# [MODIFY-GUARD] gate_id="DATETIME-NOW-FORBIDDEN"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_datetime_now_forbidden_gate.py
# [A_module] module_id=MOD-GOV-datetime_now_forbidden_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""datetime_now_forbidden_gate.py — 生成器代码 datetime.now() 硬阻断门禁（DATETIME-NOW-FORBIDDEN）

检测 staged 生成器代码（.py）新增行中的 ``datetime.now()`` 调用——
违反 AGENTS.md §11.1.1 时间戳约定（生成器输出必须幂等，禁止实时时间源）。

病根（AGENTS.md §11.1.1）
--------------------------
生成器中使用 ``datetime.now()`` 会导致每次运行输出不同的时间戳，
产生非幂等噪音 auto-commit——修改 depgraph (PostgreSQL) 后重生文档时，
即使数据无变化也会因时间戳变化触发 auto-commit，污染 git 历史。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified .py 文件
  2. 过滤到生成器文件（路径含 /generators/ 或文件名以 generate_ 开头）
  3. 解析 diff，检查 added 行中是否含 ``datetime.now(`` 调用
  4. 豁免 import/注释/docstring 行
  5. 命中 -> 硬阻断（passed=False）

设计权衡
--------
1. **只检测生成器文件**：非生成器代码（如运行时服务）使用 ``datetime.now()``
   是合法的。生成器判定：路径含 ``/generators/`` 或文件名以 ``generate_`` 开头。
2. **只检测 added 行**：存量 ``datetime.now()`` 由人工检测命令排查（§11.1.1），
   gate 只防止新增违规。对修改文件，只检查 diff 中的 added 行。
3. **正则匹配**：``datetime\\.now\\s*\\(`` 同时覆盖 ``datetime.now()``
   和 ``datetime.datetime.now()``（正则引擎在后者中匹配第二个 ``datetime``）。
4. **fail-open on git error**：git diff 失败时不阻断（由其他 gate 管完整性）。
5. **priority=34**：在 FILE-PLACEMENT-TTL(33) 之后、R5-DIGIT-SUFFIX(35) 之前，
   与文件放置/TTL 组同组（生成器代码质量检测）。
6. **hard-block 而非 warn**：``datetime.now()`` 在生成器中是确定性违规
   （违反 §11.1.1），不是疑似风险，应硬阻断。

Usage::

    from zephyr.gov_enforcement.commit_gates.datetime_now_forbidden_gate import make_datetime_now_forbidden_gate

    registry.register(make_datetime_now_forbidden_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
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

__all__ = ["make_datetime_now_forbidden_gate"]

# 生成器文件判定：路径含 /generators/ 或文件名以 generate_ 开头
_GENERATORS_DIR_PART = "/generators/"
_GENERATOR_FILE_PREFIX = "generate_"

# 匹配 datetime.now( —— 同时覆盖 datetime.now() 和 datetime.datetime.now()
# （正则引擎在 "datetime.datetime.now()" 中匹配第二个 "datetime.now("）
_DATETIME_NOW_RE = re.compile(r"datetime\.now\s*\(")


def _is_generator_file(py_file: str) -> bool:
    """判定 .py 文件是否为生成器代码。

    判定规则：
    1. 路径含 ``/generators/``（如 ``scripts/governance/d5_architecture/generators/``）
    2. 文件名以 ``generate_`` 开头（如 ``generate_project_depgraph.py``）

    Args:
        py_file: 相对路径（/ 或 \\ 分隔）。

    Returns:
        True 如果是生成器文件。
    """
    normalized = py_file.replace("\\", "/")
    if _GENERATORS_DIR_PART in normalized:
        return True
    basename = normalized.rsplit("/", 1)[-1]
    return basename.startswith(_GENERATOR_FILE_PREFIX)


def make_datetime_now_forbidden_gate() -> GateSpec:
    """构造生成器代码 ``datetime.now()`` 硬阻断 GateSpec。

    Returns:
        GateSpec(gate_id="DATETIME-NOW-FORBIDDEN", priority=34)。
        priority=34——在 FILE-PLACEMENT-TTL(33) 之后、R5-DIGIT-SUFFIX(35) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged added/modified .py 文件
        try:
            diff_result = gateway._run_git(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"]
            )
            if diff_result.returncode != 0:
                logger.warning(
                    "DATETIME-NOW-FORBIDDEN gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                    diff_result.returncode,
                )
                return True, ""
            staged = [f.replace("\\", "/") for f in diff_result.stdout.strip().splitlines() if f]
        except Exception as e:
            logger.warning(
                "DATETIME-NOW-FORBIDDEN gate fail-open: git diff 异常(%s: %s)，检测器失效。",
                type(e).__name__, e, exc_info=True
            )
            return True, ""

        # 2. 过滤到生成器 .py 文件 + tests/ 豁免
        gen_files = [
            f for f in staged
            if f.endswith(".py")
            and not is_test_exempt(f)
            and _is_generator_file(f)
        ]
        if not gen_files:
            return True, ""

        # 3. 检测每个生成器文件的 added 行
        violations: list[str] = []
        for py_file in gen_files:
            # 3a. 读取 staged 完整文件，预计算 docstring 行号集合（豁免 docstring）
            file_content = _read_staged_file(gateway, py_file)
            docstring_lines = _extract_docstring_lines(file_content) if file_content else set()

            # 3b. 解析 diff，获取 added 行及行号
            try:
                file_diff = gateway._run_git(
                    ["git", "diff", "--cached", "--unified=0", "--", py_file]
                )
            except Exception as e:
                logger.warning(
                    "DATETIME-NOW-FORBIDDEN gate: git diff 失败 file=%s, %s",
                    py_file, e, exc_info=True,
                )
                continue
            if file_diff.returncode != 0:
                continue

            added_lines = _parse_diff_with_line_numbers(file_diff.stdout)
            for line_no, content in added_lines:
                # 豁免：docstring 内的行
                if line_no in docstring_lines:
                    continue
                # 豁免：注释 / import
                if _is_exempt_line(content):
                    continue
                if _DATETIME_NOW_RE.search(content):
                    violations.append(
                        f"  {py_file}:{line_no}: datetime.now() 调用 -> {content.strip()}"
                    )

        # 4. 硬阻断：检出违规则 fail-closed
        if violations:
            detail = (
                "DATETIME-NOW-FORBIDDEN：生成器代码中检测到 datetime.now() 调用，\n"
                "  违反 AGENTS.md §11.1.1 时间戳约定（生成器输出必须幂等，禁止实时时间源）。\n"
                + "\n".join(violations)
                + "\n-> 移除 datetime.now() 调用，改用 git log 时间戳或固定占位符。"
            )
            logger.error("DATETIME-NOW-FORBIDDEN gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(gate_id="DATETIME-NOW-FORBIDDEN", check=_check, priority=34)
