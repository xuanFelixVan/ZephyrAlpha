#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-SCRIPTS-006 | scripts/governance/check_commit_message.py | §ARCH-PREVENTABILITY-LAYER-001 Phase 4 P4-3
# [MODULE] scripts.governance.check_commit_message
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib (json, os, re, subprocess, sys, pathlib)
# [CONSUMERS] .github/workflows/commit_message_guard.yml
# [STARTUP] event_driven  GitHub Actions pull_request 事件自动触发（非 manual）
# [MATURITY] production
# [INVARIANTS] 零项目依赖（纯 stdlib，CI 无需安装项目即可运行）；merge commit 豁免；[GW:session_id] 标记 + session_id 合法性校验；CI 模式（registry 不存在）降级为 session_id 格式校验
# [MODIFY-GUARD] _GW_MARKER_RE / _SESSION_ID_RE / _REGISTRY_PATH / _WHITELIST_TYPES / _MERGE_PREFIX_RE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] registry 文件不存在/损坏降级为格式校验；git log 失败 exit 2
# [TESTS] tests/governance/test_check_commit_message.py
# [A_module] module_id=MOD-SCRIPTS-006 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m07-orphan  M07豁免: 被 .github/workflows/commit_message_guard.yml 调用（非 import 引用，是 CLI 调用）
# noqa: m11-perm-manual-legitimate  M11豁免: GitHub Actions pull_request 事件自动触发（ubuntu-latest），非 manual 命令行脚本
"""check_commit_message.py — GitHub Actions PR commit message guard (P4-3).

#ARCH-PREVENTABILITY-LAYER-001 Phase 4 P4-3 (2026-07-20)
=========================================================
- **治本动机**：原计划 server-side pre-receive hook 在 GitHub-hosted 仓库
  不可部署（需 GitHub Enterprise）。改走 GitHub Actions——对 PR 的每个
  commit 检查 commit message 是否带 ``[GW:session_id]`` 标记 + session_id
  合法性（对标 ``forged_gw_marker_gate.py`` 的检测逻辑）。
- **强制层级**：PR 阶段（非 commit 阶段）。本地 commit 仍可绕过，但 push
  到 GitHub 后 PR 阶段会阻断 merge（配合 Branch Protection required
  status check）。
- **设计原则**：
  1. **零项目依赖**——纯 stdlib 实现，CI 无需安装项目即可运行（快速）
  2. **复用 forged_gw_marker_gate 的判定逻辑**——``[GW:`` 标记 +
     session_id 注册表校验
  3. **merge commit 豁免**——GitHub merge commit 由平台生成，无 [GW:] 标记
  4. **白名单豁免**——doc-only / tests-only / chore / merge 等 conventional
     commit type 无需 [GW:] 标记（与 GitCommitGateway 豁免清单一致）

判定逻辑（与 forged_gw_marker_gate.py 对齐）
---------------------------------------------
- merge commit（``Merge branch``/``Merge pull request`` 前缀）→ 放行
- commit msg 含 ``[GW:`` + session_id 已注册 → 放行（合法 GW commit）
- commit msg 含 ``[GW:`` + session_id 未注册 → **阻断**（forged_gw_marker）
- commit msg 不含 ``[GW:`` + type ∈ 白名单（docs/tests/chore/ci/style/refactor）
  → 放行（白名单 commit 无需 GW 标记）
- commit msg 不含 ``[GW:`` + type ∉ 白名单 → **阻断**（non-GW commit）

Usage
-----
本脚本设计为 GitHub Actions workflow 调用::

    # .github/workflows/commit_message_guard.yml
    - name: Check commit messages
      run: python scripts/governance/check_commit_message.py ${{ github.event.pull_request.base.sha }}..${{ github.event.pull_request.head.sha }}

Exit Codes
----------
- 0: 所有 commit 通过检查
- 1: 有违规 commit（阻断 PR merge）

环境变量
--------
- ``ZEPHYR_COMMIT_MSG_GUARD_STRICT``：设为 ``1`` 时禁用白名单豁免（所有
  非 merge commit 都必须带 [GW:] 标记）。默认 ``0``（启用白名单）。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: check_commit_message.py — GitHub Actions PR commit message guard (P4-3).
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


from _shared.constants import EXIT_PASS, EXIT_FINDINGS, EXIT_ERROR

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# 与 forged_gw_marker_gate.py 对齐的常量（复制以保持零依赖）
_GW_MARKER_RE = re.compile(r"\[GW:")
_SESSION_ID_RE = re.compile(r"\[GW:(sess-[^\]:}]*)")

# SessionRegistry 文件路径（与 session_concurrency.py:_REGISTRY_PATH 对齐）
# 注意：.runtime/ 在 .gitignore 中，CI 环境无此文件——此时降级为格式校验
_REGISTRY_PATH = Path(".runtime") / "session_registry.json"

# session_id 格式正则（与 session_claim.generate_session_id 对齐）
# 格式：sess-{4-8位数字}-{14位时间戳YYYYMMDDHHMMSS}
# CI 无 registry 时用此格式校验替代注册表查询（fail-open for CI）
_SESSION_ID_FORMAT_RE = re.compile(r"^sess-\d{4,8}-\d{14}$")

# 白名单 conventional commit type（无需 [GW:] 标记）
# 与 GitCommitGateway 的 doc-only / tests-only 豁免对齐
_WHITELIST_TYPES = frozenset({
    "docs",      # 文档变更
    "test",      # 测试变更
    "chore",     # 构建/工具变更
    "ci",        # CI 配置变更
    "style",     # 代码风格变更（不影响逻辑）
    "refactor",  # 重构（不改行为）
    "revert",    # 回滚
    "perf",      # 性能优化（不改行为）
})

# Conventional commit type 正则（type(scope): description）
_CONVENTIONAL_RE = re.compile(r"^([a-z]+)(?:\([^)]*\))?!?:")

# merge commit 前缀正则（GitHub merge commit / squash merge / manual merge）
_MERGE_PREFIX_RE = re.compile(
    r"^(?:Merge (?:branch|pull request|remote-tracking)|"
    r"Squashed commit|"
    r"#\d+ )",
    re.IGNORECASE,
)


def _extract_session_id(commit_msg: str) -> str | None:
    """从 commit message 提取 [GW:session_id] 标记中的 session_id。

    与 forged_gw_marker_gate._extract_session_id 对齐。
    """
    if not commit_msg:
        return None
    match = _SESSION_ID_RE.search(commit_msg)
    if not match:
        return None
    return match.group(1)


def _load_registered_sessions(registry_path: Path) -> set[str]:
    """加载 SessionRegistry 中所有已注册的 session_id。

    与 SessionRegistry._load 对齐（文件不存在/损坏返回空 set）。
    在 CI 环境中，registry 文件是 commit 入库的快照——已 merge 的 session
    仍保留在 registry 中（除非显式 unregister），故合法 GW commit 的
    session_id 一定可查到。

    Args:
        registry_path: .runtime/session_registry.json 路径

    Returns:
        set[str] — 已注册 session_id 集合；文件不存在/损坏返回空 set
    """
    try:
        if not registry_path.exists():
            return set()
        content = registry_path.read_text(encoding="utf-8")
        if not content.strip():
            return set()
        data = json.loads(content)
        if not isinstance(data, dict):
            return set()
        return {sid for sid in data.keys() if isinstance(sid, str) and sid.startswith("sess-")}
    except (OSError, ValueError):
        return set()


def _extract_commit_type(subject: str) -> str | None:
    """从 commit subject 提取 conventional commit type。

    Args:
        subject: commit message 第一行

    Returns:
        type 字符串（如 ``docs``/``feat``）；非 conventional 格式返回 None
    """
    match = _CONVENTIONAL_RE.match(subject)
    if not match:
        return None
    return match.group(1)


def _is_merge_commit(subject: str) -> bool:
    """判断是否为 merge commit（GitHub merge / squash merge / manual merge）。"""
    return bool(_MERGE_PREFIX_RE.match(subject))


def _check_commit(
    commit_sha: str,
    commit_msg: str,
    registered_sessions: set[str],
    strict: bool,
) -> list[str]:
    """检查单个 commit 的 message 是否合规。

    Args:
        registered_sessions: 已注册 session_id 集合。**空集合表示 CI 无
            registry 文件**（.runtime/ 在 .gitignore 中），此时降级为
            session_id 格式校验（sess-NNNN-YYYYMMDDHHMMSS），避免所有
            合法 GW commit 在 CI 上被误判为 forged。

    Returns:
        list[str] — 违规原因列表（空=合规）
    """
    violations: list[str] = []
    subject = commit_msg.split("\n", 1)[0].strip() if commit_msg else ""

    # 1. merge commit 豁免
    if _is_merge_commit(subject):
        return violations

    # 2. 提取 [GW:session_id] 标记
    session_id = _extract_session_id(commit_msg)

    if session_id is not None:
        # 含 [GW: 标记——校验 session_id 合法性
        if registered_sessions:
            # 本地环境：registry 存在，校验注册表成员资格
            if session_id not in registered_sessions:
                violations.append(
                    f"  {commit_sha[:8]}: forged_gw_marker — [GW:{session_id}] "
                    f"session_id 未在 SessionRegistry 注册（疑似伪造）"
                )
        else:
            # CI 环境：registry 不存在（.runtime/ gitignored），降级为格式校验
            # 格式合法 = session_id 由 generate_session_id 生成（非手工伪造）
            if not _SESSION_ID_FORMAT_RE.match(session_id):
                violations.append(
                    f"  {commit_sha[:8]}: forged_gw_marker — [GW:{session_id}] "
                    f"session_id 格式不合规（CI 模式：需匹配 sess-NNNN-YYYYMMDDHHMMSS）"
                )
        # 合法=放行
        return violations

    # 3. 不含 [GW: 标记——检查是否在白名单
    if not strict:
        commit_type = _extract_commit_type(subject)
        if commit_type and commit_type in _WHITELIST_TYPES:
            return violations  # 白名单 type 豁免

    # 4. 不含 [GW: 标记且不在白名单——non-GW commit
    violations.append(
        f"  {commit_sha[:8]}: non_gw_commit — commit message 缺 [GW:session_id] 标记 "
        f"且 type 不在白名单 {sorted(_WHITELIST_TYPES)}（subject: {subject[:60]!r}）"
    )
    return violations


def _get_pr_commits(base_sha: str, head_sha: str) -> list[tuple[str, str]]:
    """获取 PR 范围内的 commit 列表。

    Args:
        base_sha: PR base SHA（merge target）
        head_sha: PR head SHA（merge source）

    Returns:
        list[(sha, message)] — commit 列表，按时间顺序

    Raises:
        subprocess.CalledProcessError: git log 失败
    """
    result = subprocess.run(  # noqa: bare-subprocess  CI 环境（ubuntu-latest）无 process_pool 依赖，纯 stdlib 实现需裸 subprocess
        ["git", "log", "--format=%H%x1f%B%x1e", f"{base_sha}..{head_sha}"],
        capture_output=True,
        text=True,
        check=True,
    )
    commits: list[tuple[str, str]] = []
    for record in result.stdout.split("\x1e"):
        record = record.strip("\n")
        if not record:
            continue
        sha, _, msg = record.partition("\x1f")
        commits.append((sha.strip(), msg))
    return commits


def main(argv: list[str]) -> int:
    """CLI 入口。

    Args:
        argv: ``[base_sha..head_sha]`` 或 ``[base_sha, head_sha]``

    Returns:
        0=通过，1=有违规
    """
    if not argv:
        print(
            "Usage: check_commit_message.py <base_sha> <head_sha>\n"
            "       check_commit_message.py <base_sha>..<head_sha>",
            file=sys.stderr,
        )
        return EXIT_ERROR
    # 解析参数：支持 "base..head" 和 "base head" 两种形式
    if len(argv) == 1 and ".." in argv[0]:
        base_sha, head_sha = argv[0].split("..", 1)
    elif len(argv) >= 2:
        base_sha, head_sha = argv[0], argv[1]
    else:
        print(f"Error: invalid arguments: {argv}", file=sys.stderr)
        return EXIT_ERROR
    if not base_sha or not head_sha:
        print(f"Error: empty base_sha or head_sha: base={base_sha!r} head={head_sha!r}", file=sys.stderr)
        return EXIT_ERROR
    strict = os.environ.get("ZEPHYR_COMMIT_MSG_GUARD_STRICT", "0") == "1"

    # 加载已注册 session
    registered = _load_registered_sessions(_REGISTRY_PATH)

    # 获取 PR 范围内的 commit
    try:
        commits = _get_pr_commits(base_sha, head_sha)
    except subprocess.CalledProcessError as e:
        print(f"Error: git log failed: {e}", file=sys.stderr)
        print(f"  stderr: {e.stderr}", file=sys.stderr)
        return EXIT_ERROR
    if not commits:
        print(f"No commits in range {base_sha[:8]}..{head_sha[:8]}")
        return EXIT_PASS
    print(f"Checking {len(commits)} commit(s) in range {base_sha[:8]}..{head_sha[:8]}")
    print(f"  strict mode: {strict}")
    print(f"  registered sessions: {len(registered)}")

    all_violations: list[str] = []
    for sha, msg in commits:
        violations = _check_commit(sha, msg, registered, strict)
        all_violations.extend(violations)

    if all_violations:
        print(f"\nFAIL: {len(all_violations)} violation(s) detected:", file=sys.stderr)
        for v in all_violations:
            print(v, file=sys.stderr)
        print(
            "\n修复指引:\n"
            "  1. forged_gw_marker: 使用 GitCommitGateway/session_worktree_commit 提交，\n"
            "     禁止手工添加 [GW:session_id] 标记\n"
            "  2. non_gw_commit: 使用白名单 type (docs/test/chore/ci/style/refactor/revert/perf)\n"
            "     或通过 GitCommitGateway 提交（自动添加 [GW:session_id] 标记）",
            file=sys.stderr,
        )
        return EXIT_FINDINGS
    print(f"\nPASS: all {len(commits)} commit(s) compliant")
    return EXIT_PASS


# ── Stage 4 公共 API 别名（for testing, thin wrappers） ──
extract_session_id = _extract_session_id
load_registered_sessions = _load_registered_sessions
extract_commit_type = _extract_commit_type
is_merge_commit = _is_merge_commit
check_commit = _check_commit

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
