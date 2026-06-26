---
module_id: KE-2751----c-001
status: active
title: grandfather-registry.yaml —— cache_manager.py 自动维护
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# grandfather-registry.yaml —— cache_manager.py 自动维护

grandfather-registry.yaml —— cache_manager.py 自动维护
grandfathered_duplicates:
  - dup_id: "DUP-20251101-007"
    first_detected: "2025-11-01"
    age_days: 186                           # 6个月老的重复
    status: "FOSSILIZED"
    functions: ["_parse_args_old", "parse_cli_args"]
    callers: ["cli/report.py", "cli/scan.py", "cli/watch.py"]
    archaeology:
      first_commit: "abc1234 (2025-10-15, 'initial CLI skeleton')"
      callers_with_tests: 1                 # 只有 1 个 caller 有测试 → 不满足第三定律
      rollback_plan: "git revert <fix-commit> — 单命令可回滚"
    recommendation: "KEEP——考古测试未通过（caller测试覆盖不足）。此重复是 CLI 架构的基石部分"
```
