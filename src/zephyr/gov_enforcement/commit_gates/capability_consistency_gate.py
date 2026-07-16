# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.capability_consistency_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.data.capability_validator (check_route_meta_consistency_content); zephyr.gov_enforcement.commit_gates._diff_helpers (_get_staged_py_files, _read_staged_file); zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged *_provider.py 文件中"fetch 路由能力集"与"meta.capabilities 声明集"不一致时阻断 commit（passed=False）；治本本次 8 条 ERROR 根因：路由支持某 capability 但 meta 遗漏声明（miniqmt 8 个 CapabilityContract 漏声明）；检测 staged 内 *_provider.py 文件（含 akshare/miniqmt/ifind）；AST 解析失败 fail-open（passed=True，其他 gate 处理）；git diff 不可达 fail-open（logger.warning）
# [MODIFY-GUARD] gate_id="CAP-CONSISTENCY"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff/AST 解析异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_capability_consistency_gate.py
# [A_module] module_id=MOD-GOV-capability_consistency_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""capability_consistency_gate.py — Provider 路由-meta 一致性门禁（CAP-CONSISTENCY，裁定 #ARCH-CH-022 Phase 4.4）

检测 staged ``*_provider.py`` 文件中 "fetch 路由能力集" 与 "meta.capabilities 声明集"
的一致性——不一致则硬阻断 commit。

病根（第一性原理）
-----------------
裁定 #ARCH-CH-022：本次 8 条 ERROR 级 CAP-NOT-FOUND 违规的根因是
``miniqmt_provider.py`` 的 fetch 路由字典（``_KLINE_CAPABILITIES`` /
``_FINANCIAL_CAPABILITIES``）支持 ``kline_15min/30min/60min`` + 5 个财务报表能力，
但 ``meta.capabilities`` 只声明了 ``kline_1min/5min`` + 死声明 ``financial_statement``。
100% AI 开发模式下，注释/声明式契约的遵守率约 10%~30%，必须升级为 commit-time
机器执行门禁才能达到 ~100%。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified ``*_provider.py`` 文件
  2. 对每个文件调用 ``check_route_meta_consistency_content`` AST 校验（pure AST，无文件 I/O）
  3. 检出违规则硬阻断 commit（与 Phase 4.3 运行时 WARN 配合——gate 阻新违规，
     运行时 WARN 不阻断已在运行的生产实例，渐进式收紧）

设计权衡
--------
1. **只检测 ``*_provider.py``**：gate 专防 provider 路由-meta 漂移，不检测其他文件。
2. **fail-open on 解析失败**：AST 解析失败时返回 passed=True（其他 gate 处理语法错误）。
3. **pure AST，无文件 I/O**：直接用 staged index 内容做 AST 解析，不导入模块（避免
   副作用/SDK 依赖），不写临时文件（staged 内容可能与工作区不同）。
4. **priority=98**：在 TEST-SOURCE-CONSISTENCY(96) / DEPGRAPH-WRITE-PATH(97) 之后，
   作为最高优先级 gate 之一，在 commit 流程末段执行。

Usage::

    from zephyr.gov_enforcement.commit_gates.capability_consistency_gate import (
        make_capability_consistency_gate,
    )

    registry.register(make_capability_consistency_gate())
"""

from __future__ import annotations

import logging

from zephyr.data.capability_validator import check_route_meta_consistency_content
from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _get_staged_py_files,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_capability_consistency_gate"]

# provider 文件路径后缀（相对 repo root）：检测 staged 文件名以 _provider.py 结尾
_PROVIDER_SUFFIX = "_provider.py"


def _is_provider_file(file_rel_path: str) -> bool:
    """判断文件是否为 provider 实现文件（路径以 _provider.py 结尾）。

    Args:
        file_rel_path: 文件相对路径（可能含正斜杠或反斜杠）。

    Returns:
        True 表示文件是 provider 实现文件（akshare/miniqmt/ifind 等）。
    """
    normalized = file_rel_path.replace("\\", "/")
    return normalized.endswith(_PROVIDER_SUFFIX)


def _check_provider_content(content: str, provider_file: str) -> list[str]:
    """检查 provider 文件内容的路由-meta 一致性，返回违规列表。

    直接调用 ``check_route_meta_consistency_content``（pure AST，无文件 I/O），
    无需写临时文件——staged 内容可能与工作区不同（部分暂存场景），故必须用
    index 版本内容而非工作区文件。

    Args:
        content: provider 文件完整内容（staged index 版本）。
        provider_file: provider 文件相对路径（用于错误消息）。

    Returns:
        违规描述列表（空列表表示一致或解析失败 fail-open）。
    """
    try:
        return check_route_meta_consistency_content(content)
    except Exception as e:
        logger.warning(
            "CAP-CONSISTENCY: 解析 %s 失败（fail-open）: %s",
            provider_file, e, exc_info=True,
        )
        return []


def make_capability_consistency_gate() -> GateSpec:
    """构造 Provider 路由-meta 一致性 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="CAP-CONSISTENCY", priority=98)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged added/modified .py 文件
        staged = _get_staged_py_files(gateway, gate_name="CAP-CONSISTENCY")
        if not staged:
            return True, ""

        # 2. 过滤 provider 实现文件（路径以 _provider.py 结尾）
        provider_files = [f for f in staged if _is_provider_file(f)]
        if not provider_files:
            return True, ""

        # 3. 检测每个 provider 文件的路由-meta 一致性
        violations: list[str] = []
        for provider_file in provider_files:
            content = _read_staged_file(gateway, provider_file)
            if not content:
                continue
            file_violations = _check_provider_content(content, provider_file)
            for v in file_violations:
                violations.append(f"  {provider_file}: {v}")

        # 4. 硬阻断
        if violations:
            detail = (
                "CAP-CONSISTENCY (裁定 #ARCH-CH-022 Phase 4.4)：检测到 Provider 路由-meta 不一致\n"
                "  fetch 路由能力集与 meta.capabilities 声明集不一致（治本本次 8 条 ERROR 根因）。\n"
                + "\n".join(violations)
                + "\n-> 修复方案：在对应 *_provider.py 的 meta.capabilities 中补全漏声明的 capability"
                + "\n   字符串声明用 'xxx'；需声明行为契约时用 CapabilityContract('xxx', supports_symbols_null=True)"
                + "\n   删除路由不支持的死声明（meta.capabilities 声明但 fetch 路由不支持）"
            )
            logger.error("CAP-CONSISTENCY gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(
        gate_id="CAP-CONSISTENCY",
        check=_check,
        priority=98,
    )
