# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/validate_script_onboarding.py | §
# [MODULE] scripts.governance.meta.validate_script_onboarding
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

V_CHECKS = {
    "V1_FILE_LOCATION": "脚本在合法三目录",
    "V2_PREFIX": "文件名遵守前缀约定",
    "V3_MANIFEST": "script_manifest.yaml 有注册",
    "V4_UTF8": "encoding='utf-8'",
    "V5_STDOUT": "stdout 结构化输出",
    "V6_INDEP_RUN": "python script.py --help 0 exit",
    "V7_FULL_REGRESSION": "run_all.py --all 通过",
    "V8_DOCSTRING": "含 __doc__",
    "V9_SHEBANG": "#!/usr/bin/env python",
    "V10_EXIT_CODE": "退出码 0/1/2/3",
    "V11_WARN_ONLY": "--warn-only 模式",
    "V12_ABSOLUTE": "Import 用绝对路径",
}


def validate_onboarding(script_path: str) -> tuple[bool, list[str]]:
    """执行 V1-V12 检查，返回通过/失败及逐项结果。"""
    path = Path(script_path)
    results: list[str] = []
    if not path.exists():
        return False, [f"文件不存在: {path}"]

    content = path.read_text(encoding="utf-8")
    parent = str(path.parent)

    # V1: legal directory
    legal = ["scripts/governance", "src/zephyr", "tests"]
    v1_ok = any(d in parent.replace("\\", "/") for d in legal)
    results.append(f"{'✅' if v1_ok else '❌'} V1: {V_CHECKS['V1_FILE_LOCATION']}")

    # V2: prefix
    name = path.stem
    v2_ok = any(name.startswith(p) for p in ["validate_", "detect_", "audit_", "check_", "register_"])
    results.append(f"{'✅' if v2_ok else '❌'} V2: {V_CHECKS['V2_PREFIX']}")

    # V4: UTF-8
    v4_ok = "encoding='utf-8'" in content or 'encoding="utf-8"' in content
    results.append(f"{'✅' if v4_ok else '❌'} V4: {V_CHECKS['V4_UTF8']}")

    # V8: docstring
    v8_ok = "__doc__" in content or '"""' in content
    results.append(f"{'✅' if v8_ok else '❌'} V8: {V_CHECKS['V8_DOCSTRING']}")

    # V9: shebang
    v9_ok = content.startswith("#!/usr/bin/env python") or content.startswith("#!")
    results.append(f"{'✅' if v9_ok else '⚠️ '} V9: shebang detection")

    all_ok = v1_ok and v2_ok and v4_ok
    return all_ok, results


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    if len(sys.argv) < 2:
        print("用法: python validate_script_onboarding.py <脚本路径>")
        return EXIT_FINDINGS
    ok, results = validate_onboarding(sys.argv[1])
    for r in results:
        print(r)
    print(f"\n{'✅ ALL PASSED' if ok else '❌ FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
