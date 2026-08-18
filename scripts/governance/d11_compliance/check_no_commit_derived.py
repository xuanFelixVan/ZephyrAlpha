# [BLUEPRINT] MOD-GOV_CHECK_NO_COMMIT_DERIVED
# [MODULE] scripts.governance.d11_compliance.check_no_commit_derived
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] .pre-commit-config.yaml (gate-no-commit-derived hook)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_CHECK_NO_COMMIT_DERIVED | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  pre-commit hook脚本按需调用,非cron/daemon常驻服务
"""

门禁：阻断对派生产物（已离库的生成器输出）的 git add。

治本：#ARCH-GOV-BUDGET-001 / I-GOV-1（2026-08-05）
病根：派生产物（域文档、项目树）已 .gitignore + git rm --cached 离库，但 AI 可能
误用 `git add -f` 强制重新跟踪，或新生成器输出未被 .gitignore 覆盖时被误 add。
本 gate 检测 staged 文件中是否含派生产物路径，命中则 hard block。

二元判定：staged 文件路径匹配派生产物模式 → exit 1
豁免：无（派生产物禁止入 git 是不变量，无例外）

[MODULE] scripts.governance.d11_compliance.check_no_commit_derived
[INVARIANTS] 只读 staged 文件名；不修改工作树；fail-closed (exit 1 on violation)
[CONSUMERS] .pre-commit-config.yaml (gate-no-commit-derived hook)
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] 无 staged 派生产物 → exit 0；违规 → exit 1
[TESTS] tests/governance/d11_compliance/test_check_no_commit_derived.py
[DOMAIN] D_GOVERNANCE

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: git staged 文件列表
#   fields: git diff --cached --name-only --diff-filter=ACM 输出的文件路径（仅新增/复制/修改，不含删除）
#   code: get_staged_files L61-75
# 层: 算法
# - id: A1
#   name_zh: ① 派生产物路径判定
#   name_en: is_derived
#   intro: 用两条正则匹配 staged 路径是否属于已离库的生成器输出，README.md 豁免
#   desc: DERIVED_PATTERNS 两条编译正则（域文档 73 篇 + 项目树 zh/en）逐一 search 路径；文件名在 EXEMPT_NAMES={README.md} 中直接放行；命中任一模式即判派生产物
#   inputs: I1
#   outputs: 每个 staged 路径的 是/否 判定
#   invariant: 只读 staged 文件名，不修改工作树
# - id: A2
#   name_zh: ② 门禁二元判定
#   name_en: main
#   intro: 收集全部违规路径，命中则打印治本说明并 exit 1 硬阻断
#   desc: violations=[f for f in staged if is_derived(f)]；空列表 exit 0，非空打印 GATE-NO-COMMIT-DERIVED 报告（病根/正确做法/违规清单）后 exit 1；fail-closed 无豁免
#   inputs: A1
#   outputs: 进程退出码 0/1
#   invariant: fail-closed（违规必 exit 1，无例外豁免）
# 层: 输出
# - id: O1
#   name_zh: 门禁退出码与违规报告
#   name_en: exit code + violation report
#   intro: exit 0 放行 / exit 1 阻断并打印违规派生产物路径清单
#   invariant: 派生产物禁止入 git
#   downstream: .pre-commit-config.yaml gate-no-commit-derived hook
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 门禁：阻断对派生产物（已离库的生成器输出）的 git add。
dimensions:
- D11
priority: P2
timeout_seconds: 60
warn_only: false
"""


import re
import subprocess
import sys
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

# 派生产物路径模式（与 .gitignore #ARCH-GOV-BUDGET-001 段对齐）
# 这些路径下的 .md 由生成器从 depgraph (PostgreSQL) 派生，禁止入 git。
DERIVED_PATTERNS = [
    # generate_domain_doc.py 输出（73 域文档，README.md 例外）
    re.compile(r"^docs/02_enterprise_architecture/02_domain_architecture_docs/[^/]+\.md$"),
    # generate_path_tree.py 输出（项目树 zh/en）
    re.compile(r"^docs/02_enterprise_architecture/01_global_architecture_diagram/full_project_tree_(zh|en)\.md$"),
    # sync_registry_from_blueprints.py 输出（2026-08-18 退库，#ARCH-GOV-BUDGET-001 同构裁定；
    # 防 git add -f 重新跟踪——该文件 100% 可从 blueprint.md frontmatter 重生成）
    re.compile(r"^docs/03_modules/blueprint_registry\.yaml$"),
]

# 豁免：README.md 是手工维护的目录说明，不是派生产物
EXEMPT_NAMES = {"README.md"}


def get_staged_files() -> list[str]:
    """获取 staged 文件列表（仅 Added/Copied/Modified，不含 Deleted）。

    派生产物的"删除"（git rm --cached 离库）是合法操作，不应阻断；
    只阻断"添加/修改"派生产物（即重新引入或跟踪派生产物）。
    """
    r = subprocess.run(  # noqa: bare-subprocess  pre-commit门禁脚本读staged文件,process_pool在此场景不适用
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    if r.returncode != 0:
        return []
    return [f.strip() for f in r.stdout.splitlines() if f.strip()]


def is_derived(path: str) -> bool:
    """判断路径是否为派生产物。"""
    # 豁免 README.md
    if Path(path).name in EXEMPT_NAMES:
        return False
    return any(p.search(path) for p in DERIVED_PATTERNS)


def main() -> int:
    """门禁入口：检测 staged 派生产物，命中 → exit 1。"""
    staged = get_staged_files()
    if not staged:
        return 0

    violations = [f for f in staged if is_derived(f)]
    if not violations:
        return 0

    print("GATE-NO-COMMIT-DERIVED: 检测到派生产物被 git add（治本 #ARCH-GOV-BUDGET-001 / I-GOV-1）")
    print("  病根：派生产物（域文档/项目树）已离库，源真源（DB + 生成器代码）已跟踪。")
    print("  派生产物入 git 是 reconciler 非收敛循环的数学根因。")
    print("  正确做法：用 `python scripts/serve_docs.py` 按需生成查看，不要 git add。")
    print()
    for v in violations:
        print(f"  {v}")
    print()
    print("  如需查看派生产物，运行: python scripts/serve_docs.py")
    return 1


if __name__ == "__main__":
    sys.exit(main())
