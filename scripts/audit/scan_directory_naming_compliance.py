#!/usr/bin/env python3
from __future__ import annotations

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
扫描目录命名合规性（P6.1～P6.2）。

对照 PATH_STANDARD.md §1.1：
  - 编号前缀：使用 2 位数字（00_、01_、02_ 等）
  - 英文命名：小写字母 + 下划线
  - 禁止中文目录名
  - 禁止空格
  - 禁止特殊字符（除下划线、连字符）

仓库根执行示例:
  python scripts/governance/scan_directory_naming_compliance.py --date 20260411
  python scripts/governance/scan_directory_naming_compliance.py --prefix docs/
  python scripts/governance/scan_directory_naming_compliance.py --check-registration

输出:
  docs/09_AUDIT/STATE/DIRECTORY_NAMING_COMPLIANCE_<date>.json
  docs/09_AUDIT/STATE/DIRECTORY_NAMING_COMPLIANCE_<date>.md
"""

import argparse
import json
import os
import re
import subprocess
from collections import defaultdict
from datetime import date
from pathlib import Path

GEN = "scripts/governance/scan_directory_naming_compliance.py"

VALID_PREFIX_PATTERN = re.compile(r"^\d{2}_")
INVALID_CHARS_PATTERN = re.compile(r"[^\w\-]")
CHINESE_PATTERN = re.compile(r"[\u4e00-\u9fff]")


def git_ls_files(repo_root: Path) -> list[str]:
    out = subprocess.check_output(
        ["git", "-c", "core.quotePath=false", "ls-files"],
        cwd=repo_root,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return [ln.strip().replace("\\", "/") for ln in out.splitlines() if ln.strip()]


def extract_directories(paths: list[str], prefix: str | None) -> set[str]:
    dirs: set[str] = set()
    pre = (prefix or "").replace("\\", "/")
    if pre and not pre.endswith("/"):
        pre += "/"
    for rel in paths:
        if pre and not rel.startswith(pre):
            continue
        parts = rel.split("/")
        for i in range(1, len(parts)):
            dir_path = "/".join(parts[:i])
            if dir_path:
                dirs.add(dir_path)
    return dirs


def check_directory_name(dir_name: str) -> dict:
    issues: list[str] = []

    if CHINESE_PATTERN.search(dir_name):
        issues.append("包含中文字符")

    if " " in dir_name:
        issues.append("包含空格")

    if INVALID_CHARS_PATTERN.search(dir_name.replace("_", "").replace("-", "")):
        issues.append("包含特殊字符")

    if not VALID_PREFIX_PATTERN.match(dir_name):
        if dir_name not in {"docs", "scripts", "src", "tests", "config", "data", ".git", ".github", ".venv", ".pytest_cache", "__pycache__", "node_modules"}:
            issues.append("缺少 2 位数字前缀（如 00_、01_）")

    return {
        "name": dir_name,
        "has_chinese": bool(CHINESE_PATTERN.search(dir_name)),
        "has_space": " " in dir_name,
        "has_special_chars": bool(INVALID_CHARS_PATTERN.search(dir_name.replace("_", "").replace("-", ""))),
        "missing_prefix": not VALID_PREFIX_PATTERN.match(dir_name) and dir_name not in {"docs", "scripts", "src", "tests", "config", "data", ".git", ".github", ".venv", ".pytest_cache", "__pycache__", "node_modules"},
        "issues": issues,
    }


def scan_directories(repo_root: Path, prefix: str | None) -> dict:
    paths = git_ls_files(repo_root)
    dirs = extract_directories(paths, prefix)

    results: dict[str, list[dict]] = defaultdict(list)
    summary = {
        "total_directories": len(dirs),
        "with_chinese": 0,
        "with_space": 0,
        "with_special_chars": 0,
        "missing_prefix": 0,
        "compliant": 0,
    }

    for dir_path in sorted(dirs):
        dir_name = os.path.basename(dir_path)
        check_result = check_directory_name(dir_name)
        check_result["path"] = dir_path

        if check_result["has_chinese"]:
            summary["with_chinese"] += 1
            results["chinese"].append(check_result)
        if check_result["has_space"]:
            summary["with_space"] += 1
            results["space"].append(check_result)
        if check_result["has_special_chars"]:
            summary["with_special_chars"] += 1
            results["special_chars"].append(check_result)
        if check_result["missing_prefix"]:
            summary["missing_prefix"] += 1
            results["missing_prefix"].append(check_result)

        if not check_result["issues"]:
            summary["compliant"] += 1

    return {
        "summary": summary,
        "issues": dict(results),
    }


def render_markdown(data: dict, date_str: str) -> str:
    lines = [
        f"# 目录命名合规性扫描报告",
        f"",
        f"> **生成脚本**: `{GEN}`",
        f"> **扫描日期**: {date_str}",
        f"",
        f"---",
        f"",
        f"## 扫描摘要",
        f"",
        f"| 指标 | 数量 |",
        f"|------|------|",
        f"| 总目录数 | {data['summary']['total_directories']} |",
        f"| 包含中文 | {data['summary']['with_chinese']} |",
        f"| 包含空格 | {data['summary']['with_space']} |",
        f"| 包含特殊字符 | {data['summary']['with_special_chars']} |",
        f"| 缺少编号前缀 | {data['summary']['missing_prefix']} |",
        f"| 合规目录 | {data['summary']['compliant']} |",
        f"",
    ]

    issues = data.get("issues", {})

    if issues.get("chinese"):
        lines.extend([
            f"## 包含中文的目录",
            f"",
            f"| 路径 | 目录名 |",
            f"|------|--------|",
        ])
        for item in issues["chinese"]:
            lines.append(f"| `{item['path']}` | `{item['name']}` |")
        lines.append("")

    if issues.get("space"):
        lines.extend([
            f"## 包含空格的目录",
            f"",
            f"| 路径 | 目录名 |",
            f"|------|--------|",
        ])
        for item in issues["space"]:
            lines.append(f"| `{item['path']}` | `{item['name']}` |")
        lines.append("")

    if issues.get("special_chars"):
        lines.extend([
            f"## 包含特殊字符的目录",
            f"",
            f"| 路径 | 目录名 |",
            f"|------|--------|",
        ])
        for item in issues["special_chars"]:
            lines.append(f"| `{item['path']}` | `{item['name']}` |")
        lines.append("")

    if issues.get("missing_prefix"):
        lines.extend([
            f"## 缺少编号前缀的目录",
            f"",
            f"> **说明**: 以下目录未使用 2 位数字前缀（如 `00_`、`01_`）。部分根目录（如 `docs`、`scripts`）为例外。",
            f"",
            f"| 路径 | 目录名 |",
            f"|------|--------|",
        ])
        for item in issues["missing_prefix"]:
            lines.append(f"| `{item['path']}` | `{item['name']}` |")
        lines.append("")

    if not any(issues.values()):
        lines.extend([
            f"## 结论",
            f"",
            f"**所有目录命名均合规**。",
            f"",
        ])

    lines.extend([
        f"---",
        f"",
        f"## 参考标准",
        f"",
        f"- [PATH_STANDARD.md](../../docs/05_IMPLEMENTATION/02_DEVELOPMENT/PATH_STANDARD.md) §1.1",
        f"- [FILE_NAMING_STANDARD.md](../../docs/09_AUDIT/STANDARDS/FILE_NAMING_STANDARD.md)",
        f"",
    ])

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="扫描目录命名合规性")
    parser.add_argument("--date", default=date.today().strftime("%Y%m%d"), help="报告日期 (YYYYMMDD)")
    parser.add_argument("--prefix", default=None, help="仅扫描指定前缀下的目录")
    parser.add_argument("--output-dir", default="docs/09_AUDIT/STATE", help="输出目录")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    output_dir = repo_root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"扫描目录命名合规性...")
    data = scan_directories(repo_root, args.prefix)

    base_name = f"DIRECTORY_NAMING_COMPLIANCE_{args.date}"

    json_path = output_dir / f"{base_name}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"JSON 报告: {json_path}")

    md_path = output_dir / f"{base_name}.md"
    md_content = render_markdown(data, args.date)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"MD 报告: {md_path}")

    print(f"\n摘要:")
    print(f"  总目录数: {data['summary']['total_directories']}")
    print(f"  包含中文: {data['summary']['with_chinese']}")
    print(f"  包含空格: {data['summary']['with_space']}")
    print(f"  包含特殊字符: {data['summary']['with_special_chars']}")
    print(f"  缺少编号前缀: {data['summary']['missing_prefix']}")
    print(f"  合规目录: {data['summary']['compliant']}")

    return 0


if __name__ == "__main__":
    exit(main())
