# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/manage_script_ab_test.py | §
# [MODULE] scripts.governance.meta.manage_script_ab_test
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
"""
manage_script_ab_test.py — 脚本 A/B 对照模式 (Kayenta-style)



对标 B45（Script A/B 对照）+ Netflix Kayenta 自动 Canary 分析。

在 Shadow Mode 基础上增加统计对照能力：
将同一脚本的新旧版本对同一代码库扫描——对比他们的 Finding 产出差异，
做多维度统计比较（Finding数量/严重度分布/误报率），判断是否有"significant degradation"。

概念对齐 Kayenta:
  baseline = 旧版本脚本（当前生产版本）
  canary   = 新版本脚本（待验证版本）
  judgement = 统计显著性检验 → Pass/Fail/Marginal

Usage:
    python scripts/governance/meta/manage_script_ab_test.py --baseline d7_code/validate_test_coverage.py --canary d7_code/validate_test_coverage_v2.py
    python scripts/governance/meta/manage_script_ab_test.py --baseline d7_code/validate_test_coverage.py --canary d7_code/validate_test_coverage_v2.py --target-scope src/
    python scripts/governance/meta/manage_script_ab_test.py --baseline d7_code/validate_test_coverage.py --canary d7_code/validate_test_coverage_v2.py --json
    python scripts/governance/meta/manage_script_ab_test.py --list-canaries
"""

from __future__ import annotations

