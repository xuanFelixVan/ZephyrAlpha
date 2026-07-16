# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/run_all.py | §
# [MODULE] scripts.arch_guard.run_all
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.arch_guard.__init__
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
"""Architecture Guard 编排器

读取 manifest.yaml，执行所有 status=active 的 fitness function。
对标 Google Tricorder Presubmit——在 CI Pipeline 中调用。

用法: python scripts/arch_guard/run_all.py [--strict]

exit codes（本编排器语义，独立约定）：
  0=all pass，1=存在失败的 fitness function，2=编排/执行层面的错误。
与 `scripts/governance/run_all.py` 的 CT-SCRIPT-GATE-001 **四档语义（含 3=基础设施异常）并非同一标尺**——CI 中应分别解读，勿混用 exit code 数字含义。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import yaml

ARCH_GUARD_ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ARCH_GUARD_ROOT / "manifest.yaml"


def load_manifest() -> dict:
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_ff(ff: dict) -> tuple[bool, str]:
    script_path = ARCH_GUARD_ROOT / ff["path"]
    if not script_path.exists():
        return False, f"脚本不存在: {script_path}"

    try:
        env = {"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(ARCH_GUARD_ROOT.parent.parent),
            encoding="utf-8",
            errors="replace",
            env={**dict(os.environ), **env} if hasattr(os, "environ") else env,
        )
        passed = result.returncode == 0
        msg = result.stdout.strip() or result.stderr.strip() or "(无输出)"
        return passed, msg
    except subprocess.TimeoutExpired:
        return False, f"超时（60s）: {ff['name']}"
    except Exception as e:
        return False, f"执行错误: {e}"


def main() -> int:
    manifest = load_manifest()
    active_ffs = [ff for ff in manifest["fitness_functions"] if ff["status"] == "active"]

    if not active_ffs:
        print("没有任何 active 状态的 fitness function——全部通过。")
        return 0

    print(f"Architecture Guard — 执行 {len(active_ffs)} 条 active fitness function\n")

    failed = []
    passed = []

    for ff in active_ffs:
        print(f"  [{ff['id']}] {ff['name']} ... ", end="", flush=True)
        ok, msg = run_ff(ff)
        if ok:
            print("[PASS]")
            passed.append(ff)
        else:
            print("[FAIL]")
            print(f"        {msg}")
            failed.append((ff, msg))

    print(f"\n{'=' * 60}")
    skipped_n = len(manifest["fitness_functions"]) - len(active_ffs)
    print(f"结果：{len(passed)} PASS / {len(failed)} FAIL / {skipped_n} 未激活")
    print(f"{'=' * 60}")

    if failed:
        print("\n[FAIL] 以下不变量被违反（阻塞 PR）：")
        for ff, msg in failed:
            print(f"  - {ff['invariant_id']} {ff['name']}: {msg}")
        return 1

    print("\n[OK] 所有 active 不变量强制执行通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
