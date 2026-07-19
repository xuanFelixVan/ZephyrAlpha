# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 硬阻断——commit 含 src/zephyr/**/*.py 业务代码变更但 session 未调 rule_discovery.discover_applicable_rules / capability_lookup.find 时阻断（passed=False）；tests/-only 放行；.md-only 放行；non-Zephyr 项目放行；merge commit 放行；audit log 目录缺失→fail-closed 阻断（防"删目录绕过"攻击向量）；session_id 缺失→放行（SESSION-REQUIRED gate 已先行阻断，本 gate 不重复检查）；commit msg 含 [no-lookup:reason] 标记→放行（逃生通道，reason 持久化到 detail）；ZEPHYR_BYPASS_LOOKUP=1 环境变量→放行（紧急逃生，与 ZEPHYR_COMMIT_GATEWAY=1 同级）
# [MODIFY-GUARD] gate_id="CAPABILITY-LOOKUP-REQUIRED"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；audit log 路径 _LOOKUP_AUDIT_DIR；豁免前缀 _EXEMPT_PATH_PREFIXES；逃生标记 _BYPASS_MARKER_PREFIX
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——audit log 读取异常降级为 fail-closed 阻断（passed=False，detail 含修复指引）；session_id 缺失降级为放行（其他 gate 已检查）
# [TESTS] tests/governance/commit_gates/test_capability_lookup_required_gate.py
# [A_module] module_id=MOD-GOV-capability_lookup_required_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 无时间触发
"""capability_lookup_required_gate.py — Capability Lookup 强制门禁（CAPABILITY-LOOKUP-REQUIRED，#ARCH-GOV-CONVERGENCE-META Phase 3.4a）

检测 commit 含 ``src/zephyr/**/*.py`` 业务代码变更时，当前 session 是否调用了
``rule_discovery.discover_applicable_rules`` 或 ``capability_lookup.find``。
未调用则硬阻断——强制 AI 在施工前查询适用规则（病根3：可发现性缺口的代码层兜底）。

病根3（规则可发现性被动反查）治本
---------------------------------
AGENTS.md §7 + rule_discovery_server.py（Phase 3.2b）建立了规则发现基础设施：
- rule_ai_perception_index.yaml（Phase 3.2a）—— 64 条规则的感知索引
- rule_discovery MCP 工具 —— 按 operation/scope/domain 查询适用规则
- capability_lookup —— 按别名/关键词反查 capability 真源

但这些都是**被动查询**——AI 不调用就不发现。新 AI 若跳过 AGENTS.md 或不调用 MCP 工具，
可在 commit 时直接提交代码导致：① 违反未发现的规则 ② 重复造轮子（已有 capability 未扩展）。

本 gate 在 commit 时自动检查 session 级 audit log（``.runtime/lookup_audit/<session_id>.jsonl``），
若 log 不存在或为空则阻断——把"应调用 MCP 工具"从君子协定升级为代码层强制。

设计权衡
--------
1. **硬阻断而非 warn-only**：CAPABILITY-OVERLAP gate 是 warn-only（token 启发式匹配
   可能误报）；本 gate 用 audit log 精确比对（log 存在/不存在，二值无歧义），故硬阻断。
2. **tests/-only 与 .md-only 放行**：测试与文档非业务代码，无规则适用性检查需求。
3. **session_id 缺失放行**：SESSION-REQUIRED gate（priority=31）已先行检查 session 注册，
   到本 gate 时 session_id 必然有效；若意外为空，放行避免重复阻断。
4. **fail-closed（audit log 目录缺失）**：删目录绕过是红蓝攻击向量，对标 create_guard
   fail-closed 设计。YAML/JSON 解析失败亦 fail-closed。
5. **priority=110**：在 UNDEFINED-NAME(106)/SCRIPTS-IMPORT-INTEGRITY(104) 之后执行——
   先过基础语法检查，再过 capability lookup 强制（语义层约束）。
6. **逃生通道**：``[no-lookup:reason]`` commit msg 标记 + ``ZEPHYR_BYPASS_LOOKUP=1``
   环境变量。reason 持久化到 commit detail 便于审计。

audit log 格式（JSONL，每行一条调用记录）::

    {"ts": "2026-07-19T08:00:00Z", "tool": "rule_discovery.discover_applicable_rules",
     "query": {"operation": "file_write"}, "result_count": 1, "rule_ids": ["TRAE-001"]}

写入方：``rule_discovery_server._discover_applicable_rules`` 与
``capability_lookup.CapabilityLookup.find``（Phase 3.4a 同步扩展）。

Usage::

    from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import make_capability_lookup_required_gate
    registry.register(make_capability_lookup_required_gate())
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

__all__ = ["make_capability_lookup_required_gate", "LOOKUP_AUDIT_DIR_REL"]

# audit log 目录（相对 REPO_ROOT）
LOOKUP_AUDIT_DIR_REL = ".runtime/lookup_audit"

# 业务代码前缀——commit 含此前缀的 .py 变更才触发本 gate
_BUSINESS_CODE_PREFIX = "src/zephyr/"

# .md-only / .json-only / .yaml-only 等纯文档/配置变更的扩展名集合
# 这些变更不涉及业务代码逻辑，无规则适用性检查需求
_DOC_ONLY_EXTENSIONS = (".md", ".rst", ".txt")

# 逃生通道标记前缀（commit msg 中）
_BYPASS_MARKER_PREFIX = "[no-lookup:"

# 紧急逃生环境变量
_BYPASS_ENV_VAR = "ZEPHYR_BYPASS_LOOKUP"


def _get_audit_log_path(session_id: str) -> Path:
    """构造 session 的 audit log 文件路径。"""
    return REPO_ROOT / LOOKUP_AUDIT_DIR_REL / f"{session_id}.jsonl"


def _audit_log_dir_exists() -> bool:
    """检查 audit log 目录是否存在。

    目录不存在视为"AI session 启动 smoke test 失败"——fail-closed 阻断。
    红蓝攻击向量：删目录绕过 audit log 检查。
    """
    return (REPO_ROOT / LOOKUP_AUDIT_DIR_REL).is_dir()


def _has_business_code_changes(files: list[str]) -> bool:
    """检测 commit 是否含 src/zephyr/**/*.py 业务代码变更（非 tests/）。

    Args:
        files: commit 文件绝对路径列表。

    Returns:
        True 表示含业务代码变更（需触发本 gate）。
    """
    for f in files:
        if is_test_exempt(f):
            continue
        try:
            rel = os.path.relpath(f, str(REPO_ROOT)).replace("\\", "/")
        except (ValueError, OSError):
            continue
        if rel.startswith(_BUSINESS_CODE_PREFIX) and rel.endswith(".py"):
            return True
    return False


def _is_doc_only_commit(files: list[str]) -> bool:
    """检测 commit 是否仅含 .md/.rst/.txt 文档变更（无 .py 业务代码）。

    纯文档变更不涉及业务逻辑，无需规则适用性检查。
    """
    if not files:
        return False
    for f in files:
        try:
            rel = os.path.relpath(f, str(REPO_ROOT)).replace("\\", "/")
        except (ValueError, OSError):
            return False
        if not rel.lower().endswith(_DOC_ONLY_EXTENSIONS):
            return False
    return True


def _has_bypass_marker(detail: str | None) -> tuple[bool, str]:
    """检测 commit msg 是否含 [no-lookup:reason] 逃生标记。

    Returns:
        (True, reason) 表示命中逃生通道；reason 为空串表示无理由（不允许，要求 reason 非空）。
    """
    if not detail:
        return False, ""
    idx = detail.find(_BYPASS_MARKER_PREFIX)
    if idx < 0:
        return False, ""
    start = idx + len(_BYPASS_MARKER_PREFIX)
    end = detail.find("]", start)
    if end < 0:
        return False, ""
    reason = detail[start:end].strip()
    return True, reason


def _count_valid_log_entries(log_path: Path) -> tuple[int, str | None]:
    """读取 audit log 文件，统计有效 entry 数。

    Returns:
        (entry_count, error_msg)。entry_count > 0 表示有有效调用记录。
        error_msg 非 None 表示读取/解析失败（fail-closed）。
    """
    if not log_path.is_file():
        return 0, None  # 文件不存在=未调用，entry_count=0
    try:
        content = log_path.read_text(encoding="utf-8")
    except OSError as e:
        return 0, f"audit log 读取失败: {e}"
    count = 0
    for line_num, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as e:
            return 0, f"audit log L{line_num} JSON 解析失败: {e}"
        if isinstance(entry, dict) and "tool" in entry:
            count += 1
    return count, None


def _is_merge_commit(detail: str | None) -> bool:
    """检测是否为 merge commit（subject 以 'merge ' 开头）。

    POST-COMMIT-GUARD 已对 merge commit 豁免，本 gate 同步豁免。
    """
    if not detail:
        return False
    return detail.lower().startswith("merge ")


def _check_bypass(commit_msg: str | None) -> tuple[bool, str] | None:
    """检查逃生通道（env var / commit msg marker / merge commit）。

    Returns:
        None 表示未命中逃生通道（继续后续检查）；
        (True, msg) 表示命中且放行；
        (False, msg) 表示命中但参数无效需阻断（如 reason 为空）。
    """
    if os.environ.get(_BYPASS_ENV_VAR) == "1":
        logger.warning(
            "CAPABILITY-LOOKUP-REQUIRED gate: 紧急逃生通道启用（ZEPHYR_BYPASS_LOOKUP=1），"
            "请在 commit 后人工确认未引入规则违反。"
        )
        return True, "ZEPHYR_BYPASS_LOOKUP=1 emergency bypass"
    if not commit_msg:
        return None
    hit, reason = _has_bypass_marker(commit_msg)
    if hit:
        if not reason:
            return False, (
                "commit msg 含 [no-lookup:] 标记但 reason 为空——"
                "MUST 提供 reason（如 [no-lookup:doc-only-fix]）。"
            )
        logger.warning(
            "CAPABILITY-LOOKUP-REQUIRED gate: 逃生通道启用（reason=%s），"
            "请在 commit 后人工确认未引入规则违反。", reason,
        )
        return True, f"bypass via [no-lookup:{reason}]"
    if _is_merge_commit(commit_msg):
        return True, "merge commit exempt"
    return None


def _check_exemptions(files: list[str]) -> tuple[bool, str] | None:
    """检查豁免场景（空 files / doc-only / tests-only / 无业务代码）。

    Returns:
        None 表示不豁免（继续后续检查）；
        (True, msg) 表示豁免放行。
    """
    if not files:
        return True, "no files to check"
    if _is_doc_only_commit(files):
        return True, "doc-only commit exempt"
    non_test_files = [f for f in files if not is_test_exempt(f)]
    if not non_test_files:
        return True, "tests-only commit exempt"
    if not _has_business_code_changes(files):
        return True, "no src/zephyr/**/*.py business code changes"
    return None


def _check_audit_log(session_id: str) -> tuple[bool, str]:
    """检查 audit log（目录存在性 + entry 数）。

    Returns:
        (passed, msg) — fail-closed：目录缺失/解析失败/entry_count=0 均阻断。
    """
    if not _audit_log_dir_exists():
        return False, (
            f"CAPABILITY-LOOKUP-REQUIRED: audit log 目录缺失 "
            f"({REPO_ROOT / LOOKUP_AUDIT_DIR_REL})。"
            f"修复：mkdir {LOOKUP_AUDIT_DIR_REL} 或确认 .runtime/ 未被误删。"
            f"病根3治本：删目录绕过是红蓝攻击向量，fail-closed 阻断。"
        )
    log_path = _get_audit_log_path(session_id)
    entry_count, err = _count_valid_log_entries(log_path)
    if err is not None:
        return False, (
            f"CAPABILITY-LOOKUP-REQUIRED: audit log 解析失败 ({log_path.name}): {err}。"
            f"修复：删除损坏的 log 文件后重新调用 rule_discovery.discover_applicable_rules。"
        )
    if entry_count == 0:
        return False, (
            f"CAPABILITY-LOOKUP-REQUIRED: session '{session_id}' 未调用 "
            f"rule_discovery.discover_applicable_rules 或 capability_lookup.find。"
            f"AI MUST 在施工前（写第一行业务代码前）调用 MCP 工具查询适用规则。"
            f"示例：rule_discovery.discover_applicable_rules(operation='file_write')。"
            f"逃生通道：commit msg 含 [no-lookup:<reason>] 标记或设 ZEPHYR_BYPASS_LOOKUP=1。"
        )
    return True, f"audit log OK ({entry_count} entries for session '{session_id}')"


def make_capability_lookup_required_gate() -> GateSpec:
    """构造 Capability Lookup 强制门禁 GateSpec。

    Returns:
        GateSpec(gate_id="CAPABILITY-LOOKUP-REQUIRED", priority=110)。
        priority=110 在 UNDEFINED-NAME(106)/SCRIPTS-IMPORT-INTEGRITY(104) 之后——
        先过基础语法检查，再过 capability lookup 强制（语义层约束）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 治本: 非 Zephyr 项目（tmp_path 测试仓库等）skip
        governance_dir = gateway.project_root / "scripts" / "governance" / "d1_structure"
        if not governance_dir.is_dir():
            return True, "non-Zephyr project (no scripts/governance/d1_structure), skipping CAPABILITY-LOOKUP-REQUIRED"

        # 逃生通道检查（env / msg marker / merge）
        commit_msg: str | None = kwargs.get("commit_message") or kwargs.get("message")
        bypass_result = _check_bypass(commit_msg)
        if bypass_result is not None:
            return bypass_result

        # 豁免检查（空 / doc-only / tests-only / 无业务代码）
        exempt = _check_exemptions(files)
        if exempt is not None:
            return exempt

        # session_id 缺失放行（SESSION-REQUIRED gate priority=31 已先行检查）
        session_id = kwargs.get("session_id", "")
        if not session_id or session_id in ("unknown", "none", "null"):
            return True, "session_id missing (SESSION-REQUIRED gate priority=31 handles this)"

        # audit log 检查（fail-closed）
        return _check_audit_log(session_id)

    return GateSpec(gate_id="CAPABILITY-LOOKUP-REQUIRED", check=_check, priority=110)