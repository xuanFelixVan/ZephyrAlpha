# [TTL] permanent
"""test_untracked_phantom_docs_guard.py — 幻影区未跟踪 .md 常驻守卫（P1）。

治本 #FMS-PHANTOM-DOCS（2026-09-27，st-fms-tc-20260927）：
docs/02_enterprise_architecture/02_domain_architecture_docs/ 等永久区目录存在
"从未入 git、且被 .gitignore 吞掉导致 is_clean 返回空=假干净"的幻影件
（S8 簿 §⑤14）。本守卫用 `git ls-files --error-unmatch` 的等价集判定
"盘上未跟踪且未被 .gitignore 放行"的 .md，锁死 docs/ 永久三区（01/02/03）。

判别力口径：
- 只计"未跟踪 AND 未被 .gitignore 排除"的 .md（`git ls-files --others --exclude-standard`）——
  即 directory_contract 允许、ignore 规则放行的真幻影（该进来的没进来）。
- 被 .gitignore 主动排除的（如 02_domain_architecture_docs/*.md，541 行 ignore+542 行只放行
  README）= 设计外，不计入本守卫（守"被 ignore 的不硬塞"铁律），另见交付说明。
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

# 永久区三区（directory_contract permanent zone paths 子集，见 directory_contract.yaml:204-223）
PERMANENT_DOC_DIRS = [
    "docs/01_policies_and_standards",
    "docs/02_enterprise_architecture",
    "docs/03_modules",
]


def _untracked_not_ignored_md() -> list[str]:
    """返回永久区下"未跟踪且未被 .gitignore 排除"的 .md 相对路径列表。"""
    out = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "--", *PERMANENT_DOC_DIRS],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [ln for ln in out.splitlines() if ln.strip().endswith(".md")]


def test_no_untracked_phantom_md_in_permanent_docs() -> None:
    """该目录（docs/01|02|03 永久区）无未跟踪 .md：幻影件必须入库或按设计外处置。"""
    phantom = _untracked_not_ignored_md()
    assert not phantom, (
        "发现未跟踪且未被 .gitignore 放行的 .md（幻影区）——须 git add 纳入（册先行登记 "
        "creation_token），或若确属设计外请改 .gitignore 显式排除：\n  " + "\n  ".join(phantom)
    )
