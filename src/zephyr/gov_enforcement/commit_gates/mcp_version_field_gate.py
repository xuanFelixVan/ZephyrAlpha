# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.mcp_version_field_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers (_read_staged_file); zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——检测 staged mcp.json 文件顶层缺 version 字段时阻断（5.35 API 版本管理防复发）；非 .py 检测面（JSON 存在性检查）；json.loads 失败 fail-open（由其他 gate 管 JSON 完整性）；git diff 不可达 fail-open；检出违规则 fail-closed 阻断（passed=False）；无 noqa（存在性检查无行级豁免语义）
# [MODIFY-GUARD] gate_id="MCP-VERSION-FIELD"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff/json.loads 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_mcp_version_field_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
mcp_version_field_gate.py — MCP version 字段缺失硬阻断门禁（MCP-VERSION-FIELD）

检测 staged ``mcp.json`` 文件顶层缺 ``version`` 字段（5.35 API 版本管理防复发）。

病根（5.35 API 版本管理）
--------------------------
- MCP 工具无 version + api_version_contract 死代码 + 无 deprecation
- 治本：``mcp.json`` version 字段 + ERR_API_SUNSET 入 MCP 管道

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified 文件（非 .py，需直接用 ``gateway.run_git``）
  2. 过滤文件名以 ``mcp.json`` 结尾的文件
  3. 对每个 mcp.json：``_read_staged_file`` 读取 → ``json.loads``
  4. 检查顶层是否含 ``version`` 字段（``"version" in data``）
  5. 缺失 -> 硬阻断（passed=False）

设计权衡
--------
1. **非 .py 检测面**：这是 5 个 gate 中唯一检测 JSON 文件的 gate，
   ``_get_staged_py_files`` 不适用（只获取 .py），需直接用 ``gateway.run_git``
   获取全部 staged 文件再过滤。
2. **fail-open on json.loads**：JSON 语法错误由其他 gate 管完整性，
   本 gate 只管 version 字段存在性——解析失败时不阻断。
3. **无 noqa**：存在性检查无行级豁免语义（要么有 version 字段，要么没有）。
4. **fail-open on git error**：git diff 失败时不阻断。
5. **priority=126**：在 ZEPHYR-ENV-DIRECT-ACCESS(125) 之后、200 段之前。
6. **hard-block**：version 字段缺失是确定性违规，应硬阻断。

Usage::

    from zephyr.gov_enforcement.commit_gates.mcp_version_field_gate import make_mcp_version_field_gate

    registry.register(make_mcp_version_field_gate())

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: mcp_version_field_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① make_mcp_version_field_gate
#   name_en: make_mcp_version_field_gate
#   intro: 构造 MCP version 字段缺失硬阻断 GateSpec。
#   desc: 构造 MCP version 字段缺失硬阻断 GateSpec。 Returns: GateSpec(gate_id="MCP-VERSION-FIELD", priority=…；源码 L180-L213
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

import json
import logging

from zephyr.gov_enforcement.commit_gates._diff_helpers import _read_staged_file
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_mcp_version_field_gate"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注

# mcp.json 文件名后缀（可能多个，如 config/mcp.json、src/.../mcp.json）
_MCP_JSON_SUFFIX = "mcp.json"


def _get_staged_files(gateway) -> list[str] | None:
    """获取 staged added/modified 文件列表（非 .py 过滤，含全部类型）。

    失败返回 None（fail-open）。
    """
    try:
        result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
        if result.returncode != 0:
            logger.warning(
                "MCP-VERSION-FIELD gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                result.returncode,
            )
            return None
        return [f.replace("\\", "/") for f in result.stdout.strip().splitlines() if f]
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "MCP-VERSION-FIELD gate fail-open: git diff 异常(%s: %s)，检测器失效。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None


def _filter_mcp_json_files(staged: list[str]) -> list[str]:
    """过滤文件名以 mcp.json 结尾的文件。"""
    return [f for f in staged if f.endswith(_MCP_JSON_SUFFIX)]


def _scan_file_for_violation(gateway, mcp_file: str) -> str | None:
    """检测单个 mcp.json 文件是否缺 version 字段。

    Returns:
        违规描述字符串，无违规返回 None。
    """
    content = _read_staged_file(gateway, mcp_file)
    if content is None:
        # git show 失败（fail-open）—— 由其他 gate 管文件完整性
        logger.warning(
            "MCP-VERSION-FIELD gate: 读取 staged 文件失败 file=%s，fail-open 跳过。",
            mcp_file,
        )
        return None

    # json.loads 解析（fail-open on JSONDecodeError）
    try:
        data = json.loads(content)
    except (json.JSONDecodeError, ValueError) as e:
        # JSON 语法错误由其他 gate 管完整性，本 gate 只管 version 字段存在性
        logger.warning(
            "MCP-VERSION-FIELD gate: json.loads 失败 file=%s（%s），fail-open 跳过（JSON 完整性由其他 gate 管理）。",
            mcp_file,
            type(e).__name__,
        )
        return None

    # data 必须是 dict（mcp.json 顶层是对象）
    if not isinstance(data, dict):
        logger.warning(
            "MCP-VERSION-FIELD gate: mcp.json 顶层非 object file=%s（type=%s），fail-open 跳过。",
            mcp_file,
            type(data).__name__,
        )
        return None

    # 检查 version 字段存在性
    if "version" not in data:
        return (
            f"  {mcp_file}: 缺顶层 version 字段（5.35 API 版本管理防复发）"
            f'\n     应补: 在 mcp.json 顶层加 "version": "<语义版本号>"'
        )
    return None


def _format_violation_detail(violations: list[str]) -> str:
    return (
        "MCP-VERSION-FIELD：检测到 mcp.json 缺顶层 version 字段（5.35 API 版本管理防复发），\n"
        '  所有 staged mcp.json 文件 MUST 含顶层 "version" 字段。\n'
        + "\n".join(violations)
        + '\n-> 在 mcp.json 顶层加 "version": "<语义版本号>"（如 "1.0.0"）。'
    )


def make_mcp_version_field_gate() -> GateSpec:
    """构造 MCP version 字段缺失硬阻断 GateSpec。

    Returns:
        GateSpec(gate_id="MCP-VERSION-FIELD", priority=126)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged added/modified 文件（全部类型，非 .py 过滤）
        staged = _get_staged_files(gateway)
        if staged is None:
            return True, ""  # fail-open

        # 2. 过滤 mcp.json 文件
        mcp_files = _filter_mcp_json_files(staged)
        if not mcp_files:
            return True, ""

        # 3. 检测每个 mcp.json 的 version 字段
        violations: list[str] = []
        for mcp_file in mcp_files:
            violation = _scan_file_for_violation(gateway, mcp_file)
            if violation:
                violations.append(violation)

        # 4. 硬阻断：检出违规则 fail-closed
        if violations:
            detail = _format_violation_detail(violations)
            logger.error("MCP-VERSION-FIELD gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(gate_id="MCP-VERSION-FIELD", check=_check, priority=126)
