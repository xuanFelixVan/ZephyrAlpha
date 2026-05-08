---
task_id: "TASK-KB-0022"
source_blueprint: "MOD-KB-001"
source_section: "§7.7 Human-Gated 权限模型 + §7.8 灾难恢复 + §7.9 部分回滚与事务"

title: "Human-Gated 三层权限模型实现——AUTO/HUMAN_GATED/OWNER_ONLY + 灾难恢复方案落地 + 部分回滚事务机制"
description: |
  实现蓝图 §7.7/§7.8/§7.9 定义的三种运维机制：
  (1) §7.7 Human-Gated 三层写入权限模型（对标 ISSUE-008）：
     - L1 AUTO：A1/A4/A5/A6/A7/B3 类别——纯事实/自动阻断发现→系统自动生成→直接入库→Owner 零参与（示例："3587个误报源于一个多余的反斜杠"）
     - L2 HUMAN_GATED：A2/A3/A8/B1/B2 类别——决策/策略/推断→系统生成草稿→推送 Owner yes/no→确认后入库
       · S1 系统自动生成 KE/KB 草稿（格式符合 §3.2.2/§3.11，标记 status:DRAFT）
       · S2 推送 Owner 通知（Feishu MCP/Webhook 可配置，含对比表——回复 Y 确认 / N 驳回）
       · Owner 时间预算 ≤12 min/月（A2确认 2次/月×30s + B1/B2 3次/月×30s + A3 5次/月×30s + Track C 2次/月×60s + 冲突裁决 1次/月×120s = ~13次/月·≤12min）
       · 拒绝冷却机制：同类型建议被 Owner 拒绝≥3次→该类型 30d 冷却期→冷却期内不再推送→冷却结束重置计数——对标 macOS "Snooze for 1 hour"
       · pending_approval 字段追加到 KE Schema frontmatter——(pending_approval:bool, pending_since:datetime, approval_deadline: datetime (7d)）
     - L3 OWNER_ONLY：Track C（C1/C2/C3）——Owner 画像→仅 Owner 可创建/修改，系统仅可建议——完全参与
  (2) §7.8 灾难恢复——三重备份(ChromaDB .pkl/LLF .md/SQLite .db)→每天1次backup或每周full → restore全自动化——从.sql备份恢复→push到ChromaDB→re-index LLF markdown——RTO<25min, RPO=0（MD在Git零丢失）
  (3) §7.9 部分回滚事务——上下文 in_memory→差量回滚 delete KE/unlink→JSON re-apply up to 5 rollback state——reversible_operation 包装三元：SUCCESS→commit→失败→reverse function apply
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\human_gated.py"
    description: "新建——L1 AUTO/L2 HUMAN_GATED/L3 OWNER_ONLY 三层权限 + per-category fine-grained + confirm_moderation_request()"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\disaster_recovery.py"
    description: "新建——backup_all() (md+db+chroma)→restore_from_backup()→auto_restore_if_corrupt(detected)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\undo_stack.py"
    description: "新建——JsonLine undo_stack(最多5状态) + reversible_operation(reverse_fn) + commit/fail 两动作"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\human_gated.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\disaster_recovery.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\undo_stack.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§7.7 Human-Gated权限 + §7.8 灾难恢复 + §7.9 部分回滚与事务"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 10000
timeout_minutes: 40

acceptance_criteria:
  - "human_gated.py 实现 L1/L2/L3 三层权限判定——`check_write_permission(category, ke_source) → AUTO | HUMAN_GATED | OWNER_ONLY`"
  - "L1 AUTO 条目——category∈{A1,A4,A5,A6,A7,B3}→系统直接入库→status SUBMITTED 无需Owner确认"
  - "L2 HUMAN_GATED——category∈{A2,A3,A8,B1,B2}→生成草稿→push Owner yes/no→Y→入库 SUBMITTED / N→REJECTED+记录驳回理由→系统学习偏好→更新 Track C"
  - "L3 OWNER_ONLY——category∈{C1,C2,C3}→仅Owner可创建修改——系统仅可建议"
  - "pending_approval 字段(KE frontmatter)——pending_approval:bool + pending_since:datetime + approval_deadline(7d)"
  - "拒绝冷却——同类型被拒≥3次→30d冷却期→期间系统停止推送同类型"
  - "Owner 月耗时预算 ≤12min——L2十三条审批流+冲突裁决→冷却机制防止骚扰"
  - "disaster_recovery.py backup_all() 产生 (sql.bak + markdown.tar.gz + chroma_ke_entries.pkl + chroma_vibe_rules.pkl + chroma_blueprints.pkl + chroma_failure_patterns.pkl)"
  - "disaster_recovery.py restore_from_backup() 在损坏检测 verified 后自动触发"
  - "undo_stack.py reversible_operation(forward_fn, reverse_fn)→(result, rollback_fn)——rollback_fn callable(spec)反向执行"
  - "最多容纳5个回退状态——超出→抛出 UndoStackFull"

rollback_instructions: |
  1. 删除 src/zephyr/kb/human_gated.py, disaster_recovery.py, undo_stack.py
  2. 若备份目录已产生——删除 backup 子目录
  3. 若 per_category 权限表已建 SQL——手动 ALTER TABLE ——

depends_on: ["TASK-KB-0021"]
blocked_by: []
status: "created"
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-KB-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
