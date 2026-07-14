# [BLUEPRINT] MOD-INF-005 | scripts/governance/test_lock_scenarios.py | §
# [MODULE] scripts.governance.test_lock_scenarios
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
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
test_lock_scenarios.py — RULE-ZERO 锁协议场景 B/C 验证

场景 B: 两个 AI 同时修改同一文件 → 后到者被阻塞
场景 C: AI-1 锁定并修改脚本，AI-2 仅使用（运行）该脚本 → 不冲突

用法:
  python scripts/governance/test_lock_scenarios.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import subprocess
import sys
import threading
from pathlib import Path

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

LOCK_SCRIPT = str(REPO_ROOT / "scripts" / "lock_files.py")
TEST_SCRIPT = str(REPO_ROOT / "scripts" / "governance" / "d3_metadata" / "generate_derived_files.py")

SCENARIO_B_FILE = str(REPO_ROOT / "scripts" / "governance" / "_test_lock_target.py")
SESSION_A = "session-test-20260507-A"
SESSION_B = "session-test-20260507-B"

PASS = 0
FAIL = 0


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """_run implementation."""
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT), **kwargs)


def _ok(label: str) -> None:
    """_ok implementation."""
    global PASS
    PASS += 1
    print(f"  PASS: {label}")


def _ng(label: str, detail: str = "") -> None:
    """_ng implementation."""
    global FAIL
    FAIL += 1
    print(f"  FAIL: {label}" + (f" — {detail}" if detail else ""))


def setup():
    """setup implementation."""
    target = Path(SCENARIO_B_FILE)
    target.write_text("# test target for lock scenario B\nprint('hello')\n", encoding="utf-8")
    _run([sys.executable, LOCK_SCRIPT, "release-all", SESSION_A])
    _run([sys.executable, LOCK_SCRIPT, "release-all", SESSION_B])
    _run([sys.executable, LOCK_SCRIPT, "cleanup"])


def teardown():
    """teardown implementation."""
    Path(SCENARIO_B_FILE).unlink(missing_ok=True)
    _run([sys.executable, LOCK_SCRIPT, "release-all", SESSION_A])
    _run([sys.executable, LOCK_SCRIPT, "release-all", SESSION_B])
    _run([sys.executable, LOCK_SCRIPT, "cleanup"])


def test_scenario_b():
    """
    B: AI-A acquires lock → AI-B tries acquire → BLOCKED → AI-A releases → AI-B acquires → OK
    """
    print("\n" + "=" * 60)
    print("  Scenario B: Two AIs modify the SAME file")
    print("=" * 60)

    r = _run([sys.executable, LOCK_SCRIPT, "acquire", SCENARIO_B_FILE, SESSION_A, "--task", "AI-A editing"])
    if r.returncode != 0:
        _ng("AI-A acquire (should succeed)", r.stdout.strip())
        return
    _ok("AI-A acquired lock on target file")

    r = _run([sys.executable, LOCK_SCRIPT, "acquire", SCENARIO_B_FILE, SESSION_B, "--task", "AI-B editing"])
    if r.returncode == 0:
        _ng("AI-B acquire (should be BLOCKED by AI-A)", "lock_files returned 0 but should return non-zero")
    else:
        _ok("AI-B was BLOCKED (cannot acquire while AI-A holds lock)")

    r = _run([sys.executable, LOCK_SCRIPT, "release", SCENARIO_B_FILE, SESSION_A])
    if r.returncode != 0:
        _ng("AI-A release", r.stdout.strip())
        return
    _ok("AI-A released lock")

    r = _run([sys.executable, LOCK_SCRIPT, "acquire", SCENARIO_B_FILE, SESSION_B, "--task", "AI-B editing"])
    if r.returncode != 0:
        _ng("AI-B acquire after AI-A release (should succeed)", r.stdout.strip())
        return
    _ok("AI-B acquired lock after AI-A released")

    _run([sys.executable, LOCK_SCRIPT, "release", SCENARIO_B_FILE, SESSION_B])


