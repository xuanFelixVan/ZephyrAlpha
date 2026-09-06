# [BLUEPRINT] MOD-D_GOV_SCRIPTS | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] scripts.governance.commit_derived_sync
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib（subprocess/pathlib/sys）；scripts/git_commit.py（GitCommitGateway CLI）
# [CONSUMERS] AI 会话收尾（construction_workflow_sop.md §4 清单第 15 项）；手工：python scripts/governance/commit_derived_sync.py
# [STARTUP] manual（python scripts/governance/commit_derived_sync.py [--dry-run]）
# [MATURITY] production
# [INVARIANTS] 只提交派生家族白名单内的脏文件；白名单外脏文件一律跳过并明示（防搭便车提交真实修改）；--dry-run 零写入
# [MODIFY-GUARD] _DERIVED_PATTERNS（派生家族白名单变更须同步 workspace_governance_policy.md §2.1）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无匹配文件 exit 0（无事可做）；网关失败 exit 非 0 透传；--dry-run 仅打印计划
# [TESTS] 手动：python scripts/governance/commit_derived_sync.py --dry-run
# [A_module] module_id=MOD-D_GOV_SCRIPTS | layer=script | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""派生残留一键收口（2026-09-07 triage 根治配套）——治"每次都处理了，每次又都会再次出现"。

背景（第一性原理）：
  治理脚本（depgraph 扫描器/注册表生成器/规则完整性校验器）每次运行都重写一批派生文件。
  其中纯信息类（手册统计 AUTO 块/README 快照/latest.json 等）已由 workspace_hygiene_reconciler
  post-commit 自动 git restore 自愈；但持久化类不能自动还原——
    ① blueprint.md 统计区（混合内容文件，整文件还原会误伤未提交正文——#ARCH-BLUEPRINT-AUTOSYNC-MISCLASSIFY-001 教训）
    ② scripts/governance/meta/rules_integrity_db.json（金标哈希 DB，还原=写入→还原死循环，2026-07-22 教训）
    ③ rule_catalog_registry.yaml / registry_master_index.yaml（新生成条目=真实内容，须持久化）
  这些文件跨多域（COMMIT_SCOPE_VIOLATION 拦截单域提交），AI 任务 commit 不含它们 → 持续残留。
  历史模式：每轮会话累积 → 下个 AI 重新 triage → 循环往复。

用法（会话收尾一条命令）：
  python scripts/governance/commit_derived_sync.py            # 收口（走 GitCommitGateway）
  python scripts/governance/commit_derived_sync.py --dry-run  # 仅查看将提交什么
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GATEWAY = REPO / "scripts" / "git_commit.py"

# 派生家族白名单（与 workspace_governance_policy.md §2.1 / workspace_hygiene_reconciler 对齐）
# ——命中这些模式的脏文件才允许收口；其余一律跳过明示
_DERIVED_PATTERNS: tuple[str, ...] = (
    # 持久化类（不能 auto-restore，必须 commit）
    "docs/03_modules/",  # blueprint.md 统计区（注意：若该蓝图有本会话真实未提交正文，应由任务 commit 先行，本脚本后跑）
    "scripts/governance/meta/rules_integrity_db.json",
    "docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml",
    "docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml",
    "architecture_model/index.yaml",
    # 自愈类兜底（reconciler 通常已还原；若有残留一并收口，保持 HEAD 新鲜）
    "docs/02_enterprise_architecture/04_architecture_principles_decisions/project_handbook/",
    "docs/02_enterprise_architecture/04_architecture_principles_decisions/README.md",
    "data/architecture_health/",
)


def _dirty_files() -> list[str]:
    out = subprocess.run(
        ["git", "-c", "core.quotepath=false", "status", "--porcelain=v1", "-uno"],
        capture_output=True, text=True, encoding="utf-8", cwd=REPO, timeout=30,
    ).stdout
    files = []
    for line in out.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip().strip('"')
        # 只收 modified（M）；unmerged/added/deleted 不属于"派生残留"语义
        if line[:2].strip() in ("M", "MM", "AM") or line[0] == "M" or line[1] == "M":
            files.append(path)
    return files


def _classify(files: list[str]) -> tuple[list[str], list[str]]:
    derived, skipped = [], []
    for f in files:
        if any(f.startswith(p) or f == p.rstrip("/") for p in _DERIVED_PATTERNS):
            derived.append(f)
        else:
            skipped.append(f)
    return derived, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="派生残留一键收口")
    parser.add_argument("--dry-run", action="store_true", help="仅打印计划，不提交")
    parser.add_argument("--session", default="derived-sync", help="GitCommitGateway session 标识")
    args = parser.parse_args()

    files = _dirty_files()
    if not files:
        print("工作区无 tracked 脏文件，无需收口。")
        return 0
    derived, skipped = _classify(files)
    if not derived:
        print(f"无派生家族残留（{len(skipped)} 个非派生脏文件由所属任务处理）：")
        for f in skipped:
            print(f"  skip {f}")
        return 0

    print(f"派生残留 {len(derived)} 个将收口：")
    for f in derived:
        print(f"  + {f}")
    if skipped:
        print(f"跳过非派生脏文件 {len(skipped)} 个（不搭便车）：")
        for f in skipped:
            print(f"  - {f}")
    if args.dry_run:
        print("[dry-run] 未提交。")
        return 0

    msg = (
        "chore(derived): 派生残留一键收口（commit_derived_sync.py）——"
        f"{len(derived)} 个派生家族文件（blueprint 统计区/注册表索引/金标哈希/手册统计块）"
        " [no-lookup:continuation] [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001]"
    )
    cmd = [
        sys.executable, str(GATEWAY),
        "--session", args.session,
        "--allow-overlap", "--allow-multi-domain",
        "--files", ",".join(derived),
        "--message", msg,
    ]
    ret = subprocess.run(cmd, cwd=REPO).returncode
    if ret != 0:
        print(f"FAILED: GitCommitGateway exit={ret}", file=sys.stderr)
    else:
        print(f"OK: 已收口 {len(derived)} 个派生文件。")
    return ret


if __name__ == "__main__":
    raise SystemExit(main())
