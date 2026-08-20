# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.zephyr_env_direct_access_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——检测 src/zephyr/ 代码(.py)新增行直接访问 os.environ["ZEPHYR_ENV"] 或 os.environ.get("ZEPHYR_ENV") 时阻断（5.34 环境隔离防复发，应走 config 层）；config 层目录(src/zephyr/shared/foundation/config)豁免；tests/ 豁免；import/注释/docstring 豁免；# noqa: e34-env 豁免；git diff 不可达 fail-open；检出违规则 fail-closed 阻断
# [MODIFY-GUARD] gate_id="ZEPHYR-ENV-DIRECT-ACCESS"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_zephyr_env_direct_access_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""zephyr_env_direct_access_gate.py — ZEPHYR_ENV 直访硬阻断门禁（ZEPHYR-ENV-DIRECT-ACCESS）

检测 staged 代码（src/zephyr/ .py）新增行中直接访问 ``os.environ["ZEPHYR_ENV"]``
或 ``os.environ.get("ZEPHYR_ENV")`` —— 应通过 config 层统一读取，避免散落直访
导致环境判断不一致（5.34 环境隔离防复发）。

病根（5.34 环境隔离）
--------------------
- ZEPHYR_ENV 与枚举不匹配 + is_prod() 零调用 + 散落直访
- 治本：config 层 canonical 读取 + is_prod() 生产写守卫

设计权衡
--------
1. **只检测 added 行**：存量由仪表盘 M30 监控，gate 只防新增。
2. **config 层豁免**：``src/zephyr/shared/foundation/config`` 目录合法直读 env。
3. **priority=125**：在既有 gate 之后、200 段之前。
4. **noqa 豁免**：合法场景用 ``# noqa: e34-env`` 并附理由说明文本（≥10字符）。
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

__all__ = ["make_zephyr_env_direct_access_gate"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注

_SRC_ZEPHYR_PREFIX = "src/zephyr/"
# config 层目录豁免（合法直读 env 的唯一入口）
_CONFIG_DIR_PART = "src/zephyr/shared/foundation/config"
_NOQA_MARKER = "e34-env"

# os.environ["ZEPHYR_ENV"] / os.environ['ZEPHYR_ENV'] / os.environ.get("ZEPHYR_ENV")
_ENV_SUBSCRIPT_RE = re.compile(r"os\.environ\[['\"]ZEPHYR_ENV['\"]\]")
_ENV_GET_RE = re.compile(r"os\.environ\.get\(['\"]ZEPHYR_ENV['\"]")


def _is_config_layer(py_file: str) -> bool:
    """config 层目录豁免（合法直读 env）。"""
    return _CONFIG_DIR_PART in py_file.replace("\\", "/")


def _has_noqa_exempt(content: str) -> bool:
    return f"# noqa: {_NOQA_MARKER}" in content


def _scan_file_for_violations(gateway, py_file: str) -> list[str]:
    violations: list[str] = []
    file_content = _read_staged_file(gateway, py_file)
    docstring_lines = _extract_docstring_lines(file_content) if file_content else set()

    added_lines = _get_added_lines(gateway, py_file, gate_name="ZEPHYR-ENV-DIRECT-ACCESS")
    for line_no, content in added_lines:
        if line_no in docstring_lines:
            continue
        if _is_exempt_line(content):
            continue
        if _has_noqa_exempt(content):
            continue
        if _ENV_SUBSCRIPT_RE.search(content):
            violations.append(
                f"  {py_file}:{line_no}: os.environ['ZEPHYR_ENV'] 直访（应走 config 层）-> {content.strip()}"
            )
            continue
        if _ENV_GET_RE.search(content):
            violations.append(
                f"  {py_file}:{line_no}: os.environ.get('ZEPHYR_ENV') 直访（应走 config 层）-> {content.strip()}"
            )
    return violations


def _format_violation_detail(violations: list[str]) -> str:
    return (
        "ZEPHYR-ENV-DIRECT-ACCESS：检测到 ZEPHYR_ENV 直接访问（5.34 环境隔离防复发），\n"
        "  禁止 os.environ['ZEPHYR_ENV'] / os.environ.get('ZEPHYR_ENV') 散落直访。\n"
        + "\n".join(violations)
        + "\n-> 改走 config 层（zephyr.shared.foundation.config）统一读取；"
        "config 层自身或合法场景用 # noqa: e34-env 豁免并附理由说明文本。"
    )


def make_zephyr_env_direct_access_gate() -> GateSpec:
    """构造 ZEPHYR_ENV 直访硬阻断 GateSpec。

    Returns:
        GateSpec(gate_id="ZEPHYR-ENV-DIRECT-ACCESS", priority=125)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        staged = _get_staged_py_files(gateway, gate_name="ZEPHYR-ENV-DIRECT-ACCESS")
        if not staged:
            return True, ""

        target_files = [
            f
            for f in staged
            if f.replace("\\", "/").startswith(_SRC_ZEPHYR_PREFIX) and not _is_config_layer(f) and not is_test_exempt(f)
        ]
        if not target_files:
            return True, ""

        violations: list[str] = []
        for py_file in target_files:
            violations.extend(_scan_file_for_violations(gateway, py_file))

        if violations:
            detail = _format_violation_detail(violations)
            logger.error("ZEPHYR-ENV-DIRECT-ACCESS gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(gate_id="ZEPHYR-ENV-DIRECT-ACCESS", check=_check, priority=125)
