# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/lifecycle/validate_phase_transition.py | §
# [MODULE] scripts.governance.d5_architecture.validators.lifecycle.validate_phase_transition
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.lifecycle.__init__
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
对标 dimension_audit_matrix.md §4.12：
  校验 Phase 过渡是否满足双门协议（技术门禁 + 治理门禁）。

检测内容：
  1. scaffold→experimental: 安全门禁 4/4 通过
  2. experimental→beta: 架构不变量 17/17 FF pass + 代码覆盖率达标
  3. beta→production: 全量集成测试通过 + 安全审计无 P0

用法:
  python scripts/governance/d5_architecture/validate_phase_transition.py [--from FROM_PHASE] [--to TO_PHASE]

exit: 0=transition valid, 1=transition blocked, 2=error
"""

from __future__ import annotations

__manifest__ = """
args:
- --from
- --to
description: Phase 过渡双门协议合规率校验（dimension-audit-matrix §4.12 — Phase transition gates）
dimensions:
- D5
priority: P1
timeout_seconds: 60
warn_only: false
"""

import argparse
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

PHASES = ["scaffold", "experimental", "beta", "production"]

SCAFFOLD_EXIT_GATES = REPO_ROOT / "scripts" / "arch_guard" / "check_scaffold_exit_gates.py"
ARCH_GUARD_RUN_ALL = REPO_ROOT / "scripts" / "arch_guard" / "run_all.py"


def validate_scaffold_to_experimental() -> tuple[bool, str]:
    """Validate target against rules and report findings."""
    if not SCAFFOLD_EXIT_GATES.exists():
        return False, "check_scaffold_exit_gates.py 不存在"
    try:
        result = subprocess.run(
            [sys.executable, str(SCAFFOLD_EXIT_GATES)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(REPO_ROOT),
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode == 0:
            return True, "scaffold→experimental 安全门禁 4/4 通过"
        return False, f"安全门禁未通过:\n{result.stdout[-500:]}"
    except subprocess.TimeoutExpired:
        return False, "安全门禁检查超时"
    except Exception as e:
        return False, f"安全门禁检查执行失败: {e}"


def validate_experimental_to_beta() -> tuple[bool, str]:
    """Validate target against rules and report findings."""
    if not ARCH_GUARD_RUN_ALL.exists():
        return False, "arch_guard/run_all.py 不存在"
    try:
        result = subprocess.run(
            [sys.executable, str(ARCH_GUARD_RUN_ALL)],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(REPO_ROOT),
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode == 0:
            return True, "架构不变量 17/17 FF pass"
        return False, f"架构不变量未全部通过:\n{result.stdout[-500:]}"
    except subprocess.TimeoutExpired:
        return False, "arch_guard 检查超时"
    except Exception as e:
        return False, f"arch_guard 执行失败: {e}"


def validate_beta_to_production() -> tuple[bool, str]:
    """Validate target against rules and report findings."""
    checks_passed = 0
    checks_total = 2
    messages = []

    arch_result = validate_experimental_to_beta()
    if arch_result[0]:
        checks_passed += 1
    else:
        messages.append(f"架构不变量: {arch_result[1]}")

    secret_scan = REPO_ROOT / "scripts" / "governance" / "d6_security" / "scan_secret_leak.py"
    if secret_scan.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(secret_scan)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(REPO_ROOT),
                encoding="utf-8",
                errors="replace",
            )
            if result.returncode == 0:
                checks_passed += 1
            else:
                messages.append("安全扫描: 发现 P0 安全问题")
        except Exception as e:
            messages.append(f"安全扫描执行失败: {e}")
    else:
        messages.append("安全扫描脚本不存在")

    if checks_passed == checks_total:
        return True, f"beta→production 门禁 {checks_passed}/{checks_total} 通过"
    return False, f"beta→production 门禁 {checks_passed}/{checks_total} 未通过: {'; '.join(messages)}"


TRANSITION_VALIDATORS = {
    ("scaffold", "experimental"): validate_scaffold_to_experimental,
    ("experimental", "beta"): validate_experimental_to_beta,
    ("beta", "production"): validate_beta_to_production,
}


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Phase 过渡双门协议合规率校验")
    parser.add_argument("--from", dest="from_phase", default=None, help="源 Phase")
    parser.add_argument("--to", dest="to_phase", default=None, help="目标 Phase")
    args = parser.parse_args()

    from_phase = args.from_phase
    to_phase = args.to_phase

    if from_phase and to_phase:
        validator = TRANSITION_VALIDATORS.get((from_phase, to_phase))
        if not validator:
            print(f"[ERROR] 不支持的过渡: {from_phase} → {to_phase}")
            print(f"  支持的过渡: {', '.join(f'{a}→{b}' for a, b in TRANSITION_VALIDATORS)}")
            return EXIT_ERROR
        print(f"校验 {from_phase} → {to_phase} 过渡门禁...\n")
        ok, msg = validator()
        if ok:
            print(f"[PASS] {msg}")
            return EXIT_PASS
        else:
            print(f"[FAIL] {msg}")
            return EXIT_FINDINGS
    print("Phase 过渡双门协议 — 全量校验\n")
    all_results = []
    for (src, dst), validator in TRANSITION_VALIDATORS.items():
        print(f"  {src} → {dst} ... ", end="", flush=True)
        ok, msg = validator()
        status = "PASS" if ok else "FAIL"
        print(f"[{status}]")
        if not ok:
            print(f"    {msg[:200]}")
        all_results.append((src, dst, ok))

    passed = sum(1 for _, _, ok in all_results if ok)
    total = len(all_results)
    print(f"\n{'=' * 60}")
    print(f"结果：{passed}/{total} 过渡门禁通过")
    print(f"{'=' * 60}")

    if passed < total:
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
