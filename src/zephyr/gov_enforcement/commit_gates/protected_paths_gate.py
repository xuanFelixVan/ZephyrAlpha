# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.protected_paths_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); scripts.governance.d6_security.check_protected_paths (PROTECTED_PATTERNS 真源)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__ (via auto_register_gates)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged 文件含受保护路径（.gitignore/.gitattributes/AGENTS.md 等）且 commit message 无 [ARCH-APPROVAL:ISSUE_ID] 逃生标记时阻断；有逃生标记则放行并落审计；环境变量 ZEPHYR_PROTECTED_PATHS_BYPASS=1 放行（紧急逃生通道，落审计）；staged 为空放行；issue registry 读取异常降级为放行（fail-open，避免 registry 损坏阻断所有 commit）
# [MODIFY-GUARD] gate_id="PROTECTED-PATHS"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；PROTECTED_PATTERNS 真源=scripts/governance/d6_security/check_protected_paths.py（本 gate 不复制清单，运行时 import 复用）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——issue registry 读取异常降级为放行（fail-open）；pattern 匹配异常降级为放行
# [TESTS] tests/governance/commit_gates/test_protected_paths_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-MODEL-LIFECYCLE-001
"""
protected_paths_gate.py — 受保护路径写入检测门禁（PROTECTED-PATHS，#ARCH-MODEL-LIFECYCLE-001 P1 治本）

检测 staged 文件中是否包含受保护路径（.gitignore/.gitattributes/AGENTS.md 等）。
命中时硬阻断，除非 commit message 含 ``[ARCH-APPROVAL:ISSUE_ID]`` 逃生通道标记。

病根（第一性原理）
-----------------
``check_protected_paths.py`` 是手动工具（``--path``/``--session-log``），无自动触发源。
100% AI 开发场景下，AI 批量重写文件时曾副作用回退 ``.gitignore``/``.gitattributes`` 的
模型排除规则，导致 27 个代码包重新被误忽略。君子协定不够，需要机器可执行的自动防护。

治本方案：双层自动防护
----------------------
1. **Layer 1（本 gate）**: in-process，走 ``GitCommitGateway.commit()`` 时拦截
   （A 层主防线，``--no-verify`` 绕不过）
2. **Layer 2（pre-commit hook）**: 走 ``git commit`` 时拦截（``--no-verify`` 可绕过但有审计）
3. **Layer 3（已有）**: ``check_protected_paths.py`` 手动工具（兜底）

逃生通道设计
------------
- commit message 含 ``[ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001]`` 标记 → 放行（落审计）
- 环境变量 ``ZEPHYR_PROTECTED_PATHS_BYPASS=1`` → 放行（紧急逃生，落审计）
- issue_id 可被 post-commit reconciler 校验是否在 architecture_issue_registry.yaml 登记

设计权衡
--------
1. **硬阻断而非 warn-only**：受保护路径回退是高严重度事故（27 包误忽略），
   warn-only 在 100% AI 场景下不构成闭环（AI 把 warn 当"通过"）
2. **fail-open for registry**：issue registry 读取异常降级为放行，
   避免 registry 损坏阻断所有 commit（治理工具不能成为单点故障）
3. **不复制 PROTECTED_PATTERNS**：真源是 ``check_protected_paths.py``，
   本 gate 运行时 import 复用，避免多真源漂移
4. **priority=28**：在所有 gate 之前执行（基础设施级检查，最早拦截），
   早于 FORGED-GW-MARKER(29) / DIRECTORY-CONTRACT(30) / SESSION-REQUIRED(31)

关联
----
- 裁定: #ARCH-MODEL-LIFECYCLE-001 P1（双层自动防护治本）
- 手动工具真源: scripts/governance/d6_security/check_protected_paths.py
- issue 登记: docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml
- pre-commit hook: .pre-commit-config.yaml (gate-protected-paths)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: file_path 参数
#   fields: 参数 file_path，类型注解 str
#   code: protected_paths_gate.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: files 参数
#   fields: 参数 files，类型注解 list[str]
#   code: protected_paths_gate.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① make_protected_paths_gate
#   name_en: make_protected_paths_gate
#   intro: 构造受保护路径写入检测 GateSpec。
#   desc: 构造受保护路径写入检测 GateSpec。 Returns: GateSpec(gate_id="PROTECTED-PATHS", priority=28)。 priority…；源码 L259-L354
#   inputs: 无参数
#   outputs: GateSpec
# - id: A2
#   name_zh: ② is_protected
#   name_en: is_protected
#   intro: 公共接口：检查文件路径是否受保护（Stage 4 公共化）。
#   desc: 公共接口：检查文件路径是否受保护（Stage 4 公共化）。；源码 L358-L360
#   inputs: file_path
#   outputs: bool
# - id: A3
#   name_zh: ③ find_protected_hits
#   name_en: find_protected_hits
#   intro: 公共接口：找出 staged 文件中的受保护路径命中（Stage 4 公共化）。
#   desc: 公共接口：找出 staged 文件中的受保护路径命中（Stage 4 公共化）。；源码 L363-L365
#   inputs: files
#   outputs: list[tuple[str, str]]
# 层: 输出
# - id: O1
#   name_zh: GateSpec
#   name_en: GateSpec
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__…
# - id: O2
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

# 逃生通道 env（紧急逃生，落审计）
_BYPASS_ENV = "ZEPHYR_PROTECTED_PATHS_BYPASS"

# [ARCH-APPROVAL:ISSUE_ID] 标记检测正则——真源=check_protected_paths.APPROVAL_MARKER_RE
# （SSoT，_load_protected_patterns 同通道 import）；import 失败回退本地编译同款。
# 匹配 [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001] / [ARCH-APPROVAL:#ARCH-007] 等
_APPROVAL_MARKER_RE = re.compile(r"\[ARCH-APPROVAL:(#?ARCH-[A-Z0-9_-]+)\]")
_APPROVAL_MARKER_RE_LOADED = False

# 受保护路径真源——运行时 import check_protected_paths.PROTECTED_PATTERNS
# 避免复制造成多真源漂移（SSoT 原则）
_PROTECTED_PATTERNS: list[tuple[str, str]] | None = None


def _load_protected_patterns() -> list[tuple[str, str]]:
    """从 check_protected_paths.py 加载受保护路径清单（SSoT 复用）。

    Returns:
        受保护路径列表 [(pattern, reason), ...]。
        import 失败时返回空列表（fail-open，但会落 warning）。
    """
    global _PROTECTED_PATTERNS
    if _PROTECTED_PATTERNS is not None:
        return _PROTECTED_PATTERNS

    try:
        # check_protected_paths.py 在 scripts/governance/d6_security/ 下，
        # 不在 src/zephyr/ 包结构中，需要路径注入 import
        import sys

        from zephyr.shared.io.paths import REPO_ROOT

        gov_dir = Path(REPO_ROOT) / "scripts" / "governance" / "d6_security"
        if str(gov_dir) not in sys.path:
            sys.path.insert(0, str(gov_dir))
        from check_protected_paths import PROTECTED_PATTERNS  # type: ignore[import-not-found]

        _PROTECTED_PATTERNS = list(PROTECTED_PATTERNS)
        # B4 治本（2026-08-19）：审批标记正则 SSoT 对齐（同通道 import，禁复制防漂移）
        global _APPROVAL_MARKER_RE, _APPROVAL_MARKER_RE_LOADED
        if not _APPROVAL_MARKER_RE_LOADED:
            from check_protected_paths import APPROVAL_MARKER_RE  # type: ignore[import-not-found]

            _APPROVAL_MARKER_RE = APPROVAL_MARKER_RE
            _APPROVAL_MARKER_RE_LOADED = True
    except Exception:  # noqa: BLE001 — fail-open: import 失败降级为内置清单
        # import 失败——降级为内置最小清单（.gitignore/.gitattributes/AGENTS.md）
        # 这是 fail-open 的保守降级：至少保护核心文件
        _PROTECTED_PATTERNS = [
            (".git/", "只读——禁止任何操作"),
            ("AGENTS.md", "重大修改须 Owner 审批"),
            (".gitignore", "模型排除规则（ARCH-MODEL-LIFECYCLE-001），修改须通过该流程审批"),
            (".gitattributes", "LFS 规则已移除（ARCH-MODEL-LIFECYCLE-001），修改须通过该流程审批"),
        ]
    return _PROTECTED_PATTERNS


def _audit_bypass(gateway: object, files: list[str], reason: str, issue_id: str | None = None) -> None:
    """落审计：逃生通道使用记录（PROTECTED-PATHS gate 真源）。

    fail-open：审计写入失败不阻断 commit（check_all ERROR_CONTRACT：永不抛异常）。

    Args:
        gateway: GitCommitGateway 实例（取 project_root）。
        files: staged 文件列表。
        reason: 逃生原因（"env_bypass" / "approval_marker"）。
        issue_id: 审批标记中的 issue_id（reason="approval_marker" 时填）。
    """
    try:
        root = Path(getattr(gateway, "project_root", "."))
        audit_dir = root / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": int(time.time()),  # 审计事件时间戳（m46-time 豁免：gate 审计需 epoch 秒）
            "gate": "PROTECTED-PATHS",
            "reason": reason,
            "issue_id": issue_id,
            "files_count": len(files),
            "protected_hits": [f for f in files if _is_protected(f)],
        }
        with (audit_dir / "protected_paths_bypass.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001
        # 审计写入失败不阻断 commit
        pass


def _is_protected(file_path: str) -> bool:
    """检查文件路径是否匹配受保护路径清单。

    Args:
        file_path: 文件相对路径（可能含正斜杠或反斜杠）。

    Returns:
        True=受保护，False=不受保护。pattern 匹配异常降级为 False（保守不阻断）。
    """
    try:
        normalized = file_path.replace("\\", "/")
        # 去除前导 ./（git status 有时输出 ./path）
        if normalized.startswith("./"):
            normalized = normalized[2:]
        for pattern, _reason in _load_protected_patterns():
            if pattern in normalized or normalized.startswith(pattern):
                return True
        return False
    except Exception:  # noqa: BLE001
        return False


def _find_protected_hits(files: list[str]) -> list[tuple[str, str]]:
    """从 staged 文件列表中找出受保护路径命中。

    Args:
        files: staged 文件相对路径列表。

    Returns:
        命中列表 [(file_path, reason), ...]。
    """
    hits: list[tuple[str, str]] = []
    patterns = _load_protected_patterns()
    for f in files:
        try:
            normalized = f.replace("\\", "/")
            if normalized.startswith("./"):
                normalized = normalized[2:]
            for pattern, reason in patterns:
                if pattern in normalized or normalized.startswith(pattern):
                    hits.append((f, reason))
                    break
        except Exception:  # noqa: BLE001
            continue
    return hits


def make_protected_paths_gate() -> GateSpec:
    """构造受保护路径写入检测 GateSpec。

    Returns:
        GateSpec(gate_id="PROTECTED-PATHS", priority=28)。
        priority=28 早于 FORGED-GW-MARKER(29) / DIRECTORY-CONTRACT(30) / SESSION-REQUIRED(31)，
        确保受保护路径检查最先执行（基础设施级检查，最早拦截）。
    """

    def _check(gateway: object, files: list[str], **kwargs: Any) -> tuple[bool, str]:
        """检测 staged 文件中是否含受保护路径。

        判定逻辑：
        - staged 为空 → 放行
        - 无受保护路径命中 → 放行
        - 有命中 + ZEPHYR_PROTECTED_PATHS_BYPASS=1 env → 放行（落审计）
        - 有命中 + commit message 含 [ARCH-APPROVAL:ISSUE_ID] → 放行（落审计）
        - 有命中 + 无逃生通道 → 阻断
        """
        # 1. staged 为空 → 放行
        if not files:
            return True, "no staged files, skip protected paths check"

        # 2. 找受保护路径命中
        hits = _find_protected_hits(files)
        if not hits:
            return True, "no protected paths in staged files"

        # 3. 有命中——检查逃生通道
        # 3a. 环境变量逃生通道（紧急）
        if os.environ.get(_BYPASS_ENV) == "1":
            _audit_bypass(gateway, files, "env_bypass")
            return True, (
                f"PROTECTED-PATHS: {len(hits)} protected file(s) staged but {_BYPASS_ENV}=1 env set "
                f"(emergency bypass, audited): {hits[:3]}"
            )

        # 3b. commit message 审批标记逃生通道
        commit_msg: str | None = kwargs.get("commit_message") or kwargs.get("message")
        if commit_msg:
            match = _APPROVAL_MARKER_RE.search(commit_msg)
            if match:
                issue_id = match.group(1)
                _audit_bypass(gateway, files, "approval_marker", issue_id)
                return True, (
                    f"PROTECTED-PATHS: {len(hits)} protected file(s) staged but commit message "
                    f"contains [ARCH-APPROVAL:{issue_id}] (approved, audited): {hits[:3]}"
                )

        # 3c. B4 治本（2026-08-19）：merge finalize 场景审批转置——受保护改动在分支侧
        # commit 已验过 [ARCH-APPROVAL]（Layer 1 在分支 commit 时检查），merge commit 只是
        # 搬运，重复要求 merge message 带标记=重复审批（05/08 两域被拦实证）。
        # 判据：gateway 检测到在途 merge（B2① 落地后=显式 --merge-finalize 场景）；
        # 逐文件枚举分支侧 commit 链（HEAD..第二父），任一带标记→放行（落审计）；
        # 核验异常/无标记→维持阻断（受保护路径高危区 fail-closed）。
        try:
            if getattr(gateway, "_is_merge_in_progress", lambda: False)():
                from check_protected_paths import (  # type: ignore[import-not-found]
                    _branch_side_approved,
                    _branch_side_commits_touching,
                    _merge_head_shas,
                )

                gw_cwd = str(getattr(gateway, "project_root", ".") or ".")
                merge_shas = _merge_head_shas(cwd=gw_cwd)
                if merge_shas:
                    unapproved: list[str] = []
                    approved_issue: str | None = None
                    for f, _reason in hits:
                        commits = _branch_side_commits_touching(merge_shas, f, cwd=gw_cwd)
                        ok, issue = _branch_side_approved(commits, cwd=gw_cwd)
                        if ok:
                            approved_issue = approved_issue or issue
                        else:
                            unapproved.append(f)
                    if not unapproved:
                        _audit_bypass(gateway, files, "merge_branch_approval", approved_issue)
                        return True, (
                            f"PROTECTED-PATHS: {len(hits)} protected file(s) from merge, "
                            f"branch-side commits approved "
                            f"([ARCH-APPROVAL:{approved_issue}], audited): {hits[:3]}"
                        )
        except Exception:  # noqa: BLE001 — 合并态核验异常不打开逃生口，维持阻断判定
            pass

        # 4. 有命中 + 无逃生通道 → 阻断
        hits_desc = "; ".join(f"{f} ({r})" for f, r in hits[:5])
        return False, (
            f"PROTECTED-PATHS: staged files contain protected paths ({len(hits)} hit(s)): "
            f"{hits_desc}. 修改受保护路径须经审批流程。"
            f"逃生通道：① commit message 加 [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001] 标记；"
            f"② 紧急情况设 ZEPHYR_PROTECTED_PATHS_BYPASS=1 env（落审计）。"
            f"详见 #ARCH-MODEL-LIFECYCLE-001 与 check_protected_paths.py。"
        )

    return GateSpec(gate_id="PROTECTED-PATHS", check=_check, priority=28)


# ── Stage 4 公共化（2026-08-03）：public wrapper ──
def is_protected(file_path: str) -> bool:
    """公共接口：检查文件路径是否受保护（Stage 4 公共化）。"""
    return _is_protected(file_path)


def find_protected_hits(files: list[str]) -> list[tuple[str, str]]:
    """公共接口：找出 staged 文件中的受保护路径命中（Stage 4 公共化）。"""
    return _find_protected_hits(files)
