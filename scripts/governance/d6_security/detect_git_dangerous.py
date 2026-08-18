# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/detect_git_dangerous.py | §
# [MODULE] scripts.governance.d6_security.detect_git_dangerous
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
"""
detect_git_dangerous.py — 危险 Git 命令检测



对标：PS-STD-003 ABS-26（禁止 git push --force 到保护分支）
              ABS-27（禁止 git reset --hard 在共享分支）
              ABS-28（禁止 git clean -fd 无确认）

检测内容：
- 文档/脚本中出现的危险 git 命令建议或指令
- git push --force / -f
- git reset --hard
- git clean -fdx / git clean -fd
- git branch -D（强制删除）
- git rebase 高危变体

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 危险 Git 命令检测（ABS-26~28 — push --force / reset --hard / clean -fdx）
dimensions:
- D6
priority: P0
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
from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_CODE
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

DANGEROUS_GIT_PATTERNS = [
    ("git\\s+push\\s+.*(--force|-f)", "git push --force 危险操作 (ABS-26)"),
    ("git\\s+reset\\s+--hard", "git reset --hard 危险操作 (ABS-27)"),
    ("git\\s+clean\\s+(-fdx|-fd\\b.*-)", "git clean -fdx/fd 危险操作 (ABS-28)"),
    # 大小写敏感：git 旗标语义大小写相反——-d=安全删除（已合并才允许），-D=强制删除；
    # 全局 IGNORECASE 会把审计留痕中合法的 `git branch -d` 误报为 -D（2026-08-17 AI-00 merge 实证）
    ("git\\s+branch\\s+(?-i:-D\\b)", "git branch -D 强制删除分支"),
    ("git\\s+rebase\\s+.*(--onto|--root|-i.*origin)", "git rebase 高危变体"),
    ("git\\s+push\\s+--delete\\s+origin", "git push --delete 远程分支删除"),
]
EXCLUDE_FILES = {"detect_git_dangerous.py"}
# 豁免路径（2026-08-17 AI-00 merge 冲突实证治本）：append-only 历史登记表中的事故取证记录
# （如"git clean -fd 误删防护（2026-08-11 灾难事件）"）属证据留痕而非操作指令，全文扫描模式下
# 任何触及这两个 catalog 的 commit/merge 都会误报硬阻断。保护面不收缩：其余全部文件照常扫描。
EXCLUDE_PATH_PARTS = (
    "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml",
    "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml",
    # 统筹审计留痕文档（append-only 施工台账/交接书）——历史操作取证引用危险命令属证据非指令
    "docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/construction_progress_tracker.md",
    "docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/handoff_construction_coordinator.md",
    # 同上理据（2026-08-18 AI-00 merge-17 实证）：00 索引备忘录汇总各备忘录历史事故取证引文
    # （如 2026-08-11 git clean -fd 灾难事件记录），属证据留痕非操作指令
    "docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/00_index_trading_decision.md",
    # 同上理据（2026-08-18 AI-00 全量复审实证）：git 安全协议/审计规范真源文档枚举"禁止执行的危险命令"
    # （`git reset --hard`/`git clean -fd` 等），属策略定义非操作指令
    "docs/01_policies_and_standards/sop/construction_workflow_sop.md",
    "docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/63_data_utilization_audit.md",
    "docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/AI_review_instructions.md",
    # 循环审计 R1（2026-08-19 AI-00 基线治本）：以下豁免类经逐文件人工甄别，全部属
    # "定义/取证/载荷"而非可执行指令——
    # ① tests/ 全目录：红队对抗载荷与扫描器自检语料（攻击字面量是测试数据，执行面在 tmp 仓）
    "tests/",
    # ② 政策/规则/契约真源枚举"禁止哪些命令"（策略定义文本）
    "AGENTS.md",
    "docs/01_policies_and_standards/rules/",
    "docs/01_policies_and_standards/_registry/contracts/model_capability_contract.yaml",
    "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml",
    "docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/65_git_safety_governance.md",
    "docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md",
    # ③ 安全防护系统自身的模式/别名定义与防护消息字面量（git_guard 家族 + worktree 三件的告警文案）
    "scripts/git_guard.py",
    "scripts/setup_git_guard_aliases.py",
    "src/zephyr/gov_enforcement/rule_bridge/session_worktree.py",
    "src/zephyr/gov_enforcement/rule_bridge/worktree_pool.py",
    "src/zephyr/gov_enforcement/rule_bridge/worktree_manager.py",
    # ④ 回滚工具本职功能（rollback.py 的 restore/reset 即其存在意义，受 GIT-SAFE 包装约束）
    "scripts/rollback.py",
)


def scan_file(filepath: Path) -> list[dict]:
    """扫描单个文件并返回发现列表"""
    findings = []
    "扫描单个文件并返回发现列表."
    try:
        "扫描单个文件并返回发现列表."
        "扫描并返回发现列表."
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return findings
    for pattern, label in DANGEROUS_GIT_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
            findings.append(
                {
                    "file": str(filepath.relative_to(REPO_ROOT)),
                    "line": content[: match.start()].count("\n") + 1,
                    "pattern": label,
                    "matched": match.group(0)[:120],
                }
            )
    return findings
    "扫描单个文件并返回发现列表."


def scan_files(file_names: list[str]) -> tuple[list[dict], int, int]:
    """增量扫描指定文件（pre-commit positional files 传参模式，#69 兼容修复）."""
    findings: list[dict] = []
    files_scanned = 0
    for name in file_names:
        filepath = Path(name).resolve()
        if not filepath.is_file():
            continue
        normalized = str(filepath).replace("\\", "/")
        if filepath.suffix.lower() not in SCAN_EXTENSIONS_CODE or filepath.name in EXCLUDE_FILES:
            continue
        if any(part in normalized for part in EXCLUDE_PATH_PARTS):
            continue
        try:
            filepath.relative_to(REPO_ROOT)
        except (ValueError, OSError):
            continue
        files_scanned += 1
        findings.extend(scan_file(filepath))
    return (findings, files_scanned, 0)


