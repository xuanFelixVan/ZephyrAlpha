# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.ruling_commit_verified_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.gov_enforcement.commit_gates._reference_helpers (get_head_content)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只检测 staged 触发文件中**新增的**"已完成（commit XXX）"声明（diff-based，不阻断历史）；fail-closed——commit hash 不存在时阻断；跳过 tests/ 豁免区；触发文件 ruling_*.md + architecture_issue_registry.yaml；正则匹配"已完成...commit <7-40 hex>"；用 git cat-file -e 验证 hash 存在性；非 git 仓库（tmp_path 测试）skip；逃生通道 commit msg 含 [no-verify-ruling:<reason>]
# [MODIFY-GUARD] gate_id="RULING-COMMIT-VERIFIED"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；priority=109
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git 异常降级为 fail-closed 阻断（passed=False，detail 含修复指引）
# [TESTS] tests/governance/commit_gates/test_ruling_commit_verified_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-WORKSPACE-DRIFT-SYSTEMIC-001
"""ruling_commit_verified_gate.py — 文档"已完成"声明 commit hash 真实性硬验证门禁（RULING-COMMIT-VERIFIED）

检测 staged 触发文件中**新增的**"已完成（commit XXX）"声明，验证 XXX 在 git history 中真实存在。
命中不存在的 hash 则阻断 commit（``RULING_COMMIT_VERIFIED_VIOLATION``）。

病根（第一性原理，#ARCH-WORKSPACE-DRIFT-SYSTEMIC-001 盲区 4）
------------------------------------------------------------
AI 在 ruling 文档或 architecture_issue_registry.yaml 中写"已完成（commit XXX）"但 XXX 可能：
1. 不存在（AI 凭记忆捏造 / 拼写错误 / 截断错误）
2. 是其他仓库的 commit hash（跨仓库混淆）
3. 未合并到当前分支（声明完成但实际未 merge）

100% AI 开发场景下，后续 AI 读取这些声明时会基于错误信息做决策——
"裁定已 resolved，commit XXX 已落地"→ 实际 XXX 不存在 → 后续工作建立在幻觉上。

治本方案
--------
在 GitCommitGateway pre-commit 阶段注册门禁，检测**新增的**"已完成"声明中的
commit hash，用 ``git cat-file -e <hash>`` 验证存在性。只检测新增声明（diff-based），
不阻断历史声明——增量检测让历史问题逐步清理，新声明零容忍。

设计决策
--------
1. **只检测新增声明**：通过 ``git show HEAD:<path>`` 获取 HEAD 版本，比较
   新增的"已完成...commit XXX"声明。新文件（HEAD 不存在）的全部声明视为新增。
2. **fail-closed**：commit hash 不存在 / git 异常时阻断——100% AI 场景下 warn 无效。
3. **触发文件范围**：``docs/_archive/ruling_*.md``（迁移后主路径）+
   ``docs/02_enterprise_architecture/ruling_*.md``（向后兼容）+
   ``architecture_issue_registry.yaml``——治本聚焦，不扫全项目。
4. **priority=109**：原 77 与 BLUEPRINT-FORMAT 撞号（#ARCH-GATE-PRIORITY-UNIQUENESS-001
   Phase 1 治本），后到者让位迁移至 109——紧邻 CAPABILITY-LOOKUP-REQUIRED(110)，
   同属"AI 行为强制/文档真实性"类检查（RULING-COMMIT-VERIFIED 验证文档声明真实性，
   CAPABILITY-LOOKUP-REQUIRED 强制 AI 查 capability，都是 AI 行为约束）。
   历史先例（后到者让位）：DATA-TASK 78->41 / RENAME-DEPGRAPH-SYNC 36->39 /
   ORPHAN-MODULE 86->89 / DOC-REF-BROKEN 88->91 / RULING-COMMIT-VERIFIED 77->109
5. **正则提取**：``已完成.*?commit\\s+([0-9a-f]{7,40})`` 匹配
   "已完成（commit fadd3fdc）" / "已完成 2026-07-20，commit 2cee176f81，merge ..." 等。
6. **逃生通道**：commit message 含 ``[no-verify-ruling:<reason>]`` 标记时 skip
   （对标 CAPABILITY-LOOKUP-REQUIRED 的 [no-lookup] 模式）。
7. **非 git 仓库 skip**：tmp_path 测试仓库等非 Zephyr 项目返回 None 跳过。

Usage::

    from zephyr.gov_enforcement.commit_gates.ruling_commit_verified_gate import make_ruling_commit_verified_gate

    registry.register(make_ruling_commit_verified_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import logging
import os
import re
import subprocess
from pathlib import Path

from zephyr.gov_enforcement.commit_gates._reference_helpers import get_head_content
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    GateSpec,
    is_test_exempt,
)
from zephyr.shared.infra.process_pool import run_subprocess_hidden

logger = logging.getLogger(__name__)

__all__ = ["make_ruling_commit_verified_gate"]

# "已完成...commit <7-40 hex>" 声明检测正则
# 匹配："已完成（commit fadd3fdc）" / "已完成 2026-07-20，commit 2cee176f81，merge ..."
# / "Phase 1 已完成（commit 290df512 + 0a69d345）"（取第一个 hash）
# 大小写不敏感（"已完成" 中文不分大小写，"commit" 英文支持 COMMIT/Commit）
# 使用 re.DOTALL 让 . 匹配换行（多行 block scalar 中"已完成...commit"可能跨行）
_RULING_COMMIT_RE = re.compile(
    r"已完成.*?commit\s+([0-9a-f]{7,40})",
    re.IGNORECASE | re.DOTALL,
)

# 触发文件路径模式（相对路径，正斜杠）
# 1. docs/_archive/ruling_*.md（迁移后主路径，2026-07-23 从 02_enterprise_architecture/ 迁入）
# 2. docs/02_enterprise_architecture/ruling_*.md（向后兼容，防止遗漏）
# 3. docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml
_TRIGGER_PATTERNS = (
    "docs/_archive/ruling_",
    "docs/02_enterprise_architecture/ruling_",
    "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml",
)

# 逃生通道标记（commit message 中）
_ESCAPE_MARKER = "[no-verify-ruling:"

# git cat-file 超时（秒）
_GIT_CAT_FILE_TIMEOUT = 10


def _is_trigger_file(rel_path: str) -> bool:
    """判断文件是否为触发文件（ruling_*.md 或 architecture_issue_registry.yaml）。"""
    rel = rel_path.replace("\\", "/")
    for pattern in _TRIGGER_PATTERNS:
        if rel.startswith(pattern) or rel == pattern:
            return True
    return False


def _extract_commit_hashes(content: str) -> set[str]:
    """从文本提取所有"已完成...commit XXX"声明中的 commit hash。

    Args:
        content: 文件文本。

    Returns:
        commit hash 集合（如 {"fadd3fdc", "290df512"}）。
    """
    return set(_RULING_COMMIT_RE.findall(content))


def _verify_commit_exists(project_root: Path, commit_hash: str) -> bool:
    """验证 commit hash 在 git history 中真实存在。

    用 ``git cat-file -e <hash>`` 验证（轻量，不读对象内容）。

    Args:
        project_root: 仓库根路径。
        commit_hash: 待验证的 commit hash（7-40 hex）。

    Returns:
        True 表示存在；False 表示不存在或 git 命令失败（fail-closed）。
    """
    try:
        result = run_subprocess_hidden(
            ["git", "cat-file", "-e", commit_hash + "^{commit}"],
            capture_output=True,
            cwd=str(project_root),
            timeout=_GIT_CAT_FILE_TIMEOUT,
        text=False)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError) as e:
        logger.warning(
            "ruling_commit_verified_gate: git cat-file failed for %s: %s",
            commit_hash, e,
        )
        return False  # fail-closed


def _check_escape_marker(kwargs: dict) -> bool:
    """检测 commit message 是否含逃生通道标记 [no-verify-ruling:<reason>]。

    Args:
        kwargs: gate check_all 传入的 kwargs（含 commit_message）。

    Returns:
        True 表示启用逃生通道（skip 检测）。
    """
    commit_message = kwargs.get("commit_message", "") or ""
    return _ESCAPE_MARKER in commit_message


def _format_violations_detail(violations: list[tuple[str, list[str]]]) -> str:
    """格式化违规详情。

    Args:
        violations: [(rel_path, [invalid_hash, ...]), ...] 列表。

    Returns:
        格式化的错误详情字符串。
    """
    detail_lines = []
    for rel, hashes in violations:
        detail_lines.append(f"  - {rel}: commit {', commit '.join(hashes)}")
    return (
        "RULING_COMMIT_VERIFIED_VIOLATION——以下文件新增了'已完成（commit XXX）'声明，"
        "但 XXX 在 git history 中不存在：\n"
        + "\n".join(detail_lines)
        + "\n修复：1) 确认 commit hash 拼写正确（7-40 hex）；"
        "2) 确认 commit 已合并到当前分支（git log --oneline | findstr <hash>）；"
        "3) 如为占位/草稿，移除'已完成'声明或改为'待完成'。"
        "逃生通道：commit message 含 [no-verify-ruling:<reason>] 标记。"
    )


def _detect_violations(
    project_root: Path,
    files: list[str],
) -> tuple[list[tuple[str, list[str]]], str | None]:
    """遍历触发文件，检测新增"已完成"声明中不存在的 commit hash。

    Args:
        project_root: 仓库根路径。
        files: commit 涉及的文件列表（绝对路径）。

    Returns:
        (violations, error) ——
        violations: [(rel_path, [invalid_hash, ...]), ...] 列表；
        error: 非 None 时表示 git 操作失败（fail-closed），调用方应直接返回。
    """
    violations: list[tuple[str, list[str]]] = []

    for f in files:
        if not os.path.isfile(f):
            continue
        rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
        if is_test_exempt(rel):
            continue
        if not _is_trigger_file(rel):
            continue

        try:
            current_content = Path(f).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        current_hashes = _extract_commit_hashes(current_content)
        if not current_hashes:
            continue

        # 获取 HEAD 版本，计算新增声明（diff-based）
        try:
            head_content = get_head_content(project_root, rel)
        except OSError as e:
            return [], f"git show failed for {rel} (fail-closed): {e}"

        if head_content is None:
            new_hashes = current_hashes  # 新文件，全部视为新增
        else:
            head_hashes = _extract_commit_hashes(head_content)
            new_hashes = current_hashes - head_hashes

        if not new_hashes:
            continue

        # 验证新增 commit hash 存在性
        invalid_hashes = sorted(
            h for h in new_hashes if not _verify_commit_exists(project_root, h)
        )
        if invalid_hashes:
            violations.append((rel, invalid_hashes))

    return violations, None


def make_ruling_commit_verified_gate() -> GateSpec:
    """构造"已完成"声明 commit hash 硬验证门禁 GateSpec（fail-closed，阻断型）。

    Returns:
        GateSpec(gate_id="RULING-COMMIT-VERIFIED", priority=109)。
        priority=109——原 77 与 BLUEPRINT-FORMAT 撞号（#ARCH-GATE-PRIORITY-UNIQUENESS-001
        Phase 1 治本），后到者让位迁移至 109，紧邻 CAPABILITY-LOOKUP-REQUIRED(110)，
        同属"AI 行为强制/文档真实性"类检查.
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 逃生通道：commit message 含 [no-verify-ruling:<reason>]
        if _check_escape_marker(kwargs):
            return True, "escape marker [no-verify-ruling] detected, skipping"

        # 非 Zephyr 项目 skip（tmp_path 测试仓库等）
        _governance_dir = gateway.project_root / "scripts" / "governance" / "d1_structure"
        if not _governance_dir.is_dir():
            return True, "non-Zephyr project, skipping RULING-COMMIT-VERIFIED"

        violations, error = _detect_violations(gateway.project_root, files)
        if error is not None:
            return False, error
        if violations:
            return False, _format_violations_detail(violations)
        return True, ""

    return GateSpec(gate_id="RULING-COMMIT-VERIFIED", check=_check, priority=109)
