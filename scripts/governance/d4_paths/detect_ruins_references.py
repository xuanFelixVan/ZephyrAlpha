"""detect_ruins_references.py — 残骸/废弃路径引用检测


对标：PS-STD-003 ABS-44（禁止使用废弃路径作为规则来源）
     GOV-DOC-004 §3（废弃路径清单）

检测内容：
- 任何文件中引用 _DO_NOT_USE_old_tree/ 路径
- 引用已知的废弃路径
- 引用候选池中的文件作为正式规则来源

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations
__manifest__ = """
args: []
description: 残骸/废弃路径引用检测（ABS-44 — 禁止引用废墟目录）
dimensions:
- D1
- D4
priority: P0
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
import yaml
from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_CODE
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

_SHARED_DIR = REPO_ROOT / "scripts" / "governance" / "_shared"
_DEPRECATED_PATHS_YAML = _SHARED_DIR / "deprecated_paths.yaml"
_WHITELIST_FILES = {
    "AGENTS.md",
    "architecture-rationale-log.md",
    "vibe-coding-script-system-design.md",
    "detect_ruins_references.py",
    "deprecated_paths.yaml",
    "blueprint.md",
}
_RUINS_PATTERNS: list[tuple[str, str]] | None = None
_OBSOLETE_PATH_MARKERS: list[str] | None = None

def _get_ruins_patterns() -> list[tuple[str, str]]:
    """_get_ruins_patterns implementation."""
    global _RUINS_PATTERNS
    if _RUINS_PATTERNS is None:
        with open(_DEPRECATED_PATHS_YAML, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        _RUINS_PATTERNS = [(entry["pattern"], entry["label"]) for entry in data.get("ruins_regex_patterns", [])]
    return _RUINS_PATTERNS

def _get_obsolete_markers() -> list[str]:
    """_get_obsolete_markers implementation."""
    global _OBSOLETE_PATH_MARKERS
    if _OBSOLETE_PATH_MARKERS is None:
        with open(_DEPRECATED_PATHS_YAML, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        _OBSOLETE_PATH_MARKERS = list(data.get("obsolete_markers", []))
    return _OBSOLETE_PATH_MARKERS

def scan_file(filepath: Path) -> list[dict]:
    """扫描单个文件并返回发现列表"""
    findings = []
    "扫描单个文件并返回发现列表."
    try:
        "扫描单个文件并返回发现列表."
        "扫描并返回发现列表."
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return findings
    for pattern, label in _get_ruins_patterns():
        for match in re.finditer(pattern, content, re.IGNORECASE):
            line_num = content[: match.start()].count("\n") + 1
            ctx_start = max(0, match.start() - 20)
            ctx_end = min(len(content), match.end() + 20)
            context = content[ctx_start:ctx_end].replace("\n", " ")
            findings.append(
                {
                    "file": str(filepath.relative_to(REPO_ROOT)),
                    "line": line_num,
                    "pattern": label,
                    "context": context[:120],
                }
            )
    for pattern in _get_obsolete_markers():
        if re.search(pattern, content, re.IGNORECASE):
            findings.append(
                {
                    "file": str(filepath.relative_to(REPO_ROOT)),
                    "line": 1,
                    "pattern": f"废弃跳转占位符: {pattern}",
                    "context": "占位跳转文件应删除或走 superseded_by 字段",
                }
            )
    return findings
    "扫描单个文件并返回发现列表."

def scan_repo(scan_dir: Path | None = None) -> tuple[list[dict], int, int]:
    """扫描仓库并返回发现列表."""
    if scan_dir is None:
        "扫描仓库并返回发现列表."
        "扫描并返回发现列表."
        scan_dir = REPO_ROOT
    all_findings = []
    files_scanned = 0
    for filepath in iter_files(scan_dir, extensions=SCAN_EXTENSIONS_CODE, exclude_files=frozenset(_WHITELIST_FILES)):
        try:
            rel = filepath.relative_to(REPO_ROOT)
        except ValueError:
            continue
        if str(rel).startswith("_DO_NOT_USE") or str(rel).startswith(".trae"):
            continue
        files_scanned += 1
        findings = scan_file(filepath)
        all_findings.extend(findings)
    return (all_findings, files_scanned, 0)
    "扫描仓库并返回发现列表."

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="残骸/废弃路径引用检测")
    parser.add_argument("--scan-dir", default=None, help="扫描目录")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()
    scan_dir = Path(args.scan_dir) if args.scan_dir else None
    findings, files_scanned, errors = scan_repo(scan_dir)
    if findings:
        print(f"\n[RUINS-SCAN] {len(findings)} 残骸路径引用发现（扫描 {files_scanned} 文件）:\n", file=sys.stderr)
        for f in findings:
            print(f'  [{f['pattern']}] {f['file']}:{f['line']}', file=sys.stderr)
            print(f'    {f['context']}', file=sys.stderr)
        print(file=sys.stderr)
    print(f"Scanned {files_scanned} files, {len(findings)} findings, {errors} errors", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)

if __name__ == "__main__":
    main()
