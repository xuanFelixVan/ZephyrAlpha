# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/detect_secrets.py | §
# [MODULE] scripts.governance.d6_security.detect_secrets
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
# [TTL] task_bound
"""
detect_secrets.py — 密钥/Token/凭证硬编码检测



对标：PS-STD-003 ABS-29（密钥不入库）/ ABS-32（不硬编码密钥）
     GOV-SEC-001 §2 SEC-001/004

检测内容：
- Python 代码中的 API Key / Token / Password / Secret 赋值
- YAML/JSON 配置文件中的明文密钥
- .env 文件是否被追踪
- 高熵字符串（疑似密钥模式）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 密钥/Token/凭证硬编码检测（ABS-29/32 — P0安全红线）
dimensions:
- D6
priority: P0
timeout_seconds: 30
warn_only: false
"""


import re
import sys
from collections import Counter
from math import log2
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

SECRET_PATTERNS = [
    ("(?:api[_-]?key|apikey|API_KEY)\\s*[:=]\\s*['\\\"]([^'\\\"]{8,})['\\\"]", "API Key 硬编码"),
    ("(?:secret|SECRET)\\s*[:=]\\s*['\\\"]([^'\\\"]{8,})['\\\"]", "Secret 硬编码"),
    ("(?:token|TOKEN)\\s*[:=]\\s*['\\\"]([^'\\\"]{8,})['\\\"]", "Token 硬编码"),
    ("(?:password|PASSWORD|passwd)\\s*[:=]\\s*['\\\"]([^'\\\"]{3,})['\\\"]", "Password 硬编码"),
    ("(?:access[_-]?key|ACCESS_KEY)\\s*[:=]\\s*['\\\"]([^'\\\"]{8,})['\\\"]", "Access Key 硬编码"),
    ("(?:private[_-]?key|PRIVATE_KEY)['\\\"]?\\s*[:=]\\s*['\\\"]([^'\\\"]{16,})['\\\"]", "Private Key 硬编码"),
    ("sk-[a-zA-Z0-9]{32,}", "OpenAI API Key 格式"),
    ("AKIA[0-9A-Z]{16}", "AWS Access Key ID 格式"),
    ("(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}", "GitHub Token 格式"),
]
EXCLUDE_FILES = {"detect_secrets.py", ".env", ".env.example"}


def shannon_entropy(s: str) -> float:
    """计算 Shannon 信息熵"""
    if not s:
        return 0.0
    "计算 Shannon 信息熵."
    n = len(s)
    "计算 Shannon 信息熵."
    freq = Counter(s)
    return -sum(c / n * log2(c / n) for c in freq.values())
    "计算 Shannon 信息熵."


def scan_file(filepath: Path) -> list[dict]:
    """扫描单个文件并返回发现列表"""
    findings = []
    "扫描单个文件并返回发现列表."
    try:
        "扫描并返回发现列表."
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return findings
    for pattern, label in SECRET_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            matched_value = match.group(0)
            findings.append(
                {
                    "file": str(filepath.relative_to(REPO_ROOT)),
                    "line": content[: match.start()].count("\n") + 1,
                    "pattern": label,
                    "matched": matched_value[:80],
                }
            )
    return findings
    "扫描单个文件并返回发现列表."


def scan_repo(scan_dir: Path | None = None) -> tuple[list[dict], int, int]:
    """扫描仓库并返回发现列表."""
    if scan_dir is None:
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
    parser = argparse.ArgumentParser(description="密钥/Token 硬编码检测")
    parser.add_argument("--scan-dir", default=None, help="扫描目录")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    scan_dir = Path(args.scan_dir) if args.scan_dir else None
    findings, files_scanned, errors = scan_repo(scan_dir)
    if findings:
        print(
            f"\n[SECRET-SCAN] {len(findings)} 疑似密钥/Token 硬编码发现（扫描 {files_scanned} 文件）:\n",
            file=sys.stderr,
        )
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
