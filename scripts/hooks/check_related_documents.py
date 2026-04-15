# AI-generated: frontmatter parent_document / related_documents 路径存在性检查（红队 T5/B9）
"""检查暂存 .md 的 YAML 中 parent_document 与 related_documents 是否指向存在的文件。"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from governance.hook_support import git_staged_paths, resolve_repo_root  # noqa: E402


def _extract_frontmatter(content: str) -> dict[str, Any] | None:
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 3)
    if end < 0:
        return None
    block = content[3:end]
    try:
        data = yaml.safe_load(block) or {}
        return data if isinstance(data, dict) else None
    except yaml.YAMLError:
        return None


def _collect_paths(meta: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for key in ("parent_document", "related_documents"):
        val = meta.get(key)
        if val is None:
            continue
        if isinstance(val, str):
            out.append(val.strip())
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, str):
                    out.append(item.strip())
    return [p for p in out if p]


def check_related_documents(repo: Path, paths: list[Path]) -> int:
    md_files = [p for p in paths if p.suffix.lower() == ".md" and p.is_file() and "docs" in p.parts]
    if not md_files:
        return 0
    errors: list[str] = []
    for md in md_files:
        try:
            content = md.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{md.relative_to(repo)}: 读取失败 {exc}")
            continue
        meta = _extract_frontmatter(content)
        if not meta:
            continue
        base = md.parent
        for rel in _collect_paths(meta):
            if rel.startswith(("http://", "https://")):
                continue
            target = (base / rel).resolve()
            if not target.exists():
                errors.append(f"{md.relative_to(repo)}: {rel} -> 不存在")
    if errors:
        print("[check_related_documents] frontmatter 路径无效：", file=sys.stderr)
        for line in errors[:80]:
            print(f"  {line}", file=sys.stderr)
        if len(errors) > 80:
            print(f"  ... 另有 {len(errors) - 80} 条", file=sys.stderr)
        return 1
    return 0


def main() -> None:
    repo = resolve_repo_root()
    args = [a for a in sys.argv[1:] if a]
    paths = [repo / a if not Path(a).is_absolute() else Path(a) for a in args] if args else git_staged_paths(repo)
    sys.exit(check_related_documents(repo, paths))


if __name__ == "__main__":
    main()
