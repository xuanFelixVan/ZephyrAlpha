# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.datetime_now_forbidden_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——两类检测面：①生成器代码(.py)新增行含 datetime.now() 任何形式调用时阻断（生成器输出必须幂等）；②src/zephyr/ 全量代码(.py)新增行含 time.time() 或 datetime.now() 无参数调用（naive datetime）时阻断（5.46 时区处理防复发）；tests/ 豁免；import/注释/docstring 豁免；# noqa: m46-time 豁免；YAML/git diff 不可达 fail-open（logger.warning 检测器失效）；检出违规则 fail-closed 阻断（passed=False）
# [MODIFY-GUARD] gate_id="DATETIME-NOW-FORBIDDEN"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_datetime_now_forbidden_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
r"""
datetime_now_forbidden_gate.py — 时间戳约定硬阻断门禁（DATETIME-NOW-FORBIDDEN）

检测 staged 代码（.py）新增行中的时间戳误用，覆盖两类场景：
  1. 生成器代码中 ``datetime.now()`` 任何形式（违反 AGENTS.md §11.1.1 生成器幂等约定）
  2. src/zephyr/ 全量代码中 ``time.time()`` 或 ``datetime.now()`` 无参数
     （违反 5.46 时区处理约定——应改用 ``now_utc()`` 或 ``datetime.now(UTC)``）

病根（5.46 时间与时区处理 + AGENTS.md §11.1.1）
------------------------------------------------
- 生成器中使用 ``datetime.now()`` 导致非幂等 auto-commit，污染 git 历史
- 运行时代码中 ``time.time()`` 用于 TTL 计算易引入时区漂移
- ``datetime.now()`` 无参数产生 naive datetime，与 aware datetime 混用 100+ 处

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified .py 文件
  2. 双轨过滤：生成器文件（路径含 /generators/ 或文件名以 generate_ 开头）
     + src/zephyr/ 文件
  3. 解析 diff，检查 added 行中的违规模式
  4. 豁免 import/注释/docstring 行 + noqa:m46-time 标记
  5. 命中 -> 硬阻断（passed=False）

设计权衡
--------
1. **双轨检测面**：生成器中 ``datetime.now()`` 任何形式都禁（非幂等）；
   src/zephyr/ 全量中只禁 ``time.time()`` 和 ``datetime.now()`` 无参数
   （运行时服务使用 ``datetime.now(UTC)`` 是合法的）。
2. **只检测 added 行**：存量违规由仪表盘 M02/M21 监控，gate 只防新增。
3. **正则匹配**：``datetime\.now\s*\(\s*\)`` 精确匹配无参数形式，
   ``time\.time\s*\(`` 匹配 ``time.time()`` 调用。
4. **fail-open on git error**：git diff 失败时不阻断（由其他 gate 管完整性）。
5. **priority=34**：在 FILE-PLACEMENT-TTL(33) 之后、R5-DIGIT-SUFFIX(35) 之前。
6. **hard-block**：时间戳误用是确定性违规，应硬阻断。
7. **noqa 豁免**：合法场景（如 benchmark 基准测试）可用 noqa:m46-time 标记豁免。

Usage::

    from zephyr.gov_enforcement.commit_gates.datetime_now_forbidden_gate import make_datetime_now_forbidden_gate

    registry.register(make_datetime_now_forbidden_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: datetime_now_forbidden_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① make_datetime_now_forbidden_gate
#   name_en: make_datetime_now_forbidden_gate
#   intro: 构造时间戳约定硬阻断 GateSpec（双轨检测面）。
#   desc: 构造时间戳约定硬阻断 GateSpec（双轨检测面）。 Returns: GateSpec(gate_id="DATETIME-NOW-FORBIDDEN", priority=…；源码 L263-L295
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

# src/zephyr/ 全量检测面前缀
_SRC_ZEPHYR_PREFIX = "src/zephyr/"

# noqa 豁免标记（MUST 在 noqa_exempt_registry.yaml 登记）
_NOQA_MARKER = "m46-time"

# 匹配 datetime.now( —— 同时覆盖 datetime.now() 和 datetime.datetime.now()
# （正则引擎在 "datetime.datetime.now()" 中匹配第二个 "datetime.now("）
_DATETIME_NOW_RE = re.compile(r"datetime\.now\s*\(")

# 匹配 datetime.now() 无参数（naive datetime）—— 精确匹配 () 内无内容
_DATETIME_NOW_NAIVE_RE = re.compile(r"datetime\.now\s*\(\s*\)")

# 匹配 time.time( —— 用于 TTL/时间戳计算
_TIME_TIME_RE = re.compile(r"\btime\.time\s*\(")


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


def _is_src_zephyr_file(py_file: str) -> bool:
    """判定 .py 文件是否在 src/zephyr/ 目录下（5.46 全量检测面）。

    Args:
        py_file: 相对路径（/ 或 \\ 分隔）。

    Returns:
        True 如果文件路径以 ``src/zephyr/`` 开头。
    """
    normalized = py_file.replace("\\", "/")
    return normalized.startswith(_SRC_ZEPHYR_PREFIX)


def _has_noqa_exempt(content: str) -> bool:
    """检查行是否含 ``# noqa: m46-time`` 豁免标记。"""
    return f"# noqa: {_NOQA_MARKER}" in content


