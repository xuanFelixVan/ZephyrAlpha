# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/scan_secret_leak.py | §
# [MODULE] scripts.governance.d6_security.scan_secret_leak
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
对标 06-security_architecture.md §6.3 L3-Audit：
  周扫描全库 secret 泄漏，Finding 写 docs/_working/audit/findings/。

与 detect_secrets.py 的区别：
  - detect_secrets.py = CI pre_commit 级轻量扫描（单文件/增量）
  - scan_secret_leak.py = 全库深度扫描 + 历史对比 + Finding 持久化

用法:
  python scripts/governance/d6_security/scan_secret_leak.py [--full] [--baseline BASELINE_JSON]
                                                            [--output FINDINGS_DIR]

exit: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

import os

__manifest__ = """
args:
- --full
- --baseline
- --output
description: 全库 secret 泄漏周扫描 + 历史快照对比（06-SEC §6.3 L3-Audit — P1安全深度扫描）
dimensions:
- D6
priority: P1
timeout_seconds: 120
warn_only: false
"""

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_CODE
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
from _shared.walk import iter_files

ensure_utf8_stdout()

BASELINE_DIR = REPO_ROOT / "data" / "security_baselines"
FINDINGS_DIR = REPO_ROOT / "docs" / "_working" / "audit" / "findings"

SECRET_PATTERNS_DEEP = [
    (
        re.compile(r"(?:api[_-]?key|apikey|API_KEY)\s*[:=]\s*['\"][^'\"]{8,}['\"]", re.IGNORECASE),
        "API Key 硬编码",
        "P0",
    ),
    (re.compile(r"(?:secret|SECRET)\s*[:=]\s*['\"][^'\"]{8,}['\"]", re.IGNORECASE), "Secret 硬编码", "P0"),
    (re.compile(r"(?:token|TOKEN)\s*[:=]\s*['\"][^'\"]{8,}['\"]", re.IGNORECASE), "Token 硬编码", "P0"),
    (re.compile(r"(?:password|PASSWORD|passwd)\s*[:=]\s*['\"][^'\"]{3,}['\"]", re.IGNORECASE), "Password 硬编码", "P0"),
    (re.compile(r"sk-[a-zA-Z0-9]{32,}", re.IGNORECASE), "OpenAI API Key", "P0"),
    (re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE), "AWS Access Key ID", "P0"),
    (re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}", re.IGNORECASE), "GitHub Token", "P0"),
    (
        re.compile(r"(?:private[_-]?key|PRIVATE_KEY)['\"]?\s*[:=]\s*['\"][^'\"]{16,}['\"]", re.IGNORECASE),
        "Private Key",
        "P1",
    ),
    (re.compile(r"(?:access[_-]?key|ACCESS_KEY)\s*[:=]\s*['\"][^'\"]{8,}['\"]", re.IGNORECASE), "Access Key", "P1"),
    (
        re.compile(
            r"(?:database[_-]?url|DATABASE_URL|DB_URL)\s*[:=]\s*['\"][^'\"]*:[^'\"]*@[^'\"]*['\"]", re.IGNORECASE
        ),
        "数据库连接串含密码",
        "P1",
    ),
]

EXCLUDE_FILES = frozenset(
    {
        "scan_secret_leak.py",
        "detect_secrets.py",
        "scan_runtime_log_secrets.py",
        ".env.example",
    }
)


def scan_file(filepath: Path) -> list[dict]:
    """scan_file implementation."""
    findings = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return findings
    for pattern, label, severity in SECRET_PATTERNS_DEEP:
        for match in pattern.finditer(content):
            line_num = content[: match.start()].count("\n") + 1
            findings.append(
                {
                    "file": str(filepath.relative_to(REPO_ROOT)),
                    "line": line_num,
                    "pattern": label,
                    "severity": severity,
                    "matched": match.group(0)[:80],
                }
            )
    return findings


