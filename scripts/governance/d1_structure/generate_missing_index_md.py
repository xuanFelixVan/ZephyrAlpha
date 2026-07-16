# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/generate_missing_index_md.py | §
# [MODULE] scripts.governance.d1_structure.generate_missing_index_md
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""generate_missing_index_md.py — 扫描目录树，为缺失 index.md 的目录自动生成索引文件。



对标：AGENTS.md §6.11 索引-实际同步强制约定（index.md 必须与磁盘实际一致）
      每次新增目录或批量迁移后运行一次，确保所有目录都有导航索引。

用法：
    python generate_missing_index_md.py --root docs/01_policies_and_standards
    python generate_missing_index_md.py --root docs/ --dry-run      # 只预览
    python generate_missing_index_md.py --root docs/ --warn-only    # 巡检模式（不交互、不写入）
"""

from __future__ import annotations

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


import os
import sys
from argparse import ArgumentParser
from datetime import date
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
from _shared.frontmatter import parse_frontmatter
from _shared.yaml_utils import evaluate_ttl, load_decision_tree

ensure_utf8_stdout()

# ttl 判定树——从 ttl_vocabulary.yaml 动态加载（SSoT 唯一真源，禁止硬编码路径前缀）
# 约束：判定逻辑变更只需改 ttl_vocabulary.yaml decision_tree，本脚本自动同步
_DECISION_TREE = load_decision_tree("ttl_vocabulary.yaml")


def _infer_ttl(parent: Path) -> str:
    """按 ttl_vocabulary.yaml decision_tree 判定 index.md 的 ttl 值。

    向内收：判定逻辑唯一真源为 ttl_vocabulary.yaml decision_tree，本函数零硬编码。
    用 parent/index.md 的相对路径判定（changes/等过程目录下的 index.md → task_bound）。
    """
    try:
        rel = str(parent.resolve().relative_to(REPO_ROOT)).replace("\\", "/") + "/index.md"
    except ValueError:
        # parent 不在 REPO_ROOT 下（极端情况），保守判 task_bound
        return "task_bound"
    return evaluate_ttl(rel, None, _DECISION_TREE)


INDEX_TEMPLATE = (
    "---\n"
    "doc_type: index\n"
    "status: active\n"
    'title: "{dir_name} — 目录索引"\n'
    'module_id: "{module_id}"\n'
    'blueprint_id: "{blueprint_id}"\n'
    'version: "{version}"\n'
    'created: "{today}"\n'
    'updated: "{today}"\n'
    'ttl: "{ttl}"\n'
    "---\n\n"
    "# {dir_name}\n\n"
    "> 本文件由 `generate_missing_index_md.py` 自动生成\n"
    "> 生成日期：{today}\n\n"
    "## 目录内容\n\n"
    "| 文件/目录 | 类型 | 说明 |\n"
    "|-----------|------|------|\n"
    "{rows}\n\n"
    "## 导航\n\n"
    "- [上级目录](../index.md)\n"
)

AUTO_GEN_MARKER = "本文件由 `generate_missing_index_md.py` 自动生成"

EXCLUDE_NAMES = frozenset(
    {
        ".git",
        "__pycache__",
        ".obsidian",
        "_DO_NOT_USE",
        "node_modules",
        ".mypy_cache",
        "scripts",
        "_archive",
        ".trae",
        "_",
        "windi",
        "spikes",
    }
)


def _safe_read_dir(parent: Path) -> list[Path]:
    """_safe_read_dir implementation."""
    try:
        entries = [p for p in parent.iterdir() if p.name not in EXCLUDE_NAMES]
        entries.sort()
        return entries
    except PermissionError:
        return []


def _try_read_title(md_path: Path) -> str | None:
    """_try_read_title implementation."""
    try:
        content = md_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    fm, _body = parse_frontmatter(content)
    if isinstance(fm, dict):
        return fm.get("title")
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _read_blueprint_info(parent: Path) -> tuple[str, str]:
    """读取目录下的 blueprint.md，返回 (module_id, version)。

    如果目录下没有 blueprint.md，返回 ("", "")。
    """
    bp_path = parent / "blueprint.md"
    if not bp_path.exists():
        return "", ""
    try:
        content = bp_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return "", ""
    fm, _body = parse_frontmatter(content)
    if not isinstance(fm, dict):
        return "", ""
    module_id = str(fm.get("module_id", ""))
    version = str(fm.get("version", ""))
    return module_id, version


def _infer_blueprint_id(parent: Path) -> str:
    """从父目录链向上查找最近的 blueprint.md，返回其 module_id。

    用于为没有自己蓝图的子目录推断所属域的 blueprint_id。
    """
    current = parent.parent
    while current != current.parent:
        bp_path = current / "blueprint.md"
        if bp_path.exists():
            try:
                content = bp_path.read_text(encoding="utf-8")
                fm, _body = parse_frontmatter(content)
                if isinstance(fm, dict):
                    mid = str(fm.get("module_id", ""))
                    if mid:
                        return mid
            except (OSError, UnicodeDecodeError):
                pass
        current = current.parent
    return ""


def _build_file_rows(parent: Path) -> str:
    """_build_file_rows implementation."""
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
    """_is_tty implementation."""
    try:
        return sys.stdin.isatty()
    except (AttributeError, OSError):
        return False


def generate_index(parent: Path, dry_run: bool = False, force_update: bool = False) -> bool:
    """Generate output from input data."""
    index_path = parent / "index.md"
    if index_path.exists():
        if force_update:
            try:
                existing = index_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                existing = ""
            if AUTO_GEN_MARKER not in existing:
                return False
        else:
            return False
    dir_name = parent.name or parent.resolve().name
    today = date.today().isoformat()
    rows = _build_file_rows(parent)
    module_id, version = _read_blueprint_info(parent)
    if not module_id:
        blueprint_id = _infer_blueprint_id(parent)
    else:
        blueprint_id = module_id
    if not version:
        version = "1.0.0"
    ttl = _infer_ttl(parent)
    content = INDEX_TEMPLATE.format(
        dir_name=dir_name,
        today=today,
        rows=rows,
        module_id=module_id,
        blueprint_id=blueprint_id,
        version=version,
        ttl=ttl,
    )
    if dry_run:
        print(f"  [DRY-RUN] 将创建: {index_path}")
        return True
    try:
        atomic_write_safe(index_path, content)
        print(f"  + 已创建: {index_path}")
        return True
    except OSError as e:
        print(f"  ERROR: 无法写入 {index_path}: {e}", file=sys.stderr)
        return False


def scan_and_generate(
    root_dir: Path,
    dry_run: bool = False,
    auto_yes: bool = False,
    force_update: bool = False,
) -> tuple[int, int]:
    """scan_and_generate implementation."""
    created = 0
    checked = 0
    missing_dirs: list[Path] = []
    update_candidates: list[Path] = []

    all_dirs = [root_dir]
    all_dirs.extend(sorted(root_dir.rglob("*")))

    for dirpath in all_dirs:
        if not dirpath.is_dir():
            continue
        parts = set(dirpath.parts)
        if parts & EXCLUDE_NAMES:
            continue
        if any(p.startswith(".") for p in dirpath.parts):
            continue
        checked += 1
        idx_path = dirpath / "index.md"
        if not idx_path.exists():
            missing_dirs.append(dirpath)
        elif force_update:
            try:
                existing = idx_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                existing = ""
            if AUTO_GEN_MARKER in existing:
                update_candidates.append(dirpath)

    total_targets = len(missing_dirs) + len(update_candidates)

    if not total_targets:
        print(f"OK: 扫描 {checked} 个目录，全部已含 index.md")
        return 0, checked

    if force_update:
        print(
            f"扫描 {checked} 个目录：{len(missing_dirs)} 个缺失，{len(update_candidates)} 个自动生成待更新",
            file=sys.stderr if dry_run or auto_yes else sys.stdout,
        )
    else:
        print(
            f"扫描 {checked} 个目录，{len(missing_dirs)} 个缺失 index.md:",
            file=sys.stderr if dry_run or auto_yes else sys.stdout,
        )

    for d in missing_dirs:
        rel = str(d.relative_to(root_dir)).replace("\\", "/") or "."
        print(f"  缺失: {rel}/")
    for d in update_candidates:
        rel = str(d.relative_to(root_dir)).replace("\\", "/") or "."
        print(f"  待更新: {rel}/")

    if dry_run:
        print(f"\n[DRY-RUN] 将处理 {total_targets} 个 index.md（未实际写入）")
        return total_targets, checked

    if not auto_yes:
        if _is_tty():
            ans = input(f"\n处理 {total_targets} 个 index.md？[y/N] ")
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
        if generate_index(d, dry_run=False, force_update=force_update):
            created += 1
    for d in update_candidates:
        if generate_index(d, dry_run=False, force_update=force_update):
            created += 1

    action = "更新" if force_update else "创建"
    print(f"\n完成: {action} {created}/{total_targets} 个 index.md")
    return created, checked


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = ArgumentParser(description="为缺失 index.md 的目录自动生成索引文件")
    parser.add_argument(
        "--root",
        default="docs/",
        help="扫描根目录（相对于项目根，默认 docs/）",
    )
    parser.add_argument("--dry-run", action="store_true", help="只预览，不写入")
    parser.add_argument("--yes", "-y", action="store_true", help="跳过确认，直接创建")
    parser.add_argument("--warn-only", action="store_true", help="巡检模式：发现不阻塞（exit 0）")
    parser.add_argument("--update", action="store_true", help="强制更新模式：重新生成所有 index.md（含已存在的）")
    args = parser.parse_args()

    root_dir = (REPO_ROOT / args.root).resolve()
    if not root_dir.is_dir():
        print(f"ERROR: 目录不存在: {root_dir}", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    created, checked = scan_and_generate(
        root_dir,
        dry_run=args.dry_run,
        auto_yes=args.yes or args.warn_only,
        force_update=args.update,
    )

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if created > 0 else 0)


if __name__ == "__main__":
    main()
