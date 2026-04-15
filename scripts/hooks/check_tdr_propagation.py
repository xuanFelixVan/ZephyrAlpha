# AI-generated: 技术决策文档变更时要求联动文件同批暂存（红队 T3）
"""若暂存区包含 TDR 真源文件，则要求已存在的联动目标（如 MODULE_INVENTORY）一并暂存。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from governance.hook_support import git_staged_paths, resolve_repo_root  # noqa: E402

# 触发联动检查的「源」文件（相对仓库根）
WATCH_SOURCES = (
    "docs/01_FRAMEWORK/tech-decision-records.md",
    "docs/01_FRAMEWORK/ARCHITECTURE_DECISIONS/README.md",
)

# 若磁盘上存在，则与 WATCH 同批提交时必须一并暂存
PROPAGATION_TARGETS = (
    "docs/02_ARCHITECTURE/MODULE_INVENTORY.md",
    "docs/02_ARCHITECTURE/DEV_ENV_SETUP.md",
)


def _staged_set(repo: Path, staged: list[Path]) -> set[str]:
    out: set[str] = set()
    for p in staged:
        try:
            out.add(p.resolve().relative_to(repo).as_posix())
        except ValueError:
            continue
    return out


def _tracked_in_git(repo: Path, rel: str) -> bool:
    r = subprocess.run(
        ["git", "ls-files", "--error-unmatch", rel],
        cwd=repo,
        capture_output=True,
    )
    return r.returncode == 0


def check_tdr_propagation(repo: Path, paths: list[Path]) -> int:
    staged_rel = _staged_set(repo, paths)
    watch_hit = any(rel in staged_rel for rel in WATCH_SOURCES)
    if not watch_hit:
        return 0
    targets = sorted(set(PROPAGATION_TARGETS))
    missing: list[str] = []
    for rel in targets:
        full = repo / rel
        if not full.is_file():
            continue
        if not _tracked_in_git(repo, rel):
            continue
        if rel not in staged_rel:
            missing.append(rel)
    if missing:
        print(
            "[check_tdr_propagation] 技术决策相关文件已修改，但以下联动文件未纳入本次暂存：",
            file=sys.stderr,
        )
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        print("  请一并 git add 上述文件，或拆分为单独提交。", file=sys.stderr)
        return 1
    return 0


def main() -> None:
    """必须读取完整暂存区：不能依赖 pre-commit 传入的子集路径。"""
    repo = resolve_repo_root()
    staged = git_staged_paths(repo)
    sys.exit(check_tdr_propagation(repo, staged))


if __name__ == "__main__":
    main()
