# AI-generated: INDEX.md 内相对 Markdown 链接存在性检查（G-02 / 红队 T4）
"""仅检查暂存区内的 INDEX.md：正文中的相对链接目标是否存在。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# 保证可导入 governance.hook_support
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from governance.hook_support import git_staged_paths, resolve_repo_root  # noqa: E402

_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _resolve_link(base_dir: Path, href: str) -> Path | None:
    href = href.strip()
    if not href or href.startswith(("#", "http://", "https://", "mailto:")):
        return None
    path_part = href.split("#", 1)[0].strip()
    if not path_part:
        return None
    return (base_dir / path_part).resolve()


def check_index_links(repo: Path, paths: list[Path]) -> int:
    """检查给定路径中 INDEX.md 的相对链接。"""
    index_files = [
        p for p in paths
        if p.is_file() and p.name == "INDEX.md" and "docs" in p.parts
    ]
    if not index_files:
        return 0
    errors: list[str] = []
    for idx in index_files:
        try:
            text = idx.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{idx}: 无法读取 ({exc})")
            continue
        base = idx.parent
        for m in _LINK_RE.finditer(text):
            href = m.group(1).strip()
            tgt = _resolve_link(base, href)
            if tgt is None:
                continue
            if not tgt.exists():
                try:
                    disp = tgt.relative_to(repo)
                except ValueError:
                    disp = tgt
                errors.append(f"{idx.relative_to(repo)}: 死链 -> {href} (解析为 {disp})")
    if errors:
        print("[check_index_links] 以下 INDEX 内链无法解析到现有文件：", file=sys.stderr)
        for line in errors[:50]:
            print(f"  {line}", file=sys.stderr)
        if len(errors) > 50:
            print(f"  ... 另有 {len(errors) - 50} 条", file=sys.stderr)
        return 1
    return 0


def main() -> None:
    repo = resolve_repo_root()
    args = [a for a in sys.argv[1:] if a]
    paths = [repo / a if not Path(a).is_absolute() else Path(a) for a in args] if args else git_staged_paths(repo)
    sys.exit(check_index_links(repo, paths))


if __name__ == "__main__":
    main()
