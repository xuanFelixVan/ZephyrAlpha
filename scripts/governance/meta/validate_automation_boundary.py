# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/validate_automation_boundary.py | §
# [MODULE] scripts.governance.meta.validate_automation_boundary
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
# [TTL] permanent
"""Module docstring — see module-level docstring for details."""

from __future__ import annotations

__manifest__ = """
args: []
description: Module docstring — see module-level docstring for details.
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

import sys
from pathlib import Path

from _shared.constants import EXIT_FINDINGS

SIX_RED_LINES = [
    ("auto_modify_source", "禁止自动修改源码"),
    ("auto_delete_files", "禁止自动删除文件"),
    ("auto_modify_config", "禁止自动修改配置"),
    ("skip_gate", "禁止跳过门禁"),
    ("auto_modify_registry", "禁止自动修改登记表"),
    ("self_modify", "禁止自我修改"),
]


def validate_script(script_path: str) -> tuple[bool, list[str]]:
    """Validate target against rules and report findings."""
    path = Path(script_path)
    if not path.exists():
        return False, [f"文件不存在: {path}"]
    content = path.read_text(encoding="utf-8")
    violations: list[str] = []
    for rule_key, rule_desc in SIX_RED_LINES:
        if rule_key == "auto_delete_files" and "os.remove" in content:
            violations.append(f"违规: {rule_desc} — 检测到 os.remove()")
        if rule_key == "auto_modify_source" and ("open(" in content and "'w'" in content):
            violations.append(f"违规: {rule_desc} — 检测到 open(x, 'w')")
        if rule_key == "self_modify" and "__file__" in content and "write" in content.lower():
            violations.append(f"违规: {rule_desc} — 检测到自我写入模式")
    ok = len(violations) == 0
    return ok, violations


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    if len(sys.argv) < 2:
        print("用法: python validate_automation_boundary.py <脚本路径1> [脚本路径2 ...]")
        return EXIT_FINDINGS
    all_ok = True
    for script_path in sys.argv[1:]:
        ok, violations = validate_script(script_path)
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"{status}: {script_path}")
        for v in violations:
            print(f"  → {v}")
        if not ok:
            all_ok = False
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
