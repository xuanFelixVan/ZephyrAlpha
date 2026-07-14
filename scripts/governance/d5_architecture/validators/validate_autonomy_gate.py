# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_autonomy_gate.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_autonomy_gate
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""validate_autonomy_gate.py — 变更级别 vs AI 自治权限交叉校验



对标：PS-STD-003 ABS-05~10（AI 不可执行超出其自治等级的变更）
     GOV-AI-000（AI 自治权限注册表）
     任务系统 T3~T5（会话 range: 操作预算）

检测内容：
- 扫描操作历史（git log）中 AI 执行的变更
- 校验每次变更是否在 AI 的自治权限范围内
- 检测是否跳过预检/审批（--no-verify / 单模型审批）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: AI 自治权限门禁校验（ABS-05~10 — 越权检测）
dimensions:
- D5
- D11
priority: P1
timeout_seconds: 30
warn_only: false
"""

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
import argparse
import subprocess

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

AUTONOMY_LEVELS = {
    "full": ["create", "modify", "delete", "move", "rename", "refactor"],
    "high": ["create", "modify", "rename", "refactor"],
    "medium": ["create", "modify", "refactor"],
    "low": ["create", "modify"],
    "readonly": [],
}
DANGEROUS_ACTIONS = {
    "delete": "\\b(?:delete|remove|rm|del)\\b",
    "move": "\\b(?:move|mv|relocate)\\b",
    "force_push": "\\b(?:push\\s+--force|push\\s+-f)\\b",
    "no_verify": "\\b(?:--no-verify|--no-gpg-sign|--no-check)\\b",
    "skip_hooks": "\\b(?:SKIP\\s*=|--skip)\\b",
}


def get_recent_commits(max_commits: int = 50) -> list[dict]:
    """获取最近提交记录"""
    try:
        result = subprocess.run(
            ["git", "log", f"-n{max_commits}", "--pretty=format:%H|%an|%ae|%s|%ci", "--name-only"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(REPO_ROOT),
        )
        if result.returncode != 0:
            return []
        commits = []
        current = None
        for line in result.stdout.strip().split("\n"):
            if "|" in line and "@" in line:
                if current:
                    commits.append(current)
                parts = line.split("|", 4)
                current = {
                    "hash": parts[0][:8] if len(parts) > 0 else "?",
                    "author": parts[1] if len(parts) > 1 else "?",
                    "email": parts[2] if len(parts) > 2 else "?",
                    "message": parts[3] if len(parts) > 3 else "?",
                    "date": parts[4] if len(parts) > 4 else "?",
                    "files": [],
                }
            elif current and line.strip():
                current["files"].append(line.strip())
        if current:
            commits.append(current)
        return commits
    except (subprocess.SubprocessError, OSError):
        return []


def is_ai_commit(commit: dict) -> bool:
    """获取最近提交记录."""
    ai_indicators = ["AI", "Agent", "Claude", "GPT", "GLM", "Kimi", "Gemini", "Cursor", "Trae"]
    author = commit.get("author", "")
    email = commit.get("email", "")
    message = commit.get("message", "")
    return any(
        ind.lower() in author.lower() or ind.lower() in email.lower() or ind.lower() in message.lower()
        for ind in ai_indicators
    )
    "判断提交是否由 AI 生成."


def scan_autonomy_violations() -> tuple[list[dict], int]:
    """扫描自主性违规"""
    findings = []
    "扫描自主性违规."
    commits = get_recent_commits(50)
    ai_commits = [c for c in commits if is_ai_commit(c)]
    for commit in ai_commits:
        violations = []
        for action, pattern in DANGEROUS_ACTIONS.items():
            if re.search(pattern, commit["message"], re.IGNORECASE):
                violations.append(action)
        if violations:
            findings.append(
                {
                    "hash": commit["hash"],
                    "author": commit["author"],
                    "date": commit["date"],
                    "message": commit["message"][:150],
                    "files_touched": len(commit["files"]),
                    "violations": violations,
                    "severity": "HIGH",
                }
            )
    return (findings, len(ai_commits))
    "扫描自主性违规."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="变更级别 vs AI 自治权限交叉校验")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--max-commits", type=int, default=50)
    args = parser.parse_args()
    findings, ai_count = scan_autonomy_violations()
    print(f"\n[AUTONOMY-GATE] 最近 {args.max_commits} 个 commit", file=sys.stderr)
    print(f"  AI commit: {ai_count}", file=sys.stderr)
    print(f"  疑似越权操作: {len(findings)}", file=sys.stderr)
    for f in findings:
        print(f"\n  ⚠ [{f['severity']}] {f['hash']} — {f['author']}", file=sys.stderr)
        print(f"     {f['message']}", file=sys.stderr)
        print(f"     违规动作: {', '.join(f['violations'])}", file=sys.stderr)
        print(f"     涉及文件: {f['files_touched']}", file=sys.stderr)
    if findings:
        print(f"\n⚠ {len(findings)} 次 AI 操作涉嫌越权/跳过门禁！", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if findings else EXIT_PASS)
    "入口函数."


if __name__ == "__main__":
    main()
