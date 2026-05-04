#!/usr/bin/env python3
"""Merge README.md content into index.md, then delete README.md.

__manifest__ = """
args: []
description: 合并 README 到 index.md（目录文档整合工具）
dimensions:
- D1
- D5
priority: P2
timeout_seconds: 30
warn_only: true
"""


Strategy:
- index.md provides the structure (responsibility, file listing, exclusions, parent)
- README.md provides richer human-written description/intro
- Result: unified index.md with the best of both
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date
from pathlib import Path

import yaml
from _shared.frontmatter import parse_frontmatter

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

DOCS_ROOT = Path(__file__).resolve().parent.parent / "docs"

def extract_sections(body) -> Optional[str]:
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

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--warn-only", action="store_true", help="warn mode: exit 0 even if findings")
    args = parser.parse_args()

    pairs = []

    for root, dirs, files in os.walk(DOCS_ROOT):
        has_index = "index.md" in files
        has_readme = "README.md" in files
        if has_index and has_readme:
            pairs.append(root)

    merged = 0
    errors = 0

    for dir_path in sorted(pairs):
        index_path = os.path.join(dir_path, "index.md")
        readme_path = os.path.join(dir_path, "README.md")
        rel = os.path.relpath(dir_path, DOCS_ROOT).replace("\\", "/")

        try:
            merged_content = merge_pair(index_path, readme_path)

            # Write merged index.md
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(merged_content)

            # Delete README.md
            os.remove(readme_path)

            print(f"  MERGED: {rel or 'docs/'}")
            merged += 1
        except (OSError, yaml.YAMLError) as e:
            print(f"  ERROR: {rel or 'docs/'} — {e}", file=sys.stderr)
            errors += 1

    print("\n=== Summary ===")
    print(f"Merged: {merged}")
    print(f"Errors: {errors}")
    remaining = len(pairs) - merged - errors
    print(f"Remaining pairs: {remaining}")

if __name__ == "__main__":
    sys.exit(main() or 0)
