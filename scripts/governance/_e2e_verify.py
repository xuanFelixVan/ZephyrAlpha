# [BLUEPRINT] MOD-INF-005 | scripts/governance/_e2e_verify.py | §
"""Module docstring — see module-level docstring for details."""

import sys

print("=" * 70)
print("  ZephyrAlpha Full-Chain End-to-End Verification")
print("=" * 70)

errors = []

print("\n[1/7] zephyr.shared._cross_layer lazy load via zephyr.__init__")
try:
    import zephyr

    cl = zephyr.shared._cross_layer
    print(f"  OK: zephyr.shared._cross_layer = {cl}")
except Exception as e:
    errors.append(f"[1] _cross_layer lazy load: {e}")
    print(f"  FAIL: {e}")

print("\n[2/7] AlphaSignalPipeline + MLExperimentPipeline instantiation")
try:
    from zephyr.shared._cross_layer import AlphaSignalPipeline, MLExperimentPipeline

    ap = AlphaSignalPipeline()
    mp = MLExperimentPipeline()
    print(f"  OK: AlphaSignalPipeline={ap}, MLExperimentPipeline={mp}")
except Exception as e:
    errors.append(f"[2] Pipeline instantiation: {e}")
    print(f"  FAIL: {e}")

print("\n[3/7] Pipeline degraded run (no L02/L11 contracts)")
try:
    ar = ap.run()
    mr = mp.run()
    print(f"  Alpha: status={ar.status}, degraded={ar.degraded}, errors={len(ar.errors)}")
    print(f"  ML:    status={mr.status}, errors={len(mr.errors)}")
    if ar.status == "blocked_by_infrastructure":
        errors.append("[3] Alpha pipeline still blocked_by_infrastructure")
    if mr.status == "blocked_by_infrastructure":
        errors.append("[3] ML pipeline still blocked_by_infrastructure")
except Exception as e:
    errors.append(f"[3] Pipeline run: {e}")
    print(f"  FAIL: {e}")

print("\n[4/7] GovernanceServer MCP tools")
try:
    from zephyr.infrastructure.governance_server import GovernanceServer

    gs = GovernanceServer()
    tools = list(gs._tools.keys())
    print(f"  OK: {len(tools)} tools: {tools[:5]}...")
except Exception as e:
    errors.append(f"[4] GovernanceServer: {e}")
    print(f"  FAIL: {e}")

print("\n[5/7] FeedbackLoopScheduler FLE gate dispatch")
try:
    from zephyr.ops.feedback_loop.scheduler import FeedbackLoopScheduler

    s = FeedbackLoopScheduler()
    has_dispatch = hasattr(s, "_dispatch_fle_gates")
    has_invoke = hasattr(s, "_invoke_fle_gate")
    print(f"  _dispatch_fle_gates: {has_dispatch}, _invoke_fle_gate: {has_invoke}")
    if not has_dispatch:
        errors.append("[5] Scheduler missing _dispatch_fle_gates")
except Exception as e:
    errors.append(f"[5] Scheduler: {e}")
    print(f"  FAIL: {e}")

print("\n[6/7] GateEngine fle_gate check_type")
try:
    from zephyr.governance.rule_enforcement.gate_engine import GateEngine

    ge = GateEngine()
    print("  OK: GateEngine instantiated")
except Exception as e:
    errors.append(f"[6] GateEngine: {e}")
    print(f"  FAIL: {e}")

print("\n[7/7] auto_sync_all_registries --all --warn-only")
try:
    import subprocess

    result = subprocess.run(
        [sys.executable, "scripts/governance/auto_sync_all_registries.py", "--all", "--warn-only"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    print(f"  exit_code={result.returncode}")
    if result.returncode != 0:
        errors.append(f"[7] auto_sync exit_code={result.returncode}")
        print(f"  stderr: {result.stderr[:200]}")
    else:
        print("  OK")
except Exception as e:
    errors.append(f"[7] auto_sync: {e}")
    print(f"  FAIL: {e}")

print("\n" + "=" * 70)
if errors:
    print(f"  FAILURES: {len(errors)}")
    for e in errors:
        print(f"    {e}")
    sys.exit(1)
else:
    print("  ALL 7/7 CHECKS PASSED")
    sys.exit(0)
