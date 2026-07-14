# [BLUEPRINT]
# [MODULE] scripts.governance.verify_key_imports
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""governance/verify_key_imports 脚本 — 关键模块导入验证

结构变更后验证关键模块可正常导入。替代 onboarding_detail.md §13.5 中的内联 python -c 命令。

[BLUEPRINT] onboarding_detail.md §13.5 | 验证命令 STEP 5
[MODULE] N/A（脚本，非模块）
[INVARIANTS] 全部导入成功 → exit 0；任一失败 → exit 1
[MODIFY-GUARD] 新增关键模块时更新 KEY_MODULES 列表
[CONSUMERS] onboarding_detail.md §13.5 验证流程；结构变更后强制执行
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] ImportError → 打印错误 + exit 1
[TESTS] python scripts/governance/verify_key_imports.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: governance/verify_key_imports 脚本 — 关键模块导入验证
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys

KEY_MODULES = [
    "zephyr.shared",
    "zephyr.governance.ops_governance.budget_engine",
    "zephyr.governance.escalation.escalation_engine",
    "zephyr.security.llm_defense.llm_security.gateway",
    "zephyr.infrastructure.system_telemetry.auto_bootstrap",
    "zephyr.gov_kb.unified_memory_api",
    "zephyr.governance",
]


def main() -> None:
    """入口——逐个导入关键模块，全部成功则 exit 0。"""
    failures: list[tuple[str, str]] = []
    for mod in KEY_MODULES:
        try:
            __import__(mod)
            print(f"OK: {mod}")
        except Exception as e:
            print(f"FAIL: {mod} — {e}")
            failures.append((mod, str(e)))

    if failures:
        print(f"\n{len(failures)} 个模块导入失败:")
        for mod, err in failures:
            print(f"  {mod}: {err}")
        sys.exit(1)
    print(f"\n全部 {len(KEY_MODULES)} 个关键模块导入成功")
    sys.exit(0)


if __name__ == "__main__":
    main()
