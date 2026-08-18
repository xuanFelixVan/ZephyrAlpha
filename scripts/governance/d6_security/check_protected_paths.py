# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/check_protected_paths.py | §
# [MODULE] scripts.governance.d6_security.check_protected_paths
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d6_security.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""check_protected_paths.py — 受保护路径写入检查（IRN-010）

对标：GOV-MOD-002 IRN-010（受保护路径不可写）

检测内容：
- 检查目标路径是否在受保护清单中
- 受保护路径：.git/、AGENTS.md、meta/*.md、architecture_model/
- --staged 模式：检查 git staged 文件（pre-commit hook Layer 2，#ARCH-MODEL-LIFECYCLE-001 P1）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args:
- {flag: --path, type: str, description: "检查指定路径是否受保护"}
- {flag: --session-log, type: str, description: "检查 Session Log 中的写入记录是否违反受保护路径"}
- {flag: --staged, type: bool, description: "检查 git staged 文件是否含受保护路径（pre-commit hook 模式）"}
description: >
  受保护路径写入检查（IRN-010）——检查目标路径是否在受保护清单中。
  对标 GOV-MOD-002 ai-behavior-iron-policy.md IRN-010。
  --staged 模式为 #ARCH-MODEL-LIFECYCLE-001 P1 双层防护 Layer 2（pre-commit hook）。
dimensions:
- D6
priority: P1
timeout_seconds: 15
warn_only: false
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

# 紧急逃生 env（与 protected_paths_gate.py _BYPASS_ENV 对齐）
_BYPASS_ENV = "ZEPHYR_PROTECTED_PATHS_BYPASS"

# [ARCH-APPROVAL:ISSUE_ID] 审批标记正则（SSoT——Layer 1 protected_paths_gate 运行时
# import 复用，禁复制防漂移）。匹配 [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001] /
# [ARCH-APPROVAL:#ARCH-007] 等。
APPROVAL_MARKER_RE = re.compile(r"\[ARCH-APPROVAL:(#?ARCH-[A-Z0-9_-]+)\]")

PROTECTED_PATTERNS = [
    (".git/", "只读——禁止任何操作"),
    ("AGENTS.md", "重大修改须 Owner 审批"),
    ("docs/01_policies_and_standards/rules/", "重大修改须 Owner 审批（rules/ 下所有 .yaml）"),
    ("architecture_model/", "重大修改须 Owner 审批"),
    # 治本 2026-08-03 (ARCH-MODEL-LIFECYCLE-001 P1)：并发会话批量重写文件时
    # 曾副作用回退 .gitignore/.gitattributes 的模型排除规则修复，导致 27 个代码包
    # 重新被误忽略。加入受保护清单后，AI 会话写入这两个文件前会被 IRN-010 拦截，
    # 强制走 ARCH-MODEL-LIFECYCLE-001 流程显式审批，防止静默回退。
    (".gitignore", "模型排除规则（ARCH-MODEL-LIFECYCLE-001），修改须通过该流程审批"),
    (".gitattributes", "LFS 规则已移除（ARCH-MODEL-LIFECYCLE-001），修改须通过该流程审批"),
]

# GAP-010（2026-08-12）：AI 金融代码高敏区——下单/资金/风控/成本四类文件
# CSA 2026 实证：45% AI 代码含 OWASP Top10 漏洞、19.7% 概率幻觉不存在依赖包
# 高敏区文件变更时输出 WARNING（不阻断——人审是软约束，阻断会卡住正常迭代）
# 升级现有 gate 不新增 gate，守 I-GOV-3 gate ≤ 54
HIGH_SENSITIVITY_PATTERNS = [
    ("src/zephyr/ex_core/", "下单/执行层——AI 生成代码须人审+边界单测（涨跌停/停牌/除权/T+1/断线）"),
    ("src/zephyr/trading/", "资金计算——AI 生成代码须人审+边界单测"),
    ("src/zephyr/risk/", "风控规则——AI 生成代码须人审+边界单测"),
    ("src/zephyr/ex_sor/services/transaction_cost_optimizer.py", "成本参数——AI 生成代码须人审"),
    ("src/zephyr/ex_sor/services/slippage_analyzer.py", "滑点模型——AI 生成代码须人审"),
    ("src/zephyr/backtest/core/matching_logic.py", "撮合逻辑（回测=实盘共用）——AI 生成代码须人审"),
]


def _normalize_repo_relative(target_path: str) -> str:
    """归一化为仓库相对路径（正斜杠）。

    相对路径（含 git status 输出的 . 前缀形式）锚定 REPO_ROOT 拼接后解析，
    不依赖进程 CWD；绝对路径直接解析；不在仓库内（ValueError）保留原样。
    """
    try:
        return str((REPO_ROOT / target_path).resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return target_path.replace("\\", "/")


def check_high_sensitivity(target_path: str) -> list[str]:
    """检查路径是否在高敏区（GAP-010）。

    高敏区文件变更输出 WARNING（不阻断），提示人审+边界单测。
    与 PROTECTED_PATTERNS 不同——高敏区不拦截只提示。
    """
    warnings = []
    normalized = _normalize_repo_relative(target_path)
    for pattern, reason in HIGH_SENSITIVITY_PATTERNS:
        if pattern in normalized or normalized.startswith(pattern):
            warnings.append(
                f"GAP-010 WARN: 高敏区文件 '{target_path}' 匹配 '{pattern}' — {reason}"
            )
    return warnings


def check_path(target_path: str) -> list[str]:
    """Check compliance and report findings."""
    findings = []
    normalized = _normalize_repo_relative(target_path)
    for pattern, reason in PROTECTED_PATTERNS:
        if pattern in normalized or normalized.startswith(pattern):
            findings.append(f"IRN-010 FAIL: path '{target_path}' matches protected pattern '{pattern}' — {reason}")
    return findings


def check_session_log(session_log_path: str) -> list[str]:
    """Check compliance and report findings."""
    findings = []
    log_path = Path(session_log_path)
    if not log_path.exists():
        print(f"IRN-010 WARNING: session log '{session_log_path}' not found, skipping")
        return findings
    content = log_path.read_text(encoding="utf-8", errors="replace")
    import re

    write_entries = re.findall(
        r"(?:Write|write|创建|修改|编辑).*?['\"]?([^'\"\s]+\.(?:py|md|yaml|yml|json))['\"]?", content
    )
    for entry_path in write_entries:
        findings.extend(check_path(entry_path))
    return findings


def get_staged_files() -> list[str]:
    """获取 git staged 文件列表（新增/修改/重命名后）。

    用于 --staged 模式（pre-commit hook Layer 2）。
    """
    try:
        r = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        print(f"[ERR] git diff 失败: {type(e).__name__}: {e}", file=sys.stderr)
        return []
    if r.returncode != 0:
        print(f"[ERR] git diff rc={r.returncode}: {r.stderr}", file=sys.stderr)
        return []
    return [f for f in r.stdout.strip().split("\n") if f]


# ── B4 治本（2026-08-19）：merge 场景审批转置三件套 ─────────────────────────
# Layer 1（protected_paths_gate）运行时 import 复用本组函数（SSoT，禁复制）。
# MERGE_HEAD 判据复用 AI-R1-003 原语（git rev-parse --git-path，worktree 感知）。


def _git_read(args: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
    """只读 git 命令统一入口（10s 超时兜底，防 hook 场景挂死）。

    cwd=None 时继承进程 cwd（pre-commit hook 由 git 在 worktree 根启动，天然正确）；
    Layer 1 in-process gate 调用须显式传 gateway.project_root（worktree 感知）。
    """
    return subprocess.run(
        ["git"] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10,
        cwd=cwd,
    )


def _merge_head_shas(cwd: str | None = None) -> list[str]:
    """在途 merge 的第二父 sha 列表（octopus merge MERGE_HEAD 多行取全部）。

    无在途 merge → []；MERGE_HEAD 损坏/不可 verify → []（调用方按无审批拦，
    受保护路径高危区 fail-closed）。
    """
    try:
        r = _git_read(["rev-parse", "--git-path", "MERGE_HEAD"], cwd=cwd)
        # --git-path 相对路径锚定 git 命令执行目录（hook 场景=worktree 根），
        # 不是 REPO_ROOT（cron/外部调用进程 cwd 任意）
        anchor = Path(cwd) if cwd else Path.cwd()
        if r.returncode == 0 and r.stdout.strip():
            mh_path = Path(r.stdout.strip())
            if not mh_path.is_absolute():
                mh_path = anchor / mh_path
        else:
            mh_path = anchor / ".git" / "MERGE_HEAD"  # 回退：git 不可用时旧路径判定
        if not mh_path.exists():
            return []
        shas: list[str] = []
        for line in mh_path.read_text(encoding="ascii", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            v = _git_read(["rev-parse", "--verify", "-q", line], cwd=cwd)
            if v.returncode != 0:
                return []  # 内容损坏 → fail-closed
            shas.append(v.stdout.strip())
        return shas
    except Exception:  # noqa: BLE001 — 任何异常按"无在途 merge"回落原逻辑（即拦）
        return []


def _branch_side_commits_touching(
    merge_shas: list[str], rel_file: str, cwd: str | None = None
) -> list[str]:
    """分支侧 commit 集合：第二父可达而 HEAD 不可达（HEAD..<sha>）且触碰 rel_file。"""
    commits: set[str] = set()
    for sha in merge_shas:
        try:
            r = _git_read(["log", "--format=%H", f"HEAD..{sha}", "--", rel_file], cwd=cwd)
        except Exception:  # noqa: BLE001 — 单文件枚举失败不拖垮其余
            continue
        if r.returncode == 0:
            commits.update(ln.strip() for ln in r.stdout.splitlines() if ln.strip())
    return sorted(commits)


def _branch_side_approved(commits: list[str], cwd: str | None = None) -> tuple[bool, str | None]:
    """分支侧 commit 链任一带 [ARCH-APPROVAL] 标记即视为已审批。返回 (approved, issue_id)。"""
    for c in commits:
        try:
            r = _git_read(["log", "-1", "--format=%B", c], cwd=cwd)
        except Exception:  # noqa: BLE001 — 单 commit message 读取失败跳过
            continue
        if r.returncode == 0:
            m = APPROVAL_MARKER_RE.search(r.stdout)
            if m:
                return True, m.group(1)
    return False, None


def check_staged() -> list[str]:
    """检查 staged 文件是否含受保护路径（pre-commit hook Layer 2）。

    逃生通道：ZEPHYR_PROTECTED_PATHS_BYPASS=1 env（紧急逃生，落审计到 stderr）。
    pre-commit hook 不能访问 commit message（commit-msg hook 才可以），
    所以本层逃生通道只有 env，审批标记逃生通道在 in-process gate (Layer 1) 实现。

    B4 治本（2026-08-19）：merge 场景审批转置——受保护改动在分支侧 commit 已验过
    [ARCH-APPROVAL]（Layer 1），merge commit 只是搬运，裸 git merge 触发的 pre-commit
    拿不到分支侧 message 导致误伤（05/08 两域被拦实证）。在途 merge 时改查分支侧
    commit 审批标记：逐文件枚举 HEAD..<第二父> 触碰链，任一带标记=修改链已审批→放行；
    无标记→拦（含分支侧 sha 清单）。squash merge 无 MERGE_HEAD 不识别（本仓恒 --no-ff）；
    MERGE_HEAD 损坏/不可读 → 按无审批拦（受保护路径高危区 fail-closed）。
    """
    # 逃生通道：env
    if os.environ.get(_BYPASS_ENV) == "1":
        # 落审计到 stderr（pre-commit hook 无独立审计文件，stderr 可被 pre-commit 日志捕获）
        print("[WARN] PROTECTED-PATHS: ZEPHYR_PROTECTED_PATHS_BYPASS=1 env set, bypassing staged check", file=sys.stderr)
        return []

    files = get_staged_files()
    if not files:
        return []

    # GAP-010：高敏区 WARNING（不阻断，输出到 stderr；不受 merge 转置影响）
    for rel in files:
        for w in check_high_sensitivity(rel):
            print(w, file=sys.stderr)

    # B4：merge 场景走分支侧审批转置
    merge_shas = _merge_head_shas()
    if merge_shas:
        unapproved: list[tuple[str, list[str]]] = []
        for rel in files:
            if not check_path(rel):
                continue
            commits = _branch_side_commits_touching(merge_shas, rel)
            approved, _issue_id = _branch_side_approved(commits)
            if not approved:
                unapproved.append((rel, commits))
        if not unapproved:
            print(
                f"[INFO] PROTECTED-PATHS: merge 场景分支侧审批标记核验通过"
                f"（{len(merge_shas)} 个第二父），放行",
                file=sys.stderr,
            )
            return []
        return [
            f"IRN-010 FAIL: merge 带入受保护路径 '{rel}' 的分支侧 commit 链无 "
            f"[ARCH-APPROVAL] 审批标记（分支侧 commits: {commits or '无触碰记录'}）。"
            f"逃生通道：分支侧修改 commit message 补 [ARCH-APPROVAL:ISSUE_ID] 标记后重新 merge"
            for rel, commits in unapproved
        ]

    findings: list[str] = []
    for rel in files:
        findings.extend(check_path(rel))
    return findings


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Protected paths write check (IRN-010)")
    parser.add_argument("--path", type=str, help="Check if a specific path is protected")
    parser.add_argument("--session-log", type=str, help="Check session log for protected path violations")
    parser.add_argument("--staged", action="store_true", help="Check git staged files for protected path violations (pre-commit hook mode)")
    parser.add_argument("--warn-only", action="store_true", help="Only warn, do not fail")
    args = parser.parse_args()

    all_findings: list[str] = []

    if args.path:
        all_findings.extend(check_path(args.path))

    if args.session_log:
        all_findings.extend(check_session_log(args.session_log))

    if args.staged:
        all_findings.extend(check_staged())

    if not any([args.path, args.session_log, args.staged]):
        print("Usage: check_protected_paths.py --path <target_path> | --session-log <log_path> | --staged")
        sys.exit(EXIT_ERROR)

    for finding in all_findings:
        print(finding)

    if all_findings and not args.warn_only:
        sys.exit(EXIT_FINDINGS)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
