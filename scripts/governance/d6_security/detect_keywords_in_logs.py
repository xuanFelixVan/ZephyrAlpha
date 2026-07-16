# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/detect_keywords_in_logs.py | §
# [MODULE] scripts.governance.d6_security.detect_keywords_in_logs
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
detect_keywords_in_logs.py — 日志输出敏感关键词检测



对标：PS-STD-003 ABS-31（禁止在日志/print 中输出密钥、Token、密码等敏感信息）

检测内容：
- print() / logging.info() / logger.info() 等输出语句中包含疑似敏感关键词
- password / secret / token / api_key / credential 等敏感词出现在日志参数中
- f-string 和 .format() 中内嵌敏感变量名

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 日志输出敏感关键词检测（ABS-31 — 禁止 print/log 密钥密码）
dimensions:
- D6
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
from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_CODE
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

LOG_SENSITIVE_PATTERNS = [
    (
        "(?:print|log(?:ger)?\\.(?:info|debug|warn(?:ing)?|error|critical|exception))\\s*\\(\\s*.*\\b(password|passwd|secret|token|api[_-]?key|credential|private[_-]?key|access[_-]?key)\\b",
        "日志输出包含敏感关键词 (ABS-31)",
    ),
    (
        "(?:print|log(?:ger)?\\.(?:info|debug|warn(?:ing)?|error|critical|exception))\\s*\\(\\s*.*\\b(PASSWORD|SECRET|TOKEN|API_KEY|CREDENTIAL|PRIVATE_KEY|ACCESS_KEY)\\b",
        "日志输出包含大写敏感变量名 (ABS-31)",
    ),
    (
        "print\\s*\\(\\s*f[\"\\'].*\\{(?:password|secret|token|api_key|credential|key)\\}",
        "f-string 日志输出包含敏感变量 (ABS-31)",
    ),
]
EXCLUDE_FILES = {"detect_keywords_in_logs.py", "detect_secrets.py"}


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
    for pattern, label in LOG_SENSITIVE_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            findings.append(
                {
                    "file": str(filepath.relative_to(REPO_ROOT)),
                    "line": content[: match.start()].count("\n") + 1,
                    "pattern": label,
                    "matched": match.group(0)[:200],
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
    for filepath in iter_files(scan_dir, extensions=SCAN_EXTENSIONS_CODE, exclude_files=frozenset(EXCLUDE_FILES)):
        try:
            rel = filepath.relative_to(REPO_ROOT)
        except (ValueError, OSError):
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
    parser = argparse.ArgumentParser(description="日志输出敏感关键词检测")
    parser.add_argument("--scan-dir", default=None, help="扫描目录")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    scan_dir = Path(args.scan_dir) if args.scan_dir else None
    findings, files_scanned, errors = scan_repo(scan_dir)
    if findings:
        print(
            f"\n[LOG-SENSITIVE] {len(findings)} 日志输出含敏感关键词（扫描 {files_scanned} 文件）:\n", file=sys.stderr
        )
        for f in findings:
            print(f"  [{f['pattern']}] {f['file']}:{f['line']}", file=sys.stderr)
            print(f"    {f['matched'][:180]}", file=sys.stderr)
        print(file=sys.stderr)
    print(f"Scanned {files_scanned} files, {len(findings)} findings, {errors} errors", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
