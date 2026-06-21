---
module_id: KE-1897
status: active
title: 2.4 回滚策略矩阵
category: module_blueprint
---

# 2.4 回滚策略矩阵

2.4 回滚策略矩阵

```yaml
rollback_strategies:
  forward_fix_preferred:
    trigger: "soft_failure AND 变更 ≤ 3 文件 AND 文件未锁定"
    method: "Agent 产生 FIX-{sha} commit 直接修正"
    fallback: "连续 2 次失败 → partial_revert"
    verification: "G0 门禁"
    permission: "自动——无需 Owner"
    audit_level: "ProvenanceStandard"

  hard_failure:
    trigger: "drift / CI FAIL / G6 secrets / 熔断器 OPEN"
    method: "full_revert（git revert --no-edit {commit_sha}）"
    verification: "G0 门禁 + DB 一致性 + differential check"
    permission: "自动——无需 Owner"
    audit_level: "ProvenanceStandard"

  soft_failure:
    trigger: "G0-G3 格式/语法错误，3 次 retry 仍失败（forward-fix 已尝试但失效）"
    method: "partial_revert({commit_sha}, file_globs)"
    verification: "G0 门禁 + DB 自愈"
    permission: "自动——无需 Owner"
    audit_level: "ProvenanceStandard"

  pre_commit_failure:
    trigger: "pre-commit FAIL（GATE-18 拦截）"
    method: "discard（git checkout -- {changed_files}）"
    verification: "G0 门禁（文件恢复确认）"
    permission: "自动——无需 Owner"
    audit_level: "ProvenanceStandard"

  task_failure:
    trigger: "任务 G7 门禁 FAIL 且修复 3 次仍失败"
    method: "multi_commit（git revert {commit_sha1}..{commit_sha2}）"
    verification: "G0 门禁 + 全量 DB 恢复"
    permission: "自动——无需 Owner"
    audit_level: "ProvenanceStandard"

  manual_rollback:
    trigger: "Owner 手动触发（CLI or BREAK_GLASS token）"
    method: "hard_reset（git reset --hard {commit_sha}）"
    verification: "G0-G7 全量门禁"
    permission: "token-gated——60s 过期 token"
    audit_level: "ProvenanceFull"
```

---
