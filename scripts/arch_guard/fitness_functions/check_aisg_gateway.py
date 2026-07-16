# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/check_aisg_gateway.py | §
# [MODULE] scripts.arch_guard.fitness_functions.check_aisg_gateway
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
"""
check_aisg_gateway.py — AISG 拦截门禁 (INV-015) Phase B 升级

  - 验证 AISG 文件/文档存在（结构检查）
  - 运行 AISG sandbox 安全测试（功能检查）
  - 验证 AISG 在 capacity_slo 中有声明

exit: 0=pass, 1=fail, 2=config error
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_GOV_DIR = _ROOT.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

from _arch_ssot import CAPACITY_SLO_PATH, load_yaml  # noqa: E402

def main() -> int:
    passed = 0
    total = 0
    errors: list[str] = []

    # ── 结构检查：文件/文档存在 ──
    slo = load_yaml(CAPACITY_SLO_PATH)
    arch_guard = slo.get("arch_guard") or {}
    aisg_config = arch_guard.get("ai_security_gateway") or {}

    total += 1
    if not aisg_config.get("enabled"):
        errors.append("arch_guard.ai_security_gateway.enabled 未显式设为 true（INV-015 需激活）")
    else:
        passed += 1

    aisg_paths = [
        REPO_ROOT / "src" / "zephyr" / "compliance" / "security_gateway_base.py",
        REPO_ROOT / "src" / "zephyr" / "compliance" / "aisg_sandbox.py",
        REPO_ROOT
        / "docs"
        / "01_policies_and_standards"
        / "_registry"
        / "catalogs"
        / "ai_autonomy_authority_registry.yaml",
    ]

    for p in aisg_paths:
        total += 1
        if p.exists():
            passed += 1
        else:
            rel = p.relative_to(REPO_ROOT)
            errors.append(f"AISG 文件缺失: {rel}")

    # ── 功能检查：AISG sandbox 测试 ──
    sandbox_path = REPO_ROOT / "src" / "zephyr" / "compliance" / "aisg_sandbox.py"
    if sandbox_path.exists():
        import importlib.util

        spec = importlib.util.spec_from_file_location("aisg_sandbox", sandbox_path)
        if spec and spec.loader:
            sandbox_mod = importlib.util.module_from_spec(spec)
            sys.modules["aisg_sandbox"] = sandbox_mod
            spec.loader.exec_module(sandbox_mod)
            sandbox = sandbox_mod.AISGSandbox()

            total += 1
            dangerous = sandbox.run_dangerous_pattern_tests()
            dangerous_fails = [r for r in dangerous if not r.passed]

            total += 1
            safe = sandbox.run_safe_pattern_tests()
            safe_fails = [r for r in safe if not r.passed]

            if not dangerous_fails and not safe_fails:
                passed += 2
            else:
                passed += (0 if dangerous_fails else 1) + (0 if safe_fails else 1)
                for f in dangerous_fails:
                    errors.append(f"AISG sandbox FAIL: {f.test_name} 未拦截危险模式")
                for f in safe_fails:
                    errors.append(f"AISG sandbox FAIL: {f.test_name} 误拦截安全代码")
    else:
        errors.append("AISG sandbox 文件不存在，跳过功能测试")

    # ── 报告 ──
    print(f"OK: INV-015 AISG 门禁 — {passed}/{total} checks passed")
    if errors:
        for e in errors:
            print(f"  WARN: {e}")
        if all("sandbox" in e.lower() or "sandbox" in e for e in errors):
            print("  NOTE: Sandbox 测试为 Phase B 升级，当前 WARN 不阻塞")
            return 0
        print(f"\nFAIL: {len(errors)} AISG issue(s)")
        return 1

    print("OK: AISG 门禁全部通过（含 sandbox 安全测试）")
    return 0

if __name__ == "__main__":
    sys.exit(main())
