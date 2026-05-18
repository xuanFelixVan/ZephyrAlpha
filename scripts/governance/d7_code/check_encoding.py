# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/check_encoding.py | §
"""check_encoding.py — 编码合规校验（INJ-007）

对标：GOV-MOD-001 INJ-007（编码合规）

检测内容：
- --file: 检查指定文件的编码合规性（UTF-8 BOM/无BOM、无 CRLF、无 autoGuessEncoding）
- 包装 scripts/governance/d7_code/detect_missing_encoding.py 的功能

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args:
- {flag: --file, type: str, description: "检查指定文件的编码合规性"}
- {flag: --dir, type: str, description: "检查指定目录下所有文件的编码合规性"}
description: >
  编码合规校验（INJ-007）——UTF-8 编码、无 CRLF、无 autoGuessEncoding。
  对标 GOV-MOD-001 module-injection-rules.yaml。
dimensions:
- D7
priority: P1
timeout_seconds: 15
warn_only: false
"""

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT, EXIT_PASS, EXIT_FINDINGS, EXIT_ERROR
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

BOM = b"\xef\xbb\xbf"
CRLF = b"\r\n"
AUTO_GUESS_PATTERNS = [b"autoGuessEncoding", b"auto_guess_encoding", b"files.autoGuessEncoding"]


def check_file_encoding(filepath: str) -> list[str]:
    """Check compliance and report findings."""
    findings = []
    p = Path(filepath)
    if not p.exists():
        findings.append(f"INJ-007 FAIL: file '{filepath}' does not exist")
        return findings
    if p.is_dir():
        findings.append(f"INJ-007 FAIL: '{filepath}' is a directory, use --dir instead")
        return findings
    raw = p.read_bytes()
    if raw.startswith(BOM):
        findings.append(f"INJ-007 FAIL: file '{filepath}' has UTF-8 BOM — must be UTF-8 without BOM")
    if CRLF in raw:
        crlf_count = raw.count(CRLF)
        findings.append(f"INJ-007 WARNING: file '{filepath}' has {crlf_count} CRLF line endings — should use LF")
    for pattern in AUTO_GUESS_PATTERNS:
        if pattern in raw:
            findings.append(f"INJ-007 FAIL: file '{filepath}' contains '{pattern.decode()}' — autoGuessEncoding must be false")
    return findings


def check_dir_encoding(dirpath: str) -> list[str]:
    """Check compliance and report findings."""
    findings = []
    p = Path(dirpath)
    if not p.exists():
        findings.append(f"INJ-007 FAIL: directory '{dirpath}' does not exist")
        return findings
    for f in p.rglob("*"):
        if f.suffix in (".py", ".md", ".yaml", ".yml", ".json", ".toml"):
            findings.extend(check_file_encoding(str(f)))
    return findings


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Encoding compliance check (INJ-007)")
    parser.add_argument("--file", type=str, help="Check encoding of a specific file")
    parser.add_argument("--dir", type=str, help="Check encoding of all files in directory")
    parser.add_argument("--warn-only", action="store_true", help="Only warn, do not fail")
    args = parser.parse_args()

    all_findings: list[str] = []

    if args.file:
        all_findings.extend(check_file_encoding(args.file))

    if args.dir:
        all_findings.extend(check_dir_encoding(args.dir))

    if not any([args.file, args.dir]):
        print("Usage: check_encoding.py --file <path> | --dir <path>")
        sys.exit(EXIT_ERROR)

    for finding in all_findings:
        print(finding)

    if all_findings and not args.warn_only:
        sys.exit(EXIT_FINDINGS)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
