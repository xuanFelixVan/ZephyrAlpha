# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/check_log_secret_leak.py | §
# [MODULE] scripts.arch_guard.fitness_functions.check_log_secret_leak
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.arch_guard.fitness_functions.__init__
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
"""check_log_secret_leak.py — R2 日志不写 secret 适应度函数

对标 architecture_principles.md §1 R2（日志不写 secret）。
扫描 src/zephyr/ 下所有 Python 文件中的 structlog/logging/print 调用，
检测是否包含密钥/token/私钥等敏感 pattern。

exit: 0=无泄漏, 1=发现泄漏, 2=基础设施错误
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_GOV_DIR = _ROOT.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

SRC_ROOT = REPO_ROOT / "src" / "zephyr"

SECRET_PATTERNS = [
    re.compile(r'(?:api_?key|secret|token|password|private_?key|auth_?token)\s*=\s*["\']', re.IGNORECASE),
    re.compile(r"(?:api_?key|secret|token|password|private_?key|auth_?token)\s*\{", re.IGNORECASE),
    re.compile(r'f["\'].*(?:api_?key|secret|token|password|private_?key).*["\']', re.IGNORECASE),
]

LOG_CALL_NAMES = {"log", "info", "debug", "warning", "error", "critical", "print", "msg"}

EXEMPT_PATTERNS = [
    re.compile(r"os\.environ\.get\(", re.IGNORECASE),
    re.compile(r'config\[[\'"]', re.IGNORECASE),
    re.compile(r"settings\.", re.IGNORECASE),
    re.compile(r"#.*(?:noqa|type:\s*ignore)", re.IGNORECASE),
]

EXEMPT_PATHS = [
    "test_",
    "_test.py",
    "conftest.py",
]

def _is_exempt_path(path: Path) -> bool:
    name = path.name
    return any(e in name for e in EXEMPT_PATHS)

def _scan_file(path: Path) -> list[tuple[int, str]]:
    findings = []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return findings

    for lineno, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        has_log_call = any(f".{name}(" in stripped for name in LOG_CALL_NAMES) or "print(" in stripped
        if not has_log_call:
            continue

        has_exempt = any(e.search(stripped) for e in EXEMPT_PATTERNS)
        if has_exempt:
            continue

        for pattern in SECRET_PATTERNS:
            if pattern.search(stripped):
                findings.append((lineno, stripped[:120]))
                break

    return findings

def main() -> int:
    if not SRC_ROOT.exists():
        print(f"[SKIP] src/zephyr/ 不存在: {SRC_ROOT}")
        return 0

    total_findings = 0
    files_scanned = 0

    print("R2 日志 Secret 泄漏扫描\n")

    for py_file in SRC_ROOT.rglob("*.py"):
        if _is_exempt_path(py_file):
            continue
        files_scanned += 1
        findings = _scan_file(py_file)
        for lineno, line in findings:
            rel = py_file.relative_to(REPO_ROOT)
            print(f"  [LEAK] {rel}:{lineno} — {line}")
            total_findings += 1

    print(f"\n{'=' * 60}")
    print(f"扫描 {files_scanned} 文件，发现 {total_findings} 处疑似泄漏")
    print(f"{'=' * 60}")

    if total_findings > 0:
        print("\n[FAIL] 发现日志中可能包含 secret 的调用")
        print("修复建议：使用 os.environ.get() 或 config 对象获取敏感值，不要在日志中直接输出")
        return 1

    print("\n[OK] 未发现日志 secret 泄漏")
    return 0

if __name__ == "__main__":
    sys.exit(main())
