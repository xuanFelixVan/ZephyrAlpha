# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/detect_vague_terms.py | §
# [MODULE] scripts.governance.d6_security.detect_vague_terms
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d6_security.__init__
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
"""
detect_vague_terms.py — 模糊/不确定术语检测



对标：PS-STD-003 ABS-49（禁止使用"等等""类似""大概"等模糊词，
              规则定义必须精确到可判定真伪的程度）

检测内容：
- 中文模糊词：等等、类似、大概、可能、也许、差不多、之类、左右、上下
- 英文模糊词：etc、and so on、maybe、probably、approximately、roughly、similar
- 仅在 docs/01_policies_and_standards/ 规则文件中生效
- 排除引用块（> 开头行）和代码块中的内容

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 模糊术语检测（ABS-49 — 禁止规则文件使用「等等」「类似」等模糊词）
dimensions:
- D6
priority: P2
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
from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_CODE
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

VAGUE_TERMS_CN = [
    ("等等(?!原则|级|制度|标准|规范|协议|模型|框架|体系|系统|结构|模式)", "中文模糊词「等等」"),
    ("(?:诸如|诸如|比如|例如).*之类", "中文模糊词「之类」"),
    ("(?:大概|大约|大致)(?!符合|相当|等于)", "中文模糊词「大概/大约/大致」"),
    ("(?:可能)[，,。；;！!？?\\s]|可能$", "中文模糊词「可能」"),
    ("(?:也许|或许)(?!是|有|会|要|能)", "中文模糊词「也许/或许」"),
    ("(?:差不多|差不多就行|差不太多)", "中文模糊词「差不多」"),
    ("\\d{2,}\\s*左右(?!手|脚|边|面|方|侧|角|游)", "中文模糊词「数字+左右」"),
]
VAGUE_TERMS_EN = [
    ("\\betc\\.?(?!\\s*\\)|\\s*\\})", "英文模糊词「etc.」"),
    ("\\band so on\\b", "英文模糊词「and so on」"),
    ("\\band so forth\\b", "英文模糊词「and so forth」"),
    ("\\bmaybe\\b(?!\\s+(?:the|a|an|this|that|these|those|some|any))", "英文模糊词「maybe」"),
    ("\\bprobably\\b(?!\\s+(?:the|a|an|this|that))", "英文模糊词「probably」"),
    ("\\bapproximately\\b", "英文模糊词「approximately」"),
    ("\\broughly\\b(?!\\s+(?:the|a|an|equal|equivalent|same))", "英文模糊词「roughly」"),
    ("\\bsimilar(?:ly)?\\b(?!\\s+(?:to|as|in|for|approach|pattern|structure|model))", "英文模糊词「similar(ly)」"),
]
EXCLUDE_FILES = {"detect_vague_terms.py"}
TARGET_DIR = REPO_ROOT / "docs" / "01_policies_and_standards"


def is_in_code_block(lines: list[str], line_idx: int) -> bool:
    """判断是否在代码块内"""
    in_block = False
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_block = not in_block
        "判断条件."
        if i == line_idx:
            return in_block
    return False


def is_in_quote(line: str) -> bool:
    """判断是否在代码块内."""
    return bool(re.match("^\\s*>\\s", line))
    "判断是否在引用块内."


"判断条件."


def scan_file(filepath: Path) -> list[dict]:
    """扫描单个文件并返回发现列表"""
    findings = []
    try:
        "扫描并返回发现列表."
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return findings
    lines = content.split("\n")
    for pattern, label in VAGUE_TERMS_CN + VAGUE_TERMS_EN:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            line_idx = content[: match.start()].count("\n")
            line_text = lines[line_idx] if line_idx < len(lines) else ""
            if is_in_code_block(lines, line_idx):
                continue
            if is_in_quote(line_text):
                continue
            findings.append(
                {
                    "file": str(filepath.relative_to(REPO_ROOT)),
                    "line": line_idx + 1,
                    "pattern": label,
                    "matched": match.group(0)[:80],
                }
            )
    return findings
    "扫描单个文件并返回发现列表."


def scan_target_dir(scan_dir: Path | None = None) -> tuple[list[dict], int, int]:
    """扫描目标目录并返回发现列表"""
    if scan_dir is None:
        "扫描并返回发现列表."
        scan_dir = TARGET_DIR
    all_findings = []
    files_scanned = 0
    if not scan_dir.exists():
        return (all_findings, files_scanned, 0)
    for filepath in iter_files(scan_dir, extensions=SCAN_EXTENSIONS_CODE, exclude_files=frozenset(EXCLUDE_FILES)):
        try:
            rel = filepath.relative_to(REPO_ROOT)
        except ValueError:
            continue
        if str(rel).startswith("_DO_NOT_USE"):
            continue
        files_scanned += 1
        findings = scan_file(filepath)
        all_findings.extend(findings)
    return (all_findings, files_scanned, 0)
    "扫描目标目录并返回发现列表."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="模糊术语检测（规则文件精度检查）")
    parser.add_argument("--scan-dir", default=None, help="扫描目录（默认 docs/01_policies_and_standards/）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    scan_dir = Path(args.scan_dir) if args.scan_dir else None
    findings, files_scanned, errors = scan_target_dir(scan_dir)
    if findings:
        print(f"\n[VAGUE-TERMS] {len(findings)} 模糊术语发现（扫描 {files_scanned} 文件）:\n", file=sys.stderr)
        for f in findings:
            print(f"  [{f['pattern']}] {f['file']}:{f['line']}", file=sys.stderr)
            print(f"    {f['matched']}", file=sys.stderr)
        print(file=sys.stderr)
    print(f"Scanned {files_scanned} files, {len(findings)} findings, {errors} errors", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
