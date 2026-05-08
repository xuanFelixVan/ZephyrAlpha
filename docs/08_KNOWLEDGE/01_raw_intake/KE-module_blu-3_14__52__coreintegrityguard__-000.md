---
module_id: KE-module_blu-3_14__52__coreintegrityguard__-000
title: 3.14 #52: CoreIntegrityGuard (M-41)
category: module_blueprint
---

# 3.14 #52: CoreIntegrityGuard (M-41)

3.14 #52: CoreIntegrityGuard (M-41)

文件：`D:\ZephyrAlpha\src\zephyr\shared\core_integrity_guard.py`

- IMMUTABLE_CORE清单：kill_switch.py / error_budget_tracker.py / circuit_breaker.py / token_budget_tracker.py / graceful_shutdown.py / startup_guard.py
- `pre_commit_check(changed_files)`: 核心文件变更→BLOCK+要求Owner dual-sign-off
- `daily_integrity_check()`: 哈希校验，不匹配→P0告警
