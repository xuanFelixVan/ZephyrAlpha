# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/check_scaffold_exit_gates.py | §
# [MODULE] scripts.arch_guard.check_scaffold_exit_gates
# [DOMAIN] D-GOVERNANCE
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
"""check_scaffold_exit_gates.py — scaffold→experimental 安全门禁检查

对标 architecture_endgame_locked.md §6 + 06-security_architecture.md §10.2。
4 条安全门禁：

  G1: git-secrets pre_commit hook 已部署 (06-SEC SG-1)
  G2: 全库 secret 泄漏扫描已执行且无 P0 发现 (06-SEC SG-2)
  G3: audit.db schema 已物理创建 (06-SEC SG-3)
  G4: 06-SEC 视图 status=active 且被 00-overview.md §5 引用 (06-SEC SG-4)

exit: 0=all gates pass, 1=gates not passed, 2=infrastructure error
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
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


SEC_VIEW_PATH = (
    REPO_ROOT / "docs" / "02_enterprise_architecture" / "target-architecture" / "06-security_architecture.md"
)
OVERVIEW_PATH = REPO_ROOT / "docs" / "02_enterprise_architecture" / "target-architecture" / "00-overview.md"


def check_security_view_active() -> tuple[bool, str]:
    if not SEC_VIEW_PATH.exists():
        return False, "06-security_architecture.md 不存在"
    try:
        sec_content = SEC_VIEW_PATH.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return False, f"无法读取 06-SEC: {e}"
    if "status: active" not in sec_content:
        return False, "06-SEC 视图 status != active"
    if not OVERVIEW_PATH.exists():
        return False, "00-overview.md 不存在"
    try:
        ov_content = OVERVIEW_PATH.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return False, f"无法读取 00-overview: {e}"
    sec_refs = ["06-security", "安全架构", "Security Architecture"]
    found = [r for r in sec_refs if r in ov_content]
    if not found:
        return False, "00-overview.md 未引用 06-SEC 视图"
    return True, f"06-SEC status=active + 00-overview 引用 ({', '.join(found[:2])})"


GATES = [
    ("G1", "git-secrets hook", check_git_secrets_hook),
    ("G2", "secret 泄漏扫描", check_scan_secret_leak),
    ("G3", "audit.db 创建", check_audit_db),
    ("G4", "06-SEC 视图治理", check_security_view_active),
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
        print("  G4: 确认 detect_secrets.py 可正常执行")
        return 1

    print("\n[OK] 所有安全门禁通过。scaffold→experimental 过渡条件满足。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