__manifest__ = """
args: []
description: ⚠ __manifest__ 缺失——请添加元数据块
dimensions: []
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import json as json_mod
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

# 治本(2026-06-30): REPO_ROOT 真源来自 _shared.constants, 消除 parents[N] 硬编码
# 原 parents[2] 实为 scripts 目录而非 repo root, 变量名误导且路径计算有 bug
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT as _REPO_ROOT  # noqa: E402
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
_SCRIPTS_DIR = _REPO_ROOT / "scripts" / "governance"
_AB_LOG_DIR = _SCRIPTS_DIR / "meta" / "ab_test_results"
_KAYENTA_THRESHOLD_PASS = 0.95  # noqa: gate-vocab  治本(ARCH-036 P3-A5): Kayenta AB测试通过阈值，脚本专用
_KAYENTA_THRESHOLD_MARGINAL = 0.75  # noqa: gate-vocab  治本(ARCH-036 P3-A5): Kayenta AB测试边际阈值，脚本专用
_DEGRADATION_SENSITIVITY = 0.15

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _run_script(script_path: str, target_scope: str | None = None) -> dict:
    """_run_script implementation."""
    cmd = [sys.executable, script_path, "--warn-only"]
    if target_scope:
        cmd.extend(["--target-scope", target_scope])

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(_REPO_ROOT),
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONPATH": str(_SCRIPTS_DIR)},
    )

    combined = proc.stdout + proc.stderr
    findings: list[dict] = []
    for line in proc.stdout.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            findings.append(json_mod.loads(line))
        except json_mod.JSONDecodeError:
            pass

    return {
        "exit_code": proc.returncode,
        "finding_count": len(findings),
        "findings": findings,
        "output_lines": len(combined.split("\n")),
    }


def _classify_by_severity(findings: list[dict]) -> dict[str, int]:
    """_classify_by_severity implementation."""
    counts: dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    for f in findings:
        sev = f.get("severity", "LOW")
        if sev in counts:
            counts[sev] += 1
    return counts


def _compute_judgement(baseline_count: int, canary_count: int, baseline_sev: dict, canary_sev: dict) -> dict:
    """_compute_judgement implementation."""
    if baseline_count == 0 and canary_count == 0:
        score = 1.0
        verdict = "PASS"
        return {"score": score, "verdict": verdict, "reason": "Both scripts found no issues"}

    if baseline_count == 0:
        score = 1.0 - min(canary_count / max(1, canary_count), 1.0) * 0.3
    else:
        ratio = canary_count / baseline_count
        drift = abs(1.0 - ratio)
        score = 1.0 - min(drift, 1.0)

    critical_drift = abs(canary_sev.get("CRITICAL", 0) - baseline_sev.get("CRITICAL", 0))
    high_drift = abs(canary_sev.get("HIGH", 0) - baseline_sev.get("HIGH", 0))
    if critical_drift > 0 or high_drift > 3:
        score -= 0.2

    score = max(0.0, min(1.0, score))

    if score >= _KAYENTA_THRESHOLD_PASS:
        verdict = "PASS"
    elif score >= _KAYENTA_THRESHOLD_MARGINAL:
        verdict = "MARGINAL"
    else:
        verdict = "FAIL"

    reasons = []
    if canary_count > baseline_count * 1.5:
        reasons.append(f"Canary found {canary_count - baseline_count} more findings ({ratio:.1%} increase)")
    if canary_count < baseline_count * 0.5:
        reasons.append(
            f"Canary missed {baseline_count - canary_count} findings ({(1 - ratio):.1%} decrease) — possible regression"
        )
    if critical_drift > 0:
        reasons.append(
            f"CRITICAL mismatch: baseline={baseline_sev.get('CRITICAL', 0)} vs canary={canary_sev.get('CRITICAL', 0)}"
        )

    return {
        "score": round(score, 4),
        "verdict": verdict,
        "reason": "; ".join(reasons) if reasons else "Within acceptable variance",
        "degradation_significant": verdict == "FAIL",
    }


def run_ab_test(baseline: str, canary: str, target_scope: str | None = None) -> dict:
    """run_ab_test implementation."""
    _AB_LOG_DIR.mkdir(parents=True, exist_ok=True)

    baseline_path = str(_SCRIPTS_DIR / baseline) if not baseline.startswith(str(_REPO_ROOT)) else baseline
    canary_path = str(_SCRIPTS_DIR / canary) if not canary.startswith(str(_REPO_ROOT)) else canary

    if not Path(baseline_path).exists():
        return {"error": f"Baseline script not found: {baseline_path}"}
    if not Path(canary_path).exists():
        return {"error": f"Canary script not found: {canary_path}"}

    baseline_result = _run_script(baseline_path, target_scope)
    canary_result = _run_script(canary_path, target_scope)

    baseline_sev = _classify_by_severity(baseline_result["findings"])
    canary_sev = _classify_by_severity(canary_result["findings"])
    judgement = _compute_judgement(
        baseline_result["finding_count"],
        canary_result["finding_count"],
        baseline_sev,
        canary_sev,
    )

    report = {
        "timestamp": datetime.now(UTC).isoformat(),
        "baseline_script": baseline,
        "canary_script": canary,
        "baseline": {
            "exit_code": baseline_result["exit_code"],
            "finding_count": baseline_result["finding_count"],
            "by_severity": baseline_sev,
        },
        "canary": {
            "exit_code": canary_result["exit_code"],
            "finding_count": canary_result["finding_count"],
            "by_severity": canary_sev,
        },
        "judgement": judgement,
    }

    ts_str = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    report_path = _AB_LOG_DIR / f"ab-{baseline.replace('/', '-')}-{ts_str}.json"
    atomic_write_safe(report_path, json_mod.dumps(report, ensure_ascii=False, indent=2))
    return report


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="脚本 A/B 对照模式")
    parser.add_argument("--baseline", type=str, help="Baseline 脚本路径（相对于 scripts/governance/）")
    parser.add_argument("--canary", type=str, help="Canary 脚本路径（相对于 scripts/governance/）")
    parser.add_argument("--target-scope", type=str, help="限制扫描范围")
    parser.add_argument("--list-canaries", action="store_true", help="列出历史 A/B 测试结果")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    if args.list_canaries:
        if _AB_LOG_DIR.exists():
            for report_file in sorted(_AB_LOG_DIR.glob("ab-*.json"), reverse=True)[:10]:
                print(f"  {report_file.name}", file=sys.stderr)
        else:
            print("无历史 A/B 测试", file=sys.stderr)
        return

    if not args.baseline or not args.canary:
        parser.error("--baseline and --canary are required")
        return

    result = run_ab_test(args.baseline, args.canary, args.target_scope)
    if args.json:
        print(json_mod.dumps(result, ensure_ascii=False, indent=2))
    else:
        j = result["judgement"]
        verdict_icon = {"PASS": "✅", "MARGINAL": "⚠️", "FAIL": "🔴"}.get(j["verdict"], "❓")
        print(f"\n[AB-TEST] {verdict_icon} {j['verdict']} — Score: {j['score']:.2%}", file=sys.stderr)
        print(f"  Baseline ({args.baseline}): {result['baseline']['finding_count']} findings", file=sys.stderr)
        print(f"  Canary   ({args.canary}): {result['canary']['finding_count']} findings", file=sys.stderr)
        print(f"  {j['reason']}", file=sys.stderr)
        sys.exit(0 if j["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
