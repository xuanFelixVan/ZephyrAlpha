# AI-generated: STANDARDS 目录新增 .md 须在 INDEX.md 登记（红队 T5/B5）
"""监视 docs/09_AUDIT/STANDARDS 与 docs/01_GOVERNANCE/STANDARDS（若存在）。"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from governance.hook_support import git_staged_paths, resolve_repo_root  # noqa: E402

_STANDARDS_DIRS = (
    "docs/09_AUDIT/STANDARDS",
    "docs/01_GOVERNANCE/STANDARDS",
)


def _norm(p: Path, repo: Path) -> str:
    try:
        return p.resolve().relative_to(repo).as_posix()
    except ValueError:
        return str(p)


def check_standards_index(repo: Path, paths: list[Path]) -> int:
    errors: list[str] = []
    for std_dir in _STANDARDS_DIRS:
        std_path = repo / std_dir
        index_file = std_path / "INDEX.md"
        if not index_file.is_file():
            continue
        try:
            index_body = index_file.read_text(encoding="utf-8")
        except OSError:
            continue
        for p in paths:
            if not p.is_file() or p.suffix.lower() != ".md":
                continue
            try:
                rel = p.resolve().relative_to(std_path)
            except ValueError:
                continue
            if rel.name == "INDEX.md":
                continue
            # 新文件必须在 INDEX 正文中出现（文件名或相对路径）
            needle = rel.as_posix()
            if rel.name not in index_body and needle not in index_body:
                errors.append(
                    f"{_norm(p, repo)} 未在 {std_dir}/INDEX.md 中登记",
                )
    if errors:
        print("[check_standards_index_registration] 以下文件未在 STANDARDS/INDEX.md 登记：", file=sys.stderr)
        for e in errors[:40]:
            print(f"  {e}", file=sys.stderr)
        return 1
    return 0


def main() -> None:
    repo = resolve_repo_root()
    args = [a for a in sys.argv[1:] if a]
    paths = [repo / a if not Path(a).is_absolute() else Path(a) for a in args] if args else git_staged_paths(repo)
    sys.exit(check_standards_index(repo, paths))


if __name__ == "__main__":
    main()
