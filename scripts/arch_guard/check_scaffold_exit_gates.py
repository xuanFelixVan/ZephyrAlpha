# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/check_scaffold_exit_gates.py | §
# [MODULE] scripts.arch_guard.check_scaffold_exit_gates
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
"""check_scaffold_exit_gates.py — scaffold→experimental 安全门禁检查

对标 architecture_model/cross_cutting/invariants.yaml 安全不变量。
4 条安全门禁：

  G1: git-secrets pre_commit hook 已部署 (06-SEC SG-1)
  G2: 全库 secret 泄漏扫描已执行且无 P0 发现 (06-SEC SG-2)
  G3: audit.db schema 已物理创建 (06-SEC SG-3)
  G4: invariants.yaml 安全不变量已定义且有 owner+enforcement (06-SEC SG-4)

exit: 0=all gates pass, 1=gates not passed, 2=infrastructure error
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_GOV_DIR = _ROOT.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402
from _shared.yaml_utils import load_yaml  # noqa: E402

GIT_SECRETS_HOOK = REPO_ROOT / ".git" / "hooks" / "pre_commit"
AUDIT_DB_PATH = REPO_ROOT / "data" / "audit.db"
DETECT_SECRETS_SCRIPT = REPO_ROOT / "scripts" / "governance" / "d6_security" / "detect_secrets.py"
SECRET_LEAK_SCAN_SCRIPT = REPO_ROOT / "scripts" / "governance" / "d6_security" / "scan_secret_leak.py"

def check_git_secrets_hook() -> tuple[bool, str]:
    if not GIT_SECRETS_HOOK.exists():
        return False, "git-secrets pre_commit hook 未部署 (.git/hooks/pre_commit 不存在)"
    try:
        content = GIT_SECRETS_HOOK.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return False, f"无法读取 pre_commit hook: {e}"
    zephyr_patterns = ["ZEPHYR_SECRET", "ZEPHYR_API_KEY", "ZEPHYR_TOKEN"]
    found = [p for p in zephyr_patterns if p in content]
    if not found:
        return False, "pre_commit hook 存在但未包含 ZEPHYR_SECRET_* pattern"
    return True, f"git-secrets hook 已部署 (含 {', '.join(found)})"

def check_scan_secret_leak() -> tuple[bool, str]:
    scanner = SECRET_LEAK_SCAN_SCRIPT if SECRET_LEAK_SCAN_SCRIPT.exists() else DETECT_SECRETS_SCRIPT
    if not scanner.exists():
        return False, f"secret 扫描脚本不存在: {scanner.relative_to(REPO_ROOT)}"
    try:
        result = subprocess.run(
            [sys.executable, str(scanner), "--warn-only"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(REPO_ROOT),
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode == 0:
            return True, "secret 扫描通过 (无 P0 发现)"
        return False, f"secret 扫描发现异常 (exit={result.returncode})"
    except subprocess.TimeoutExpired:
        return False, "secret 扫描超时 (120s)"
    except Exception as e:
        return False, f"secret 扫描执行失败: {e}"

def check_audit_db() -> tuple[bool, str]:
    if AUDIT_DB_PATH.exists() and AUDIT_DB_PATH.stat().st_size > 0:
        return True, f"audit.db 已创建 ({AUDIT_DB_PATH.stat().st_size} bytes)"
    return False, "audit.db 未物理创建或为空"

INVARIANTS_PATH = REPO_ROOT / "architecture_model" / "cross_cutting" / "invariants.yaml"
_SECURITY_CATEGORIES = {"capital_safety", "boundary_integrity"}

def check_security_invariants_active() -> tuple[bool, str]:
    """G4: invariants.yaml 安全不变量已定义且有 owner+enforcement。

    真源迁移：security_architecture.md 已删除（2026-07-01），
    安全基线真源迁至 architecture_model/cross_cutting/invariants.yaml
    （capital_safety / boundary_integrity category）。
    """
    if not INVARIANTS_PATH.exists():
        return False, "invariants.yaml 不存在"
    data = load_yaml(INVARIANTS_PATH)
    if not data:
        return False, "invariants.yaml 为空或无法解析"
    invariants = data.get("invariants", [])
    if not isinstance(invariants, list) or not invariants:
        return False, "invariants.yaml 无 invariant 条目"
    sec_invs = [
        i for i in invariants
        if isinstance(i, dict) and i.get("category") in _SECURITY_CATEGORIES
    ]
    if not sec_invs:
        return False, "invariants.yaml 无 capital_safety/boundary_integrity 条目"
    missing = [
        i.get("id", "?") for i in sec_invs
        if not i.get("owner") or not i.get("enforcement")
    ]
    if missing:
        return False, f"安全不变量缺少 owner/enforcement: {', '.join(missing)}"
    return True, f"{len(sec_invs)} 条安全不变量已定义且有 owner+enforcement"

GATES = [
    ("G1", "git-secrets hook", check_git_secrets_hook),
    ("G2", "secret 泄漏扫描", check_scan_secret_leak),
    ("G3", "audit.db 创建", check_audit_db),
    ("G4", "安全不变量治理", check_security_invariants_active),
]

def main() -> int:
    print("scaffold→experimental 安全门禁检查\n")

    passed = []
    failed = []

    for gate_id, gate_name, check_fn in GATES:
        print(f"  [{gate_id}] {gate_name} ... ", end="", flush=True)
        ok, msg = check_fn()
        if ok:
            print(f"[PASS] {msg}")
            passed.append(gate_id)
        else:
            print(f"[FAIL] {msg}")
            failed.append((gate_id, gate_name, msg))

    print(f"\n{'=' * 60}")
    print(f"结果：{len(passed)} PASS / {len(failed)} FAIL")
    print(f"{'=' * 60}")

    if failed:
        print("\n[FAIL] 以下门禁未通过（阻塞 scaffold→experimental 过渡）：")
        for gid, gname, gmsg in failed:
            print(f"  - {gid} {gname}: {gmsg}")
        print("\n修复建议：")
        print("  G1: 运行 scripts/hooks/git_secrets_setup.sh 部署 hook")
        print("  G2: 运行 detect_secrets.py --warn-only 确认无 P0 发现")
        print("  G3: 运行 scripts/governance/d6_security/init_audit_db.py 创建 audit.db")
        print("  G4: 确认 architecture_model/cross_cutting/invariants.yaml 存在且安全不变量有 owner+enforcement")
        return 1

    print("\n[OK] 所有安全门禁通过。scaffold→experimental 过渡条件满足。")
    return 0

if __name__ == "__main__":
    sys.exit(main())