def scan_full(scan_dir: Path | None = None) -> list[dict]:
    """scan_full implementation."""
    target = scan_dir or REPO_ROOT
    all_findings = []
    for filepath in iter_files(target, extensions=SCAN_EXTENSIONS_CODE, exclude_files=EXCLUDE_FILES):
        try:
            rel = filepath.relative_to(REPO_ROOT)
        except (ValueError, OSError):
            continue
        if str(rel).startswith("_DO_NOT_USE") or str(rel).startswith(".trae"):
            continue
        findings = scan_file(filepath)
        all_findings.extend(findings)
    return all_findings


def save_secret_baseline(findings: list[dict]) -> Path:
    """save_secret_baseline implementation.

    重命名自 save_baseline（2026-06-26），消除与 manage_baseline.save_baseline 的
    命名冲突——本函数使用 JSON 对象格式（非 JSONL）+ 元组键对比（非 sha256），
    签名与用途均不同，保留为独立适配层而非强行统一（裁定见 anti_hallucination
    报告 W2-T2）。
    """
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    baseline_path = BASELINE_DIR / f"secret_baseline_{ts}.json"
    atomic_write_safe(
        baseline_path,
        json.dumps(
            {"timestamp": datetime.now(UTC).isoformat(), "findings": findings, "total": len(findings)},
            ensure_ascii=False,
            indent=2,
        ),
    )
    return baseline_path


def compare_with_baseline(findings: list[dict], baseline_path: Path) -> list[dict]:
    """compare_with_baseline implementation."""
    try:
        with open(baseline_path, encoding="utf-8") as f:
            prev = json.load(f)
    except Exception:
        return []
    prev_set = {(f["file"], f["line"], f["pattern"]) for f in prev.get("findings", [])}
    new_findings = []
    for f in findings:
        key = (f["file"], f["line"], f["pattern"])
        if key not in prev_set:
            f["status"] = "NEW"
            new_findings.append(f)
    return new_findings


def write_findings_report(findings: list[dict], new_findings: list[dict]) -> Path | None:
    """write_findings_report implementation."""
    if not findings:
        return None
    FINDINGS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    report_path = FINDINGS_DIR / f"sec_leak_{ts}.json"
    report = {
        "id": f"sec_leak_{ts}",
        "timestamp": datetime.now(UTC).isoformat(),
        "total_findings": len(findings),
        "new_findings": len(new_findings),
        "p0_count": sum(1 for f in findings if f.get("severity") == "P0"),
        "p1_count": sum(1 for f in findings if f.get("severity") == "P1"),
        "findings": findings,
        "new": new_findings,
    }
    atomic_write_safe(report_path, json.dumps(report, ensure_ascii=False, indent=2))
    return report_path


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="全库 secret 泄漏周扫描")
    parser.add_argument("--full", action="store_true", help="全库扫描（默认）")
    parser.add_argument("--baseline", type=str, help="对比基线 JSON 文件")
    parser.add_argument("--output", type=str, help="Finding 输出目录")
    args = parser.parse_args()

    findings = scan_full()
    new_findings = []

    if args.baseline:
        baseline_path = Path(args.baseline)
        new_findings = compare_with_baseline(findings, baseline_path)

    baseline_path = save_secret_baseline(findings)

    p0 = [f for f in findings if f.get("severity") == "P0"]
    p1 = [f for f in findings if f.get("severity") == "P1"]

    print("\n[SECRET-SCAN] 全库扫描完成")
    print(f"  总发现: {len(findings)} (P0: {len(p0)}, P1: {len(p1)})")
    print(f"  新增发现: {len(new_findings)}")
    print(f"  基线已保存: {baseline_path.relative_to(REPO_ROOT)}")

    if findings:
        print(f"\n  P0 发现 ({len(p0)}):")
        for f in p0[:20]:
            print(f"    {f['file']}:{f['line']} [{f['pattern']}]")
        if len(p0) > 20:
            print(f"    ... 还有 {len(p0) - 20} 项")
        if p1:
            print(f"\n  P1 发现 ({len(p1)}):")
            for f in p1[:10]:
                print(f"    {f['file']}:{f['line']} [{f['pattern']}]")
            if len(p1) > 10:
                print(f"    ... 还有 {len(p1) - 10} 项")

    report_path = write_findings_report(findings, new_findings)
    if report_path:
        print(f"  Finding 报告: {report_path.relative_to(REPO_ROOT)}")

    if p0:
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
