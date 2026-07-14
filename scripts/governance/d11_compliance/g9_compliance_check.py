# [BLUEPRINT] MOD-INF-005 | scripts/governance/g9_compliance_check.py | §
# [MODULE] scripts.governance.g9_compliance_check
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
"""G9 四蓝图跨模块集成合规门禁执行器.

机械执行 7 项检查，零人工介入。

用法
----
    python scripts/governance/g9_compliance_check.py              # 完整检查
    python scripts/governance/g9_compliance_check.py --warn-only  # 仅报错，不退出
"""

from __future__ import annotations

__manifest__ = """
args: []
description: G9 四蓝图跨模块集成合规门禁执行器.
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import re
import subprocess
import sys
from pathlib import Path

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

_PROJECT_ROOT = REPO_ROOT


def _grep_file(pattern: str, target: Path) -> bool:
    """_grep_file implementation."""
    if not target.exists():
        return False
    content = target.read_text(encoding="utf-8")
    return bool(re.search(pattern, content))


def _check_rbac_integration() -> tuple[bool, str]:
    """_check_rbac_integration implementation."""
    target = _PROJECT_ROOT / "src" / "zephyr" / "pipeline" / "pipeline_orchestrator.py"
    ok = _grep_file(r"(from zephyr\.agent_rbac|from zephyr\.governance\.escalation\.rbac_bridge)", target)
    return ok, f"Pipeline imports RBAC: {'YES' if ok else 'NO'}"


def _check_audit_integration() -> tuple[bool, str]:
    """_check_audit_integration implementation."""
    target = _PROJECT_ROOT / "src" / "zephyr" / "pipeline" / "pipeline_orchestrator.py"
    ok = _grep_file(r"from zephyr\.audit_trail", target)
    return ok, f"Pipeline imports audit_trail: {'YES' if ok else 'NO'}"


def _check_kb_external_access() -> tuple[bool, str]:
    """_check_kb_external_access implementation."""
    target = _PROJECT_ROOT / "src" / "zephyr" / "pipeline" / "pipeline_orchestrator.py"
    ok = _grep_file(r"from zephyr\.kb", target)
    return ok, f"Pipeline imports kb: {'YES' if ok else 'NO'} (WARNING only)"


def _check_agent_spec_cli() -> tuple[bool, str]:
    """_check_agent_spec_cli implementation."""
    target = _PROJECT_ROOT / "src" / "zephyr" / "agent-spec" / "__main__.py"
    ok = target.exists()
    return ok, f"agent-spec __main__.py exists: {'YES' if ok else 'NO'}"


def _check_agent_spec_importable() -> tuple[bool, str]:
    """_check_agent_spec_importable implementation."""
    try:
        import zephyr.autonomy_core  # noqa: F401

        return True, "agent-spec importable: YES"
    except Exception as exc:
        return False, f"agent-spec importable: NO ({exc})"


def _check_audit_writer_called() -> tuple[bool, str]:
    """_check_audit_writer_called implementation."""
    target = _PROJECT_ROOT / "src" / "zephyr" / "pipeline" / "pipeline_orchestrator.py"
    ok = _grep_file(r"(AuditWriter|_write_audit|_audit_writer)", target)
    return ok, f"Pipeline calls AuditWriter: {'YES' if ok else 'NO'}"


def _check_blueprint_status_sync() -> tuple[bool, str]:
    """_check_blueprint_status_sync implementation."""
    script = _PROJECT_ROOT / "scripts" / "governance" / "sync_blueprint_status.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        cwd=str(_PROJECT_ROOT),
    )
    clean = "CLEAN" in (result.stdout + result.stderr) and result.returncode == 0
    return clean, f"sync_blueprint_status: {'CLEAN' if clean else 'DRIFT'} (exit={result.returncode})"


_CHECKS = [
    ("G9-CHK-001", "agent-rbac → Pipeline", _check_rbac_integration, True),
    ("G9-CHK-002", "audit-trail → Pipeline", _check_audit_integration, True),
    ("G9-CHK-003", "knowledge-base external access", _check_kb_external_access, False),
    ("G9-CHK-004", "agent-spec CLI entry", _check_agent_spec_cli, True),
    ("G9-CHK-005", "agent-spec importable", _check_agent_spec_importable, True),
    ("G9-CHK-006", "AuditWriter called by Pipeline", _check_audit_writer_called, True),
    ("G9-CHK-007", "blueprint status sync", _check_blueprint_status_sync, True),
]


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    warn_only = "--warn-only" in sys.argv
    passed = 0
    failed = 0
    errors: list[str] = []

    for check_id, title, check_fn, is_error in _CHECKS:
        try:
            ok, msg = check_fn()
        except Exception as exc:
            ok = False
            msg = f"{title}: EXCEPTION {exc}"

        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {check_id}  {msg}")

        if ok:
            passed += 1
        else:
            failed += 1
            if is_error:
                errors.append(f"{check_id}: {msg}")

    print(f"\n{'=' * 60}")
    print(f"PASS: {passed}  FAIL: {failed}  TOTAL: {passed + failed}")

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")

    if warn_only or not errors:
        return EXIT_PASS
    return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
