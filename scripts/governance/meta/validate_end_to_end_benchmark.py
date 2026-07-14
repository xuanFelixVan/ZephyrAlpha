# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/validate_end_to_end_benchmark.py | §
# [MODULE] scripts.governance.meta.validate_end_to_end_benchmark
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.__init__
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
"""validate_end_to_end_benchmark.py — END-TO-END 基准测试引擎

对标 B59（END-TO-END 基准测试）+ Kayenta Score Computation。

维护一个已知标准测试项目（test_fixtures/），每次 run_all.py 扫描该测试项目。
已知应产出 X 条 CRITICAL + Y 条 HIGH + Z 条 MEDIUM。
实际产出偏离 > 10% → 脚本系统退化告警。

这个机制能发现"所有脚本都在运行但有一个静默失效"的情况。

Usage:
    python scripts/governance/meta/validate_end_to_end_benchmark.py
    python scripts/governance/meta/validate_end_to_end_benchmark.py --setup
    python scripts/governance/meta/validate_end_to_end_benchmark.py --tolerance 0.15
    python scripts/governance/meta/validate_end_to_end_benchmark.py --json
"""

from __future__ import annotations
from _shared.constants import REPO_ROOT
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

__manifest__ = """
args:
  - --tolerance
  - --setup
  - --json
  - --warn-only
  - --jsonl
description: >
  END-TO-END 基准测试引擎——维护已知标准测试项目，每次 run_all.py 扫描后对比已知预期产出，
  实际产出偏离超阈值 → 脚本系统退化告警，可发现脚本静默失效。
dimensions:
- D1
- D7
priority: P1
timeout_seconds: 60
warn_only: false
"""


import json as json_mod
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = REPO_ROOT
_SCRIPTS_DIR = _REPO_ROOT / "scripts" / "governance"
_BENCHMARK_DIR = _SCRIPTS_DIR / "meta" / "benchmark"
_TEST_FIXTURES_DIR = _BENCHMARK_DIR / "test_fixtures"
_EXPECTED_RESULTS = _BENCHMARK_DIR / "expected_results.json"
_BENCHMARK_HISTORY = _BENCHMARK_DIR / "history.jsonl"

# 基准预期值——手工校准后的 golden reference
DEFAULT_EXPECTED: dict = {
    "total_findings_min": 8,
    "total_findings_max": 50,
    "by_severity": {"CRITICAL": 1, "HIGH": 3, "MEDIUM": 5, "LOW": 2},
    "severity_tolerance": 0.15,
}

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def setup_benchmark() -> dict:
    """setup_benchmark implementation."""
    _TEST_FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    bad_file = _TEST_FIXTURES_DIR / "bad_frontmatter.md"
    atomic_write_safe(
        bad_file,
        """# Test Document
Some body text without frontmatter.
This should trigger D3 metadata validation.
""",
    )

    bad_imports = _TEST_FIXTURES_DIR / "bad_imports.py"
    atomic_write_safe(
        bad_imports,
        """import os
import nonexistent_package_xyz
from typing import List, Dict, Any

def test_function():
    pass
""",
    )

    incomplete_doc = _TEST_FIXTURES_DIR / "incomplete_module.py"
    atomic_write_safe(
        incomplete_doc,
        """
def calculate(x: int, y: int) -> int:
    return x + y

class DataProcessor:

    def process(self):
        pass
""",
    )

    bad_structure = _TEST_FIXTURES_DIR
    (bad_structure / "orphan_file_without_module_registration.py").write_text(
        """
def helper(x):
    return x * 2
""",
        encoding="utf-8",
    )

    atomic_write_safe(_EXPECTED_RESULTS, json_mod.dumps(DEFAULT_EXPECTED, ensure_ascii=False, indent=2))
    return {"status": "setup_complete", "fixtures": 4, "path": str(_TEST_FIXTURES_DIR.relative_to(_REPO_ROOT))}


def _load_expected() -> dict:
    """_load_expected implementation."""
    if not _EXPECTED_RESULTS.exists():
        return DEFAULT_EXPECTED
    with open(_EXPECTED_RESULTS, encoding="utf-8") as f:
        return json_mod.load(f)