def test_scenario_c():
    """
    C: AI-1 locks script → AI-2 runs that same script → RUNS OK (no conflict)
    """
    print("\n" + "=" * 60)
    print("  Scenario C: AI-1 MODIFIES script  +  AI-2 USES script")
    print("=" * 60)

    script_path = str(Path(TEST_SCRIPT).relative_to(REPO_ROOT)).replace("\\", "/")
    r = _run([sys.executable, LOCK_SCRIPT, "acquire", TEST_SCRIPT, SESSION_A, "--task", "AI-A patching script"])
    if r.returncode != 0:
        _ng("AI-A acquire lock on test script", r.stdout.strip())
        return
    _ok(f"AI-A locked {script_path} (simulating script editing)")

    r = _run([sys.executable, TEST_SCRIPT, "--apply"])
    if r.returncode != 0:
        _ng("AI-B run locked script (should still work)", r.stdout.strip())
        detail = r.stdout.strip()[-200:] if r.stdout else r.stderr.strip()[-200:]
        print(f"       detail: {detail}")
    else:
        _ok(f"AI-B ran {script_path} successfully while AI-A holds lock")

    r = _run([sys.executable, LOCK_SCRIPT, "release", TEST_SCRIPT, SESSION_A])
    if r.returncode != 0:
        _ng("AI-A release", r.stdout.strip())
    else:
        _ok("AI-A released lock")


def test_scenario_c_concurrent():
    """
    C-concurrent: AI-1 locks script, holds for 3s. Meanwhile AI-2 runs it 3 times in parallel.
    All runs should succeed — lock on .py file does NOT block execution.
    """
    print("\n" + "=" * 60)
    print("  Scenario C-Concurrent: 3 parallel runs while script is locked")
    print("=" * 60)

    script_path = str(Path(TEST_SCRIPT).relative_to(REPO_ROOT)).replace("\\", "/")
    r = _run([sys.executable, LOCK_SCRIPT, "acquire", TEST_SCRIPT, SESSION_A, "--task", "AI-A patching script"])
    if r.returncode != 0:
        _ng("AI-A acquire", r.stdout.strip())
        return
    _ok(f"AI-A locked {script_path}")

    results = []
    errors = []

    def runner(idx):
        """runner implementation."""
        r = _run([sys.executable, TEST_SCRIPT, "--apply"])
        results.append((idx, r.returncode))
        if r.returncode != 0:
            errors.append((idx, r.stdout.strip()[-200:] if r.stdout else r.stderr.strip()[-200:]))

    threads = [threading.Thread(target=runner, args=(i,)) for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    all_ok = all(rc == 0 for _, rc in results)
    if all_ok:
        _ok("3/3 concurrent runs PASSED while script was locked")
    else:
        failed = [idx for idx, rc in results if rc != 0]
        _ng(f"Some runs failed: idx={failed}", str(errors))

    _run([sys.executable, LOCK_SCRIPT, "release", TEST_SCRIPT, SESSION_A])
    _ok("AI-A released lock")


def main():
    """Entry point: parse args, run logic, return exit code."""
    print("=" * 60)
    print("  RULE-ZERO Lock Protocol: Scenario B + C Test")
    print("=" * 60)

    setup()
    try:
        test_scenario_b()
        test_scenario_c()
        test_scenario_c_concurrent()
    finally:
        teardown()

    print("\n" + "=" * 60)
    total = PASS + FAIL
    print(f"  Results: {PASS}/{total} PASS, {FAIL}/{total} FAIL")
    print("=" * 60)

    if FAIL > 0:
        print("\n  VERDICT: TESTS FAILED — some lock scenarios are broken")
        sys.exit(EXIT_FINDINGS)
    else:
        print("\n  VERDICT: ALL PASS — lock protocol works correctly")
        print("  - Scenario B: modification conflict is properly blocked")
        print("  - Scenario C: usage (run) is never blocked by modification lock")
        sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
