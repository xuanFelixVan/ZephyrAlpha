---
module_id: KE-module_blu-2_2____________________d-021-0-000
title: 2.2 自动回滚触发 + 失败信号分类（决策 D-021-02 + D-021-05）
category: module_blueprint
---

# 2.2 自动回滚触发 + 失败信号分类（决策 D-021-02 + D-021-05）

2.2 自动回滚触发 + 失败信号分类（决策 D-021-02 + D-021-05）

> **决策 D-021-02（修订）**：auto_guard 后验失败时自动触发回滚，无需 Owner 确认。回滚操作写入审计日志。Owner 事后异步审阅。
>
> **决策 D-021-05（新增）**：失败信号按严重程度三分类，不同类型触发不同的回滚策略。克服 B15 中"所有 FAIL 一视同仁"的问题。
>
> **决策依据**：与 MOD-INF-018 先干后验模式一致。10+ 并发对话不可能等 Owner 确认。不同失败类型的恢复策略完全不同——格式错误应该重试，数据泄露应该立即回滚。

```yaml
failure_signal_classifier:
  hard_failure:
    sources: ["drift detected", "CI FAIL", "G6 secrets_detection", "circuit_breaker OPEN"]
    action: "立即回滚——full_revert"
    retry: "0 次"
    notification: "立即通知 Owner + 标记为 CRITICAL"

  soft_failure:
    sources: ["G0 文件存在性", "G1 YAML 语法", "G2 frontmatter", "G3 encoding"]
    action: "等待 3 次 retry（agent auto-fix）→ 仍失败则 partial_revert"
    retry: "3 次"
    notification: "第 3 次失败后通知 Owner"

  transient:
    sources: ["timeout", "network error", "SQLite locked"]
    action: "仅重试，不触发回滚"
    retry: "5 次"
    notification: "第 5 次失败后通知 Owner"

auto_rollback_flow:
  trigger: "auto_guard 后验失败（已分类为 hard/soft/transient）"

  step_0_evaluate:
    who: "RollbackExecutor"
    what: "失败评估——检查是否满足 forward-fix 条件"
    forward_fix_condition: "变更范围 ≤ 3 文件 AND soft_failure AND 文件未被锁定"
    forward_fix_action: "优先让 Agent 产生 FIX-{sha} commit 直接修正（不再 revert）"
    forward_fix_fallback: "连续 2 次 forward-fix 失败 → 进入 rollback 流程"

  step_0_preflight:
    who: "RollbackExecutor"
    what: "安全预检——working tree状态 / HEAD状态 / remote同步状态 / 依赖影响分析"
    dirty_tree: "git stash → 暂存未提交变更"
    detached_head: "拒绝自动回滚 → DEFER_TO_HUMAN"
    remote_ahead: "git pull --rebase 后再预检"
    dependency_impact: "从 blueprint-registry 加载依赖图 → 标记受影响模块"

  step_0b_preview:
    who: "RollbackExecutor"
    what: "生成回滚预览——受影响文件列表 + 冲突风险评估"
    output: "{changed_files: [...], conflict_risk: low/medium/high, dependency_impact: [...]}"

  step_0c_kill_escalation:
    who: "KillSwitchManager"
    what: "评估是否需要升级 Kill 级别"
    L1_Session_Kill: "暂停该 agent session 的所有写操作（默认）"
    L2_Skill_Kill: "禁写特定类型的文件（YAML/Python 等）——3 次重试失败后自动升级"
    L3_Global_Kill: "全量 hard_reset——需要 token 且仅 Owner 可触发"

  step_1_acquire_lock:
    who: "RollbackExecutor"
    what: "获取全局回滚锁（rollback.lock）+ 写入 in_flight 文件"
    execution_id: "UUIDv7——全局唯一回滚执行 ID"
    in_flight_file: ".zephyr/rollback_in_flight/{execution_id}.json"
    queue: "并发请求按优先级排队（P0 hard_failure 跳队），超时 10s 返回 BUSY"
    budget_check: "并发 ≤ 3 AND 日配额 ≤ 20 → 超 budget 则拒绝 → DEFER_TO_HUMAN"

  step_2_rollback:
    who: "RollbackExecutor (via RollbackStateMachine)"
    what: "按分类执行对应回滚策略——每步独立状态追踪 + 幂等保护"
    hard_failure: "git revert --no-edit {commit_sha}"
    soft_failure: "partial_revert({commit_sha}, file_globs)"
    discard: "git checkout -- {changed_files}"
    note: "不等待人类确认"
    crash_protection: "每步完成后 fsync + 更新 in_flight 文件 → 崩溃恢复从最后 SUCCESS 步继续"

  step_3_verify:
    who: "RollbackVerifier"
    what: "回滚后验证——G0 门禁 + __pycache__ 清理 + DB 一致性修复 + 逐行 differential check"

  step_4_audit:
    who: "Audit Trail (MOD-INF-020)"
    what: "回滚操作写入审计日志（ProvenanceStandard 级别 + HMAC-SHA256 签名）"

  step_5_post_process:
    who: "