def run_benchmark(tolerance: float | None = None) -> dict:
    """run_benchmark implementation."""
    if not _TEST_FIXTURES_DIR.exists():
        setup_benchmark()

    expected = _load_expected()
    tol = tolerance if tolerance is not None else expected.get("severity_tolerance", 0.15)

    temp_output = _BENCHMARK_DIR / "bench_result.jsonl"

    proc = subprocess.run(
        [
            sys.executable,
            str(_SCRIPTS_DIR / "run_all.py"),
            "--target-scope",
            str(_TEST_FIXTURES_DIR),
            "--warn-only",
            "--output",
            str(temp_output),
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(_REPO_ROOT),
        encoding="utf-8",
        errors="replace",
    )

    findings: list[dict] = []
    if temp_output.exists():
        with open(temp_output, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    findings.append(json_mod.loads(line))
                except json_mod.JSONDecodeError:
                    continue

    actual_by_sev: dict[str, int] = {}
    for f in findings:
        sev = f.get("severity", "LOW")
        actual_by_sev[sev] = actual_by_sev.get(sev, 0) + 1

    drift_details: list[dict] = []
    score = 1.0
    for sev, exp_cnt in expected.get("by_severity", {}).items():
        actual = actual_by_sev.get(sev, 0)
        if exp_cnt == 0 and actual == 0:
            continue
        drift = abs(actual - exp_cnt) / max(exp_cnt, 1)
        score -= drift * 0.25
        if drift > tol:
            drift_details.append(
                {
                    "severity": sev,
                    "expected": exp_cnt,
                    "actual": actual,
                    "drift_pct": round(drift * 100, 1),
                    "status": "DEGRADED" if actual < exp_cnt else "ELEVATED",
                }
            )

    total = len(findings)
    exp_min = expected.get("total_findings_min", 0)
    exp_max = expected.get("total_findings_max", 100)
    range_ok = exp_min <= total <= exp_max
    if not range_ok:
        score -= 0.3

    verdict = "PASS" if score >= 0.85 else ("MARGINAL" if score >= 0.70 else "FAIL")

    result = {
        "timestamp": datetime.now(UTC).isoformat(),
        "verdict": verdict,
        "score": round(max(0.0, min(1.0, score)), 4),
        "total_findings": total,
        "expected_range": f"{exp_min}-{exp_max}",
        "range_ok": range_ok,
        "drift_found": len(drift_details) > 0,
        "drift_details": drift_details,
        "by_severity": actual_by_sev,
        "degradation_detected": verdict != "PASS",
    }

    _BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
    with open(_BENCHMARK_HISTORY, "a", encoding="utf-8") as f:
        f.write(json_mod.dumps(result, ensure_ascii=False) + "\n")

    if temp_output.exists():
        temp_output.unlink()

    return result


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    import argparse

    parser = argparse.ArgumentParser(description="END-TO-END governance benchmark (Kayenta-style drift)")
    parser.add_argument("--tolerance", type=float, default=None, help="severity 漂移相对容忍度")
    parser.add_argument("--setup", action="store_true", help="初始化 fixture")
    parser.add_argument("--json", action="store_true", help="格式化 JSON 报告")
    parser.add_argument("--warn-only", action="store_true", help="FAIL 仍 exit 0")
    parser.add_argument("--jsonl", action="store_true", help="单行 JSON（含 severity）")
    args = parser.parse_args()

    tolerance = args.tolerance

    if args.setup:
        result = setup_benchmark()
        print("[BENCHMARK] ✅ 已创建4个测试fixture + 预期结果配置", file=sys.stderr)
        return

    result = run_benchmark(tolerance)
    if args.json:
        print(json_mod.dumps(result, ensure_ascii=False, indent=2))
    elif args.jsonl:
        passed = result["verdict"] == "PASS"
        print(
            json_mod.dumps(
                {
                    "severity": "INFO" if (passed or args.warn_only) else "HIGH",
                    "check_id": "E2E-BENCH",
                    "verdict": result["verdict"],
                    "score": result["score"],
                },
                ensure_ascii=False,
            )
        )
    else:
        verdict_icon = {"PASS": "✅", "MARGINAL": "⚠️", "FAIL": "🔴"}.get(result["verdict"], "❓")
        print(f"\n[BENCHMARK] {verdict_icon} {result['verdict']} — Score: {result['score']:.2%}", file=sys.stderr)
        print(f"  Findings: {result['total_findings']} (期望 {result['expected_range']})", file=sys.stderr)
        print(f"  按严重度: {result['by_severity']}", file=sys.stderr)
        if result["drift_found"]:
            print("  严重度漂移:", file=sys.stderr)
            for d in result["drift_details"]:
                arrow = "↓" if d["actual"] < d["expected"] else "↑"
                print(
                    f"    [{d['status']}] {d['severity']}: {d['expected']} → {d['actual']} {arrow}{d['drift_pct']:.0f}%",
                    file=sys.stderr,
                )
    code = 0 if result["verdict"] == "PASS" else 1
    if args.warn_only:
        code = 0
    sys.exit(code)


if __name__ == "__main__":
    main()
