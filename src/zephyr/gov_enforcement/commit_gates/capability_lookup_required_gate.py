# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.shared.io.paths (REPO_ROOT); zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy (BYPASS_MARKER_PREFIX, BYPASS_ENV_VAR, has_bypass_marker, is_emergency_bypass, is_exempt_reason)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——commit 含 src/zephyr/**/*.py 业务代码变更但 session 未调 rule_discovery.discover_applicable_rules / capability_lookup.find 时阻断（passed=False）；tests/-only 放行；.md-only 放行；non-Zephyr 项目放行；merge commit 放行；audit log 目录缺失→fail-closed 阻断（防"删目录绕过"攻击向量）；session_id 缺失→放行（SESSION-REQUIRED gate 已先行阻断，本 gate 不重复检查）；commit msg 含 [no-lookup:reason] 标记→白名单匹配则放行，非白名单则硬阻断（#ARCH-066 gate-time 白名单检查）；ZEPHYR_BYPASS_LOOKUP=1 环境变量→放行（紧急逃生，与 ZEPHYR_COMMIT_GATEWAY=1 同级）
# [MODIFY-GUARD] gate_id="CAPABILITY-LOOKUP-REQUIRED"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；audit log 路径 _LOOKUP_AUDIT_DIR；豁免前缀 _EXEMPT_PATH_PREFIXES；逃生标记 BYPASS_MARKER_PREFIX（共享模块）；白名单 is_exempt_reason（共享模块）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——audit log 读取异常降级为 fail-closed 阻断（passed=False，detail 含修复指引）；session_id 缺失降级为放行（其他 gate 已检查）
# [TESTS] tests/governance/commit_gates/test_capability_lookup_required_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [RELATED_ARCH] #ARCH-066 (bypass 策略共享模块 + gate-time 白名单检查), #ARCH-GOV-CONVERGENCE-META Phase 3.4a
# noqa: m10-time-trigger  M10豁免: 无时间触发
"""capability_lookup_required_gate.py — Capability Lookup 强制门禁（CAPABILITY-LOOKUP-REQUIRED，#ARCH-GOV-CONVERGENCE-META Phase 3.4a, #ARCH-066）

检测 commit 含 ``src/zephyr/**/*.py`` 业务代码变更时，当前 session 是否调用了
``rule_discovery.discover_applicable_rules`` 或 ``capability_lookup.find``。
未调用则硬阻断——强制 AI 在施工前查询适用规则（病根3：可发现性缺口的代码层兜底）。

#ARCH-066 治本（bypass 策略共享 + gate-time 白名单检查）
---------------------------------------------------
原设计：``[no-lookup:any-string]`` 零摩擦放行——任何非空 reason 都通过，
白名单分类只在 post-commit reconciler 做（太晚，已产生 critical_warn 误报）。

治本：
1. **共享策略模块** ``capability_lookup_bypass_policy.py``——gate 和 reconciler 共用
   ``BYPASS_MARKER_PREFIX`` / ``BYPASS_ENV_VAR`` / ``is_exempt_reason`` / ``has_bypass_marker``
2. **gate-time 白名单检查**——``_check_bypass`` 中非白名单 reason 硬阻断（passed=False），
   仅白名单 reason（gate-fix/test-fix/continuation 等 16 项）放行
3. **trae_077 YAML 升级为数据真源**——``load_bypass_policy()`` fail-open 加载白名单+阈值

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
6. **逃生通道**：``[no-lookup:reason]`` commit msg 标记（reason MUST 匹配白名单关键词）
   + ``ZEPHYR_BYPASS_LOOKUP=1`` 环境变量（紧急逃生，高摩擦）。reason 持久化到 commit detail。

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

from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
    BYPASS_ENV_VAR,
    BYPASS_MARKER_PREFIX,
    has_bypass_marker,
    is_emergency_bypass,
    is_exempt_reason,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt
from zephyr.shared.io.paths import MAIN_REPO_ROOT, REPO_ROOT

logger = logging.getLogger(__name__)

__all__ = ["make_capability_lookup_required_gate", "LOOKUP_AUDIT_DIR_REL"]

# audit log 目录（相对 MAIN_REPO_ROOT——观测数据锚定主仓库，#ARCH-WORKTREE-ENV-001：
# worktree 进程内 REPO_ROOT=worktree 根，用 REPO_ROOT 会把审计证据分裂到
# worktree 并随 abort 丢失；门禁读端与写入端统一锚 MAIN_REPO_ROOT，从根上
# 消除"从主仓复制 audit jsonl 进 worktree 过门禁"的 workaround 语义稀释）
LOOKUP_AUDIT_DIR_REL = ".runtime/lookup_audit"

# 业务代码前缀——commit 含此前缀的 .py 变更才触发本 gate
_BUSINESS_CODE_PREFIX = "src/zephyr/"

# .md-only / .json-only / .yaml-only 等纯文档/配置变更的扩展名集合
# 这些变更不涉及业务代码逻辑，无规则适用性检查需求
_DOC_ONLY_EXTENSIONS = (".md", ".rst", ".txt")

# 逃生通道标记前缀和紧急逃生环境变量——从共享模块导入（#ARCH-066 消除双真源）
# BYPASS_MARKER_PREFIX / BYPASS_ENV_VAR / has_bypass_marker / is_emergency_bypass / is_exempt_reason
# 均来自 capability_lookup_bypass_policy.py，gate 和 reconciler 共用。


def _get_audit_log_path(session_id: str) -> Path:
    """构造 session 的 audit log 文件路径。"""
    return MAIN_REPO_ROOT / LOOKUP_AUDIT_DIR_REL / f"{session_id}.jsonl"


def _audit_log_dir_exists() -> bool:
    """检查 audit log 目录是否存在。

    目录不存在视为"AI session 启动 smoke test 失败"——fail-closed 阻断。
    红蓝攻击向量：删目录绕过 audit log 检查。
    """
    return (MAIN_REPO_ROOT / LOOKUP_AUDIT_DIR_REL).is_dir()


def _has_business_code_changes(files: list[str], root: Path | str | None = None) -> bool:
    """检测 commit 是否含 src/zephyr/**/*.py 业务代码变更（非 tests/）。

    Args:
        files: commit 文件绝对路径列表。
        root: 文件分类锚定根（默认 REPO_ROOT=进程工作区；网关调用方传
            gateway.project_root——commit 文件所在工作区，worktree 场景下
            两者不同，#ARCH-WORKTREE-ENV-001）。

    Returns:
        True 表示含业务代码变更（需触发本 gate）。
    """
    anchor = str(root) if root is not None else str(REPO_ROOT)
    for f in files:
        if is_test_exempt(f):
            continue
        try:
            rel = os.path.relpath(f, anchor).replace("\\", "/")
        except (ValueError, OSError):
            continue
        if rel.startswith(_BUSINESS_CODE_PREFIX) and rel.endswith(".py"):
            return True
    return False


def _is_doc_only_commit(files: list[str], root: Path | str | None = None) -> bool:
    """检测 commit 是否仅含 .md/.rst/.txt 文档变更（无 .py 业务代码）。

    纯文档变更不涉及业务逻辑，无需规则适用性检查。
    root 语义同 _has_business_code_changes。
    """
    if not files:
        return False
    anchor = str(root) if root is not None else str(REPO_ROOT)
    for f in files:
        try:
            rel = os.path.relpath(f, anchor).replace("\\", "/")
        except (ValueError, OSError):
            return False
        if not rel.lower().endswith(_DOC_ONLY_EXTENSIONS):
            return False
    return True


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

    #ARCH-066: gate-time 白名单检查——非白名单 reason 硬阻断（不再零摩擦放行）。
    白名单关键词见 capability_lookup_bypass_policy.py 或 trae_077 YAML。

    Returns:
        None 表示未命中逃生通道（继续后续检查）；
        (True, msg) 表示命中且放行；
        (False, msg) 表示命中但参数无效需阻断（reason 为空 / 非白名单）。
    """
    if is_emergency_bypass():
        logger.warning(
            "CAPABILITY-LOOKUP-REQUIRED gate: 紧急逃生通道启用（ZEPHYR_BYPASS_LOOKUP=1），"
            "请在 commit 后人工确认未引入规则违反。"
        )
        return True, "ZEPHYR_BYPASS_LOOKUP=1 emergency bypass"
    if not commit_msg:
        return None
    hit, reason = has_bypass_marker(commit_msg)
    if hit:
        if not reason:
            return False, (
                "commit msg 含 [no-lookup:] 标记但 reason 为空——MUST 提供 reason（如 [no-lookup:gate-fix-xxx]）。"
            )
        if not is_exempt_reason(reason):
            return False, (
                "CAPABILITY-LOOKUP-REQUIRED: [no-lookup:] reason 不匹配白名单关键词——"
                "MUST 使用白名单 reason（如 gate-fix/test-fix/continuation/"
                "investigated/mechanical/sync 等），或设 ZEPHYR_BYPASS_LOOKUP=1 紧急逃生。"
                "白名单见 capability_lookup_bypass_policy.py 或 trae_077 YAML。"
            )
        logger.warning(
            "CAPABILITY-LOOKUP-REQUIRED gate: 逃生通道启用（reason=%s, whitelist match），"
            "请在 commit 后人工确认未引入规则违反。",
            reason,
        )
        return True, f"bypass via [no-lookup:{reason}] (whitelist match)"
    if _is_merge_commit(commit_msg):
        return True, "merge commit exempt"
    return None


