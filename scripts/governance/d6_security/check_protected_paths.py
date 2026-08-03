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


def check_path(target_path: str) -> list[str]:
    """Check compliance and report findings."""
    findings = []
    normalized = target_path.replace("\\", "/")
    # 去除前导 ./（git status 有时输出 ./path）
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if not normalized.startswith("/"):
        try:
            normalized = str(Path(target_path).resolve().relative_to(REPO_ROOT)).replace("\\", "/")
        except ValueError:
            pass
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


def check_staged() -> list[str]:
    """检查 staged 文件是否含受保护路径（pre-commit hook Layer 2）。

    逃生通道：ZEPHYR_PROTECTED_PATHS_BYPASS=1 env（紧急逃生，落审计到 stderr）。
    pre-commit hook 不能访问 commit message（commit-msg hook 才可以），
    所以本层逃生通道只有 env，审批标记逃生通道在 in-process gate (Layer 1) 实现。
    """
    # 逃生通道：env
    if os.environ.get(_BYPASS_ENV) == "1":
        # 落审计到 stderr（pre-commit hook 无独立审计文件，stderr 可被 pre-commit 日志捕获）
        print("[WARN] PROTECTED-PATHS: ZEPHYR_PROTECTED_PATHS_BYPASS=1 env set, bypassing staged check", file=sys.stderr)
        return []

    files = get_staged_files()
    if not files:
        return []

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
