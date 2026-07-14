# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/syncers/merge_readme_to_index.py | §
# [MODULE] scripts.governance.d5_architecture.syncers.merge_readme_to_index
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.syncers.__init__
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
# [TTL] task_bound
#!/usr/bin/env python3
"""


Strategy:
- index.md provides the structure (responsibility, file listing, exclusions, parent)
- README.md provides richer human-written description/intro
- Result: unified index.md with the best of both
"""

from __future__ import annotations

import os

__manifest__ = """
args:
  - --warn-only
  - --jsonl
description: 合并 README 到 index.md（目录文档整合工具）
dimensions:
- D1
- D5
priority: P2
timeout_seconds: 30
warn_only: true
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import yaml

_SCRIPT = Path(__file__).resolve()

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
from _shared.frontmatter import parse_frontmatter

ensure_utf8_stdout()

DOCS_ROOT = REPO_ROOT / "docs"


def extract_sections(body: str) -> dict[str, str]:
    """Extract key sections from index.md body."""
    sections = {}
    current_section = "_intro"
    current_lines = []

    for line in body.split("\n"):
        if line.startswith("## "):
            if current_lines:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections[current_section] = "\n".join(current_lines).strip()

    return sections


def merge_pair(index_path, readme_path) -> None:
    """Merge README.md into index.md, return merged content."""
    with open(index_path, encoding="utf-8") as f:
        index_raw = f.read()
    with open(readme_path, encoding="utf-8") as f:
        readme_raw = f.read()

    index_fm, index_body = parse_frontmatter(index_raw)
    readme_fm, readme_body = parse_frontmatter(readme_raw)

    index_sections = extract_sections(index_body)
    readme_sections = extract_sections(readme_body)

    # Merge frontmatter: index.md base, enriched with README.md metadata
    merged_fm = dict(index_fm)
    for key in ["module_id", "title", "classification", "layer"]:
        if key in readme_fm and key not in merged_fm:
            merged_fm[key] = readme_fm[key]
    merged_fm["doc_type"] = "index"
    merged_fm["status"] = "active"
    merged_fm["merged_from"] = "README.md + index.md"
    merged_fm["date"] = date.today().isoformat()

    # Build merged body
    lines = []

    # Title - prefer README.md title if it has a better one
    r_title = readme_sections.pop("_intro", "")
    i_title = index_sections.pop("_intro", "")

    # Use the more descriptive title/intro
    if len(r_title) > len(i_title):
        # README.md intro is richer — use it as the intro
        # Extract the first heading from README intro
        lines.append(r_title)
    elif i_title:
        lines.append(i_title)
    elif r_title:
        lines.append(r_title)

    # Responsibility section (from index.md)
    resp = index_sections.pop("责任声明（Single Responsibility）", "")
    if not resp:
        resp = index_sections.pop("责任声明", "")
    if resp:
        lines.append("")
        lines.append("## 责任声明（Single Responsibility）")
        lines.append("")
        lines.append(resp)

    # File listing (from index.md)
    fl = index_sections.pop("文件清单", "")
    if fl:
        lines.append("")
        lines.append("## 文件清单")
        lines.append("")
        lines.append(fl)

    # Additional content from README.md (sections not in index.md)
    readme_extra_sections = {}
    for key, val in readme_sections.items():
        if val.strip() and key not in [
            "_intro",
            "责任声明（Single Responsibility）",
            "责任声明",
            "文件清单",
            "排除规则",
            "父级目录",
        ]:
            readme_extra_sections[key] = val

    if readme_extra_sections:
        lines.append("")
        for key, val in readme_extra_sections.items():
            lines.append(f"## {key}")
            lines.append("")
            lines.append(val)
            lines.append("")

    # Remaining index.md sections (exclusions, parent, etc.)
    for key in ["排除规则", "排除规则（不应放入本目录的内容）", "父级目录", "父级"]:
        val = index_sections.pop(key, "")
        if val:
            lines.append("")
            lines.append(f"## {key}")
            lines.append("")
            lines.append(val)

    # Any leftover index sections
    for key, val in index_sections.items():
        if val.strip():
            lines.append("")
            lines.append(f"## {key}")
            lines.append("")
            lines.append(val)

    # Build final content
    frontmatter_str = yaml.dump(merged_fm, allow_unicode=True, default_flow_style=False).strip()
    body_str = "\n".join(lines).strip()

    return f"---\n{frontmatter_str}\n---\n\n{body_str}\n"


def main() -> int:
    """入口函数."""
    parser = argparse.ArgumentParser(description="Merge README.md into index.md within docs/.")
    parser.add_argument("--warn-only", action="store_true", help="warn mode: exit 0 even if findings")
    parser.add_argument("--jsonl", action="store_true", help="单行 JSON 摘要输出")
    args = parser.parse_args()

    pairs = []

    for dirpath in sorted(DOCS_ROOT.rglob("*")):
        if not dirpath.is_dir():
            continue
        files = [f.name for f in dirpath.iterdir() if f.is_file()]
        has_index = "index.md" in files
        has_readme = "README.md" in files
        if has_index and has_readme:
            pairs.append(dirpath)

    merged = 0
    errors = 0

    for dir_path in sorted(pairs):
        index_path = dir_path / "index.md"
        readme_path = dir_path / "README.md"
        rel = str(dir_path.relative_to(DOCS_ROOT)).replace("\\", "/")

        try:
            merged_content = merge_pair(str(index_path), str(readme_path))

            atomic_write_safe(index_path, merged_content)

            if not args.warn_only:
                backup_dir = readme_path.parent / ".backup"
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / f"{readme_path.stem}_{date.today().isoformat()}.md"
                readme_path.replace(backup_path)
                print(f"  MERGED+BACKUP: {rel or 'docs/'} (README → {backup_path.name})")
            else:
                print(f"  MERGED (README kept, --warn-only): {rel or 'docs/'}")
            merged += 1
        except (OSError, yaml.YAMLError) as e:
            print(f"  ERROR: {rel or 'docs/'} — {e}", file=sys.stderr)
            errors += 1

    print("\n=== Summary ===")
    print(f"Merged: {merged}")
    print(f"Errors: {errors}")
    remaining = len(pairs) - merged - errors
    print(f"Remaining pairs: {remaining}")

    exit_code = 1 if errors else 0
    if args.jsonl:
        print(
            json.dumps(
                {
                    "severity": "HIGH" if errors else "INFO",
                    "check_id": "MERGE-README-INDEX",
                    "merged": merged,
                    "errors": errors,
                    "pairs": len(pairs),
                },
                ensure_ascii=False,
            )
        )
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