def _check_exemptions(files: list[str], root: Path | str | None = None) -> tuple[bool, str] | None:
    """检查豁免场景（空 files / doc-only / tests-only / 无业务代码）。

    Returns:
        None 表示不豁免（继续后续检查）；
        (True, msg) 表示豁免放行。
    """
    if not files:
        return True, "no files to check"
    if _is_doc_only_commit(files, root):
        return True, "doc-only commit exempt"
    non_test_files = [f for f in files if not is_test_exempt(f)]
    if not non_test_files:
        return True, "tests-only commit exempt"
    if not _has_business_code_changes(files, root):
        return True, "no src/zephyr/**/*.py business code changes"
    return None


def _check_audit_log(session_id: str) -> tuple[bool, str]:
    """检查 audit log（目录存在性 + entry 数）。

    Returns:
        (passed, msg) — fail-closed：目录缺失/解析失败/entry_count=0 均阻断。
    """
    # 调公共 wrapper（audit_log_dir_exists / get_audit_log_path）而非私有
    # _audit_log_dir_exists / _get_audit_log_path——Stage 4 公共化后公共 wrapper
    # 是模块级名字，测试 patch "...capability_lookup_required_gate.audit_log_dir_exists"
    # 才能命中（与 forged_gw_marker_gate B1 修复同模式）。
    if not audit_log_dir_exists():
        return False, (
            f"CAPABILITY-LOOKUP-REQUIRED: audit log 目录缺失 "
            f"({MAIN_REPO_ROOT / LOOKUP_AUDIT_DIR_REL})。"
            f"修复：mkdir {LOOKUP_AUDIT_DIR_REL} 或确认 .runtime/ 未被误删。"
            f"病根3治本：删目录绕过是红蓝攻击向量，fail-closed 阻断。"
        )
    log_path = get_audit_log_path(session_id)
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
            f"逃生通道：commit msg 含 [no-lookup:<白名单 reason>] 标记"
            f"（如 gate-fix/test-fix/continuation）或设 ZEPHYR_BYPASS_LOOKUP=1。"
            f"白名单见 trae_077 YAML。"
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
        # 文件分类锚定 gateway.project_root（commit 文件所在工作区，worktree 场景
        # 与模块级 REPO_ROOT 不同，#ARCH-WORKTREE-ENV-001）
        exempt = _check_exemptions(files, gateway.project_root)
        if exempt is not None:
            return exempt

        # session_id 缺失放行（SESSION-REQUIRED gate priority=31 已先行检查）
        session_id = kwargs.get("session_id", "")
        if not session_id or session_id in ("unknown", "none", "null"):
            return True, "session_id missing (SESSION-REQUIRED gate priority=31 handles this)"

        # audit log 检查（fail-closed）
        return _check_audit_log(session_id)

    return GateSpec(gate_id="CAPABILITY-LOOKUP-REQUIRED", check=_check, priority=110)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def get_audit_log_path(session_id) -> Path:
    """公共接口：get_audit_log_path（Stage 4 公共化）。"""
    return _get_audit_log_path(session_id)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def audit_log_dir_exists() -> bool:
    """公共接口：audit_log_dir_exists（Stage 4 公共化）。"""
    return _audit_log_dir_exists()
