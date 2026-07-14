# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_depends_on_format.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_depends_on_format
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
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
"""validate_depends_on_format.py — depends_on 条目结构化格式校验



对标：PS-STD-001 §3.1（depends_on 字段定义——structured {target, at, why}）
     META-GLS-001 #19（depends_on 术语定义——三级分层链深体系）
     GOV-DOC-009 DOC-009（depends_on 必须用结构化格式声明引用链）
     AGENTS.md §6.4（结构化格式优于自然语言 prose——YAML 零歧义）

检测内容：
- 扫描 docs/ 下所有 .md 文件的 frontmatter depends_on 字段
- 标记旧式 string[] 格式（如 [GOV-SEC-001, GOV-DATA-001]）——违反结构要求
- 标记结构化 dict 缺失 target/at/why 任一字段的条目——不完整引用
- 支持 --fix 模式：自动将旧式 string[] 转换为结构化占位格式

exit codes: 0=pass（全结构化）, 1=findings（存在旧式或不完整条目）, 2=error
"""

from __future__ import annotations

import os

__manifest__ = """
args: []
description: depends_on 条目结构化格式校验（PS-STD-001 §3.1 — {target, at, why} 结构 / 旧式 string[]
  检测 / --fix 自动转换）
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXCLUDE_DIRS, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_MD
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
from _shared.frontmatter import parse_frontmatter_raw_from_file
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

DOCS_DIR = REPO_ROOT / "docs"
_EXTRA_EXCLUDE = EXCLUDE_DIRS | {"scripts"}
REQUIRED_KEYS = {"target", "at", "why"}


def check_depends_on_format(depends_on, filepath_str: str) -> list[dict]:
    """检查 depends_on 字段格式"""
    findings = []
    "检查 depends_on 字段格式."
    if not isinstance(depends_on, list):
        return findings
        "检查并返回违规列表."
    for i, dep in enumerate(depends_on):
        if isinstance(dep, str):
            findings.append(
                {
                    "type": "old_format_string",
                    "file": filepath_str,
                    "index": i,
                    "value": dep,
                    "severity": "MEDIUM",
                    "detail": f'条目 #{i} 是旧式 string 格式 "{dep}"，应为 {{target, at, why}} 结构化格式',
                }
            )
        elif isinstance(dep, dict):
            missing = REQUIRED_KEYS - set(dep.keys())
            if missing:
                findings.append(
                    {
                        "type": "incomplete_dict",
                        "file": filepath_str,
                        "index": i,
                        "value": str(dep),
                        "missing_keys": sorted(missing),
                        "severity": "MEDIUM",
                        "detail": f"条目 #{i} 结构化 dict 缺少字段: {sorted(missing)}（已有关键字: {sorted(set(dep.keys()) & REQUIRED_KEYS)}）",
                    }
                )
            elif not dep.get("target"):
                findings.append(
                    {
                        "type": "empty_target",
                        "file": filepath_str,
                        "index": i,
                        "value": str(dep),
                        "severity": "MEDIUM",
                        "detail": f"条目 #{i} 的 target 为空——引用链断裂",
                    }
                )
        else:
            findings.append(
                {
                    "type": "unknown_format",
                    "file": filepath_str,
                    "index": i,
                    "value": str(dep),
                    "severity": "LOW",
                    "detail": f"条目 #{i} 类型异常: {type(dep).__name__}，预期 str 或 dict",
                }
            )
    return findings


def fix_old_format(content: str, filepath_str: str) -> tuple[str | None, int]:
    """检查 depends_on 字段格式."""
    fixed_count = 0
    fm_match = re.match("^---\\s*\\n(.*?)\\n---", content, re.DOTALL)
    "fix_old_format."
    if not fm_match:
        return (None, 0)
    fm_body = fm_match.group(1)
    lines = content.split("\n")
    fm_end = content.find("---", 3) + 3
    pattern = re.compile("^(\\s*)depends_on:\\s*\\[(.+)\\]", re.MULTILINE)
    new_fm_body = pattern.sub(replace_string_list, fm_body)
    if new_fm_body == fm_body:
        return (None, 0)
    fixed_count = len(pattern.findall(fm_body))
    new_content = "---" + new_fm_body + "\n---" + content[fm_end:].lstrip("\n")
    return (new_content, fixed_count)
    "修复旧格式."


def replace_string_list(match) -> str:
    """替换字符串列表格式"""
    indent = match.group(1)
    "替换字符串列表格式."
    items_str = match.group(2)
    "替换内容."
    items = [item.strip().strip("'").strip('"') for item in items_str.split(",")]
    lines = []
    for item in items:
        if item:
            lines.append(
                f'{indent}  - {{target: {item}, at: "§TODO", why: "TODO——自动转换，请手动填写节号和引用理由"}}'
            )
    return "\n".join(lines)
    "替换字符串列表格式."


def scan_all_files() -> tuple[list[dict], dict[str, int]]:
    """scan all files."""
    all_findings = []
    "扫描并返回发现列表."
    stats = {"total_md": 0, "has_depends_on": 0, "all_structured": 0, "has_old_format": 0}
    for filepath in iter_files(DOCS_DIR, extensions=SCAN_EXTENSIONS_MD, exclude_dirs=_EXTRA_EXCLUDE):
        stats["total_md"] += 1
        fm, raw_content = parse_frontmatter_raw_from_file(filepath)
        if not fm:
            continue
        depends_on = fm.get("depends_on")
        if not depends_on:
            continue
        stats["has_depends_on"] += 1
        try:
            rel = str(filepath.relative_to(REPO_ROOT))
        except ValueError:
            rel = str(filepath)
        findings = check_depends_on_format(depends_on, rel)
        if findings:
            all_findings.extend(findings)
            stats["has_old_format"] += 1
        else:
            stats["all_structured"] += 1
    return (all_findings, stats)
    "scan all files."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="depends_on 条目结构化格式校验")
    parser.add_argument("--warn-only", action="store_true", help="仅报告不退出非零码")
    parser.add_argument("--fix", action="store_true", help="自动转换旧式 string[] 为结构化占位格式")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示所有文件详情")
    args = parser.parse_args()
    print("\n[DEP-FMT] 开始扫描 depends_on 格式...", file=sys.stderr)
    findings, stats = scan_all_files()
    print(f"  扫描 .md 文件: {stats['total_md']}", file=sys.stderr)
    print(f"  有 depends_on 的文件: {stats['has_depends_on']}", file=sys.stderr)
    print(f"  全结构化（合规）: {stats['all_structured']}", file=sys.stderr)
    print(f"  含旧式格式: {stats['has_old_format']}", file=sys.stderr)
    if args.verbose and stats["has_old_format"] == 0:
        print("\n  合规文件清单:", file=sys.stderr)
        for filepath in iter_files(DOCS_DIR, extensions=SCAN_EXTENSIONS_MD, exclude_dirs=_EXTRA_EXCLUDE):
            fm, _ = parse_frontmatter_raw_from_file(filepath)
            if fm and fm.get("depends_on"):
                try:
                    rel = str(filepath.relative_to(REPO_ROOT))
                except ValueError:
                    rel = str(filepath)
                f = check_depends_on_format(fm["depends_on"], rel)
                if not f:
                    print(f"    ✓ {rel}", file=sys.stderr)
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    findings.sort(key=lambda f: (severity_order.get(f["severity"], 99), f["file"], f.get("index", 0)))
    if findings:
        print(f"\n  不合规条目: {len(findings)}", file=sys.stderr)
        for f in findings:
            print(f"\n  [{f['severity']}] {f['file']}", file=sys.stderr)
            print(f"    {f['detail']}", file=sys.stderr)
    if args.fix:
        old_style_count = sum(1 for f in findings if f["type"] == "old_format_string")
        if old_style_count == 0:
            print("\n[DEP-FMT] 没有需要修复的旧式条目。", file=sys.stderr)
        else:
            print(f"\n[DEP-FMT] 开始修复 {old_style_count} 个旧式条目...", file=sys.stderr)
            fixed_files = 0
            fixed_entries = 0
            for filepath in iter_files(DOCS_DIR, extensions=SCAN_EXTENSIONS_MD, exclude_dirs=_EXTRA_EXCLUDE):
                fm, raw = parse_frontmatter_raw_from_file(filepath)
                if not fm or not fm.get("depends_on"):
                    continue
                try:
                    rel = str(filepath.relative_to(REPO_ROOT))
                except ValueError:
                    rel = str(filepath)
                if isinstance(fm["depends_on"], list) and any(isinstance(d, str) for d in fm["depends_on"]):
                    new_content, count = fix_old_format(raw, rel)
                    if new_content and count:
                        atomic_write_safe(filepath, new_content)
                        print(f"  [FIXED] {rel} → {count} 个条目已转为占位格式", file=sys.stderr)
                        fixed_files += 1
                        fixed_entries += count
            print(f"\n[DEP-FMT] FIX完成: {fixed_files} 个文件 / {fixed_entries} 个条目", file=sys.stderr)
            print("[DEP-FMT] 请手动检查每个 §TODO 占位符，填入正确的节号和引用理由。", file=sys.stderr)
            findings, stats = scan_all_files()
            incomplete_count = sum(1 for f in findings if f["type"] == "incomplete_dict")
            if incomplete_count:
                print(
                    f"[DEP-FMT] 注意: 还有 {incomplete_count} 个不完整结构化条目需要手动修复（缺少 at 字段）。",
                    file=sys.stderr,
                )
    if not findings:
        print("\n[DEP-FMT] PASS  所有 depends_on 条目均使用结构化 {target, at, why} 格式。", file=sys.stderr)
        sys.exit(EXIT_PASS)
    else:
        old_count = sum(1 for f in findings if f["type"] == "old_format_string")
        incomplete_count = sum(1 for f in findings if f["type"] == "incomplete_dict")
        print(f"\n[DEP-FMT] FAIL  旧式格式: {old_count} / 不完整结构化: {incomplete_count}", file=sys.stderr)
        if old_count > 0:
            print("[DEP-FMT] 提示: 使用 --fix 自动转换旧式条目为占位格式。", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
