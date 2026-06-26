---
module_id: KE-2486
status: active
title: 8.4 完整迭代伪代码
category: module_blueprint
ttl: permanent
---

# 8.4 完整迭代伪代码

8.4 完整迭代伪代码

```python
def run_full_audit(orchestrator: AuditOrchestrator) -> GlobalAuditReport:
    git_backup = GitBackupManager()
    audit_id = f"audit-{datetime.now():%Y%m%d-%H%M}"
    git_backup.create_pre_tag(audit_id)

    global_converged = False
    global_round = 0
    max_global_rounds = 3

    while not global_converged and global_round < max_global_rounds:
        global_round += 1

        # Phase 1: 发现
        discovery_result = orchestrator.run_phase_discovery()

        # Phase 2: 审计（结构 + 语义）
        for dim in orchestrator.structural_dimensions:
            orchestrator.run_dimension_until_converged_or_stuck(dim)
        orchestrator.run_dimension_until_converged_or_stuck(DIM-SEMANTIC-001)

        # Phase 3: 修复
        orchestrator.run_phase_repair(discovery_result)

        # Phase 4: Git 快照（修复后）
        git_backup.create_repaired_tag(audit_id, global_round)

        # Phase 5: 红白对抗
        red_blue = orchestrator.run_red_blue_adversarial()

        if red_blue.blocked_rate == 1.0:
            # Phase 6: 全局收敛判定
            if orchestrator.all_dimensions_converged():
                global_converged = True
                git_backup.create_converged_tag(audit_id)
        else:
            # 对抗未通过 → 修复绕过点 → 重试
            orchestrator.fix_bypasses(red_blue.bypassed_scenarios)

    return orchestrator.final_report(
        converged=global_converged,
        total_rounds=global_round,
        pending_human_decisions=orchestrator.escalation_queue
    )
```

---