def _get_staged_files(gateway) -> list[str] | None:
    # 获取 staged added/modified .py 文件；失败返回 None（fail-open）
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
        if diff_result.returncode != 0:
            logger.warning(
                "DATETIME-NOW-FORBIDDEN gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                diff_result.returncode,
            )
            return None
        return [f.replace("\\", "/") for f in diff_result.stdout.strip().splitlines() if f]
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "DATETIME-NOW-FORBIDDEN gate fail-open: git diff 异常(%s: %s)，检测器失效。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None


def _filter_target_py_files(staged: list[str]) -> list[str]:
    # 过滤到目标 .py 文件（生成器 OR src/zephyr/）+ tests/ 豁免
    return [
        f
        for f in staged
        if f.endswith(".py") and not is_test_exempt(f) and (_is_generator_file(f) or _is_src_zephyr_file(f))
    ]


def _scan_file_for_violations(gateway, py_file: str) -> list[str]:
    # 检测单个文件的 added 行，返回违规列表
    violations: list[str] = []
    # 3a. 读取 staged 完整文件，预计算 docstring 行号集合（豁免 docstring）
    file_content = _read_staged_file(gateway, py_file)
    docstring_lines = _extract_docstring_lines(file_content) if file_content else set()

    # 3b. 解析 diff，获取 added 行及行号
    # --ignore-cr-at-eol：EOL 规范化提交（CRLF→LF 机械翻转）全文件行伪"added"，
    # 会把存量违规误报为新增——按内容判定 added，行尾差异不计（2026-08-16 EOL 批实证）
    try:
        file_diff = gateway.run_git(["git", "diff", "--cached", "--unified=0", "--ignore-cr-at-eol", "--", py_file])
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "DATETIME-NOW-FORBIDDEN gate: git diff 失败 file=%s, %s",
            py_file,
            e,
            exc_info=True,
        )
        return violations
    if file_diff.returncode != 0:
        return violations

    # 3c. 判定检测模式：生成器文件全量检测 datetime.now(；
    #     src/zephyr/ 文件只检测 time.time( 和 datetime.now() 无参数
    is_generator = _is_generator_file(py_file)

    added_lines = _parse_diff_with_line_numbers(file_diff.stdout)
    for line_no, content in added_lines:
        # 豁免：docstring 内的行
        if line_no in docstring_lines:
            continue
        # 豁免：注释 / import
        if _is_exempt_line(content):
            continue
        # 豁免：noqa 标记
        if _has_noqa_exempt(content):
            continue

        if is_generator:
            # 生成器：任何 datetime.now( 形式都禁
            if _DATETIME_NOW_RE.search(content):
                violations.append(
                    f"  {py_file}:{line_no}: 生成器代码 datetime.now() 调用 -> {content.strip()}"  # noqa: m46-time  M46豁免: 检测器源码含检测模式字符串用于违规消息构造
                )
                continue
        # src/zephyr/ 全量：检测 time.time( 和 datetime.now() 无参数
        if _TIME_TIME_RE.search(content):
            violations.append(
                f"  {py_file}:{line_no}: time.time() 调用（应改 now_utc()）-> {content.strip()}"  # noqa: m46-time  M46豁免: 检测器源码含检测模式字符串用于违规消息构造
            )
            continue
        if _DATETIME_NOW_NAIVE_RE.search(content):
            violations.append(
                f"  {py_file}:{line_no}: datetime.now() naive（应改 datetime.now(UTC) 或 now_utc()）-> {content.strip()}"  # noqa: m46-time  M46豁免: 检测器源码含检测模式字符串用于违规消息构造
            )
    return violations


def _format_violation_detail(violations: list[str]) -> str:
    # 硬阻断：检出违规则 fail-closed
    return (
        "DATETIME-NOW-FORBIDDEN：检测到时间戳误用（5.46 时区处理防复发 + AGENTS.md §11.1.1），\n"
        "  生成器代码禁止 datetime.now() 任何形式；src/zephyr/ 全量禁止 time.time() 和 datetime.now() 无参数。\n"  # noqa: m46-time  M46豁免: 检测器源码含检测模式字符串用于违规消息构造
        + "\n".join(violations)
        + "\n-> 改用 now_utc()（time_utils SSoT）或 datetime.now(UTC)；合法场景用 # noqa: m46-time 豁免。"  # noqa: m46-time  M46豁免: 检测器源码含检测模式字符串用于违规消息构造
    )


def make_datetime_now_forbidden_gate() -> GateSpec:
    """构造时间戳约定硬阻断 GateSpec（双轨检测面）。

    Returns:
        GateSpec(gate_id="DATETIME-NOW-FORBIDDEN", priority=34)。
        priority=34——在 FILE-PLACEMENT-TTL(33) 之后、R5-DIGIT-SUFFIX(35) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged added/modified .py 文件
        staged = _get_staged_files(gateway)
        if staged is None:
            return True, ""

        # 2. 过滤到目标 .py 文件（生成器 OR src/zephyr/）+ tests/ 豁免
        target_files = _filter_target_py_files(staged)
        if not target_files:
            return True, ""

        # 3. 检测每个目标文件的 added 行
        violations: list[str] = []
        for py_file in target_files:
            violations.extend(_scan_file_for_violations(gateway, py_file))

        # 4. 硬阻断：检出违规则 fail-closed
        if violations:
            detail = _format_violation_detail(violations)
            logger.error("DATETIME-NOW-FORBIDDEN gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(gate_id="DATETIME-NOW-FORBIDDEN", check=_check, priority=34)
