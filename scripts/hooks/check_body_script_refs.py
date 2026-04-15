# AI-generated: Markdown 正文中 python scripts/... 命令引用的脚本是否存在（红队 A3）
"""扫描暂存 docs/**/*.md 正文中的 `python scripts/...py` 形式引用。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from governance.hook_support import git_staged_paths, resolve_repo_root  # noqa: E402

# 匹配 python scripts\xxx.py 或 python scripts/xxx.py
_SCRIPT_CMD = re.compile(
    r"(?:^|\s)python\s+((?:scripts[/\\][^\s#]+\.py))",
    re.IGNORECASE | re.MULTILINE,
)


def check_body_script_refs(repo: Path, paths: list[Path]) -> int:
    md_files = [p for p in paths if p.suffix.lower() == ".md" and p.is_file() and "docs" in p.parts]
    if not md_files:
        return 0
    errors: list[str] = []
    for md in md_files:
        try:
            body = md.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{md.relative_to(repo)}: 读取失败 {exc}")
            continue
        for m in _SCRIPT_CMD.finditer(body):
            rel = m.group(1).replace("\\", "/")
            target = repo / rel
            if not target.is_file():
                errors.append(f"{md.relative_to(repo)}: 引用不存在 -> {rel}")
    if errors:
        print("[check_body_script_refs] 正文中的脚本路径不存在：", file=sys.stderr)
        for line in errors[:60]:
            print(f"  {line}", file=sys.stderr)
        return 1
    return 0


def main() -> None:
    repo = resolve_repo_root()
    args = [a for a in sys.argv[1:] if a]
    paths = [repo / a if not Path(a).is_absolute() else Path(a) for a in args] if args else git_staged_paths(repo)
    sys.exit(check_body_script_refs(repo, paths))


if __name__ == "__main__":
    main()
