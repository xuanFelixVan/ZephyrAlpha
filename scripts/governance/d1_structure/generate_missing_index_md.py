"""generate_missing_index_md.py — 扫描目录树，为缺失 index.md 的目录自动生成索引文件。

__manifest__ = """
args:
- --root
- docs/
description: 扫描目录树，自动为缺失 index.md 的目录生成索引文件（AGENTS.md §6.11 索引-实际同步强制约定）
dimensions:
- D1
priority: P2
timeout_seconds: 120
warn_only: true
"""


对标：AGENTS.md §6.11 索引-实际同步强制约定（index.md 必须与磁盘实际一致）
      每次新增目录或批量迁移后运行一次，确保所有目录都有导航索引。

用法：
    python generate_missing_index_md.py --root docs/01_policies_and_standards
    python generate_missing_index_md.py --root docs/ --dry-run      # 只预览
    python generate_missing_index_md.py --root docs/ --warn-only    # 巡检模式（不交互、不写入）
"""

from __future__ import annotations

import sys
from argparse import ArgumentParser
from datetime import date
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter

ensure_utf8_stdout()

INDEX_TEMPLATE = (
    '---\n'
    'doc_type: index\n'
    'status: active\n'
    'title: "{dir_name} — 目录索引"\n'
    'version: "1.0.0"\n'
    'created: "{today}"\n'
    'updated: "{today}"\n'
    '---\n\n'
    '# {dir_name}\n\n'
    '> 本文件由 `generate_missing_index_md.py` 自动生成\n'
    '> 生成日期：{today}\n\n'
    '## 目录内容\n\n'
    '| 文件/目录 | 类型 | 说明 |\n'
    '|-----------|------|------|\n'
    '{rows}\n\n'
    '## 导航\n\n'
    '- [上级目录](../index.md)\n'
    '- [项目根](../../index.md)\n'
)

EXCLUDE_NAMES = frozenset(
    {".git", "__pycache__", ".obsidian", "_DO_NOT_USE", "node_modules",
     ".mypy_cache", "scripts", "_archive", ".trae", "_", "windi", "spikes"}
)


def _safe_read_dir(parent: Path) -> list[Path]:
    try:
        entries = [p for p in parent.iterdir() if p.name not in EXCLUDE_NAMES]
        entries.sort()
        return entries
    except PermissionError:
        return []


def _try_read_title(md_path: Path) -> str | None:
    try:
        content = md_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    fm = parse_frontmatter(content)
    if fm and isinstance(fm, dict):
        return fm.get("title")
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _build_file_rows(parent: Path) -> str:
    rows: list[str] = []
    for entry in _safe_read_dir(parent):
        name = entry.name
        if entry.is_dir():
            if (entry / "index.md").exists():
                title = _try_read_title(entry / "index.md")
                desc = title or name
            else:
                desc = name
            rows.append(f"| [{name}/]({name}/index.md) | 目录 | {desc} |")
        elif name.endswith(".md"):
            title = _try_read_title(entry)
            desc = title or name
            rows.append(f"| [{name}]({name}) | Markdown | {desc} |")
        elif name.endswith(".yaml") or name.endswith(".yml"):
            rows.append(f"| [{name}]({name}) | YAML | |")
        elif name.endswith(".py"):
            rows.append(f"| [{name}]({name}) | Python | |")
        elif name.endswith(".json"):
            rows.append(f"| [{name}]({name}) | JSON | |")
        else:
            rows.append(f"| [{name}]({name}) | 文件 | |")
    return "\n".join(rows) if rows else "| (空目录) | | |"


def _is_tty() -> bool:
    try:
        return sys.stdin.isatty()
    except (AttributeError, OSError):
        return False


def generate_index(parent: Path, dry_run: bool = False) -> bool:
    index_path = parent / "index.md"
    if index_path.exists():
        return False
    dir_name = parent.name or parent.resolve().name
    today = date.today().isoformat()
    rows = _build_file_rows(parent)
    content = INDEX_TEMPLATE.format(dir_name=dir_name, today=today, rows=rows)
    if dry_run:
        print(f"  [DRY-RUN] 将创建: {index_path}")
        return True
    try:
        index_path.write_text(content, encoding="utf-8")
        print(f"  + 已创建: {index_path}")
        return True
    except OSError as e:
        print(f"  ERROR: 无法写入 {index_path}: {e}", file=sys.stderr)
        return False


def scan_and_generate(
    root_dir: Path, dry_run: bool = False, auto_yes: bool = False,
) -> tuple[int, int]:
    created = 0
    checked = 0
    missing_dirs: list[Path] = []

    for dirpath in sorted(root_dir.rglob("*")):
        if not dirpath.is_dir():
            continue
        parts = set(dirpath.parts)
        if parts & EXCLUDE_NAMES:
            continue
        if any(p.startswith(".") for p in dirpath.parts):
            continue
        checked += 1
        if not (dirpath / "index.md").exists():
            missing_dirs.append(dirpath)

    if not missing_dirs:
        print(f"OK: 扫描 {checked} 个目录，全部已含 index.md")
        return 0, checked

    print(
        f"扫描 {checked} 个目录，{len(missing_dirs)} 个缺失 index.md:",
        file=sys.stderr if dry_run or auto_yes else sys.stdout,
    )
    for d in missing_dirs:
        rel = str(d.relative_to(root_dir)).replace("\\", "/") or "."
        print(f"  缺失: {rel}/")

    if dry_run:
        print(f"\n[DRY-RUN] 将创建 {len(missing_dirs)} 个 index.md（未实际写入）")
        return len(missing_dirs), checked

    if not auto_yes:
        if _is_tty():
            ans = input(f"\n创建 {len(missing_dirs)} 个 index.md？[y/N] ")
            if ans.lower() != "y":
                print("已取消")
                return 0, checked
        else:
            print(
                "\n  非交互模式 — 跳过创建（用 --yes 或 --dry-run 操作）",
                file=sys.stderr,
            )
            return len(missing_dirs), checked

    for d in missing_dirs:
        if generate_index(d, dry_run=False):
            created += 1

    print(f"\n完成: 创建 {created}/{len(missing_dirs)} 个 index.md")
    return created, checked


def main() -> None:
    parser = ArgumentParser(
        description="为缺失 index.md 的目录自动生成索引文件"
    )
    parser.add_argument(
        "--root", default="docs/",
        help="扫描根目录（相对于项目根，默认 docs/）",
    )
    parser.add_argument("--dry-run", action="store_true", help="只预览，不写入")
    parser.add_argument("--yes", "-y", action="store_true", help="跳过确认，直接创建")
    parser.add_argument("--warn-only", action="store_true",
                        help="巡检模式：发现不阻塞（exit 0）")
    args = parser.parse_args()

    root_dir = (REPO_ROOT / args.root).resolve()
    if not root_dir.is_dir():
        print(f"ERROR: 目录不存在: {root_dir}", file=sys.stderr)
        sys.exit(2)

    created, checked = scan_and_generate(
        root_dir,
        dry_run=args.dry_run,
        auto_yes=args.yes or args.warn_only,
    )

    if args.warn_only:
        sys.exit(0)
    sys.exit(1 if created > 0 else 0)


if __name__ == "__main__":
    main()
