# [BLUEPRINT] MOD-INF-005 | scripts/governance/vms_version_sync_check.py | §
# [MODULE] scripts.governance.vms_version_sync_check
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
# [TTL] permanent
"""
VMS 版本同步检查器 — MOD-INF-011 · TASK-INF-0222
===================================================
P1 · 比对蓝图版本号与模块代码版本号一致性

用法
----
    python scripts/governance/vms_version_sync_check.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: VMS 版本同步检查器 — MOD-INF-011 · TASK-INF-0222
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
import sys
from pathlib import Path

from _shared.constants import EXIT_FINDINGS, EXIT_PASS

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

VMS_DIR = PROJECT_ROOT / "src" / "zephyr" / "vector-memory"
BLUEPRINT = (
    PROJECT_ROOT / "docs" / "03_modules" / "infrastructure_runtime_integration" / "vector-memory" / "blueprint.md"
)

EXPECTED_BLUEPRINT_VERSION = "v0.7.0"
EXPECTED_MODULE_VERSION = "v0.1.0"


def check_blueprint_version() -> tuple[bool, str]:
    """Check compliance and report findings."""
    if not BLUEPRINT.exists():
        return False, f"蓝图文件不存在: {BLUEPRINT}"

    content = BLUEPRINT.read_text(encoding="utf-8")
    match = re.search(r"v\d+\.\d+\.\d+", content)
    if match:
        version = match.group(0)
        if version == EXPECTED_BLUEPRINT_VERSION:
            return True, f"蓝图版本: {version} ✓"
        return False, f"蓝图版本: {version} (期望 {EXPECTED_BLUEPRINT_VERSION})"
    return False, "未找到蓝图版本号"


def check_module_version() -> tuple[bool, str]:
    """Check compliance and report findings."""
    init_file = VMS_DIR / "__init__.py"
    if not init_file.exists():
        return False, "__init__.py 不存在"

    content = init_file.read_text(encoding="utf-8")
    match = re.search(r"v\d+\.\d+\.\d+", content)
    if match:
        version = match.group(0)
        if version == EXPECTED_MODULE_VERSION:
            return True, f"模块版本: {version} ✓"
        return False, f"模块版本: {version} (期望 {EXPECTED_MODULE_VERSION})"
    return False, "未找到模块版本号"


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    print("VMS 版本同步检查")
    print("=" * 50)

    bp_ok, bp_msg = check_blueprint_version()
    mod_ok, mod_msg = check_module_version()

    print(f"  蓝图: {bp_msg}")
    print(f"  模块: {mod_msg}")

    if bp_ok and mod_ok:
        print("\n✅ 版本同步检查通过")
        sys.exit(EXIT_PASS)
    else:
        print("\n❌ 版本不同步")
        sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