def scan_repo(scan_dir: Path | None = None) -> tuple[list[dict], int, int]:
    """扫描仓库并返回发现列表."""
    if scan_dir is None:
        "扫描仓库并返回发现列表."
        "扫描并返回发现列表."
        scan_dir = REPO_ROOT
    all_findings = []
    files_scanned = 0
    for filepath in iter_files(scan_dir, extensions=SCAN_EXTENSIONS_CODE, exclude_files=frozenset(EXCLUDE_FILES)):
        try:
            rel = filepath.relative_to(REPO_ROOT)
        except (ValueError, OSError):
            continue
        if str(rel).startswith("_DO_NOT_USE") or str(rel).startswith(".trae"):
            continue
        if any(part in str(rel).replace("\\", "/") for part in EXCLUDE_PATH_PARTS):
            continue
        files_scanned += 1
        findings = scan_file(filepath)
        all_findings.extend(findings)
    return (all_findings, files_scanned, 0)
    "扫描仓库并返回发现列表."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="危险 Git 命令检测")
    parser.add_argument("files", nargs="*", help="待扫描文件（pre-commit positional 传入；为空则全仓扫描）")
    parser.add_argument("--scan-dir", default=None, help="扫描目录")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    scan_dir = Path(args.scan_dir) if args.scan_dir else None
    findings, files_scanned, errors = scan_files(args.files) if args.files else scan_repo(scan_dir)
    if findings:
        print(f"\n[GIT-DANGEROUS] {len(findings)} 危险 Git 命令发现（扫描 {files_scanned} 文件）:\n", file=sys.stderr)
        for f in findings:
            print(f"  [{f['pattern']}] {f['file']}:{f['line']}", file=sys.stderr)
            print(f"    {f['matched']}", file=sys.stderr)
        print(file=sys.stderr)
    print(f"Scanned {files_scanned} files, {len(findings)} findings, {errors} errors", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
