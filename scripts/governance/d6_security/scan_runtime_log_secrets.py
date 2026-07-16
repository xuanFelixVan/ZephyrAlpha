# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/scan_runtime_log_secrets.py | §
# [MODULE] scripts.governance.d6_security.scan_runtime_log_secrets
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
对标 architecture_principles.md §1bis R2 安全红线：
  "日志输出禁止包含密钥/Token/Secret 值"

检测方式：
  - 扫描 src/zephyr/ 下所有 .py 文件
  - 搜索 logger.info/debug/warning/error/critical + print 中
    直接拼接密钥变量的模式
  - 搜索 f-string / format() / % 格式化中包含
    secret/key/token/password 变量的模式

exit: 0=pass, 1=violations found, 2=error
"""

from __future__ import annotations

__manifest__ = """
args:
- --warn-only
description: R2 日志不写 secret 运行时扫描（architecture-principles §1bis R2 — P0安全红线）
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
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

SRC_ROOT = REPO_ROOT / "src" / "zephyr"

_SECRET_KW = (
    r"(?:"
    r"api[_-]?key|apikey|secret[_-]?key|secret[_-]?value|access[_-]?key|private[_-]?key"
    r"|password|passwd|auth[_-]?token|access[_-]?token|refresh[_-]?token|bearer[_-]?token"
    r"|encryption[_-]?key|signing[_-]?key|credential"
    r")"
)
_SAFE_EXCLUSION = (
    r"(?!"
    r"token[_-]?estimate|token[_-]?budget|token[_-]?count|token[_-]?limit"
    r"|secrets\.token_hex|secrets\.token_urlsafe|secrets\.token_bytes"
    r"|sanitize_secret|mask_secret|redact_secret"
    r"|secret_name|secret_key_name|key_name|key_id"
    r"|token_type|token_issuer|token_audience"
    r")"
)

LOG_SECRET_PATTERNS = [
    (
        re.compile(
            r"(?:logger|logging|log)\s*(?:\.\s*(?:info|debug|warning|error|critical|exception))\s*\("
            r"[^)]*" + _SAFE_EXCLUSION + r".*\b" + _SECRET_KW + r"\b",
            re.IGNORECASE,
        ),
        "日志语句包含密钥变量名",
    ),
    (
        re.compile(
            r"(?:print|pprint)\s*\(" r"[^)]*" + _SAFE_EXCLUSION + r".*\b" + _SECRET_KW + r"\b",
            re.IGNORECASE,
        ),
        "print 语句包含密钥变量名",
    ),
    (
        re.compile(
            r'f["\x27][^"\x27]*\{[^}]*' + _SAFE_EXCLUSION + r".*\b" + _SECRET_KW + r"\b" + r"[^}]*\}",
            re.IGNORECASE,
        ),
        "f-string 包含密钥变量插值",
    ),
    (
        re.compile(
            r"\.(?:format|format_map)\s*\(" r"[^)]*" + _SAFE_EXCLUSION + r".*\b" + _SECRET_KW + r"\b",
            re.IGNORECASE,
        ),
        "format() 调用包含密钥变量名",
    ),
    (
        re.compile(
            r"log\.structlog\.bind\s*\(" r"[^)]*" + _SAFE_EXCLUSION + r".*\b" + _SECRET_KW + r"\b",
            re.IGNORECASE,
        ),
        "structlog.bind() 绑定密钥变量",
    ),
]

EXCLUDE_DIRS = {"__pycache__", ".git", "tests", "docs"}
EXCLUDE_FILES = {"scan_runtime_log_secrets.py", "detect_secrets.py", "detect_keywords_in_logs.py"}


def check_file(file_path: Path) -> list[str]:
    """Check compliance and report findings."""
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return violations

    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        for pattern, description in LOG_SECRET_PATTERNS:
            if pattern.search(stripped):
                violations.append(f'  {file_path.relative_to(REPO_ROOT)}:{i}: {description} — "{stripped[:120]}"')
                break
    return violations


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    import argparse

    parser = argparse.ArgumentParser(description="R2 日志不写 secret 运行时扫描")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（exit 0）")
    args = parser.parse_args()

    if not SRC_ROOT.exists():
        print("src/zephyr/ 目录不存在 — 跳过 R2 日志扫描")
        return EXIT_PASS
    all_violations: list[str] = []
    for py_file in SRC_ROOT.rglob("*.py"):
        if any(excl in py_file.parts for excl in EXCLUDE_DIRS):
            continue
        if py_file.name in EXCLUDE_FILES:
            continue
        violations = check_file(py_file)
        all_violations.extend(violations)

    if all_violations:
        print(f"[FAIL] R2 日志不写 secret — 发现 {len(all_violations)} 处违规:")
        for v in all_violations:
            print(v)
        print()
        print("R2 安全红线：日志输出禁止包含密钥/Token/Secret 值。")
        print("请使用脱敏函数（如 mask_secret()）替换直接输出。")
        if args.warn_only:
            print("[WARN-ONLY] 以上违规未阻断。")
            return EXIT_PASS
        return EXIT_FINDINGS
    print("[OK] R2 日志不写 secret — 无违规")
    print("   已扫描 src/zephyr/ 下所有 .py 文件。")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
