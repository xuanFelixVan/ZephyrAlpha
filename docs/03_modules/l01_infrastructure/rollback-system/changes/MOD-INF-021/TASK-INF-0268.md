---
task_id: "TASK-INF-0268"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 10 + §6.17 B123-B130 + 决策 D-021-38 + §9 exit codes 40-46"
title: "对抗性安全——Runbook/KnowGoodState/陈旧度/凭据轮替/WAL/冲突检测/意图存档/滥用检测"
description: |
  实现 Phase 10 对抗性安全基础设施，覆盖 B123-B130：
  B123 Runbook 自动生成——回滚操作从审计日志自动生成下次可用的 Runbook
  B124 knowngoodstate 已验证正确状态收据——回滚后自动声明当前状态为已知好状态
  B125 回滚目标陈旧度——回滚目标 >30天未验证 → exit 42 (TARGET_STALE_OVER_30D)
  B126 凭据自动轮替——回滚触发 credentials rotation → 关联 exit 43 (CREDENTIAL_LEAK_DETECTED)
  B127 Rollback WAL——回滚预写日志确保回滚本身可回滚 (exit 45 ROLLBACK_WAL_INCOMPLETE)
  B128 多 Agent 冲突检测——两个 AI agent 同时修改文件 → 冲突仲裁 → 串行化
  B129 意图存档——回滚前原始操作意图 (why was this done) 不可丢失 (exit 46 INTENT_ARCHIVE_PRUNE)
  B130 回滚滥用检测——检测 unconventionally 高频回滚模式 → exit 44 ROLLBACK_ABUSE_DETECTED
  涵盖 R21-R30 AI 主动对抗与沙盒穿透风险。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\runbook_generator.py"
    description: "Runbook 自动生成——审计日志 → 可复用回滚操作手册"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\knowngoodstate_ledger.py"
    description: "KnowGoodState——回滚后自动声明已验证正确状态"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_target_staleness.py"
    description: "回滚目标陈旧度——>30天 → exit 42 + 告警"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\credential_rotation_trigger.py"
    description: "凭据自动轮替——回滚后触发密钥 rotation"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_wal.py"
    description: "Rollback WAL——回滚预写日志 (回滚本身的回滚可逆)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\cross_agent_conflict_detector.py"
    description: "多 Agent 冲突检测——双写冲突 → 仲裁 → 串行化"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\intent_archiver.py"
    description: "意图存档——why this was done → 不可丢失"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_abuse_detector.py"
    description: "回滚滥用检测——unusually 高频回滚 → exit 44 + L3 Kill"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\runbook_generator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\knowngoodstate_ledger.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_target_staleness.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\credential_rotation_trigger.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_wal.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\cross_agent_conflict_detector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\intent_archiver.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_abuse_detector.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.17 B123-B130 对抗性安全 + D-021-38 + R21-R30"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 16000
timeout_minutes: 60
acceptance_criteria:
  - "runbook: 审计日志自动生成下次可用的 Runbook (markdown)"
  - "knowngoodstate: 回滚后 ledgdr/verified 条目 → sha256 block"
  - "staleness: 回滚目标 >30d → exit 42 → Owner confirm"
  - "credential: 回滚触发 credentials manager API → 自动轮替"
  - "wal: 每个刀片操作写 WAL entry → 回滚自身可逆"
  - "cross_agent: 双 agent 写同文件 → 冲突仲裁 → 排他锁"
  - "intent_archive: agent 填 why_reverted → hash 永久存储"
  - "abuse_detector: ⌀ 回滚/agent > 10 / ⌀  → exit 44 → ptrace"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\runbook_generator.py
  2. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\knowngoodstate_ledger.py
  3. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_target_staleness.py
  4. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\credential_rotation_trigger.py
  5. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_wal.py
  6. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\cross_agent_conflict_detector.py
  7. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\intent_archiver.py
  8. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_abuse_detector.py
depends_on:
  - "TASK-INF-0267"
blocked_by: []
status: "done"
tags_fn: ["infra"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-021"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
