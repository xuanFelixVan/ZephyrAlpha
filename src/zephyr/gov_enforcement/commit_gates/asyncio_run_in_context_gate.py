# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.asyncio_run_in_context_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——检测 src/zephyr/ 全量代码(.py)新增行含 asyncio.run()/asyncio.get_event_loop()/asyncio.new_event_loop() 调用时阻断（5.100 异步资源生命周期防复发）；tests/ 豁免；import/注释/docstring 豁免；# noqa: a100-asyncio 豁免；git diff 不可达 fail-open（logger.warning 检测器失效）；检出违规则 fail-closed 阻断（passed=False）；canonical 替代 zephyr...async_utils.run_coroutine_sync
# [MODIFY-GUARD] gate_id="ASYNCIO-RUN-IN-CONTEXT"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_asyncio_run_in_context_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""asyncio_run_in_context_gate.py — 异步上下文误用硬阻断门禁（ASYNCIO-RUN-IN-CONTEXT）

检测 staged 代码（src/zephyr/ 全量 .py）新增行中的异步 API 误用：
  - ``asyncio.run()`` —— 在 async 上下文内静默绕过、跨线程死锁风险
  - ``asyncio.get_event_loop()`` —— Python 3.12+ 弃用、无运行循环时行为不确定
  - ``asyncio.new_event_loop()`` —— 应交由 canonical async_utils 统一管理

病根（5.100 异步资源生命周期）
------------------------------
- ``asyncio.run`` 在 async 上下文内静默绕过安全扫描
- ``run_coroutine_threadsafe`` 死锁
- canonical 替代：``zephyr...async_utils.run_coroutine_sync``（R103 已治本存量）

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified .py 文件
  2. 过滤到 src/zephyr/ 文件 + tests/ 豁免
  3. 解析 diff，检查 added 行中的违规模式
  4. 豁免 import/注释/docstring 行 + noqa:a100-asyncio 标记
  5. 命中 -> 硬阻断（passed=False）

设计权衡
--------
1. **只检测 added 行**：存量违规由仪表盘 M23 监控，gate 只防新增。
2. **正则匹配**：精确匹配三种弃用/危险调用形式。
3. **fail-open on git error**：git diff 失败时不阻断。
4. **priority=122**：在既有 gate（max 121）之后、200 段之前。
5. **noqa 豁免**：合法场景（如 async_utils canonical 实现自身）可用 noqa:a100-asyncio。

Usage::

    from zephyr.gov_enforcement.commit_gates.asyncio_run_in_context_gate import make_asyncio_run_in_context_gate

    registry.register(make_asyncio_run_in_context_gate())
"""

from __future__ import annotations

import logging
import re

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _extract_docstring_lines,
    _get_added_lines,
    _get_staged_py_files,
    _is_exempt_line,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_asyncio_run_in_context_gate"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注

# src/zephyr/ 全量检测面前缀
_SRC_ZEPHYR_PREFIX = "src/zephyr/"

# noqa 豁免标记（MUST 在 noqa_exempt_registry.yaml 登记）
_NOQA_MARKER = "a100-asyncio"

# 匹配 asyncio.run( / asyncio.get_event_loop( / asyncio.new_event_loop(
_ASYNCIO_RUN_RE = re.compile(r"\basyncio\.run\s*\(")
_ASYNCIO_GET_LOOP_RE = re.compile(r"\basyncio\.get_event_loop\s*\(")
_ASYNCIO_NEW_LOOP_RE = re.compile(r"\basyncio\.new_event_loop\s*\(")


def _is_src_zephyr_file(py_file: str) -> bool:
    """判定 .py 文件是否在 src/zephyr/ 目录下。"""
    return py_file.replace("\\", "/").startswith(_SRC_ZEPHYR_PREFIX)


def _has_noqa_exempt(content: str) -> bool:
    """检查行是否含 ``# noqa: a100-asyncio`` 豁免标记。"""
    return f"# noqa: {_NOQA_MARKER}" in content


def _match_violation(content: str) -> str | None:
    """返回命中模式描述，未命中返回 None。"""
    if _ASYNCIO_RUN_RE.search(content):
        return "asyncio.run()（应改 async_utils.run_coroutine_sync）"
    if _ASYNCIO_GET_LOOP_RE.search(content):
        return "asyncio.get_event_loop()（Python 3.12+ 弃用，应改 async_utils canonical）"
    if _ASYNCIO_NEW_LOOP_RE.search(content):
        return "asyncio.new_event_loop()（应交由 async_utils 统一管理）"
    return None


def _scan_file_for_violations(gateway, py_file: str) -> list[str]:
    """检测单个文件的 added 行，返回违规列表。"""
    violations: list[str] = []
    file_content = _read_staged_file(gateway, py_file)
    docstring_lines = _extract_docstring_lines(file_content) if file_content else set()

    added_lines = _get_added_lines(gateway, py_file, gate_name="ASYNCIO-RUN-IN-CONTEXT")
    for line_no, content in added_lines:
        if line_no in docstring_lines:
            continue
        if _is_exempt_line(content):
            continue
        if _has_noqa_exempt(content):
            continue
        matched = _match_violation(content)
        if matched:
            violations.append(f"  {py_file}:{line_no}: {matched} -> {content.strip()}")
    return violations


def _format_violation_detail(violations: list[str]) -> str:
    return (
        "ASYNCIO-RUN-IN-CONTEXT：检测到异步 API 误用（5.100 异步资源生命周期防复发），\n"
        "  src/zephyr/ 全量禁止 asyncio.run() / asyncio.get_event_loop() / asyncio.new_event_loop()。\n"
        + "\n".join(violations)
        + "\n-> 改用 zephyr...async_utils.run_coroutine_sync（canonical）；"
        "合法场景用 # noqa: a100-asyncio 豁免并附理由说明文本。"
    )


def make_asyncio_run_in_context_gate() -> GateSpec:
    """构造异步上下文误用硬阻断 GateSpec。

    Returns:
        GateSpec(gate_id="ASYNCIO-RUN-IN-CONTEXT", priority=122)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        staged = _get_staged_py_files(gateway, gate_name="ASYNCIO-RUN-IN-CONTEXT")
        if not staged:
            return True, ""

        target_files = [f for f in staged if _is_src_zephyr_file(f) and not is_test_exempt(f)]
        if not target_files:
            return True, ""

        violations: list[str] = []
        for py_file in target_files:
            violations.extend(_scan_file_for_violations(gateway, py_file))

        if violations:
            detail = _format_violation_detail(violations)
            logger.error("ASYNCIO-RUN-IN-CONTEXT gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(gate_id="ASYNCIO-RUN-IN-CONTEXT", check=_check, priority=122)
